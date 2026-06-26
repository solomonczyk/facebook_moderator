"""Test rate limiter: blocks excessive runs."""

import sys
sys.path.insert(0, '.')

from app.account_worker.rate_limiter import RateLimiter


def test_first_run_allowed():
    rl = RateLimiter(max_runs_per_hour=3)
    allowed, reason = rl.can_run()
    assert allowed is True


def test_exceeds_max_runs():
    rl = RateLimiter(max_runs_per_hour=2)
    rl.record_run()
    rl.record_run()
    allowed, reason = rl.can_run()
    assert allowed is False
    assert "Max 2" in reason


def test_runs_this_hour_count():
    rl = RateLimiter(max_runs_per_hour=5)
    rl.record_run()
    rl.record_run()
    assert rl.runs_this_hour == 2


if __name__ == '__main__':
    test_first_run_allowed()
    test_exceeds_max_runs()
    test_runs_this_hour_count()
    print("[PASS] All rate limiter tests passed")
