"""Intake request/response models."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ManualPasteRequest:
    source_type: str = "operator_pasted_text"
    source_name: str = "Facebook"
    source_group: str = ""
    source_url: str | None = None
    raw_text: str = ""
    operator: str = ""


@dataclass
class BrowserSelectionRequest:
    capture_method: str = "browser_extension_visible_selection"
    page_url: str = ""
    page_title: str = ""
    selected_text: str = ""
    source_group: str = ""
    captured_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    operator: str = ""


@dataclass
class ClipboardRequest:
    capture_method: str = "clipboard_intake"
    raw_text: str = ""
    operator: str = ""


@dataclass
class VisibleGroupRequest:
    capture_method: str = "own_group_visible_intake"
    page_url: str = ""
    source_group: str = ""
    visible_text_blocks: list[str] = field(default_factory=list)
    captured_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    operator: str = ""


@dataclass
class IntakeResponse:
    success: bool
    event_id: str | None = None
    classification: str = ""
    queue_item_id: str | None = None
    suggested_reply: str = ""
    action: str = ""
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "event_id": self.event_id,
            "classification": self.classification,
            "queue_item_id": self.queue_item_id,
            "suggested_reply": self.suggested_reply[:300] if self.suggested_reply else "",
            "action": self.action,
            "errors": self.errors,
        }
