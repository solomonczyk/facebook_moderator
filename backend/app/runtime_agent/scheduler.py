"""Scheduler: timed tasks like daily digest and freshness checks."""

from datetime import datetime


class TaskScheduler:
    def __init__(self):
        self._last_digest_run: str | None = None
        self._last_freshness_check: str | None = None

    def should_run_digest(self) -> bool:
        if not self._last_digest_run:
            return True
        today = datetime.utcnow().strftime("%Y-%m-%d")
        return self._last_digest_run != today

    def mark_digest_run(self) -> None:
        self._last_digest_run = datetime.utcnow().strftime("%Y-%m-%d")

    def should_check_freshness(self) -> bool:
        if not self._last_freshness_check:
            return True
        last = datetime.fromisoformat(self._last_freshness_check)
        return (datetime.utcnow() - last).total_seconds() > 3600  # Every hour

    def mark_freshness_check(self) -> None:
        self._last_freshness_check = datetime.utcnow().isoformat()
