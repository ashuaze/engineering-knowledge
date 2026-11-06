"""Minimal local archive/restore helper for the disposable recovery experiment.

Archives never overwrite different existing bytes. Not a production backup agent.
"""
import hashlib
import os
from pathlib import Path
import shutil
import sys


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def copy(mode, source, target):
    if mode not in ('archive', 'restore'):
        raise ValueError('mode must be archive or restore')
    if not source.is_file():
        print(f'missing:{source.name}', file=sys.stderr)
        return 1
    if mode == 'archive' and target.exists():
        if source.stat().st_size != target.stat().st_size or digest(source) != digest(target):
            print(f'conflicting-archive:{target.name}', file=sys.stderr)
            return 1
        with target.open('r+b') as stream:
            os.fsync(stream.fileno())
    else:
        with source.open('rb') as incoming, target.open('xb' if mode == 'archive' else 'wb') as outgoing:
            shutil.copyfileobj(incoming, outgoing, 1024 * 1024)
            outgoing.flush()
            os.fsync(outgoing.fileno())
    if os.name != 'nt':
        directory = os.open(target.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    print(f'{mode}:{source.name}:{target.stat().st_size}:{digest(target)}', flush=True)
    return 0


if __name__ == '__main__':
    if len(sys.argv) != 4:
        raise SystemExit('usage: archive.py archive|restore source target')
    raise SystemExit(copy(sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])))
