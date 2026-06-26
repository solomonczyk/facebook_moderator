"""Runtime event types and validation."""

import uuid
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum


class EventType(str, Enum):
    FACEBOOK_OWN_GROUP_POST_SEEN = "facebook_own_group_post_seen"
    FACEBOOK_OWN_GROUP_COMMENT_SEEN = "facebook_own_group_comment_seen"
    FACEBOOK_EXTERNAL_GROUP_POST_SEEN = "facebook_external_group_post_seen"
    TELEGRAM_SUBMISSION_RECEIVED = "telegram_submission_received"
    EMPLOYER_FORM_SUBMITTED = "employer_form_submitted"
    WORKER_FORM_SUBMITTED = "worker_form_submitted"
    REVIEW_SUBMITTED = "review_submitted"
    PUBLIC_WEB_LEAD_FOUND = "public_web_lead_found"
    MANUAL_OPERATOR_ENTRY = "manual_operator_entry"
    SCHEDULED_DIGEST_RUN = "scheduled_digest_run"
    SCHEDULED_FRESHNESS_CHECK = "scheduled_freshness_check"


class CaptureMethod(str, Enum):
    MANUAL_PASTE = "manual_paste"
    CLIPBOARD_INTAKE = "clipboard_intake"
    BROWSER_EXTENSION_VISIBLE_SELECTION = "browser_extension_visible_selection"
    PUBLIC_WEB_COLLECTOR = "public_web_collector"
    TELEGRAM_BOT = "telegram_bot"
    EMPLOYER_FORM = "employer_form"
    WORKER_FORM = "worker_form"
    OPERATOR_CONSOLE = "operator_console"


@dataclass
class RuntimeEvent:
    event_id: str = field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:12]}")
    event_type: EventType = EventType.MANUAL_OPERATOR_ENTRY
    source_type: str = "manual_operator_entry"
    source_name: str = ""
    source_url: str | None = None
    source_group: str | None = None
    author_display_name: str = ""
    raw_text: str = ""
    raw_image_path: str | None = None
    visible_created_at: str | None = None
    captured_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    capture_method: CaptureMethod = CaptureMethod.MANUAL_PASTE
    operator: str = ""
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "source_type": self.source_type,
            "source_name": self.source_name,
            "source_url": self.source_url,
            "source_group": self.source_group,
            "author_display_name": self.author_display_name,
            "raw_text": self.raw_text,
            "captured_at": self.captured_at,
            "capture_method": self.capture_method.value,
            "operator": self.operator,
        }


def validate_event(event: RuntimeEvent) -> list[str]:
    errors = []
    if not event.raw_text or not event.raw_text.strip():
        errors.append("raw_text is required")
    if not event.source_name:
        errors.append("source_name is required")
    return errors
