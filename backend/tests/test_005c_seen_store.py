"""Test seen store: deduplication by content hash."""

import sys
sys.path.insert(0, '.')

from app.account_worker.seen_store import SeenStore
from app.account_worker.worker_models import CapturedItem


def _make_item(text: str) -> CapturedItem:
    import hashlib
    h = hashlib.sha256(text.encode()).hexdigest()
    return CapturedItem(item_id=f"test_{h[:8]}", raw_text=text, content_hash=h)


def test_new_item_is_new():
    store = SeenStore()
    item = _make_item("test text")
    assert store.is_new(item.content_hash) is True


def test_seen_item_not_new():
    store = SeenStore()
    item = _make_item("test text")
    store.mark_seen(item.content_hash, item.item_id)
    assert store.is_new(item.content_hash) is False


def test_filter_new_returns_only_new():
    store = SeenStore()
    item1 = _make_item("text one")
    item2 = _make_item("text two")
    store.mark_seen(item1.content_hash, item1.item_id)
    new_items = store.filter_new([item1, item2])
    assert len(new_items) == 1
    assert new_items[0].raw_text == "text two"


def test_duplicate_content_filtered():
    store = SeenStore()
    items = [_make_item("same text"), _make_item("same text")]
    new = store.filter_new(items)
    assert len(new) == 1  # Only first one
    new2 = store.filter_new([_make_item("same text")])
    assert len(new2) == 0  # Already seen


if __name__ == '__main__':
    test_new_item_is_new()
    test_seen_item_not_new()
    test_filter_new_returns_only_new()
    test_duplicate_content_filtered()
    print("[PASS] All seen store tests passed")
