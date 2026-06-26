"""
JSON schemas and validation for the aggregator.
For MVP, uses simple dict validation. Migrate to Pydantic in production.
"""

from typing import Any

# ── Lead Intake Schema ──────────────────────────────────────────────────────

LEAD_INTAKE_SCHEMA: dict[str, dict[str, Any]] = {
    "source_type": {"type": "str", "required": True},
    "source_name": {"type": "str", "required": True},
    "source_url": {"type": "str", "required": False},
    "source_group": {"type": "str", "required": False},
    "raw_text": {"type": "str", "required": False},
    "language": {"type": "str", "required": False, "default": "sr"},
    "job_type": {"type": "str", "required": True},
    "location": {"type": "str", "required": True},
    "workers_needed": {"type": "int", "required": False},
    "pay_amount": {"type": "str", "required": False},
    "pay_type": {"type": "str", "required": False},
    "accommodation": {"type": "bool", "required": False},
    "food": {"type": "bool", "required": False},
    "transport": {"type": "bool", "required": False},
    "working_hours": {"type": "str", "required": False},
    "registered_work": {"type": "bool", "required": False},
    "employer_name": {"type": "str", "required": False},
    "contact_phone": {"type": "str", "required": False},
    "contact_inbox_only": {"type": "bool", "required": False, "default": False},
}


def validate_lead_intake(data: dict) -> list[str]:
    """Validate a lead intake dict. Returns list of missing required fields."""
    errors = []
    for field, rules in LEAD_INTAKE_SCHEMA.items():
        if rules.get("required") and field not in data:
            errors.append(f"Missing required field: {field}")
    return errors


# ── Review Submission Schema ────────────────────────────────────────────────

REVIEW_SCHEMA: dict[str, dict[str, Any]] = {
    "review_type": {"type": "str", "required": True},
    "target_type": {"type": "str", "required": True},
    "target_id": {"type": "str", "required": False},
    "author_type": {"type": "str", "required": True},
    "job_lead_id": {"type": "str", "required": False},
    "rating_overall": {"type": "int", "required": True, "min": 1, "max": 5},
    "rating_pay_accuracy": {"type": "int", "required": False},
    "rating_accommodation": {"type": "int", "required": False},
    "rating_food": {"type": "int", "required": False},
    "rating_working_hours": {"type": "int", "required": False},
    "rating_payment_timeliness": {"type": "int", "required": False},
    "rating_respect": {"type": "int", "required": False},
    "text": {"type": "str", "required": True},
}


def validate_review(data: dict) -> list[str]:
    errors = []
    for field, rules in REVIEW_SCHEMA.items():
        if rules.get("required") and field not in data:
            errors.append(f"Missing required field: {field}")
    if "rating_overall" in data:
        r = data["rating_overall"]
        if not (1 <= int(r) <= 5):
            errors.append("rating_overall must be 1-5")
    return errors
