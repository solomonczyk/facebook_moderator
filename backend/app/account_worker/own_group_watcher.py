"""Own group watcher: orchestrates the capture → send pipeline."""

import uuid
from datetime import datetime

from .config import WorkerConfig
from .worker_models import WorkerState, WorkerRunResult
from .emergency_stop import EmergencyStop
from .rate_limiter import RateLimiter
from .seen_store import SeenStore
from .content_extractor import extract_items
from .event_sender import send_events
from .browser_session import BrowserSession


class OwnGroupWatcher:
    def __init__(self, config: WorkerConfig):
        self.config = config
        self.state = WorkerState.STOPPED
        self.emergency = EmergencyStop()
        self.rate_limiter = RateLimiter(
            max_runs_per_hour=config.max_runs_per_hour,
            min_seconds_between_runs=300,
        )
        self.seen = SeenStore()
        self.browser = BrowserSession(config)
        self.last_run_at: str | None = None
        self.items_sent: int = 0

    def start(self) -> tuple[bool, str]:
        allowed, blockers = self.config.can_start()
        if not allowed:
            return False, f"Cannot start: {'; '.join(blockers)}"

        if self.state == WorkerState.EMERGENCY_STOPPED:
            return False, "Worker is emergency-stopped. Reset first."

        self.emergency.reset()
        connected, msg = self.browser.connect()
        if not connected:
            return False, msg

        self.state = WorkerState.RUNNING
        return True, "Worker started"

    def stop(self) -> None:
        self.state = WorkerState.STOPPED
        self.browser.disconnect()

    def pause(self) -> None:
        if self.state == WorkerState.RUNNING:
            self.state = WorkerState.PAUSED

    def resume(self) -> None:
        if self.state == WorkerState.PAUSED:
            self.state = WorkerState.RUNNING

    def emergency_stop(self, reason: str = "") -> None:
        self.emergency.trigger(reason or "Operator emergency stop")
        self.state = WorkerState.EMERGENCY_STOPPED
        self.browser.disconnect()

    def run_once(self, dry_run: bool = False) -> WorkerRunResult:
        run_id = f"run_{uuid.uuid4().hex[:8]}"
        started = datetime.utcnow().isoformat()
        result = WorkerRunResult(run_id=run_id, started_at=started, state=self.state)

        try:
            self.emergency.check()

            if self.state != WorkerState.RUNNING:
                result.errors.append(f"Worker not running (state: {self.state.value})")
                return result

            can, reason = self.rate_limiter.can_run()
            if not can:
                result.errors.append(f"Rate limited: {reason}")
                return result

            # Read visible page content
            url = self.config.own_group_url
            html_blocks = self.browser.read_visible_page(url)
            items = extract_items(html_blocks, url)
            result.items_seen = len(items)

            # Filter duplicates
            new_items = self.seen.filter_new(items)
            result.items_new = len(new_items)

            if dry_run:
                result.ended_at = datetime.utcnow().isoformat()
                return result

            # Build events for own group only
            events = send_events(new_items, self.config)
            result.items_sent = len(events)
            self.items_sent += len(events)

            self.rate_limiter.record_run()
            self.last_run_at = datetime.utcnow().isoformat()
        except Exception as e:
            result.errors.append(str(e))
        finally:
            result.ended_at = datetime.utcnow().isoformat()

        return result

    def get_status(self) -> dict:
        return {
            "state": self.state.value,
            "own_group_url_configured": bool(self.config.own_group_url),
            "read_only": self.config.read_only,
            "draft_only": self.config.draft_only,
            "auto_actions": False,
            "last_run_at": self.last_run_at,
            "items_seen": self.seen.count,
            "items_sent_to_runtime": self.items_sent,
            "rate_limiter_runs_this_hour": self.rate_limiter.runs_this_hour,
            "emergency": self.emergency.to_dict(),
            "browser": self.browser.to_dict(),
        }
