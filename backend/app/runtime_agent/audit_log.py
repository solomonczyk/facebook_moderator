"""Audit log: immutable event processing and action tracking."""

import uuid
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class AuditEntry:
    entry_id: str = field(default_factory=lambda: f"audit_{uuid.uuid4().hex[:12]}")
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    event_id: str | None = None
    action: str = ""
    agent_version: str = "0.1.0"
    operator: str = ""
    details: str = ""
    previous_state: str = ""
    new_state: str = ""


class AuditLog:
    def __init__(self):
        self._entries: list[AuditEntry] = []

    def record(self, action: str, details: str = "", event_id: str | None = None,
               operator: str = "", previous_state: str = "", new_state: str = "") -> AuditEntry:
        entry = AuditEntry(
            event_id=event_id,
            action=action,
            operator=operator,
            details=details,
            previous_state=previous_state,
            new_state=new_state,
        )
        self._entries.append(entry)
        return entry

    def get_recent(self, limit: int = 50) -> list[AuditEntry]:
        return self._entries[-limit:]

    def get_by_event(self, event_id: str) -> list[AuditEntry]:
        return [e for e in self._entries if e.event_id == event_id]

    @property
    def count(self) -> int:
        return len(self._entries)
