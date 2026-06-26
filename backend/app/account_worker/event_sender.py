"""Event sender: converts captured items to runtime agent events."""

from ..runtime_agent.events import RuntimeEvent, EventType, CaptureMethod
from .config import WorkerConfig
from .worker_models import CapturedItem


def build_event(item: CapturedItem, config: WorkerConfig) -> RuntimeEvent:
    """Convert a captured item to a runtime agent event."""
    is_own = config.is_own_group(item.page_url)

    event_type = (
        EventType.FACEBOOK_OWN_GROUP_COMMENT_SEEN if "comment" in item.item_type
        else EventType.FACEBOOK_OWN_GROUP_POST_SEEN
    ) if is_own else EventType.FACEBOOK_EXTERNAL_GROUP_POST_SEEN

    return RuntimeEvent(
        event_type=event_type,
        source_type="own_group_post" if is_own else "facebook_operator_selection",
        source_name="Facebook",
        source_group="Sezonski rad Srbija | Poslovi i iskustva radnika" if is_own else "",
        source_url=item.source_url,
        raw_text=item.raw_text,
        visible_created_at=item.visible_timestamp,
        captured_at=item.captured_at,
        capture_method=CaptureMethod.BROWSER_EXTENSION_VISIBLE_SELECTION,
    )


def send_events(items: list[CapturedItem], config: WorkerConfig) -> list[RuntimeEvent]:
    """Build runtime events for captured items. External group items are skipped."""
    events = []
    for item in items:
        if not config.is_own_group(item.page_url) and "facebook.com/groups/" in item.page_url:
            continue  # Skip external groups
        events.append(build_event(item, config))
    return events
