"""Moderation queue: manages lead and review moderation workflow."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4
from .models import ModerationStatus, JobLead


@dataclass
class ModerationAction:
    action_id: UUID = field(default_factory=uuid4)
    lead_id: UUID | None = None
    review_id: UUID | None = None
    from_status: ModerationStatus = ModerationStatus.NEW
    to_status: ModerationStatus = ModerationStatus.NEW
    operator: str = ""
    reason: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)


class ModerationQueue:
    """Simple in-memory moderation queue. Replace with DB in production."""

    def __init__(self):
        self._queue: dict[UUID, JobLead] = {}
        self._history: list[ModerationAction] = []

    def add(self, lead: JobLead) -> None:
        self._queue[lead.lead_id] = lead

    def approve(self, lead_id: UUID, operator: str = "") -> ModerationAction:
        lead = self._queue.get(lead_id)
        action = ModerationAction(
            lead_id=lead_id,
            from_status=lead.moderation_status if lead else ModerationStatus.NEW,
            to_status=ModerationStatus.APPROVED_FOR_DIGEST,
            operator=operator,
            reason="Approved for public digest",
        )
        if lead:
            lead.moderation_status = ModerationStatus.APPROVED_FOR_DIGEST
            lead.public_digest_allowed = True
        self._history.append(action)
        return action

    def reject(self, lead_id: UUID, reason: str, operator: str = "") -> ModerationAction:
        lead = self._queue.get(lead_id)
        action = ModerationAction(
            lead_id=lead_id,
            from_status=lead.moderation_status if lead else ModerationStatus.NEW,
            to_status=ModerationStatus.REJECTED,
            operator=operator,
            reason=reason,
        )
        if lead:
            lead.moderation_status = ModerationStatus.REJECTED
            lead.public_digest_allowed = False
        self._history.append(action)
        return action

    def escalate(self, lead_id: UUID, reason: str, operator: str = "") -> ModerationAction:
        lead = self._queue.get(lead_id)
        action = ModerationAction(
            lead_id=lead_id,
            from_status=lead.moderation_status if lead else ModerationStatus.NEW,
            to_status=ModerationStatus.ESCALATED,
            operator=operator,
            reason=reason,
        )
        if lead:
            lead.moderation_status = ModerationStatus.ESCALATED
            lead.public_digest_allowed = False
        self._history.append(action)
        return action

    def get_pending(self) -> list[JobLead]:
        return [
            lead for lead in self._queue.values()
            if lead.moderation_status == ModerationStatus.NEW
        ]

    def get_escalated(self) -> list[JobLead]:
        return [
            lead for lead in self._queue.values()
            if lead.moderation_status == ModerationStatus.ESCALATED
        ]
