"""Worker audit log: records all capture cycles and state changes."""

from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class WorkerAuditEntry:
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    action: str = ""
    details: str = ""
    state_before: str = ""
    state_after: str = ""


class WorkerAudit:
    def __init__(self):
        self._entries: list[WorkerAuditEntry] = []

    def record(self, action: str, details: str = "",
               state_before: str = "", state_after: str = "") -> WorkerAuditEntry:
        entry = WorkerAuditEntry(
            action=action,
            details=details,
            state_before=state_before,
            state_after=state_after,
        )
        self._entries.append(entry)
        return entry

    @property
    def count(self) -> int:
        return len(self._entries)

    def recent(self, n: int = 30) -> list[WorkerAuditEntry]:
        return self._entries[-n:]
