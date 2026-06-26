"""Service layer: orchestrates intake pipeline (normalize -> dedup -> score -> store)."""

import json
import uuid
from datetime import datetime, date

from ..aggregator.lead_normalizer import normalize_lead, compute_missing_info, extract_phones, extract_pay
from ..aggregator.duplicate_detector import is_duplicate
from ..aggregator.freshness_scorer import score_freshness
from ..aggregator.risk_scorer import score_risk
from ..aggregator.digest_builder import build_digest
from ..aggregator.models import (
    SourceType, CaptureMethod, Language, Classification, DuplicateStatus,
    ModerationStatus, FreshnessStatus,
)

from .repositories import LeadRepository, ModerationRepository


VALID_MODERATION_ACTIONS = [
    "approve", "reject", "escalate", "mark_duplicate",
    "mark_repeat_candidate", "mark_closed",
]

ACTION_STATUS_MAP = {
    "approve": "approved_for_digest",
    "reject": "rejected",
    "escalate": "escalated",
    "mark_duplicate": "duplicate",
    "mark_repeat_candidate": "duplicate_from_previous_digest",
    "mark_closed": "closed",
}


class LeadService:
    def __init__(self, db_session):
        self.leads = LeadRepository(db_session)
        self.moderation = ModerationRepository(db_session)
        self.db = db_session

    def intake(self, raw: dict) -> dict:
        """Process a raw lead through the full pipeline."""
        lead_id = f"lead_{uuid.uuid4().hex[:12]}"

        raw_text = raw.get("raw_text", "")
        source_type = raw.get("source_type", "manual_admin_entry")
        source_name = raw.get("source_name", "")
        source_group = raw.get("source_group", "")
        post_date_str = raw.get("post_date")
        operator_confirmed = raw.get("operator_confirmed_active", False)

        # Normalize
        norm = normalize_lead(
            raw_text=raw_text or "",
            source_type=SourceType(source_type) if source_type in [e.value for e in SourceType] else SourceType.MANUAL_ADMIN_ENTRY,
            source_name=source_name,
            language=Language(raw.get("language", "sr")),
            location=raw.get("location", ""),
            job_type=raw.get("job_type", ""),
            workers_needed=raw.get("workers_needed"),
            pay_amount=raw.get("pay_amount") or (extract_pay(raw_text) if raw_text else None),
            contact_phone=raw.get("contact_phone") or (extract_phones(raw_text)[0] if raw_text and extract_phones(raw_text) else None),
            accommodation=raw.get("accommodation"),
            food=raw.get("food"),
            transport=raw.get("transport"),
            working_hours=raw.get("working_hours"),
            registered_work=raw.get("registered_work"),
            employer_name=raw.get("employer_name"),
        )

        # Score freshness
        post_date = None
        if post_date_str:
            try:
                post_date = datetime.strptime(post_date_str, "%Y-%m-%d").date()
            except ValueError:
                pass
        norm.freshness_status = score_freshness(post_date, operator_confirmed_active=operator_confirmed)

        # Score risk
        risk_level, risk_flags = score_risk(norm)
        norm.risk_level = risk_level
        norm.risk_flags = [f.value for f in risk_flags] if risk_flags else []

        # Classification
        if norm.risk_level.value == "reject":
            norm.classification = Classification.REJECT
        elif norm.risk_level.value == "high":
            norm.classification = Classification.SUSPICIOUS
        elif norm.missing_info and len(norm.missing_info) >= 6:
            norm.classification = Classification.LOW_INFO_LEAD
        elif norm.missing_info and len(norm.missing_info) >= 8:
            norm.classification = Classification.CONTACT_ONLY_LEAD
        elif norm.missing_info and len(norm.missing_info) <= 3:
            norm.classification = Classification.GOOD_LEAD

        # Check duplicates against existing leads
        existing = self.leads.get_all()
        existing_objects = []
        for e in existing:
            from ..aggregator.models import JobLead as JL
            jl = JL(
                lead_id=e.lead_id,
                contact_phone=e.contact_phone,
                location=e.location,
                job_type=e.job_type,
                employer_name=e.employer_name,
                raw_text=e.raw_text,
                source_url=e.source_url,
            )
            existing_objects.append(jl)

        dup_status, dup_of = is_duplicate(norm, existing_objects)
        norm.duplicate_status = dup_status

        # Defaults
        norm.moderation_status = ModerationStatus.NEEDS_REVIEW

        # Store
        data = {
            "lead_id": lead_id,
            "source_type": source_type,
            "source_name": source_name,
            "source_group": source_group,
            "source_url": raw.get("source_url"),
            "source_post_url": raw.get("source_post_url"),
            "source_captured_at": datetime.utcnow(),
            "source_capture_method": raw.get("source_capture_method", "operator_copy_paste"),
            "raw_text": raw_text,
            "language": raw.get("language", "sr"),
            "job_type": norm.job_type,
            "location": norm.location,
            "workers_needed": norm.workers_needed,
            "pay_amount": norm.pay_amount,
            "accommodation": norm.accommodation,
            "food": norm.food,
            "transport": norm.transport,
            "working_hours": norm.working_hours,
            "registered_work": norm.registered_work,
            "employer_name": norm.employer_name,
            "contact_phone": norm.contact_phone,
            "contact_inbox_only": norm.contact_inbox_only,
            "missing_info": norm.missing_info,
            "freshness_status": norm.freshness_status.value,
            "risk_level": norm.risk_level.value,
            "risk_flags": norm.risk_flags,
            "classification": norm.classification.value,
            "duplicate_status": norm.duplicate_status.value,
            "duplicate_of": str(dup_of.lead_id) if dup_of else None,
            "moderation_status": "pending_review",
            "public_digest_allowed": False,
            "operator_verified": False,
        }

        stored = self.leads.create(data)
        return self._to_dict(stored)

    def moderate(self, lead_id: str, action: str, reason: str = "", operator: str = "") -> dict | None:
        if action not in VALID_MODERATION_ACTIONS:
            return None
        lead = self.leads.get_by_lead_id(lead_id)
        if not lead:
            return None

        old_status = lead.moderation_status
        new_status = ACTION_STATUS_MAP[action]

        # Prevent rejected -> approved without override
        if old_status == "rejected" and new_status == "approved_for_digest":
            if "override" not in reason.lower():
                return None

        updates = {"moderation_status": new_status}
        if action == "approve":
            updates["public_digest_allowed"] = 1
        elif action == "reject":
            updates["public_digest_allowed"] = 0
        elif action == "mark_duplicate":
            updates["duplicate_status"] = "duplicate"
            updates["public_digest_allowed"] = 0
        elif action == "mark_closed":
            updates["duplicate_status"] = "closed"

        updated = self.leads.update(lead_id, updates)
        self.moderation.log_event("lead", lead_id, old_status, new_status, reason, operator)
        return self._to_dict(updated) if updated else None

    def get_digest_candidates(self) -> list[dict]:
        leads = self.leads.get_digest_candidates()
        return [self._to_dict(lead) for lead in leads]

    @staticmethod
    def _to_dict(db_lead) -> dict:
        return {
            "lead_id": db_lead.lead_id,
            "source_type": db_lead.source_type,
            "source_name": db_lead.source_name,
            "source_group": db_lead.source_group,
            "job_type": db_lead.job_type,
            "location": db_lead.location,
            "contact_phone": db_lead.contact_phone,
            "pay_amount": db_lead.pay_amount,
            "accommodation": bool(db_lead.accommodation) if db_lead.accommodation is not None else None,
            "food": bool(db_lead.food) if db_lead.food is not None else None,
            "classification": db_lead.classification,
            "freshness_status": db_lead.freshness_status,
            "risk_level": db_lead.risk_level,
            "duplicate_status": db_lead.duplicate_status,
            "moderation_status": db_lead.moderation_status,
            "public_digest_allowed": bool(db_lead.public_digest_allowed),
            "operator_verified": bool(db_lead.operator_verified),
            "missing_info": json.loads(db_lead.missing_info_json) if db_lead.missing_info_json else [],
            "created_at": db_lead.created_at.isoformat() if db_lead.created_at else None,
        }
