"""Local memory lifecycle contracts: SQLite authority, derived index and cache."""
import argparse
import hashlib
import json
import platform
import sqlite3
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

DIRECTORY = Path(__file__).resolve().parent
ROOT = DIRECTORY.parents[1]


def fingerprint(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class Store:
    def __init__(self, folder, events):
        self.folder, self.events = folder, events
        self.db = sqlite3.connect(folder / "authority.sqlite")
        self.db.row_factory = sqlite3.Row
        self.derived = sqlite3.connect(folder / "derived.sqlite")
        self.derived.row_factory = sqlite3.Row
        self.clock, self.available = 100, True
        self.db.executescript("""
          CREATE TABLE IF NOT EXISTS members(tenant TEXT, subject TEXT, active INTEGER, PRIMARY KEY(tenant,subject));
          CREATE TABLE IF NOT EXISTS sources(id TEXT PRIMARY KEY, tenant TEXT, owner TEXT, kind TEXT,
            revision INTEGER, value_hash TEXT, confirmed INTEGER, active INTEGER);
          CREATE TABLE IF NOT EXISTS memories(id TEXT PRIMARY KEY, tenant TEXT, owner TEXT, slot TEXT,
            version INTEGER, value TEXT, kind TEXT, source_id TEXT, source_revision INTEGER,
            status TEXT, expires_at INTEGER);
          CREATE TABLE IF NOT EXISTS grants(memory_id TEXT, subject TEXT, active INTEGER, PRIMARY KEY(memory_id,subject));
        """)
        self.derived.executescript("""
          CREATE TABLE IF NOT EXISTS search_index(id TEXT PRIMARY KEY, tenant TEXT, version INTEGER, value TEXT);
          CREATE TABLE IF NOT EXISTS cache(tenant TEXT, subject TEXT, query TEXT, payload TEXT,
            PRIMARY KEY(tenant,subject,query));
        """)

    def log(self, event, **fields):
        self.events.append({"sequence": len(self.events) + 1, "event": event, **fields})

    def member(self, context):
        row = self.db.execute("SELECT active FROM members WHERE tenant=? AND subject=?", context).fetchone()
        return bool(row and row[0])

    def row(self, mid):
        row = self.db.execute("SELECT * FROM memories WHERE id=?", (mid,)).fetchone()
        return dict(row) if row else None

    def source_valid(self, row):
        source = self.db.execute("SELECT * FROM sources WHERE id=?", (row["source_id"],)).fetchone()
        return bool(source and source["active"] and source["revision"] == row["source_revision"]
                    and source["tenant"] == row["tenant"] and source["owner"] == row["owner"]
                    and {"user": "preference", "tool": "observation", "model": "hypothesis"}.get(source["kind"]) == row["kind"]
                    and (row["kind"] == "hypothesis" or source["confirmed"])
                    and source["value_hash"] == fingerprint(row["value"]))

    def live(self, row):
        return bool(row and row["status"] == "active" and row["value"] is not None
                    and self.clock < row["expires_at"] and self.source_valid(row))

    def can_read(self, context, row):
        if not self.member(context) or row["tenant"] != context[0]:
            return False
        grant = self.db.execute("SELECT active FROM grants WHERE memory_id=? AND subject=?",
                                (row["id"], context[1])).fetchone()
        return row["owner"] == context[1] or bool(grant and grant[0])

    def write(self, context, mid, value, kind, source_id, revision=1, ttl=20, expected=None):
        # A deliberately small admission policy, not a general fact extractor.
        if (type(value) is not str or not 1 <= len(value) <= 160 or not value.strip()
                or type(ttl) is not int or not 1 <= ttl <= 1000
                or type(revision) is not int or revision < 1
                or kind not in ("preference", "observation", "hypothesis")):
            return "invalid"
        try:
            hashed = fingerprint(value)
        except UnicodeError:
            return "invalid"
        source = self.db.execute("SELECT * FROM sources WHERE id=?", (source_id,)).fetchone()
        if not self.member(context):
            return "denied"
        if not source or (source["tenant"], source["owner"]) != context or not source["active"]:
            return "source_denied"
        if source["revision"] != revision or source["value_hash"] != hashed:
            return "source_mismatch"
        compatible = {"user": "preference", "tool": "observation", "model": "hypothesis"}
        if compatible.get(source["kind"]) != kind or (kind != "hypothesis" and not source["confirmed"]):
            return "needs_evidence"
        status = "candidate" if kind == "hypothesis" else "active"
        prior = self.row(mid)
        if prior and (prior["tenant"], prior["owner"]) != context:
            return "denied"
        with self.db:
            if expected is None:
                if prior:
                    return "exists"
                self.db.execute("INSERT INTO memories VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                                (mid, *context, "language", 1, value, kind, source_id, revision, status, self.clock + ttl))
            else:
                if type(expected) is not int or expected < 1:
                    return "invalid"
                changed = self.db.execute("""UPDATE memories SET version=version+1,value=?,kind=?,source_id=?,
                    source_revision=?,status=?,expires_at=? WHERE id=? AND tenant=? AND owner=?
                    AND version=? AND status IN ('active','candidate')""",
                    (value, kind, source_id, revision, status, self.clock + ttl, mid, *context, expected)).rowcount
                if changed != 1:
                    return "conflict"
        self.log("authority_written", id=mid, version=self.row(mid)["version"], status=status)
        return status

    def capture(self, mid):
        row = self.row(mid)
        return dict(row) if self.live(row) else None

    def publish(self, snapshot):
        current = self.row(snapshot["id"]) if snapshot else None
        if (not self.available or not self.live(current) or current["version"] != snapshot["version"]
                or current["value"] != snapshot["value"] or current["tenant"] != snapshot["tenant"]):
            self.log("projection_rejected")
            return False
        with self.derived:
            self.derived.execute("INSERT INTO search_index VALUES(?,?,?,?) ON CONFLICT(id) DO UPDATE SET tenant=excluded.tenant,version=excluded.version,value=excluded.value",
                                 (current["id"], current["tenant"], current["version"], current["value"]))
            self.derived.execute("DELETE FROM cache")
        self.log("projection_published", id=current["id"], version=current["version"])
        return True

    def retrieve(self, context, query="language", cached=True):
        if not self.available:
            self.log("authority_unavailable")
            return {"status": "unavailable", "items": []}
        if not self.member(context):
            return {"status": "denied", "items": []}
        hit = self.derived.execute("SELECT payload FROM cache WHERE tenant=? AND subject=? AND query=?", (*context, query)).fetchone() if cached else None
        if hit:
            candidates = json.loads(hit[0]); path = "cache"
        else:
            candidates = [dict(r) for r in self.derived.execute("SELECT * FROM search_index WHERE tenant=?", (context[0],)) if query in r["value"]]
            path = "index"
            if cached:
                with self.derived:
                    self.derived.execute("INSERT OR REPLACE INTO cache VALUES(?,?,?,?)", (*context, query, json.dumps(candidates)))
        items = []
        for candidate in candidates:
            row = self.row(candidate["id"])
            if (self.live(row) and self.can_read(context, row) and row["version"] == candidate["version"]
                    and query in row["value"]):
                # Hydrate canonical content, never the copied index/cache body.
                items.append({k: row[k] for k in ("id", "version", "value", "kind", "source_id", "source_revision")})
        self.log("retrieved", path=path, subject=context[1], returned=[r["id"] for r in items])
        return {"status": "ok", "items": items}

    def delete(self, context, mid, expected):
        if type(expected) is not int or expected < 1 or not self.member(context):
            return False
        with self.db:
            changed = self.db.execute("""UPDATE memories SET version=version+1,value=NULL,source_id=NULL,
              source_revision=NULL,status='tombstone' WHERE id=? AND tenant=? AND owner=? AND version=?
              AND status IN ('active','candidate')""", (mid, *context, expected)).rowcount
        self.log("delete_requested", id=mid, applied=changed == 1)
        return changed == 1

    def purge(self, mid):
        with self.derived:
            self.derived.execute("DELETE FROM search_index WHERE id=?", (mid,))
            self.derived.execute("DELETE FROM cache")
        self.log("derived_rows_purged", id=mid)

    def snapshot(self):
        return {"memories": [dict(r) for r in self.db.execute("SELECT * FROM memories ORDER BY id")],
                "sources": [dict(r) for r in self.db.execute("SELECT * FROM sources ORDER BY id")],
                "index": [dict(r) for r in self.derived.execute("SELECT * FROM search_index ORDER BY id")],
                "cache": [dict(r) for r in self.derived.execute("SELECT * FROM cache ORDER BY tenant,subject,query")]}

    def close(self):
        self.db.close(); self.derived.close()


def run_case(name):
    checks, events, observations, reads, read_guarantees = {}, [], [], [], []
    def check(label, value):
        checks[label] = bool(value)
        if not value:
            raise AssertionError((name, label))
    cache = (ROOT / ".cache/memory-governance").resolve()
    if not cache.is_relative_to(ROOT.resolve()):
        raise ValueError("Experiment cache must stay within the workspace")
    cache.mkdir(parents=True, exist_ok=True)
    owner, collaborator, outsider = ("t1", "u1"), ("t1", "u2"), ("t2", "u3")
    with tempfile.TemporaryDirectory(prefix="run-", dir=cache) as temporary:
        folder = Path(temporary).resolve()
        if not folder.is_relative_to(cache):
            raise ValueError("Temporary database directory must stay within the experiment cache")
        store = Store(folder, events)
        try:
            with store.db:
                store.db.executemany("INSERT INTO members VALUES(?,?,1)", (owner, collaborator, outsider))
                for sid, kind, value, confirmed in (("s1", "user", "language:zh", 1), ("s2", "user", "language:en", 1),
                         ("sm", "model", "language:inferred", 0), ("st", "tool", "language:pending", 0),
                         ("stc", "tool", "language:verified", 1)):
                    store.db.execute("INSERT INTO sources VALUES(?,?,?,?,?,?,?,1)", (sid, *owner, kind, 1, fingerprint(value), confirmed))
            def create():
                check("created_active", store.write(owner, "m1", "language:zh", "preference", "s1") == "active")
                check("initial_projection", store.publish(store.capture("m1")))
            def read(context=owner, cached=True):
                result = store.retrieve(context, cached=cached); observations.append(result)
                evidence = {"clock":store.clock,"context":list(context),"result":result,"authority_rows":[]}
                for item in result["items"]:
                    row = store.row(item["id"])
                    source = store.db.execute("SELECT * FROM sources WHERE id=?", (row["source_id"],)).fetchone() if row else None
                    member = store.db.execute("SELECT active FROM members WHERE tenant=? AND subject=?", context).fetchone()
                    grant = store.db.execute("SELECT active FROM grants WHERE memory_id=? AND subject=?", (item["id"],context[1])).fetchone()
                    expected = {k:row[k] for k in ("id","version","value","kind","source_id","source_revision")} if row else None
                    valid = bool(row and item == expected and row["tenant"] == context[0]
                        and member and member[0] and (row["owner"] == context[1] or (grant and grant[0]))
                        and row["status"] == "active" and row["expires_at"] > store.clock
                        and source and source["active"] and source["revision"] == row["source_revision"]
                        and (source["tenant"],source["owner"]) == (row["tenant"],row["owner"])
                        and (source["kind"],row["kind"]) in (("user","preference"),("tool","observation"),("model","hypothesis"))
                        and (row["kind"] == "hypothesis" or source["confirmed"])
                        and source["value_hash"] == fingerprint(item["value"]))
                    read_guarantees.append(valid)
                    evidence["authority_rows"].append({"memory":row,"source":dict(source) if source else None,
                        "member_active":bool(member and member[0]),"grant_active":bool(grant and grant[0])})
                reads.append(evidence)
                return result["items"]
            if name == "user_preference":
                create()
                check("exact_value_and_provenance", read() == [{"id": "m1", "version": 1, "value": "language:zh", "kind": "preference", "source_id": "s1", "source_revision": 1}])
            elif name == "model_hypothesis":
                check("retained_as_candidate", store.write(owner, "m1", "language:inferred", "hypothesis", "sm") == "candidate")
                check("not_published", store.capture("m1") is None)
                check("not_retrieved_as_fact", read() == [])
            elif name == "tool_observation":
                check("confirmed_tool_source_accepted", store.write(owner,"m1","language:verified","observation","stc") == "active")
                check("observation_published", store.publish(store.capture("m1")))
                check("exact_observation_source", read() == [{"id":"m1","version":1,"value":"language:verified","kind":"observation","source_id":"stc","source_revision":1}])
            elif name in ("promotion_rejected", "unconfirmed_tool", "source_mismatch", "invalid_input"):
                if name == "promotion_rejected": outcome = store.write(owner, "m1", "language:inferred", "preference", "sm")
                elif name == "unconfirmed_tool": outcome = store.write(owner, "m1", "language:pending", "observation", "st")
                elif name == "source_mismatch": outcome = store.write(owner, "m1", "language:made-up", "preference", "s1")
                else:
                    outcomes = [store.write(owner, "m1", v, "preference", "s1", ttl=t) for v,t in (("language:zh",True),("language:zh",0),(chr(0xD800),20))]
                    check("invalid_inputs_rejected", outcomes == ["invalid"] * 3)
                    outcome = "invalid"
                observations.append({"write_outcome": outcome})
                check("admission_rejected", outcome in ("needs_evidence", "source_mismatch", "invalid"))
                check("no_record_created", store.row("m1") is None)
            elif name == "cas_conflict":
                create()
                other = Store(folder, events)
                try:
                    av, bv = store.row("m1")["version"], other.row("m1")["version"]
                    check("two_connections_read_same_version", av == bv == 1)
                    first = store.write(owner, "m1", "language:en", "preference", "s2", expected=av)
                    second = other.write(owner, "m1", "language:zh", "preference", "s1", expected=bv)
                    observations.append({"first": first, "second": second})
                    check("stale_writer_conflicts", first == "active" and second == "conflict")
                    check("new_value_preserved", store.row("m1")["version"] == 2 and store.row("m1")["value"] == "language:en")
                finally: other.close()
            else:
                create()
                captured = store.capture("m1")
                check("warm_cache", read()[0]["value"] == "language:zh")
                if name in ("stale_projections", "late_update_projection"):
                    check("updated", store.write(owner, "m1", "language:en", "preference", "s2", expected=1) == "active")
                    if name == "late_update_projection": check("old_worker_rejected", store.publish(captured) is False)
                    check("stale_cache_excluded", read() == [])
                    check("stale_index_excluded", read(cached=False) == [])
                    check("new_projection", store.publish(store.capture("m1")))
                    check("new_version_returned", read()[0] == {"id": "m1", "version": 2, "value": "language:en", "kind": "preference", "source_id": "s2", "source_revision": 1})
                elif name == "expiry_boundary":
                    store.clock = 119; check("before_deadline_visible", bool(read()))
                    store.clock = 120; check("at_deadline_hidden", read() == [] and read(cached=False) == [])
                    check("expired_copy_still_physically_present", bool(store.snapshot()["index"]))
                    check("expired_worker_rejected", store.publish(captured) is False)
                elif name in ("grant_revocation", "tenant_boundary", "member_revocation"):
                    with store.db: store.db.execute("INSERT INTO grants VALUES('m1',?,1)", (collaborator[1] if name != "tenant_boundary" else outsider[1],))
                    if name == "tenant_boundary":
                        check("tenant_denies_even_with_grant", read(outsider) == [])
                        with store.derived:
                            store.derived.execute("UPDATE cache SET payload=? WHERE tenant=? AND subject=?",
                                (json.dumps([captured]),*outsider))
                        check("foreign_candidate_in_subject_cache_denied", read(outsider) == [])
                    elif name == "grant_revocation":
                        check("collaborator_initially_allowed", bool(read(collaborator)))
                        with store.db: store.db.execute("UPDATE grants SET active=0")
                        check("revoked_cached_and_index_reads_hidden", read(collaborator) == [] and read(collaborator,False) == [])
                    else:
                        with store.db: store.db.execute("UPDATE members SET active=0 WHERE tenant='t1' AND subject='u1'")
                        check("inactive_member_blocked", read() == [] and observations[-1]["status"] == "denied")
                elif name in ("delete_late_fill", "logical_purge_backup", "reopen_tombstone"):
                    if name == "logical_purge_backup":
                        backup = sqlite3.connect(folder / "backup.sqlite")
                        store.db.backup(backup); backup.close()
                    check("tombstoned", store.delete(owner,"m1",1))
                    check("stale_copies_not_returned", read() == [] and read(cached=False) == [])
                    check("late_worker_rejected", store.publish(captured) is False)
                    check("same_id_not_recreated", store.write(owner,"m1","language:zh","preference","s1") == "exists")
                    check("tombstone_not_updated", store.write(owner,"m1","language:zh","preference","s1",expected=2) == "conflict")
                    if name == "reopen_tombstone":
                        store.close(); store = Store(folder, events)
                        check("tombstone_survives_reopen", store.row("m1")["status"] == "tombstone" and read() == [])
                        check("late_worker_rejected_after_reopen", store.publish(captured) is False)
                    if name == "logical_purge_backup":
                        store.purge("m1")
                        snapshot = store.snapshot()
                        check("active_rows_and_derived_content_cleared", store.row("m1")["value"] is None and snapshot["index"] == snapshot["cache"] == [])
                        backup = sqlite3.connect(folder / "backup.sqlite")
                        try: old = backup.execute("SELECT value FROM memories WHERE id='m1'").fetchone()[0]
                        finally: backup.close()
                        observations.append({"backup_retains_value": old})
                        check("backup_not_erased_by_active_delete", old == "language:zh")
                elif name == "source_withdrawal":
                    with store.db: store.db.execute("UPDATE sources SET confirmed=0 WHERE id='s1'")
                    check("revoked_confirmation_blocks_reads", read() == [] and read(cached=False) == [])
                    check("revoked_confirmation_blocks_worker", store.publish(captured) is False)
                    with store.db: store.db.execute("UPDATE sources SET confirmed=1,kind='model' WHERE id='s1'")
                    check("changed_source_kind_blocks_reads", read() == [] and read(cached=False) == [])
                    check("changed_source_kind_blocks_worker", store.publish(captured) is False)
                    with store.db: store.db.execute("UPDATE sources SET kind='user',active=0,revision=revision+1 WHERE id='s1'")
                    check("withdrawn_source_blocks_copies", read() == [] and read(cached=False) == [])
                    check("withdrawn_source_blocks_worker", store.publish(captured) is False)
                elif name == "source_revision":
                    with store.db: store.db.execute("UPDATE sources SET revision=2,value_hash=? WHERE id='s1'", (fingerprint("language:en"),))
                    check("old_source_revision_hidden", read() == [] and read(cached=False) == [])
                    check("stale_source_write_rejected", store.write(owner,"m1","language:zh","preference","s1",revision=1,expected=1) == "source_mismatch")
                    check("fresh_source_version_admitted", store.write(owner,"m1","language:en","preference","s1",revision=2,expected=1) == "active")
                    check("fresh_source_projection", store.publish(store.capture("m1")))
                    check("source_and_memory_versions_distinct", read()[0] == {"id":"m1","version":2,"value":"language:en","kind":"preference","source_id":"s1","source_revision":2})
                elif name == "authority_unavailable":
                    store.available = False
                    check("no_cached_fallback", read() == [] and observations[-1]["status"] == "unavailable")
                elif name == "derived_corruption":
                    with store.derived:
                        store.derived.execute("UPDATE search_index SET value='language:forged'")
                        store.derived.execute("UPDATE cache SET payload=?", (json.dumps([{"id":"m1","version":1,"value":"language:forged"}]),))
                    check("cached_body_not_trusted", read()[0]["value"] == "language:zh")
                    check("index_body_not_trusted", read(cached=False)[0]["value"] == "language:zh")
                else: raise AssertionError(name)
            snapshot = store.snapshot()
            check("returned_items_match_current_authority_and_access", all(read_guarantees))
        finally: store.close()
    check("temporary_files_removed", not folder.exists())
    return {"name": name, "checks": checks, "observations": observations, "read_evidence":reads,"snapshot": snapshot, "events": events}


CASES = ["user_preference", "tool_observation", "model_hypothesis", "promotion_rejected", "unconfirmed_tool", "source_mismatch", "invalid_input",
         "cas_conflict", "stale_projections", "late_update_projection", "expiry_boundary", "grant_revocation", "tenant_boundary",
         "member_revocation", "delete_late_fill", "logical_purge_backup", "reopen_tombstone", "source_withdrawal",
         "authority_unavailable", "derived_corruption", "source_revision"]


def freeze():
    files = {}
    for name in ("lab.py", "results/results.json", "results/run.txt"):
        file = DIRECTORY / name; raw = file.read_bytes()
        files[file.relative_to(ROOT).as_posix()] = {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
    (DIRECTORY / "results/manifest.json").write_text(json.dumps({"recorded_date":"2026-10-20","files":files},indent=2)+"\n",encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--freeze-manifest", action="store_true")
    options = parser.parse_args()
    if options.freeze_manifest: freeze()
    else:
        runs = [run_case(name) for name in CASES]
        for run in runs: print(f"PASS {run['name']}: {len(run['checks'])} checks",flush=True)
        print(f"PASS: {len(runs)} scenarios; {sum(len(r['checks']) for r in runs)} check results.",flush=True)
        if not options.check:
            output = DIRECTORY / "results"; output.mkdir(parents=True,exist_ok=True)
            (output/"results.json").write_text(json.dumps({"recorded_at":datetime.now(timezone.utc).isoformat(),
                "runtime":{"python":sys.version,"sqlite":sqlite3.sqlite_version,"platform":platform.platform()},
                "scope":"Local SQL records and substring index substitute, logical clock, controlled schedules; no model, vector engine, Redis, parallel threads or secure erasure.",
                "runs":runs},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
