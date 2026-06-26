"""Test lead service: intake, normalize, dedup, score, moderate."""

import sys, os
sys.path.insert(0, '.')

from app.aggregator_api.database import SessionLocal, init_db
from app.aggregator_api.service import LeadService

init_db()


def test_intake_creates_lead():
    db = SessionLocal()
    service = LeadService(db)
    result = service.intake({
        "source_type": "facebook_operator_screenshot",
        "source_name": "Malinari Srbija",
        "raw_text": "Radnici za branje malina, Arilje, 064-123-4567",
        "location": "Arilje",
        "job_type": "branje malina",
        "contact_phone": "064-123-4567",
        "post_date": "2026-06-26",
        "operator_confirmed_active": True,
    })
    assert result["lead_id"].startswith("lead_")
    assert result["location"] == "Arilje"
    assert result["job_type"] == "branje malina"
    assert result["moderation_status"] == "pending_review"
    assert result["public_digest_allowed"] is False
    assert result["operator_verified"] is False
    db.close()


def test_intake_sets_freshness():
    db = SessionLocal()
    service = LeadService(db)
    result = service.intake({
        "source_name": "Test",
        "raw_text": "Test lead",
        "location": "Test",
        "job_type": "test",
        "contact_phone": "064-999-9999",
        "post_date": "2026-06-26",
        "operator_confirmed_active": True,
    })
    assert result["freshness_status"] in ["fresh_today", "fresh_1_3_days", "fresh_4_7_days"]
    db.close()


def test_intake_classifies_lead():
    db = SessionLocal()
    service = LeadService(db)
    result = service.intake({
        "source_name": "Test",
        "raw_text": "Complete lead with good info",
        "location": "Arilje",
        "job_type": "branje malina",
        "contact_phone": "064-111-1111",
        "pay_amount": "5000 RSD dnevno",
        "accommodation": True,
        "food": True,
        "working_hours": "06-14h",
    })
    assert result["classification"] in [
        "good_lead", "low_info_lead", "contact_only_lead", "needs_clarification"
    ]
    db.close()


def test_moderate_approve():
    db = SessionLocal()
    service = LeadService(db)
    result = service.intake({
        "source_name": "Test",
        "location": "Test",
        "job_type": "test",
        "contact_phone": "064-777-7777",
    })
    lead_id = result["lead_id"]
    mod_result = service.moderate(lead_id, "approve", "valid public lead", "Andrii")
    assert mod_result is not None
    assert mod_result["moderation_status"] == "approved_for_digest"
    assert mod_result["public_digest_allowed"] is True
    db.close()


def test_moderate_reject():
    db = SessionLocal()
    service = LeadService(db)
    result = service.intake({
        "source_name": "Test",
        "location": "Test",
        "job_type": "test",
        "contact_phone": "064-666-6666",
    })
    lead_id = result["lead_id"]
    mod_result = service.moderate(lead_id, "reject", "spam", "Andrii")
    assert mod_result["moderation_status"] == "rejected"
    assert mod_result["public_digest_allowed"] is False
    db.close()


def test_rejected_not_in_digest():
    db = SessionLocal()
    service = LeadService(db)
    result = service.intake({
        "source_name": "Test",
        "location": "Test",
        "job_type": "test",
        "contact_phone": "064-555-5555",
        "accommodation": True,
        "food": True,
        "post_date": "2026-06-26",
    })
    service.moderate(result["lead_id"], "approve", "OK", "Andrii")
    result2 = service.intake({
        "source_name": "Test",
        "location": "Test2",
        "job_type": "test2",
        "contact_phone": "064-444-4444",
    })
    service.moderate(result2["lead_id"], "reject", "spam", "Andrii")
    candidates = service.get_digest_candidates()
    candidate_ids = [c["lead_id"] for c in candidates]
    assert result["lead_id"] in candidate_ids, f"Expected {result['lead_id']} in candidates, got {candidate_ids}"
    assert result2["lead_id"] not in candidate_ids
    db.close()


def test_spam_rejected_by_risk():
    db = SessionLocal()
    service = LeadService(db)
    result = service.intake({
        "source_name": "Test",
        "raw_text": "BRZA ZARADA! Klikni ovde! Kazino!",
        "location": "",
        "job_type": "",
    })
    assert result["risk_level"] in ["high", "reject"]
    db.close()


if __name__ == '__main__':
    test_intake_creates_lead()
    test_intake_sets_freshness()
    test_intake_classifies_lead()
    test_moderate_approve()
    test_moderate_reject()
    test_rejected_not_in_digest()
    test_spam_rejected_by_risk()
    print("[PASS] All lead service tests passed")
