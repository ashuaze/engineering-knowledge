"""Back up a disposable PostgreSQL 18 cluster and recover to a named WAL point.

Creates only owned source/restore directories under the workspace cache; never
connects to an existing server. Saves text evidence, not a distributable backup.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import shlex
import shutil
import socket
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
HIDDEN = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
TARGET = 'kb_before_mistake'


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def quoted(value):
    return "'" + str(value).replace("'", "''") + "'"


def helper_command(mode, source, target):
    tokens = [sys.executable, str(Path(__file__).with_name('archive.py').resolve()), mode,
              str(source), str(target)]
    if os.name == 'nt':
        # All arguments are generated local paths or PostgreSQL's %p/%f tokens.
        return ' '.join('"' + token.replace('\\', '/') + '"' for token in tokens)
    return ' '.join(shlex.quote(token) for token in tokens)


class Experiment:
    def __init__(self, pg_bin, output):
        self.pg_bin, self.output = pg_bin, output
        output.parent.mkdir(parents=True, exist_ok=True)
        cache = (ROOT/'.cache').resolve()
        cache.mkdir(exist_ok=True)
        self.work = Path(tempfile.mkdtemp(prefix='kb-recovery-', dir=cache)).resolve()
        if not self.work.is_relative_to(cache) or self.work == cache:
            raise RuntimeError('Unexpected working directory')
        self.active = []
        self.ports = []
        self.report = {'recorded_at': datetime.now(timezone.utc).isoformat(),
                       'python': platform.python_version(), 'platform': platform.system(),
                       'status': 'incomplete', 'commands': [], 'sql': [],
                       'scope': 'Owned local base backup and named restore point; no crash/power-loss, time-based target, promotion, migration or production RPO/RTO test.'}

    def binary(self, name):
        value = self.pg_bin/(name+('.exe' if os.name == 'nt' else '')) if self.pg_bin else shutil.which(name)
        if not value or not Path(value).is_file():
            raise RuntimeError(f'{name} is unavailable; provide --pg-bin with PostgreSQL 18 tools')
        return str(value)

    def command(self, name, args, *, timeout=180):
        with tempfile.TemporaryFile() as capture:
            process = subprocess.run([str(x) for x in args], stdout=capture, stderr=subprocess.STDOUT,
                                     timeout=timeout, creationflags=HIDDEN)
            capture.seek(0)
            text = capture.read().decode('utf-8',errors='replace').replace('\r\n','\n')
        self.report['commands'].append({'step':name,'tool':Path(args[0]).name,
                                        'returncode':process.returncode,'output':text})
        if process.returncode:
            raise RuntimeError(f'{name} failed: {text}')
        return text

    def port(self):
        while True:
            with socket.socket() as probe:
                probe.bind(('127.0.0.1',0))
                result = probe.getsockname()[1]
            if result not in self.ports:
                self.ports.append(result)
                return result

    def sql(self, port, sql):
        output = self.command('sql', [self.binary('psql'),'-X','-qAt','-v','ON_ERROR_STOP=1',
                              '-h','127.0.0.1','-p',port,'-U','postgres','-d','kb_recovery_lab','-c',sql])
        self.report['sql'].append({'port':port,'sql':sql,'output':output.strip()})
        return output.strip()

    def value(self, port, sql):
        return json.loads(self.sql(port,sql))

    def configure(self, directory, settings):
        with (directory/'postgresql.conf').open('a',encoding='utf-8') as stream:
            stream.write('\n# Disposable knowledge-base recovery experiment\n')
            for key,value in settings.items():
                stream.write(f'{key} = {quoted(value)}\n')

    def start(self, directory, port, name):
        self.active.append(directory)  # Also attempt shutdown after a startup timeout.
        self.command('start-'+name,[self.binary('pg_ctl'),'-D',directory,'-l',self.work/(name+'.log'),
                                   '-o',f'-h 127.0.0.1 -p {port}','-w','start'])

    def stop(self, directory):
        self.command('stop',[self.binary('pg_ctl'),'-D',directory,'-m','fast','-w','stop'])
        self.active.remove(directory)

    def await_archive(self, port, filename):
        path=self.work/'archive'/filename
        deadline=time.monotonic()+45
        while time.monotonic()<deadline:
            state=self.value(port,"SELECT json_build_object('last_archived_wal',last_archived_wal,'archived_count',archived_count,'failed_count',failed_count) FROM pg_stat_archiver")
            if path.is_file() and (self.work/'source/pg_wal/archive_status'/(filename+'.done')).is_file():
                return {'filename':filename,'bytes':path.stat().st_size,'sha256':digest(path),'archiver':state}
            time.sleep(0.1)
        raise TimeoutError(f'Archive completion was not observed for {filename}')

    def rows(self, port):
        return self.value(port,"SELECT coalesce(json_agg(t ORDER BY id),'[]'::json) FROM (SELECT id,note FROM kb_events) t")

    def run(self):
        for name in ['psql','initdb','pg_ctl','createdb','pg_basebackup','pg_verifybackup','pg_waldump']:
            self.binary(name)
        source=self.work/'source'; backup=self.work/'base'; restored=self.work/'restored'
        archive=self.work/'archive';archive.mkdir()
        source_port=self.port();restore_port=self.port()
        self.report['ports']={'source':source_port,'restored':restore_port}
        print('Initializing an owned source cluster and WAL archive...',flush=True)
        self.command('initdb',[self.binary('initdb'),'-D',source,'-U','postgres','--auth=trust',
                              '--encoding=UTF8','--locale=C','--no-instructions'])
        self.configure(source,{'wal_level':'replica','archive_mode':'on','max_wal_senders':'4',
                               'archive_command':helper_command('archive','%p',archive/'%f')})
        self.start(source,source_port,'source')
        self.command('createdb',[self.binary('createdb'),'-h','127.0.0.1','-p',source_port,'-U','postgres','kb_recovery_lab'])
        self.report['server']=self.value(source_port,"SELECT json_build_object('version',version(),'version_num',current_setting('server_version_num')::int)")
        if not 180000<=self.report['server']['version_num']<190000:
            raise RuntimeError('This experiment requires PostgreSQL 18')
        self.report['settings']=self.value(source_port,"SELECT json_build_object('fsync',current_setting('fsync'),'synchronous_commit',current_setting('synchronous_commit'),'full_page_writes',current_setting('full_page_writes'),'wal_level',current_setting('wal_level'),'archive_mode',current_setting('archive_mode'),'wal_segment_size',current_setting('wal_segment_size'))")
        self.sql(source_port,'CREATE TABLE kb_events (id integer PRIMARY KEY,note text NOT NULL)')
        self.sql(source_port,"INSERT INTO kb_events VALUES (1,'baseline')")
        self.report['baseline']=self.rows(source_port)
        first=self.value(source_port,"SELECT to_json(pg_walfile_name(pg_current_wal_insert_lsn()))")
        self.sql(source_port,'SELECT pg_switch_wal()')
        self.report['archive_before_backup']=self.await_archive(source_port,first)
        print('Taking and verifying a plain base backup...',flush=True)
        self.command('basebackup',[self.binary('pg_basebackup'),'-h','127.0.0.1','-p',source_port,
                                  '-U','postgres','-D',backup,'-Fp','-Xstream','-cfast'])
        verification=self.command('verify-backup',[self.binary('pg_verifybackup'),backup])
        manifest=backup/'backup_manifest'
        shutil.copyfile(manifest,self.output.parent/'backup_manifest.json')
        self.report['backup']={'verified':True,'verification_output':verification.strip(),
                               'manifest_sha256':digest(manifest),'files':len(json.loads(manifest.read_text())['Files']),
                               'wal_ranges':json.loads(manifest.read_text())['WAL-Ranges']}
        # Ensure the target requires a later segment absent from the base backup.
        self.sql(source_port,'SELECT pg_switch_wal()')
        self.sql(source_port,"INSERT INTO kb_events VALUES (2,'before-target')")
        target_lsn=self.value(source_port,f'SELECT to_json(pg_create_restore_point({quoted(TARGET)}))')
        target_file=self.value(source_port,f'SELECT to_json(pg_walfile_name({quoted(target_lsn)}::pg_lsn))')
        self.report['target']={'name':TARGET,'lsn':target_lsn,'wal_file':target_file,
                               'already_in_base':(backup/'pg_wal'/target_file).exists()}
        self.report['before_target']=self.rows(source_port)
        self.sql(source_port,"BEGIN; DELETE FROM kb_events WHERE id=2; INSERT INTO kb_events VALUES (3,'after-target'); COMMIT")
        self.report['source_after_changes']=self.rows(source_port)
        self.sql(source_port,'SELECT pg_switch_wal()')
        self.report['target_archive']=self.await_archive(source_port,target_file)
        self.report['archive_files']=[{'name':p.name,'bytes':p.stat().st_size,'sha256':digest(p)} for p in sorted(archive.iterdir()) if p.is_file()]
        self.stop(source)
        print('Restoring into a separate data directory and pausing at the named point...',flush=True)
        shutil.copytree(backup,restored)
        self.configure(restored,{'archive_mode':'off','archive_command':'',
                                'restore_command':helper_command('restore',archive/'%f','%p'),
                                'recovery_target_name':TARGET,'recovery_target_action':'pause',
                                'recovery_target_timeline':'current','hot_standby':'on'})
        (restored/'recovery.signal').touch()
        self.start(restored,restore_port,'restored')
        deadline=time.monotonic()+30
        while time.monotonic()<deadline:
            state=self.value(restore_port,"SELECT json_build_object('in_recovery',pg_is_in_recovery(),'pause_state',pg_get_wal_replay_pause_state(),'replay_lsn',pg_last_wal_replay_lsn(),'read_only',current_setting('transaction_read_only'))")
            if state['pause_state']=='paused':
                break
            time.sleep(0.1)
        else:
            raise TimeoutError('Named target was not reached in paused recovery')
        self.report['recovery_state']=state
        self.report['recovered_rows']=self.rows(restore_port)
        self.stop(restored)
        logs={name:(self.work/(name+'.log')).read_text(encoding='utf-8',errors='replace') for name in ['source','restored']}
        for name,text in logs.items():
            (self.output.parent/(name+'.log.txt')).write_text(text,encoding='utf-8')
        self.report['checks']={
            'postgresql_18':180000<=self.report['server']['version_num']<190000,
            'durability_settings':all(self.report['settings'][k]=='on' for k in ['fsync','synchronous_commit','full_page_writes']),
            'archive_completed_before_backup':self.report['archive_before_backup']['bytes']>0,
            'backup_verified':self.report['backup']['verified'],
            'target_wal_not_in_base':not self.report['target']['already_in_base'],
            'target_wal_archived':self.report['target_archive']['bytes']>0,
            'baseline_only':self.report['baseline']==[{'id':1,'note':'baseline'}],
            'target_rows':self.report['before_target']==[{'id':1,'note':'baseline'},{'id':2,'note':'before-target'}],
            'source_changed':self.report['source_after_changes']==[{'id':1,'note':'baseline'},{'id':3,'note':'after-target'}],
            'recovery_paused_read_only':state['in_recovery'] and state['pause_state']=='paused' and state['read_only']=='on',
            'restored_target_rows':self.report['recovered_rows']==self.report['before_target'],
            'target_wal_retrieved':f'restore:{target_file}:' in logs['restored'],
            'separate_port':source_port!=restore_port,
        }
        if not all(self.report['checks'].values()):
            raise AssertionError(self.report['checks'])
        self.report['status']='passed'

    def close(self):
        failures=[]
        for directory in list(reversed(self.active)):
            try:
                self.stop(directory)
            except Exception as error:
                failures.append(str(error))
        # Keep diagnostic logs even when the main experiment failed early.
        for name in ['source','restored']:
            log=self.work/(name+'.log')
            if log.exists():
                shutil.copyfile(log,self.output.parent/(name+'.log.txt'))
        if failures:
            self.report['cleanup']={'confirmed':False,'retained_directory':str(self.work),'errors':failures}
        else:
            cache=(ROOT/'.cache').resolve()
            if not self.work.is_relative_to(cache) or not self.work.name.startswith('kb-recovery-'):
                raise RuntimeError('Refusing cleanup outside the owned cache directory')
            shutil.rmtree(self.work)
            self.report['cleanup']={'confirmed':True,'source_and_restore_removed':True}
        self.output.write_text(json.dumps(self.report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        if failures:
            raise RuntimeError('Could not confirm cluster shutdown; inspect retained directory')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pg-bin',type=Path)
    parser.add_argument('--output',type=Path,default=ROOT/'.cache/backup-recovery/results.json')
    args=parser.parse_args()
    experiment=Experiment(args.pg_bin,args.output)
    try:
        experiment.run()
    finally:
        experiment.close()
    print(f'PASS: {len(experiment.report["checks"])} recovery checks; evidence saved to {args.output}',flush=True)


if __name__=='__main__':
    main()
