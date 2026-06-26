"""Test duplicate detection through the service layer."""

import sys
sys.path.insert(0, '.')

from app.aggregator_api.database import SessionLocal, init_db
from app.aggregator_api.service import LeadService

init_db()


def test_same_phone_detected_as_duplicate():
    db = SessionLocal()
    service = LeadService(db)

    r1 = service.intake({
        "source_name": "Test",
        "location": "Arilje",
        "job_type": "branje malina",
        "contact_phone": "064-988-5113",
    })
    r2 = service.intake({
        "source_name": "Test",
        "location": "Arilje",
        "job_type": "branje malina",
        "contact_phone": "0649885113",  # Same number, different format
    })
    possible_dup = r2["duplicate_status"] in ["duplicate", "possible_duplicate"]
    assert possible_dup, f"Expected duplicate but got {r2['duplicate_status']}"
    db.close()


def test_different_phone_is_new():
    db = SessionLocal()
    service = LeadService(db)
    r = service.intake({
        "source_name": "Test",
        "location": "Beograd",
        "job_type": "gradjevina",
        "contact_phone": "064-000-0099",
    })
    assert r["duplicate_status"] == "new"
    db.close()


if __name__ == '__main__':
    test_same_phone_detected_as_duplicate()
    test_different_phone_is_new()
    print("[PASS] All duplicate storage tests passed")
