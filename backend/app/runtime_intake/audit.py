"""Intake audit: logs all intake events for transparency."""

from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class IntakeAuditEntry:
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    intake_method: str = ""
    raw_text_preview: str = ""
    event_id: str | None = None
    success: bool = False
    errors: list[str] = field(default_factory=list)


class IntakeAudit:
    def __init__(self):
        self._entries: list[IntakeAuditEntry] = []

    def record(self, method: str, text: str, event_id: str | None = None,
               success: bool = True, errors: list[str] | None = None) -> IntakeAuditEntry:
        entry = IntakeAuditEntry(
            intake_method=method,
            raw_text_preview=text[:100] if text else "",
            event_id=event_id,
            success=success,
            errors=errors or [],
        )
        self._entries.append(entry)
        return entry

    @property
    def count(self) -> int:
        return len(self._entries)

    def recent(self, n: int = 20) -> list[IntakeAuditEntry]:
        return self._entries[-n:]
