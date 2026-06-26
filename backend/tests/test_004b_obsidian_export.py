"""Test Obsidian markdown export."""

import sys
sys.path.insert(0, '.')

from app.aggregator_api.database import SessionLocal, init_db
from app.aggregator_api.service import LeadService
from app.aggregator_api.obsidian_export import export_lead_to_obsidian

init_db()


def test_export_creates_frontmatter():
    db = SessionLocal()
    service = LeadService(db)
    result = service.intake({
        "source_name": "021.rs",
        "source_type": "public_web",
        "location": "Arilje",
        "job_type": "branje malina",
        "contact_phone": "064-123-4567",
        "pay_amount": "5000 RSD dnevno",
        "accommodation": True,
        "food": True,
    })

    assert result is not None
    md = export_lead_to_obsidian(
        type("Lead", (), {
            "lead_id": result["lead_id"],
            "source_type": result["source_type"],
            "source_group": "",
            "source_url": "",
            "source_name": result["source_name"],
            "location": result["location"],
            "job_type": result["job_type"],
            "employer_name": None,
            "contact_phone": result["contact_phone"],
            "workers_needed": None,
            "pay_amount": result["pay_amount"],
            "accommodation": 1,
            "food": 1,
            "transport": None,
            "working_hours": None,
            "registered_work": None,
            "risk_level": result["risk_level"],
            "classification": result["classification"],
            "freshness_status": result["freshness_status"],
            "operator_verified": 0,
            "moderation_status": result["moderation_status"],
            "created_at": None,
            "missing_info_json": '["radno vreme", "prijava radnika"]',
        })
    )

    assert md.startswith("---")
    assert "type: vacancy" in md
    assert "location: Arilje" in md
    assert "job_type: branje malina" in md
    assert "contact_public: 064-123-4567" in md
    assert "Nedostaje:" in md
    db.close()


if __name__ == '__main__':
    test_export_creates_frontmatter()
    print("[PASS] All obsidian export tests passed")
