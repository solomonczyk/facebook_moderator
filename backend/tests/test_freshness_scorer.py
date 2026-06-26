"""Tests for freshness scorer."""

import sys
sys.path.insert(0, '.')

from datetime import date, timedelta
from app.aggregator.freshness_scorer import score_freshness, is_digest_ready
from app.aggregator.models import FreshnessStatus


def test_fresh_today():
    assert score_freshness(date.today()) == FreshnessStatus.FRESH_TODAY


def test_fresh_1_3_days():
    assert score_freshness(date.today() - timedelta(days=2)) == FreshnessStatus.FRESH_1_3_DAYS


def test_fresh_4_7_days():
    assert score_freshness(date.today() - timedelta(days=5)) == FreshnessStatus.FRESH_4_7_DAYS


def test_stale_over_7_days():
    assert score_freshness(date.today() - timedelta(days=10)) == FreshnessStatus.STALE_OVER_7_DAYS


def test_unknown_date():
    assert score_freshness(None) == FreshnessStatus.UNKNOWN_DATE


def test_operator_confirmed_upgrades_stale():
    status = score_freshness(
        date.today() - timedelta(days=14),
        operator_confirmed_active=True,
    )
    assert status == FreshnessStatus.FRESH_4_7_DAYS


def test_is_digest_ready():
    assert is_digest_ready(FreshnessStatus.FRESH_TODAY) is True
    assert is_digest_ready(FreshnessStatus.FRESH_1_3_DAYS) is True
    assert is_digest_ready(FreshnessStatus.FRESH_4_7_DAYS) is True
    assert is_digest_ready(FreshnessStatus.STALE_OVER_7_DAYS) is False
    assert is_digest_ready(FreshnessStatus.UNKNOWN_DATE) is False


if __name__ == '__main__':
    test_fresh_today()
    test_fresh_1_3_days()
    test_fresh_4_7_days()
    test_stale_over_7_days()
    test_unknown_date()
    test_operator_confirmed_upgrades_stale()
    test_is_digest_ready()
    print("[PASS]  All freshness scorer tests passed")
