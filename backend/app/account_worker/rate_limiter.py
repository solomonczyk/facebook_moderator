"""Rate limiter: prevents excessive worker runs."""

from datetime import datetime


class RateLimiter:
    def __init__(self, max_runs_per_hour: int = 3, min_seconds_between_runs: int = 300):
        self.max_runs_per_hour = max_runs_per_hour
        self.min_seconds_between_runs = min_seconds_between_runs
        self._run_times: list[datetime] = []

    def can_run(self) -> tuple[bool, str]:
        """Check if another run is allowed. Returns (allowed, reason)."""
        now = datetime.utcnow()

        # Clean old entries
        self._run_times = [t for t in self._run_times if (now - t).total_seconds() < 3600]

        # Check max per hour
        if len(self._run_times) >= self.max_runs_per_hour:
            return False, f"Max {self.max_runs_per_hour} runs per hour reached"

        # Check minimum interval
        if self._run_times:
            last = self._run_times[-1]
            elapsed = (now - last).total_seconds()
            if elapsed < self.min_seconds_between_runs:
                return False, f"Min {self.min_seconds_between_runs}s between runs (elapsed: {elapsed:.0f}s)"

        return True, "Allowed"

    def record_run(self) -> None:
        self._run_times.append(datetime.utcnow())

    @property
    def runs_this_hour(self) -> int:
        now = datetime.utcnow()
        return len([t for t in self._run_times if (now - t).total_seconds() < 3600])
