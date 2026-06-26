"""Repository layer: CRUD operations for database entities."""

import json
from datetime import datetime
from sqlalchemy.orm import Session
from .db_models import (
    JobLeadDB, EmployerDB, WorkerDB, ReviewDB, ModerationEventDB,
    _json_list, _json_dict,
)


class LeadRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict) -> JobLeadDB:
        lead = JobLeadDB(
            lead_id=data["lead_id"],
            source_type=data.get("source_type", "manual_admin_entry"),
            source_name=data.get("source_name", ""),
            source_url=data.get("source_url"),
            source_group=data.get("source_group"),
            source_post_url=data.get("source_post_url"),
            source_captured_at=data.get("source_captured_at", datetime.utcnow()),
            source_capture_method=data.get("source_capture_method", "operator_copy_paste"),
            raw_text=data.get("raw_text"),
            language=data.get("language", "sr"),
            job_type=data.get("job_type", ""),
            location=data.get("location", ""),
            region=data.get("region"),
            country=data.get("country", "Srbija"),
            workers_needed=data.get("workers_needed"),
            pay_amount=data.get("pay_amount"),
            pay_type=data.get("pay_type"),
            accommodation=1 if data.get("accommodation") else (0 if data.get("accommodation") is False else None),
            food=1 if data.get("food") else (0 if data.get("food") is False else None),
            transport=1 if data.get("transport") else (0 if data.get("transport") is False else None),
            working_hours=data.get("working_hours"),
            registered_work=1 if data.get("registered_work") else (0 if data.get("registered_work") is False else None),
            employer_name=data.get("employer_name"),
            contact_phone=data.get("contact_phone"),
            contact_inbox_only=data.get("contact_inbox_only", False),
            missing_info_json=_json_list(data.get("missing_info", [])),
            freshness_status=data.get("freshness_status", "unknown_date"),
            risk_level=data.get("risk_level", "medium"),
            risk_flags_json=_json_list(data.get("risk_flags", [])),
            classification=data.get("classification", "needs_clarification"),
            duplicate_status=data.get("duplicate_status", "new"),
            duplicate_of=data.get("duplicate_of"),
            moderation_status=data.get("moderation_status", "pending_review"),
            public_digest_allowed=1 if data.get("public_digest_allowed") else 0,
            operator_verified=1 if data.get("operator_verified") else 0,
        )
        self.db.add(lead)
        self.db.commit()
        self.db.refresh(lead)
        return lead

    def get_by_lead_id(self, lead_id: str) -> JobLeadDB | None:
        return self.db.query(JobLeadDB).filter(JobLeadDB.lead_id == lead_id).first()

    def get_all(self, **filters) -> list[JobLeadDB]:
        q = self.db.query(JobLeadDB)
        for field, value in filters.items():
            if hasattr(JobLeadDB, field) and value is not None:
                q = q.filter(getattr(JobLeadDB, field) == value)
        return q.order_by(JobLeadDB.created_at.desc()).all()

    def get_digest_candidates(self, min_fresh: int = 5) -> list[JobLeadDB]:
        self.db.flush()
        fresh = self.db.query(JobLeadDB).filter(
            JobLeadDB.public_digest_allowed == 1,
            JobLeadDB.moderation_status == "approved_for_digest",
            JobLeadDB.risk_level.in_(["low", "medium"]),
            JobLeadDB.classification.in_([
                "good_lead", "low_info_lead", "contact_only_lead", "repeat_candidate",
            ]),
            JobLeadDB.freshness_status.in_([
                "fresh_today", "fresh_1_3_days", "fresh_4_7_days",
            ]),
        ).order_by(JobLeadDB.created_at.desc()).all()

        fresh_count = len([l for l in fresh if l.classification != "repeat_candidate"])
        if fresh_count < min_fresh:
            repeats = self.db.query(JobLeadDB).filter(
                JobLeadDB.classification == "repeat_candidate",
                JobLeadDB.public_digest_allowed == 1,
                JobLeadDB.moderation_status == "approved_for_digest",
            ).all()
            fresh.extend(repeats)
        return fresh

    def update(self, lead_id: str, updates: dict) -> JobLeadDB | None:
        lead = self.get_by_lead_id(lead_id)
        if not lead:
            return None
        for key, value in updates.items():
            if hasattr(lead, key):
                setattr(lead, key, value)
        lead.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(lead)
        return lead

    def mark_duplicate(self, lead_id: str, duplicate_of: str) -> JobLeadDB | None:
        return self.update(lead_id, {
            "duplicate_status": "duplicate",
            "duplicate_of": duplicate_of,
            "public_digest_allowed": 0,
        })


class ModerationRepository:
    def __init__(self, db: Session):
        self.db = db

    def log_event(self, entity_type: str, entity_id: str, old_status: str,
                  new_status: str, reason: str = "", operator: str = "") -> ModerationEventDB:
        event = ModerationEventDB(
            entity_type=entity_type,
            entity_id=entity_id,
            old_status=old_status,
            new_status=new_status,
            reason=reason,
            operator=operator,
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def get_history(self, entity_id: str) -> list[ModerationEventDB]:
        return self.db.query(ModerationEventDB).filter(
            ModerationEventDB.entity_id == entity_id
        ).order_by(ModerationEventDB.created_at.desc()).all()
