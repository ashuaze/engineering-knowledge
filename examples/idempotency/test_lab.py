from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Barrier
import unittest
from lab import Conflict, ReplyLost, counts, initialize, submit


class IdempotencyTests(unittest.TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db=Path(self.temp.name)/'test.sqlite'
        initialize(self.db)
        self.scope='tenant-a:user-1:POST:/orders'
        self.key='request-0001'
        self.payload={'item':'book','amount_minor':2500}

    def test_sequential_replay(self):
        first=submit(self.db,self.scope,self.key,self.payload)
        self.assertEqual(first,submit(self.db,self.scope,self.key,self.payload))
        self.assertEqual(counts(self.db),(1,1))

    def test_concurrent_replay(self):
        barrier=Barrier(8)
        def call(_):
            barrier.wait(timeout=10)
            return submit(self.db,self.scope,self.key,self.payload)
        with ThreadPoolExecutor(max_workers=8) as pool:
            responses=list(pool.map(call,range(8)))
        self.assertTrue(all(x==responses[0] for x in responses))
        self.assertEqual(counts(self.db),(1,1))

    def test_fingerprint_conflict_does_not_change_original(self):
        original=submit(self.db,self.scope,self.key,self.payload)
        with self.assertRaises(Conflict):
            submit(self.db,self.scope,self.key,dict(self.payload,amount_minor=2600))
        self.assertEqual(submit(self.db,self.scope,self.key,self.payload),original)
        self.assertEqual(counts(self.db),(1,1))

    def test_separate_scope(self):
        a=submit(self.db,self.scope,self.key,self.payload)
        b=submit(self.db,'tenant-b:user-1:POST:/orders',self.key,self.payload)
        self.assertNotEqual(a['order_id'],b['order_id'])
        self.assertEqual(counts(self.db),(2,2))

    def test_failure_before_commit_rolls_back_both_tables(self):
        with self.assertRaises(RuntimeError):
            submit(self.db,self.scope,self.key,self.payload,fail_after_insert=True)
        self.assertEqual(counts(self.db),(0,0))
        submit(self.db,self.scope,self.key,self.payload)
        self.assertEqual(counts(self.db),(1,1))

    def test_response_loss_after_commit_recovers_result(self):
        with self.assertRaises(ReplyLost):
            submit(self.db,self.scope,self.key,self.payload,lose_reply=True)
        self.assertEqual(counts(self.db),(1,1))
        result=submit(self.db,self.scope,self.key,self.payload)
        self.assertGreater(result['order_id'],0)
        self.assertEqual(counts(self.db),(1,1))

    def test_invalid_payload_leaves_no_effects(self):
        for payload in ({'item':'book','amount_minor':0},{'item':'','amount_minor':100},
                        {'item':'book','amount_minor':True},{'item':'book','amount_minor':100,'ignored':1}):
            with self.subTest(payload=payload):
                with self.assertRaises(ValueError):
                    submit(self.db,self.scope,self.key,payload)
        self.assertEqual(counts(self.db),(0,0))

    def test_normalized_equivalent_input(self):
        a=submit(self.db,self.scope,self.key,self.payload)
        b=submit(self.db,self.scope,self.key,{'amount_minor':2500,'item':' book '})
        self.assertEqual(a,b)
        self.assertEqual(counts(self.db),(1,1))


if __name__=='__main__':
    unittest.main()
