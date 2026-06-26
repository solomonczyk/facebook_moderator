"""Test database schema initialization and table structure."""

import sys
sys.path.insert(0, '.')

from app.aggregator_api.database import init_db, engine
from app.aggregator_api.db_models import Base


def test_all_tables_exist():
    init_db()
    inspector = None
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    required = ["job_leads", "employers", "workers", "reviews", "moderation_events"]
    for table in required:
        assert table in tables, f"Missing table: {table}"


def test_job_leads_columns():
    from sqlalchemy import inspect
    inspector = inspect(engine)
    columns = [c["name"] for c in inspector.get_columns("job_leads")]
    required = [
        "id", "lead_id", "source_type", "source_name", "source_url",
        "raw_text", "language", "job_type", "location", "contact_phone",
        "risk_level", "classification", "duplicate_status", "moderation_status",
        "public_digest_allowed", "operator_verified", "created_at",
    ]
    for col in required:
        assert col in columns, f"Missing column: {col}"


def test_employers_columns():
    from sqlalchemy import inspect
    columns = [c["name"] for c in inspect(engine).get_columns("employers")]
    required = ["employer_id", "display_name", "phone_numbers_json", "locations_json"]
    for col in required:
        assert col in columns, f"Missing column: {col}"


def test_moderation_events_columns():
    from sqlalchemy import inspect
    columns = [c["name"] for c in inspect(engine).get_columns("moderation_events")]
    required = ["entity_type", "entity_id", "old_status", "new_status", "reason", "operator"]
    for col in required:
        assert col in columns, f"Missing column: {col}"


if __name__ == '__main__':
    test_all_tables_exist()
    test_job_leads_columns()
    test_employers_columns()
    test_moderation_events_columns()
    print("[PASS] All database schema tests passed")
