import asyncio
import unittest
from lab import cancellation_probe, run_scenario


class AdmissionContracts(unittest.IsolatedAsyncioTestCase):
    async def test_overload_preserves_work_and_bounds(self):
        for policy in ("unbounded", "bounded", "concurrency"):
            with self.subTest(policy=policy):
                run = await run_scenario(policy, rate=200, duration=0.05,
                                         workers=2, queue_cap=2, service_seconds=0.03)
                self.assertTrue(all(run["checks"].values()))
                self.assertEqual(run["metrics"]["attempts"], 10)
                if policy == "unbounded":
                    self.assertEqual(run["metrics"]["rejected"], 0)

    async def test_await_put_transfers_pressure_to_producer(self):
        queue = asyncio.Queue(maxsize=1)
        await queue.put("first")
        entered = asyncio.Event()

        async def producer():
            entered.set()
            await queue.put("second")

        task = asyncio.create_task(producer())
        await entered.wait()
        self.assertFalse(task.done())
        self.assertEqual(queue.get_nowait(), "first")
        queue.task_done()
        await asyncio.wait_for(task, 1)
        self.assertEqual(queue.get_nowait(), "second")
        queue.task_done()
        await asyncio.wait_for(queue.join(), 1)

    async def test_client_timeout_can_leave_work_running(self):
        probe = await cancellation_probe(True)
        self.assertTrue(probe["at_timeout"]["slot_held"])
        self.assertTrue(probe["after_cleanup"]["completed"])

    async def test_cooperative_cancellation_releases_slot(self):
        probe = await cancellation_probe(False)
        self.assertTrue(probe["at_timeout"]["task_cancelled"])
        self.assertTrue(probe["after_cleanup"]["released"])


if __name__ == "__main__":
    unittest.main()
