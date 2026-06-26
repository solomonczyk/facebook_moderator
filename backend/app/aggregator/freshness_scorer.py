"""Freshness scorer: assigns freshness status based on post/capture dates."""

from datetime import datetime, date, timedelta
from .models import FreshnessStatus


def score_freshness(
    post_date: date | None,
    capture_date: date | None = None,
    operator_confirmed_active: bool = False,
) -> FreshnessStatus:
    """
    Score freshness based on post date relative to today.
    If post_date is None → unknown_date.
    If operator confirmed the lead is still active → upgrade to fresh_1_3_days max.
    """
    if post_date is None:
        return FreshnessStatus.UNKNOWN_DATE

    today = date.today()
    delta = (today - post_date).days

    if operator_confirmed_active and delta > 7:
        return FreshnessStatus.FRESH_4_7_DAYS

    if delta <= 0:
        return FreshnessStatus.FRESH_TODAY
    elif delta <= 3:
        return FreshnessStatus.FRESH_1_3_DAYS
    elif delta <= 7:
        return FreshnessStatus.FRESH_4_7_DAYS
    else:
        return FreshnessStatus.STALE_OVER_7_DAYS


def is_digest_ready(status: FreshnessStatus) -> bool:
    """Check if freshness status allows digest inclusion."""
    return status in (
        FreshnessStatus.FRESH_TODAY,
        FreshnessStatus.FRESH_1_3_DAYS,
        FreshnessStatus.FRESH_4_7_DAYS,
    )
