"""Test integration: intake → runtime agent → classification → queue."""

import sys
sys.path.insert(0, '.')

from app.aggregator_api.database import SessionLocal, init_db
from app.runtime_intake.intake_service import IntakeService
from app.runtime_agent.events import RuntimeEvent, EventType, CaptureMethod

init_db()

WORKER_EXAMPLE = (
    "Dobar dan inetreresujeme poso okolina sombora je ja Sam iz odzaka "
    "tako da mi odgovara sto blize imam dugogodisnje iskustvo za sve "
    "poljuprivredne radove grupovova sa svojim prevozom 30 ljudi hvala"
)


def test_intake_creates_agent_event():
    db = SessionLocal()
    service = IntakeService(db)

    event = RuntimeEvent(
        event_type=EventType.FACEBOOK_OWN_GROUP_COMMENT_SEEN,
        source_type="own_group_comment",
        source_name="Facebook",
        source_group="Sezonski rad Srbija",
        raw_text=WORKER_EXAMPLE,
        capture_method=CaptureMethod.BROWSER_EXTENSION_VISIBLE_SELECTION,
        operator="Andrii",
    )
    result = service.process_event(event)
    assert result.success is True
    assert result.classification == "worker_group_available"
    assert result.queue_item_id is not None
    db.close()


def test_intake_classifies_worker_group():
    db = SessionLocal()
    service = IntakeService(db)

    event = RuntimeEvent(
        event_type=EventType.MANUAL_OPERATOR_ENTRY,
        source_type="operator_pasted_text",
        source_name="Facebook",
        raw_text=WORKER_EXAMPLE,
        capture_method=CaptureMethod.MANUAL_PASTE,
        operator="Andrii",
    )
    result = service.process_event(event)
    assert result.success is True
    assert result.classification == "worker_group_available"
    db.close()


def test_auto_reply_not_submitted():
    db = SessionLocal()
    service = IntakeService(db)

    event = RuntimeEvent(
        event_type=EventType.MANUAL_OPERATOR_ENTRY,
        source_type="test",
        source_name="Test",
        raw_text=WORKER_EXAMPLE,
        capture_method=CaptureMethod.MANUAL_PASTE,
        operator="Andrii",
    )
    result = service.process_event(event)
    # suggested_reply exists but auto_reply is disabled
    assert result.suggested_reply != ""
    # No auto-posting — operator must approve
    assert service.config.auto_reply_enabled is False
    assert service.config.auto_post_enabled is False
    db.close()


if __name__ == '__main__':
    test_intake_creates_agent_event()
    test_intake_classifies_worker_group()
    test_auto_reply_not_submitted()
    print("[PASS] All runtime agent integration tests passed")
