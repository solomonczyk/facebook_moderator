"""Test runtime agent core: event processing, classification, queue."""

import sys
sys.path.insert(0, '.')

from app.aggregator_api.database import SessionLocal, init_db
from app.runtime_agent.agent_core import RuntimeAgent
from app.runtime_agent.events import RuntimeEvent, EventType, CaptureMethod
from app.runtime_agent.brain import classify, ContentClass
from app.runtime_agent.config import RuntimeConfig

init_db()

# ── Example from spec: worker group near Sombor ────────────────────────────

WORKER_GROUP_EXAMPLE = (
    "Dobar dan inetreresujeme poso okolina sombora je ja Sam iz odzaka "
    "tako da mi odgovara sto blize imam dugogodisnje iskustvo za sve "
    "poljuprivredne radove grupovova sa svojim prevozom 30 ljudi hvala"
)


def test_worker_group_classified_correctly():
    result = classify(WORKER_GROUP_EXAMPLE)
    assert result.classification == ContentClass.WORKER_GROUP_AVAILABLE, \
        f"Expected WORKER_GROUP_AVAILABLE, got {result.classification}"
    assert result.confidence > 0.5


def test_worker_group_extracts_count():
    result = classify(WORKER_GROUP_EXAMPLE)
    assert result.extracted_entities.get("workers_count") == 30


def test_worker_group_extracts_locations():
    result = classify(WORKER_GROUP_EXAMPLE)
    locations = result.extracted_entities.get("locations", [])
    has_location = any(loc.lower() in ["sombor", "odžaci"] for loc in locations)
    assert has_location, f"Expected Sombor or Odzaci in locations, got {locations}"


def test_worker_group_extracts_transport():
    result = classify(WORKER_GROUP_EXAMPLE)
    assert result.extracted_entities.get("transport") == "own_transport"


def test_worker_group_has_experience():
    result = classify(WORKER_GROUP_EXAMPLE)
    assert result.extracted_entities.get("experience") == "agricultural_or_manual"


def test_worker_group_contact_missing():
    result = classify(WORKER_GROUP_EXAMPLE)
    assert result.extracted_entities.get("contact_status") == "missing"


def test_worker_group_generates_reply():
    result = classify(WORKER_GROUP_EXAMPLE)
    assert len(result.suggested_reply) > 50
    assert "telefon" in result.suggested_reply.lower() or "kontakt" in result.suggested_reply.lower()


def test_worker_group_requires_approval():
    result = classify(WORKER_GROUP_EXAMPLE)
    assert result.operator_approval_required is True


def test_runtime_agent_processes_event():
    db = SessionLocal()
    agent = RuntimeAgent(db)
    event = RuntimeEvent(
        event_type=EventType.MANUAL_OPERATOR_ENTRY,
        source_type="facebook_operator_screenshot",
        source_name="Malinari Srbija",
        raw_text=WORKER_GROUP_EXAMPLE,
        capture_method=CaptureMethod.MANUAL_PASTE,
        operator="Andrii",
    )
    result = agent.process_event(event)
    assert result["success"] is True
    assert result["classification"] == "worker_group_available"
    assert result["operator_approval_required"] is True
    db.close()


def test_queue_item_created():
    db = SessionLocal()
    agent = RuntimeAgent(db)
    event = RuntimeEvent(
        event_type=EventType.MANUAL_OPERATOR_ENTRY,
        source_type="facebook_operator_screenshot",
        source_name="Test",
        raw_text="Tražim posao branje malina Arilje 064-123-4567",
        capture_method=CaptureMethod.MANUAL_PASTE,
    )
    agent.process_event(event)
    pending = agent.queue.get_pending_count()
    assert pending >= 1
    db.close()


if __name__ == '__main__':
    test_worker_group_classified_correctly()
    test_worker_group_extracts_count()
    test_worker_group_extracts_locations()
    test_worker_group_extracts_transport()
    test_worker_group_has_experience()
    test_worker_group_contact_missing()
    test_worker_group_generates_reply()
    test_worker_group_requires_approval()
    test_runtime_agent_processes_event()
    test_queue_item_created()
    print("[PASS] All runtime agent core tests passed")
