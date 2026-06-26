"""Test event mapper: intake payloads -> runtime events."""

import sys
sys.path.insert(0, '.')

from app.runtime_intake.event_mapper import (
    manual_paste_to_event, browser_selection_to_event,
    clipboard_to_event,
)
from app.runtime_intake.intake_models import (
    ManualPasteRequest, BrowserSelectionRequest, ClipboardRequest,
)

WORKER_EXAMPLE = (
    "Dobar dan inetreresujeme poso okolina sombora je ja Sam iz odzaka "
    "tako da mi odgovara sto blize imam dugogodisnje iskustvo za sve "
    "poljuprivredne radove grupovova sa svojim prevozom 30 ljudi hvala"
)


def test_manual_paste_maps_event():
    req = ManualPasteRequest(
        source_name="Facebook",
        source_group="Malinari Srbija",
        raw_text=WORKER_EXAMPLE,
        operator="Andrii",
    )
    event = manual_paste_to_event(req)
    assert event.raw_text == WORKER_EXAMPLE
    assert event.source_group == "Malinari Srbija"
    assert event.operator == "Andrii"


def test_browser_selection_maps_own_group():
    req = BrowserSelectionRequest(
        page_url="https://www.facebook.com/groups/992369183697618/posts/123",
        page_title="Sezonski rad Srbija | Poslovi i iskustva radnika",
        selected_text=WORKER_EXAMPLE,
        operator="Andrii",
    )
    event = browser_selection_to_event(req)
    assert event.raw_text == WORKER_EXAMPLE
    assert "992369183697618" in event.source_url
    # Own group -> facebook_own_group_comment_seen
    assert "own_group" in event.event_type.value


def test_browser_selection_external_group():
    req = BrowserSelectionRequest(
        page_url="https://www.facebook.com/groups/other-group/posts/456",
        page_title="Some Other Group",
        selected_text="Tražim radnike...",
        operator="Andrii",
    )
    event = browser_selection_to_event(req)
    assert event.raw_text == "Tražim radnike..."
    assert event.event_type.value == "facebook_external_group_post_seen"


def test_clipboard_maps_event():
    req = ClipboardRequest(raw_text=WORKER_EXAMPLE, operator="Andrii")
    event = clipboard_to_event(req)
    assert event.raw_text == WORKER_EXAMPLE
    assert event.capture_method.value == "clipboard_intake"


def test_source_url_preserved():
    req = BrowserSelectionRequest(
        page_url="https://www.facebook.com/groups/test/posts/789",
        page_title="Test",
        selected_text="Test text",
        operator="Andrii",
    )
    event = browser_selection_to_event(req)
    assert "facebook.com/groups/test" in event.source_url


if __name__ == '__main__':
    test_manual_paste_maps_event()
    test_browser_selection_maps_own_group()
    test_browser_selection_external_group()
    test_clipboard_maps_event()
    test_source_url_preserved()
    print("[PASS] All event mapper tests passed")
