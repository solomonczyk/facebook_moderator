"""Maps intake payloads to TASK 005A runtime events."""

from ..runtime_agent.events import RuntimeEvent, EventType, CaptureMethod


def manual_paste_to_event(req) -> RuntimeEvent:
    return RuntimeEvent(
        event_type=EventType.MANUAL_OPERATOR_ENTRY,
        source_type="operator_pasted_text",
        source_name=req.source_name,
        source_group=req.source_group,
        source_url=req.source_url,
        raw_text=req.raw_text,
        capture_method=CaptureMethod.MANUAL_PASTE,
        operator=req.operator,
    )


def browser_selection_to_event(req) -> RuntimeEvent:
    # Determine if own group or external
    source_group = req.source_group or _extract_group_from_url(req.page_url)
    is_own = "992369183697618" in req.page_url or "Sezonski rad Srbija" in req.page_title

    event_type = (
        EventType.FACEBOOK_OWN_GROUP_COMMENT_SEEN if is_own
        else EventType.FACEBOOK_EXTERNAL_GROUP_POST_SEEN
    )
    source_type = "own_group_comment" if is_own else "facebook_operator_selection"

    return RuntimeEvent(
        event_type=event_type,
        source_type=source_type,
        source_name="Facebook",
        source_group=source_group,
        source_url=req.page_url,
        raw_text=req.selected_text,
        capture_method=CaptureMethod.BROWSER_EXTENSION_VISIBLE_SELECTION,
        operator=req.operator,
    )


def clipboard_to_event(req) -> RuntimeEvent:
    return RuntimeEvent(
        event_type=EventType.MANUAL_OPERATOR_ENTRY,
        source_type="clipboard_intake",
        source_name="Clipboard",
        raw_text=req.raw_text,
        capture_method=CaptureMethod.CLIPBOARD_INTAKE,
        operator=req.operator,
    )


def visible_group_to_event(req) -> list[RuntimeEvent]:
    events = []
    for block in req.visible_text_blocks:
        if block.strip():
            events.append(RuntimeEvent(
                event_type=EventType.FACEBOOK_OWN_GROUP_POST_SEEN,
                source_type="own_group_post",
                source_name="Facebook",
                source_group=req.source_group,
                source_url=req.page_url,
                raw_text=block,
                capture_method=CaptureMethod.BROWSER_EXTENSION_VISIBLE_SELECTION,
                operator=req.operator,
            ))
    return events


def _extract_group_from_url(url: str) -> str:
    if "groups/" in url:
        parts = url.split("groups/")
        if len(parts) > 1:
            return parts[1].split("/")[0]
    return ""
