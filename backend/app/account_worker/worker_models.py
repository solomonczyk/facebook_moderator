"""Worker data models."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class WorkerState(str, Enum):
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    EMERGENCY_STOPPED = "emergency_stopped"
    WAITING_FOR_LOGIN = "waiting_for_login"
    ERROR = "error"


@dataclass
class CapturedItem:
    item_id: str = ""
    raw_text: str = ""
    content_hash: str = ""
    source_url: str = ""
    page_url: str = ""
    visible_timestamp: str | None = None
    item_type: str = "post"  # post or comment
    captured_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class WorkerRunResult:
    run_id: str = ""
    started_at: str = ""
    ended_at: str = ""
    items_seen: int = 0
    items_new: int = 0
    items_sent: int = 0
    errors: list[str] = field(default_factory=list)
    state: WorkerState = WorkerState.STOPPED
