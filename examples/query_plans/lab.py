"""Run real PostgreSQL 18 plans using temporary tables in a disposable cluster.

Default mode owns and stops its cluster. --external is for an explicitly prepared
loopback database named kb_query_plan_lab; no application tables are changed.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import shutil
import socket
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]


def command(args, *, input=None):
    # pg_ctl starts a background server. On Windows, an inherited pipe can keep
    # communicate() waiting after pg_ctl exits; a file does not require EOF.
    with tempfile.TemporaryFile() as output:
        completed = subprocess.run([str(a) for a in args], input=input, text=True,
                                   encoding='utf-8', errors='replace', stdout=output,
                                   stderr=subprocess.STDOUT, timeout=120,
                                   creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        output.seek(0)
        captured = output.read().decode('utf-8', errors='replace').replace('\r\n', '\n')
    if completed.returncode:
        raise RuntimeError(captured.strip())
    return captured


def nodes(plan):
    yield plan
    for child in plan.get('Plans', []):
        yield from nodes(child)


def evaluate(report):
    cases = report['cases']
    walked = {name: list(nodes(value[0]['Plan'])) for name, value in cases.items()}
    identities = list(report['result_ids'].values())
    report['checks'] = {
        'postgresql_18': 180000 <= report['server_version_num'] < 190000,
        'expected_data': report['data'] == {'rows': 200000, 'rare_rows': 40, 'broad_rows': 160000},
        'same_twenty_rows': len(identities[0]) == 20 and all(ids == identities[0] for ids in identities),
        'all_queries_executed': all('Execution Time' in value[0] for value in cases.values()),
        'six_scenarios': len(cases) == 6,
    }
    report['observations'] = {
        'before_index_sequential': any(n['Node Type'] == 'Seq Scan' for n in walked['before_index']),
        'selective_query_uses_composite_index': any(n.get('Index Name') == 'kb_orders_customer_created_id' for n in walked['after_index']),
        'broad_filter_sequential': any(n['Node Type'] == 'Seq Scan' for n in walked['broad_filter_with_index']),
        'heap_fetches_after_update': sum(n.get('Heap Fetches', 0) for n in walked['after_heap_update']),
        'heap_fetches_after_default_vacuum': sum(n.get('Heap Fetches', 0) for n in walked['after_default_vacuum']),
        'heap_fetches_after_cleanup_vacuum': sum(n.get('Heap Fetches', 0) for n in walked['after_cleanup_vacuum']),
    }
    report['summary'] = {name: {'nodes': [n['Node Type'] for n in group],
                               'execution_ms': cases[name][0]['Execution Time'],
                               'heap_fetches': sum(n.get('Heap Fetches', 0) for n in group)}
                         for name, group in walked.items()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pg-bin', type=Path, help='Directory containing psql, initdb, pg_ctl and createdb')
    parser.add_argument('--external', action='store_true', help='Use an explicitly prepared loopback kb_query_plan_lab database')
    parser.add_argument('--port', type=int, default=5432, help='Port for --external only')
    parser.add_argument('--user', default='postgres')
    parser.add_argument('--output', type=Path, default=ROOT / '.cache/query-plans/results.json')
    args = parser.parse_args()
    suffix = '.exe' if os.name == 'nt' else ''

    def binary(name):
        candidate = args.pg_bin / (name + suffix) if args.pg_bin else shutil.which(name)
        if not candidate or not Path(candidate).is_file():
            raise RuntimeError(f'{name} is unavailable; provide --pg-bin or install PostgreSQL 18 tools')
        return str(candidate)

    psql = binary('psql')
    work = None
    started = False
    cleanup_ok = True
    try:
        if args.external:
            port = args.port
        else:
            print('Preparing a disposable PostgreSQL cluster in the workspace cache...', flush=True)
            cache = (ROOT / '.cache').resolve()
            cache.mkdir(exist_ok=True)
            work = Path(tempfile.mkdtemp(prefix='kb-query-plan-', dir=cache)).resolve()
            assert work.is_relative_to(cache) and work != cache
            with socket.socket() as probe:
                probe.bind(('127.0.0.1', 0))
                port = probe.getsockname()[1]
            command([binary('initdb'), '-D', work / 'data', '-U', args.user,
                     '--auth=trust', '--encoding=UTF8', '--locale=C', '--no-instructions'])
            # If startup times out after spawning the server, still attempt a stop
            # and retain the directory whenever we cannot confirm shutdown.
            started = True
            command([binary('pg_ctl'), '-D', work / 'data', '-l', work / 'server.log',
                     '-o', f'-h 127.0.0.1 -p {port}', '-w', 'start'])
            command([binary('createdb'), '-h', '127.0.0.1', '-p', str(port), '-U', args.user, 'kb_query_plan_lab'])
        connection = ['-h', '127.0.0.1', '-p', str(port), '-U', args.user, '-d', 'kb_query_plan_lab']
        version = int(command([psql, '-X', '-At', *connection, '-c', 'SHOW server_version_num']).strip())
        if not 180000 <= version < 190000:
            raise RuntimeError(f'This recorded experiment requires PostgreSQL 18; found {version}')
        print('Capturing six query-plan scenarios on temporary synthetic data...', flush=True)
        raw = command([psql, '-X', '-qAt', '-v', 'ON_ERROR_STOP=1', *connection,
                       '-f', Path(__file__).with_suffix('.sql')])
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.with_suffix('.psql.txt').write_text(raw, encoding='utf-8')
        payload = raw.split('KB_PLAN_REPORT_BEGIN\n', 1)[1].split('\nKB_PLAN_REPORT_END', 1)[0].strip()
        report = json.loads(payload)
        report.update(recorded_at=datetime.now(timezone.utc).isoformat(), python=platform.python_version(),
                      platform=platform.system(), cluster='external-lab' if args.external else 'disposable-local',
                      scope='Temporary synthetic table; six plan observations, not a benchmark or concurrent workload.')
        evaluate(report)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        failed = [name for name, passed in report['checks'].items() if not passed]
        if failed:
            raise RuntimeError(f'Invariant checks failed: {failed}; raw results were saved')
        print(json.dumps({'checks': report['checks'], 'observations': report['observations'],
                          'summary': report['summary'], 'output': str(args.output)}, ensure_ascii=False, indent=2))
    finally:
        if started:
            try:
                command([binary('pg_ctl'), '-D', work / 'data', '-m', 'fast', '-w', 'stop'])
            except Exception as error:
                cleanup_ok = False
                print(f'Cluster stop failed; retained {work}: {error}')
        if work and cleanup_ok:
            # Never recursively delete a computed path outside this lab's workspace cache.
            cache = (ROOT / '.cache').resolve()
            assert work.is_relative_to(cache) and work.name.startswith('kb-query-plan-')
            shutil.rmtree(work)
        if not cleanup_ok:
            raise RuntimeError(f'Could not confirm shutdown; inspect the retained cluster at {work}')


if __name__ == '__main__':
    main()
