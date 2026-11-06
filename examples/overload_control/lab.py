"""Controlled asyncio admission experiment; no network or CPU capacity benchmark."""
import argparse
import asyncio
import hashlib
import json
import math
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "results"


def percentiles(values):
    """Nearest-rank quantiles; empty populations remain null."""
    values = sorted(values)
    return {f"p{p}": values[math.ceil(len(values) * p / 100) - 1] if values else None
            for p in (50, 95, 99)}


async def run_scenario(policy, rate, duration=1.2, workers=4, queue_cap=12,
                       service_seconds=0.04):
    if policy not in ("unbounded", "bounded", "concurrency"):
        raise ValueError(policy)
    if min(rate, duration, workers, queue_cap, service_seconds) <= 0:
        raise ValueError("All workload parameters must be positive")
    loop = asyncio.get_running_loop()
    epoch = loop.time()
    now = lambda: loop.time() - epoch
    queue = asyncio.Queue(maxsize=queue_cap if policy == "bounded" else 0)
    records, tasks = [], []
    active = peak_active = peak_queue = reserved = 0

    async def execute(record):
        nonlocal active, peak_active, reserved
        record["started_at"] = now()
        active += 1
        peak_active = max(peak_active, active)
        try:
            await asyncio.sleep(service_seconds)
            record["result"] = record["id"] * 3 + 7
            record["finished_at"] = now()
        finally:
            active -= 1
            if policy == "concurrency":
                reserved -= 1

    async def consume():
        while True:
            record = await queue.get()
            try:
                if record is None:
                    return
                await execute(record)
            finally:
                queue.task_done()

    consumers = ([asyncio.create_task(consume()) for _ in range(workers)]
                 if policy != "concurrency" else [])
    attempts = int(round(rate * duration))
    for item_id in range(attempts):
        scheduled = item_id / rate
        await asyncio.sleep(max(0, scheduled - now()))
        record = {"id": item_id, "scheduled_at": scheduled, "offered_at": now(),
                  "accepted": False}
        records.append(record)
        if policy == "concurrency":
            # Reserve before spawning: task creation itself is not slot acquisition.
            if reserved < workers:
                reserved += 1
                record["accepted"] = True
                tasks.append(asyncio.create_task(execute(record)))
        else:
            try:
                queue.put_nowait(record)
                record["accepted"] = True
                peak_queue = max(peak_queue, queue.qsize())
            except asyncio.QueueFull:
                pass
        if not record["accepted"]:
            record["rejected_at"] = now()

    await asyncio.sleep(max(0, duration - now()))
    arrival_end = now()
    backlog = sum(r["accepted"] and "finished_at" not in r for r in records)
    queued_at_end, active_at_end = queue.qsize(), active
    if consumers:
        await queue.join()
        drained_at = now()
        for _ in consumers:
            await queue.put(None)
        await asyncio.gather(*consumers)
    else:
        await asyncio.gather(*tasks)
        drained_at = now()
    accepted = [r for r in records if r["accepted"]]
    rejected = [r for r in records if not r["accepted"]]
    checks = {
        "outcomes_accounted": len(accepted) + len(rejected) == attempts,
        "unique_ids": len({r["id"] for r in records}) == attempts,
        "accepted_completed_correctly": all(r.get("result") == r["id"] * 3 + 7
                                            and "finished_at" in r for r in accepted),
        "timestamps_ordered": all(r["scheduled_at"] <= r["offered_at"] <= r["started_at"]
                                  <= r["finished_at"] for r in accepted)
                              and all(r["scheduled_at"] <= r["offered_at"] <= r["rejected_at"]
                                      for r in rejected),
        "active_bounded": peak_active <= workers,
        "queue_bounded": policy != "bounded" or peak_queue <= queue_cap,
        "no_business_queue_in_concurrency_mode": policy != "concurrency" or peak_queue == 0,
        "drained_and_released": active == reserved == queue.qsize() == 0
                                and all(t.done() for t in consumers + tasks),
    }
    assert all(checks.values()), checks
    ms = lambda field1, field2, population: percentiles(
        [(r[field2] - r[field1]) * 1000 for r in population])
    metrics = {
        "attempts": attempts, "accepted": len(accepted), "rejected": len(rejected),
        "completed": len(accepted), "arrival_phase_seconds": arrival_end,
        "actual_attempts_per_second": attempts / arrival_end,
        "completed_during_arrival_per_second": sum(r["finished_at"] <= arrival_end
                                                   for r in accepted) / arrival_end,
        "backlog_at_arrival_end": backlog, "queue_at_arrival_end": queued_at_end,
        "active_at_arrival_end": active_at_end,
        "peak_active": peak_active, "peak_queue": peak_queue,
        "drain_ms": (drained_at - arrival_end) * 1000,
        "total_seconds": drained_at,
        "completion_ms": ms("offered_at", "finished_at", accepted),
        "scheduled_completion_ms": ms("scheduled_at", "finished_at", accepted),
        "queue_wait_ms": ms("offered_at", "started_at", accepted),
        "service_ms": ms("started_at", "finished_at", accepted),
        "rejection_ms": ms("offered_at", "rejected_at", rejected),
        "generator_lag_ms": ms("scheduled_at", "offered_at", records),
        "generator_max_lag_ms": max(r["offered_at"] - r["scheduled_at"] for r in records) * 1000,
    }
    return {"policy": policy, "target_rate": rate, "duration": duration,
            "workers": workers, "waiting_queue_cap": queue_cap if policy == "bounded" else None,
            "configured_service_seconds": service_seconds, "metrics": metrics,
            "checks": checks, "records": records}


async def cancellation_probe(shielded, timeout=0.02):
    started, release = asyncio.Event(), asyncio.Event()
    state = {"slot_held": False, "completed": False, "released": False}

    async def operation():
        state["slot_held"] = True
        started.set()
        try:
            await release.wait()
            state["completed"] = True
        finally:
            state["slot_held"] = False
            state["released"] = True

    loop = asyncio.get_running_loop()
    task = asyncio.create_task(operation())
    await started.wait()
    begin = loop.time()
    try:
        await asyncio.wait_for(asyncio.shield(task) if shielded else task, timeout)
        raise AssertionError("Expected local timeout")
    except TimeoutError:
        snapshot = dict(state, task_done=task.done(), task_cancelled=task.cancelled())
        elapsed = loop.time() - begin
    release.set()
    await asyncio.gather(task, return_exceptions=True)
    assert snapshot["slot_held"] == shielded
    assert snapshot["task_done"] != shielded
    assert snapshot["task_cancelled"] != shielded
    assert state["completed"] == shielded and state["released"] and not state["slot_held"]
    return {"shielded": shielded, "timeout_seconds": timeout, "observed_wait_seconds": elapsed,
            "at_timeout": snapshot, "after_cleanup": state, "checks_passed": True}


async def main():
    runs = []
    policies = ["unbounded", "bounded", "concurrency"]
    for repeat in range(3):
        for rate in (40, 120, 240):
            offset = (repeat + (40, 120, 240).index(rate)) % 3
            for policy in policies[offset:] + policies[:offset]:
                run = await run_scenario(policy, rate)
                run["repeat"] = repeat + 1
                runs.append(run)
                m = run["metrics"]
                print(f"{repeat + 1} {rate:3} {policy:11} accepted={m['accepted']:3} "
                      f"rejected={m['rejected']:3} p99={m['completion_ms']['p99']:.1f}ms", flush=True)
    probes = [await cancellation_probe(shielded) for _ in range(3) for shielded in (True, False)]
    result = {"recorded_at": datetime.now(timezone.utc).isoformat(),
              "runtime": {"python": sys.version, "platform": platform.platform()},
              "scope": "Real asyncio timers and local admission only; sleep is synthetic resource occupancy.",
              "quantiles": "nearest rank; per-run accepted population, rejects separate; no averaged P99",
              "runs": runs, "cancellation_probes": probes}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: {len(runs)} runs, {sum(len(r['records']) for r in runs)} attempts, "
          f"{sum(len(r['checks']) for r in runs)} invariant checks, {len(probes)} timeout probes.")


def freeze_manifest():
    files = ["lab.py", "test_lab.py", "results/results.json", "results/tests.txt"]
    entries = {}
    for name in files:
        file = Path(__file__).resolve().parent / name
        raw = file.read_bytes()
        entries[file.relative_to(ROOT).as_posix()] = {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
    (OUT / "manifest.json").write_text(json.dumps({"recorded_date": "2026-10-19", "files": entries}, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze-manifest", action="store_true", help="Freeze code, result and saved test output after running tests")
    if parser.parse_args().freeze_manifest:
        freeze_manifest()
    else:
        asyncio.run(main())
