"""Test action queue: approve, reject, edit, mark executed."""

import sys
sys.path.insert(0, '.')

from app.runtime_agent.action_queue import ActionQueue, QueueItem, ActionType, QueueStatus


def test_queue_item_defaults():
    item = QueueItem()
    assert item.status == QueueStatus.PENDING
    assert item.operator_approval_required is True


def test_approve_changes_status():
    item = QueueItem()
    item.approve("Andrii")
    assert item.status == QueueStatus.APPROVED


def test_reject_changes_status():
    item = QueueItem()
    item.reject("spam", "Andrii")
    assert item.status == QueueStatus.REJECTED


def test_edit_updates_text():
    item = QueueItem(suggested_text="original")
    item.edit("edited text", "Andrii")
    assert item.status == QueueStatus.EDITED
    assert item.edited_text == "edited text"


def test_mark_executed():
    item = QueueItem()
    item.approve("Andrii")
    item.mark_executed("Andrii")
    assert item.status == QueueStatus.EXECUTED_MANUALLY


def test_queue_get_pending():
    q = ActionQueue()
    q.add(QueueItem(action_type=ActionType.REPLY_TO_COMMENT))
    q.add(QueueItem(action_type=ActionType.PUBLISH_OWN_GROUP_POST))
    assert q.get_pending_count() == 2


def test_queue_summary():
    q = ActionQueue()
    q.add(QueueItem(action_type=ActionType.REPLY_TO_COMMENT))
    q.add(QueueItem(action_type=ActionType.CREATE_DIGEST_POST))
    summary = q.get_summary()
    assert summary["total_pending"] == 2
    assert summary["pending_replies"] == 1
    assert summary["pending_posts"] == 0


if __name__ == '__main__':
    test_queue_item_defaults()
    test_approve_changes_status()
    test_reject_changes_status()
    test_edit_updates_text()
    test_mark_executed()
    test_queue_get_pending()
    test_queue_summary()
    print("[PASS] All action queue tests passed")
