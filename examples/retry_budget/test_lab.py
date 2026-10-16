import unittest
from lab import BudgetExhausted, FakeClock, RetryableError, call_with_budget


class RetryBudgetTests(unittest.TestCase):
    def setUp(self):
        self.timer = FakeClock()

    def run_policy(self, operation, **overrides):
        options = dict(operation_id='business-action-001', budget_s=1.0,
                       attempt_cap_s=0.6, reserve_s=0.1, max_attempts=3,
                       safe_to_retry=True, clock=self.timer,
                       pause=self.timer.advance, choose_delay=lambda cap: cap)
        options.update(overrides)
        return call_with_budget(operation, **options)

    def test_retry_uses_remaining_budget_and_stable_identifier(self):
        attempts = []
        def operation(timeout_s, identifier):
            attempts.append((timeout_s, identifier))
            self.timer.advance(0.3)
            if len(attempts) == 1:
                raise RetryableError()
            return 'ok'
        self.assertEqual(self.run_policy(operation), 'ok')
        self.assertEqual([x[1] for x in attempts], ['business-action-001'] * 2)
        self.assertAlmostEqual(attempts[0][0], 0.6)
        self.assertAlmostEqual(attempts[1][0], 0.55)

    def test_unsafe_operation_is_not_replayed(self):
        calls = []
        def operation(*args):
            calls.append(args)
            raise RetryableError()
        with self.assertRaises(RetryableError):
            self.run_policy(operation, safe_to_retry=False)
        self.assertEqual(len(calls), 1)
        self.assertEqual(self.timer(), 0)

    def test_permanent_error_is_not_retried(self):
        calls = []
        def operation(*args):
            calls.append(args)
            raise PermissionError('access revoked')
        with self.assertRaises(PermissionError):
            self.run_policy(operation)
        self.assertEqual(len(calls), 1)

    def test_attempt_limit_includes_first_call(self):
        calls = []
        def operation(*args):
            calls.append(args)
            raise RetryableError()
        with self.assertRaises(RetryableError):
            self.run_policy(operation)
        self.assertEqual(len(calls), 3)

    def test_backoff_cannot_consume_response_reserve(self):
        calls = []
        def operation(*args):
            calls.append(args)
            self.timer.advance(0.88)
            raise RetryableError()
        with self.assertRaises(BudgetExhausted):
            self.run_policy(operation)
        self.assertEqual(len(calls), 1)

    def test_late_success_does_not_prove_timely_completion(self):
        effects = []
        def operation(*args):
            effects.append('committed')
            self.timer.advance(2.0)
            return 'created'
        with self.assertRaises(BudgetExhausted):
            self.run_policy(operation)
        self.assertEqual(effects, ['committed'])

    def test_budget_is_checked_again_after_delayed_wakeup(self):
        calls = []
        def operation(*args):
            calls.append(args)
            raise RetryableError()
        with self.assertRaises(BudgetExhausted):
            self.run_policy(operation, pause=lambda _: self.timer.advance(2.0))
        self.assertEqual(len(calls), 1)


if __name__ == '__main__':
    unittest.main()
