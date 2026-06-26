"""Analyst audit log: records every decision with immutable entries."""

from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class AnalystAuditEntry:
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    decision_id: str = ""
    queue_item_id: str = ""
    action: str = ""
    risk_level: str = ""
    confidence: float = 0.0
    policy_allowed: bool = False
    executed: bool = False
    escalated: bool = False
    reasoning: str = ""
    operator: str = "analyst"


class AnalystAudit:
    def __init__(self):
        self._entries: list[AnalystAuditEntry] = []

    def record(self, decision_id: str, queue_item_id: str, action: str,
               risk_level: str, confidence: float, policy_allowed: bool,
               executed: bool, escalated: bool, reasoning: str = "") -> AnalystAuditEntry:
        entry = AnalystAuditEntry(
            decision_id=decision_id,
            queue_item_id=queue_item_id,
            action=action,
            risk_level=risk_level,
            confidence=confidence,
            policy_allowed=policy_allowed,
            executed=executed,
            escalated=escalated,
            reasoning=reasoning,
        )
        self._entries.append(entry)
        return entry

    @property
    def count(self) -> int:
        return len(self._entries)

    @property
    def executed_count(self) -> int:
        return len([e for e in self._entries if e.executed])

    @property
    def escalated_count(self) -> int:
        return len([e for e in self._entries if e.escalated])

    def recent(self, n: int = 20) -> list[AnalystAuditEntry]:
        return self._entries[-n:]

    def get_summary(self) -> dict:
        return {
            "total_decisions": self.count,
            "autonomous_executed": self.executed_count,
            "escalated_to_operator": self.escalated_count,
            "blocked_by_policy": len([e for e in self._entries if not e.policy_allowed]),
        }
