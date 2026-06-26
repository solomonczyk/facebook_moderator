"""Test event sender: captured items -> runtime events, external group rejection."""

import sys, hashlib
sys.path.insert(0, '.')

from app.account_worker.event_sender import build_event, send_events
from app.account_worker.config import WorkerConfig
from app.account_worker.worker_models import CapturedItem


def _make_item(text: str, page_url: str = "", item_type: str = "post") -> CapturedItem:
    h = hashlib.sha256(text.encode()).hexdigest()
    return CapturedItem(item_id=f"t_{h[:8]}", raw_text=text, content_hash=h,
                        page_url=page_url, item_type=item_type)


def test_build_event_own_group():
    cfg = WorkerConfig()
    cfg.own_group_url = "https://www.facebook.com/groups/992369183697618"
    item = _make_item("Radnici za berbu", "https://www.facebook.com/groups/992369183697618/posts/1")
    event = build_event(item, cfg)
    assert event.raw_text == "Radnici za berbu"
    assert "own_group" in event.event_type.value


def test_external_group_rejected():
    cfg = WorkerConfig()
    cfg.own_group_url = "https://www.facebook.com/groups/992369183697618"
    item = _make_item("External post", "https://www.facebook.com/groups/999999999/posts/2")
    events = send_events([item], cfg)
    assert len(events) == 0  # External group skipped


def test_own_group_items_sent():
    cfg = WorkerConfig()
    cfg.own_group_url = "https://www.facebook.com/groups/992369183697618"
    items = [
        _make_item("Post 1", "https://www.facebook.com/groups/992369183697618/posts/1"),
        _make_item("Post 2", "https://www.facebook.com/groups/992369183697618/posts/2"),
    ]
    events = send_events(items, cfg)
    assert len(events) == 2


if __name__ == '__main__':
    test_build_event_own_group()
    test_external_group_rejected()
    test_own_group_items_sent()
    print("[PASS] All event sender tests passed")
