"""Teaching retry policy. The supplied operation must enforce its own I/O timeout."""
import math
import random
import time


class RetryableError(Exception):
    """The adapter has classified this failure as potentially transient."""


class BudgetExhausted(Exception):
    """The result may be unknown; this exception does not roll back remote work."""


def call_with_budget(operation, *, operation_id, budget_s=1.0,
                     attempt_cap_s=0.4, max_attempts=3, reserve_s=0.05,
                     safe_to_retry=False, clock=time.monotonic,
                     pause=time.sleep, choose_delay=None):
    """max_attempts includes the first call. Only RetryableError is retried.

    This policy supplies timeout values; it cannot interrupt blocking code.
    safe_to_retry must come from the operation contract, not the error code.
    """
    if (not all(math.isfinite(x) for x in (budget_s, attempt_cap_s, reserve_s))
            or budget_s <= reserve_s or reserve_s < 0 or attempt_cap_s <= 0
            or type(max_attempts) is not int or not 1 <= max_attempts <= 10
            or not isinstance(operation_id, str) or not operation_id):
        raise ValueError('invalid budget, attempt limit or operation identifier')
    choose_delay = choose_delay or (lambda cap: random.uniform(0, cap))
    deadline = clock() + budget_s
    for attempt in range(max_attempts):
        usable = deadline - clock() - reserve_s
        if usable <= 0:
            raise BudgetExhausted('no budget for another attempt')
        timeout_s = min(attempt_cap_s, usable)
        try:
            result = operation(timeout_s, operation_id)
        except RetryableError:
            if not safe_to_retry or attempt + 1 == max_attempts:
                raise
            delay_cap = min(0.05 * 2 ** attempt, 0.4)
            delay = choose_delay(delay_cap)
            if not math.isfinite(delay) or not 0 <= delay <= delay_cap:
                raise ValueError('delay must be within the jitter range')
            if delay >= deadline - clock() - reserve_s:
                raise BudgetExhausted('backoff would consume remaining budget')
            pause(delay)
        else:
            if clock() >= deadline - reserve_s:
                raise BudgetExhausted('late result; external effects may exist')
            return result
    raise AssertionError('unreachable')


class FakeClock:
    """Deterministic elapsed time for the lab, not a network timer."""
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now

    def advance(self, duration):
        self.now += duration


def main():
    timer = FakeClock()
    attempts = []

    def remote_stub(timeout_s, operation_id):
        attempts.append((round(timeout_s, 3), operation_id))
        timer.advance(0.25)
        if len(attempts) == 1:
            raise RetryableError('simulated transient failure')
        return 'confirmed-result'

    result = call_with_budget(remote_stub, operation_id='read-report-001',
                              safe_to_retry=True, clock=timer,
                              pause=timer.advance, choose_delay=lambda cap: cap)
    print('result:', result)
    print('attempts (timeout seconds, stable operation ID):', attempts)
    print('modeled elapsed seconds:', round(timer(), 3))
    print('No network call or real cancellation was exercised.')


if __name__ == '__main__':
    main()
