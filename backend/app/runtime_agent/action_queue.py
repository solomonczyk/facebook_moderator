"""Action queue: manages pending operator actions."""

import uuid
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum


class ActionType(str, Enum):
    REPLY_TO_COMMENT = "reply_to_comment"
    REPLY_TO_POST = "reply_to_post"
    CREATE_DIGEST_POST = "create_digest_post"
    PUBLISH_OWN_GROUP_POST = "publish_own_group_post"
    ASK_FOR_MISSING_INFO = "ask_for_missing_info"
    SAVE_WORKER_LEAD = "save_worker_lead"
    SAVE_EMPLOYER_LEAD = "save_employer_lead"
    MARK_DUPLICATE = "mark_duplicate"
    MARK_CLOSED = "mark_closed"
    REQUEST_OPERATOR_REVIEW = "request_operator_review"
    REVIEW_MODERATION_NEEDED = "review_moderation_needed"
    WORKER_EMPLOYER_MATCH_FOUND = "worker_employer_match_found"


class QueueStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    EDITED = "edited"
    REJECTED = "rejected"
    EXECUTED_MANUALLY = "executed_manually"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class QueueItem:
    item_id: str = field(default_factory=lambda: f"q_{uuid.uuid4().hex[:12]}")
    action_type: ActionType = ActionType.REQUEST_OPERATOR_REVIEW
    status: QueueStatus = QueueStatus.PENDING
    event_id: str | None = None
    lead_id: str | None = None
    suggested_text: str = ""
    edited_text: str = ""
    reason: str = ""
    operator: str = ""
    operator_approval_required: bool = True
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = ""

    def approve(self, operator: str = "") -> None:
        self.status = QueueStatus.APPROVED
        self.operator = operator
        self.updated_at = datetime.utcnow().isoformat()

    def reject(self, reason: str = "", operator: str = "") -> None:
        self.status = QueueStatus.REJECTED
        self.reason = reason
        self.operator = operator
        self.updated_at = datetime.utcnow().isoformat()

    def edit(self, new_text: str, operator: str = "") -> None:
        self.edited_text = new_text
        self.status = QueueStatus.EDITED
        self.operator = operator
        self.updated_at = datetime.utcnow().isoformat()

    def mark_executed(self, operator: str = "") -> None:
        self.status = QueueStatus.EXECUTED_MANUALLY
        self.operator = operator
        self.updated_at = datetime.utcnow().isoformat()

    def to_dict(self) -> dict:
        return {
            "item_id": self.item_id,
            "action_type": self.action_type.value,
            "status": self.status.value,
            "event_id": self.event_id,
            "lead_id": self.lead_id,
            "suggested_text": self.suggested_text,
            "edited_text": self.edited_text,
            "reason": self.reason,
            "operator_approval_required": self.operator_approval_required,
            "created_at": self.created_at,
        }


class ActionQueue:
    def __init__(self):
        self._items: dict[str, QueueItem] = {}

    def add(self, item: QueueItem) -> QueueItem:
        self._items[item.item_id] = item
        return item

    def get(self, item_id: str) -> QueueItem | None:
        return self._items.get(item_id)

    def get_all(self, status: QueueStatus | None = None) -> list[QueueItem]:
        items = list(self._items.values())
        if status:
            items = [i for i in items if i.status == status]
        return sorted(items, key=lambda i: i.created_at, reverse=True)

    def get_pending_count(self) -> int:
        return len(self.get_all(QueueStatus.PENDING))

    def get_summary(self) -> dict:
        pending = self.get_all(QueueStatus.PENDING)
        return {
            "total_pending": len(pending),
            "pending_replies": len([i for i in pending if i.action_type == ActionType.REPLY_TO_COMMENT]),
            "pending_posts": len([i for i in pending if i.action_type == ActionType.PUBLISH_OWN_GROUP_POST]),
            "pending_reviews": len([i for i in pending if i.action_type == ActionType.REVIEW_MODERATION_NEEDED]),
        }
