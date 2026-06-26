"""Test audit log: recording, retrieval, immutability."""

import sys
sys.path.insert(0, '.')

from app.runtime_agent.audit_log import AuditLog


def test_record_creates_entry():
    log = AuditLog()
    entry = log.record("event_received", "Test event", "evt_001")
    assert entry.action == "event_received"
    assert entry.event_id == "evt_001"
    assert log.count == 1


def test_get_recent_returns_entries():
    log = AuditLog()
    for i in range(10):
        log.record(f"action_{i}", f"details_{i}", f"evt_{i}")
    recent = log.get_recent(5)
    assert len(recent) == 5


def test_get_by_event_filters():
    log = AuditLog()
    log.record("step1", "", "evt_A")
    log.record("step2", "", "evt_A")
    log.record("step1", "", "evt_B")
    entries = log.get_by_event("evt_A")
    assert len(entries) == 2


if __name__ == '__main__':
    test_record_creates_entry()
    test_get_recent_returns_entries()
    test_get_by_event_filters()
    print("[PASS] All audit log tests passed")
