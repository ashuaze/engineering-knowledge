"""Run seven PostgreSQL 18 concurrency scenarios in an owned disposable cluster.

Uses Python's standard library and psql; never connects to an existing database.
Sessions exchange completion markers; pg_blocking_pids proves planned lock waits.
"""
import argparse
from contextlib import ExitStack, contextmanager
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import re
import shutil
import socket
import subprocess
import tempfile
import time
import uuid

ROOT = Path(__file__).resolve().parents[2]
HIDDEN = getattr(subprocess, 'CREATE_NO_WINDOW', 0)


def command(args):
    # A server spawned by pg_ctl must not keep a captured output pipe open.
    with tempfile.TemporaryFile() as output:
        result = subprocess.run([str(a) for a in args], stdout=output,
                                stderr=subprocess.STDOUT, timeout=120, creationflags=HIDDEN)
        output.seek(0)
        text = output.read().decode('utf-8', errors='replace').replace('\r\n', '\n')
    if result.returncode:
        raise RuntimeError(text)
    return text


@contextmanager
def cluster(pg_bin):
    def binary(name):
        candidate = pg_bin / (name + ('.exe' if os.name == 'nt' else '')) if pg_bin else shutil.which(name)
        if not candidate or not Path(candidate).is_file():
            raise RuntimeError(f'{name} is unavailable; provide --pg-bin with PostgreSQL 18 tools')
        return str(candidate)

    for name in ['psql', 'initdb', 'pg_ctl', 'createdb']:
        binary(name)
    cache = (ROOT / '.cache').resolve()
    cache.mkdir(exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix='kb-inventory-', dir=cache)).resolve()
    assert work.is_relative_to(cache) and work != cache
    started = False
    stopped = True
    try:
        with socket.socket() as probe:
            probe.bind(('127.0.0.1', 0))
            port = probe.getsockname()[1]
        command([binary('initdb'), '-D', work / 'data', '-U', 'postgres', '--auth=trust',
                 '--encoding=UTF8', '--locale=C', '--no-instructions'])
        started = True
        command([binary('pg_ctl'), '-D', work / 'data', '-l', work / 'server.log',
                 '-o', f'-h 127.0.0.1 -p {port}', '-w', 'start'])
        command([binary('createdb'), '-h', '127.0.0.1', '-p', port, '-U', 'postgres', 'kb_inventory_lab'])
        yield [binary('psql'), '-X', '-qAt', '-v', 'ON_ERROR_STOP=0', '-v', 'VERBOSITY=verbose',
               '-h', '127.0.0.1', '-p', str(port), '-U', 'postgres', '-d', 'kb_inventory_lab']
    finally:
        if started:
            try:
                command([binary('pg_ctl'), '-D', work / 'data', '-m', 'fast', '-w', 'stop'])
            except Exception as error:
                stopped = False
                raise RuntimeError(f'Could not confirm cluster shutdown; retained {work}') from error
        if stopped:
            assert work.is_relative_to((ROOT / '.cache').resolve()) and work.name.startswith('kb-inventory-')
            shutil.rmtree(work)


class Session:
    def __init__(self, name, args, directory, trace):
        self.name, self.trace = name, trace
        self.path = directory / f'{name}.psql.txt'
        self.output = self.path.open('wb')
        self.process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=self.output,
                                        stderr=subprocess.STDOUT, text=True, encoding='utf-8',
                                        creationflags=HIDDEN)
        self.pending = None

    def __enter__(self):
        self.execute("SET statement_timeout = '15s'")
        self.execute("SET lock_timeout = '10s'")
        self.execute("SET deadlock_timeout = '100ms'")
        self.pid = int(self.execute('SELECT pg_backend_pid()')['output'])
        return self

    def __exit__(self, *_):
        try:
            if self.process.poll() is None:
                try:
                    self.process.stdin.write('\\q\n')
                    self.process.stdin.flush()
                    self.process.wait(timeout=5)
                except (OSError, subprocess.TimeoutExpired):
                    self.process.kill()
                    self.process.wait(timeout=5)
        finally:
            self.process.stdin.close()
            self.output.close()

    def submit(self, sql):
        assert self.pending is None, 'One outstanding command per session'
        token = 'KB_' + uuid.uuid4().hex
        # BEGIN is a protocol marker; SQLSTATE is captured before any new SQL.
        self.pending = {'token': token, 'sql': sql, 'submitted_at': time.monotonic()}
        self.process.stdin.write(f'\\echo {token}_BEGIN\n{sql};\n\\echo {token}_STATE :SQLSTATE\n\\echo {token}_END\n')
        self.process.stdin.flush()

    def finish(self, expected='00000'):
        pending = self.pending
        assert pending is not None
        token = pending['token']
        deadline = time.monotonic() + 20
        while True:
            text = self.path.read_text(encoding='utf-8', errors='replace').replace('\r\n', '\n')
            if token + '_END\n' in text:
                section = text.split(token + '_BEGIN\n', 1)[1].split(token + '_END\n', 1)[0]
                output, state = section.rsplit(token + '_STATE ', 1)
                entry = {'sequence': len(self.trace) + 1, 'session': self.name,
                         'sql': pending['sql'], 'output': output.strip(), 'sqlstate': state.strip()}
                self.trace.append(entry)
                self.pending = None
                if expected is not None and entry['sqlstate'] != expected:
                    raise AssertionError(entry)
                return entry
            if self.process.poll() is not None:
                raise RuntimeError(f'{self.name} exited before completion: {text[-2000:]}')
            if time.monotonic() >= deadline:
                raise TimeoutError(f'{self.name}: command did not complete: {pending["sql"]}')
            time.sleep(0.02)

    def execute(self, sql, expected='00000'):
        self.submit(sql)
        return self.finish(expected)

    def value(self, sql):
        return json.loads(self.execute(sql)['output'])


def allocation(request):
    assert re.fullmatch(r'[a-z-]+', request)
    return f"""WITH allocated AS (
      UPDATE kb_inventory SET remaining = remaining - 1
      WHERE sku = 'book' AND remaining >= 1 RETURNING sku
    ) INSERT INTO kb_reservations (request_id, sku, quantity)
      SELECT '{request}', sku, 1 FROM allocated RETURNING request_id"""


def wait_for_block(observer, waiter, holder):
    deadline = time.monotonic() + 8
    while time.monotonic() < deadline:
        snapshot = observer.value(f"""SELECT json_build_object('waiter', pid,
          'blockers', pg_blocking_pids(pid), 'wait_event_type', wait_event_type,
          'wait_event', wait_event) FROM pg_stat_activity WHERE pid = {waiter.pid}""")
        if holder.pid in snapshot['blockers'] and snapshot['wait_event_type'] == 'Lock':
            return snapshot
        time.sleep(0.05)
    raise AssertionError('The intended database lock wait was not observed')


def snapshot(observer, initial):
    result = observer.value("""SELECT json_build_object(
      'inventory', (SELECT json_object_agg(sku, remaining) FROM kb_inventory),
      'remaining', (SELECT sum(remaining) FROM kb_inventory),
      'reserved', (SELECT coalesce(sum(quantity),0) FROM kb_reservations),
      'requests', (SELECT coalesce(json_agg(request_id ORDER BY request_id),'[]'::json) FROM kb_reservations))""")
    result['conserves_stock'] = result['remaining'] + result['reserved'] == initial
    result['nonnegative'] = all(v >= 0 for v in result['inventory'].values())
    return result


def run_cases(a, b, observer, report, repeat):
    def reset(stock=1, pen=False):
        observer.execute('TRUNCATE kb_reservations, kb_inventory')
        observer.execute(f"INSERT INTO kb_inventory VALUES ('book',{stock})" + (",('pen',1)" if pen else ''))

    def begin(session):
        session.execute('BEGIN ISOLATION LEVEL READ COMMITTED')

    def save(name, initial, expected, **details):
        actual = snapshot(observer, initial)
        checks = {key: actual[key] == value for key, value in expected.items()}
        checks['nonnegative'] = actual['nonnegative']
        checks.update(details.pop('checks', {}))
        record = {'repeat': repeat, 'name': name, 'initial_stock': initial,
                  'actual': actual, 'checks': checks, **details}
        report['cases'].append(record)
        assert all(checks.values()), record
        print(f'PASS {repeat}-{name}', flush=True)

    reset()
    begin(a); begin(b)
    reads = [int(s.execute("SELECT remaining FROM kb_inventory WHERE sku='book'")['output']) for s in (a,b)]
    for session, request in [(a,'request-a'), (b,'request-b')]:
        session.execute("UPDATE kb_inventory SET remaining=0 WHERE sku='book'")
        session.execute(f"INSERT INTO kb_reservations VALUES ('{request}','book',1)")
        session.execute('COMMIT')
    save('stale-read', 1, {'remaining': 0, 'reserved': 2, 'conserves_stock': False},
         reads=reads, checks={'both_read_one': reads == [1,1]})

    for name, release, winner in [('conditional-update','COMMIT','request-a'), ('rollback','ROLLBACK','request-b')]:
        reset(); begin(a); begin(b)
        a.execute(allocation('request-a'))
        b.submit(allocation('request-b'))
        waited = wait_for_block(observer, b, a)
        a.execute(release)
        returned = b.finish()['output']
        b.execute('COMMIT')
        save(name, 1, {'remaining': 0, 'reserved': 1, 'requests': [winner], 'conserves_stock': True},
             lock_wait=waited, b_returned=returned,
             checks={'b_result': returned == ('' if release == 'COMMIT' else 'request-b')})

    reset(); begin(a)
    a.execute(allocation('request-a')); a.execute('COMMIT')
    begin(b)
    replay = b.execute(allocation('request-a'))['output']
    b.execute('COMMIT')
    lookup = observer.value("SELECT json_build_object('id',request_id,'sku',sku,'quantity',quantity) FROM kb_reservations WHERE request_id='request-a'")
    save('exhausted-replay', 1, {'remaining': 0, 'reserved': 1, 'requests': ['request-a'], 'conserves_stock': True},
         replay_returned=replay, lookup=lookup,
         checks={'empty_is_not_missing_original': replay == '' and lookup == {'id':'request-a','sku':'book','quantity':1}})

    reset(2); begin(a)
    a.execute(allocation('request-a')); a.execute('COMMIT')
    begin(b)
    conflict = b.execute(allocation('request-a'), expected='23505')
    b.execute('ROLLBACK')
    save('duplicate-key', 2, {'remaining': 1, 'reserved': 1, 'requests': ['request-a'], 'conserves_stock': True},
         conflict=conflict)

    reset(pen=True); begin(a); begin(b)
    a.execute("UPDATE kb_inventory SET remaining=remaining WHERE sku='book'")
    b.execute("UPDATE kb_inventory SET remaining=remaining WHERE sku='pen'")
    b.submit("UPDATE kb_inventory SET remaining=remaining WHERE sku='book'")
    waited = wait_for_block(observer, b, a)
    a.submit("UPDATE kb_inventory SET remaining=remaining WHERE sku='pen'")
    outcomes = [a.finish(expected=None), b.finish(expected=None)]
    a.execute('ROLLBACK'); b.execute('ROLLBACK')
    save('deadlock', 2, {'remaining': 2, 'reserved': 0, 'conserves_stock': True},
         first_lock_wait=waited, outcomes=outcomes,
         checks={'one_deadlock_victim': sorted(x['sqlstate'] for x in outcomes) == ['00000','40P01']})

    reset(); begin(a); begin(b)
    a.execute("UPDATE kb_inventory SET remaining=remaining WHERE sku='book'")
    b.execute("SET LOCAL lock_timeout='100ms'")
    timeout = b.execute("UPDATE kb_inventory SET remaining=remaining WHERE sku='book'", expected='55P03')
    b.execute('ROLLBACK'); a.execute('COMMIT')
    save('lock-timeout', 1, {'remaining': 1, 'reserved': 0, 'conserves_stock': True}, timeout=timeout)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pg-bin', type=Path)
    parser.add_argument('--runs', type=int, default=3)
    parser.add_argument('--output', type=Path, default=ROOT/'.cache/inventory-concurrency/results.json')
    args = parser.parse_args()
    if not 1 <= args.runs <= 10:
        parser.error('--runs must be 1..10')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    report = {'recorded_at': datetime.now(timezone.utc).isoformat(), 'python': platform.python_version(),
              'platform': platform.system(), 'repeats': args.runs, 'status': 'incomplete',
              'scope': 'Owned local PostgreSQL cluster, seven controlled schedules; not production capacity, crash recovery or an HTTP idempotency protocol.',
              'cases': [], 'trace': []}
    try:
        print('Preparing a disposable PostgreSQL cluster...', flush=True)
        with cluster(args.pg_bin) as connection, ExitStack() as stack:
            sessions = [stack.enter_context(Session(name, connection, args.output.parent, report['trace'])) for name in ['a','b','observer']]
            a,b,observer = sessions
            report['server'] = observer.value("SELECT json_build_object('version',version(),'version_num',current_setting('server_version_num')::int)")
            assert 180000 <= report['server']['version_num'] < 190000, report['server']
            observer.execute('CREATE TABLE kb_inventory (sku text PRIMARY KEY, remaining integer NOT NULL CHECK (remaining >= 0))')
            observer.execute('CREATE TABLE kb_reservations (request_id text PRIMARY KEY, sku text NOT NULL REFERENCES kb_inventory(sku), quantity integer NOT NULL CHECK (quantity > 0))')
            report['settings'] = {s.name: s.value("SELECT json_build_object('isolation',current_setting('default_transaction_isolation'),'statement_timeout',current_setting('statement_timeout'),'lock_timeout',current_setting('lock_timeout'),'deadlock_timeout',current_setting('deadlock_timeout'))") for s in sessions}
            for repeat in range(1,args.runs+1):
                run_cases(a,b,observer,report,repeat)
        report['checks'] = {'postgresql_18': True, 'all_scenarios': len(report['cases']) == 7*args.runs,
                            'all_case_checks': all(all(c['checks'].values()) for c in report['cases'])}
        assert all(report['checks'].values())
        report['status'] = 'passed'
        report['cluster_stopped_and_removed'] = True
    finally:
        args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'PASS: {len(report["cases"])} controlled scenarios; evidence saved to {args.output}', flush=True)


if __name__ == '__main__':
    main()
