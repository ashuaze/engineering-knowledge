"""Check the local archive helper's overwrite and error contracts."""
from contextlib import redirect_stdout, redirect_stderr
import io
from pathlib import Path
import tempfile
import unittest

from archive import copy

ROOT = Path(__file__).resolve().parents[2]


class ArchiveContractTests(unittest.TestCase):
    def setUp(self):
        cache=(ROOT/'.cache').resolve()
        cache.mkdir(exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(prefix='archive-test-',dir=cache)
        self.directory=Path(self.temp.name).resolve()
        if not self.directory.is_relative_to(cache):
            raise RuntimeError('Unexpected test directory')
        self.addCleanup(self.temp.cleanup)
        self.source=self.directory/'source'
        self.target=self.directory/'target'

    def invoke(self, mode):
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            return copy(mode,self.source,self.target)

    def test_archive_is_repeatable_for_identical_bytes(self):
        self.source.write_bytes(b'first wal bytes')
        self.assertEqual(self.invoke('archive'),0)
        self.assertEqual(self.invoke('archive'),0)
        self.assertEqual(self.target.read_bytes(),self.source.read_bytes())

    def test_conflicting_archive_is_preserved_and_rejected(self):
        self.source.write_bytes(b'new bytes')
        self.target.write_bytes(b'original bytes')
        self.assertEqual(self.invoke('archive'),1)
        self.assertEqual(self.target.read_bytes(),b'original bytes')

    def test_missing_source_is_failure_without_output(self):
        self.assertEqual(self.invoke('archive'),1)
        self.assertFalse(self.target.exists())

    def test_restore_replaces_owned_recovery_output(self):
        self.source.write_bytes(b'archived bytes')
        self.target.write_bytes(b'incomplete recovery output')
        self.assertEqual(self.invoke('restore'),0)
        self.assertEqual(self.target.read_bytes(),b'archived bytes')


if __name__=='__main__':
    unittest.main()
