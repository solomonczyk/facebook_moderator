"""Tool layer: wraps existing 004B components for the runtime agent."""

from dataclasses import dataclass
from sqlalchemy.orm import Session

from ..aggregator_api.service import LeadService
from ..aggregator_api.repositories import LeadRepository, ModerationRepository
from ..aggregator_api.obsidian_export import export_lead_to_obsidian


@dataclass
class ToolResult:
    success: bool
    action: str
    entity_id: str | None = None
    details: str = ""


class AgentTools:
    def __init__(self, db: Session):
        self.db = db
        self.lead_service = LeadService(db)
        self.leads = LeadRepository(db)
        self.moderation = ModerationRepository(db)

    def create_job_lead(self, data: dict) -> ToolResult:
        try:
            result = self.lead_service.intake(data)
            return ToolResult(True, "create_job_lead", result.get("lead_id"), "JobLead created")
        except Exception as e:
            return ToolResult(False, "create_job_lead", None, str(e))

    def create_worker_profile(self, data: dict) -> ToolResult:
        return ToolResult(True, "create_worker_profile", None, "Worker profile saved (stub)")

    def create_employer_profile(self, data: dict) -> ToolResult:
        return ToolResult(True, "create_employer_profile", None, "Employer profile saved (stub)")

    def update_lead_status(self, lead_id: str, status: str, reason: str = "") -> ToolResult:
        try:
            result = self.lead_service.moderate(lead_id, status, reason)
            return ToolResult(True, "update_lead_status", lead_id, f"Status -> {status}")
        except Exception as e:
            return ToolResult(False, "update_lead_status", lead_id, str(e))

    def mark_lead_closed(self, lead_id: str) -> ToolResult:
        return self.update_lead_status(lead_id, "mark_closed", "Lead closed by agent")

    def generate_digest(self) -> str:
        candidates = self.leads.get_digest_candidates()
        if not candidates:
            return "Nema dovoljno kandidata za današnji digest."
        from ..aggregator.digest_builder import build_digest
        from ..aggregator.models import JobLead as JL
        leads = []
        for c in candidates[:10]:
            leads.append(JL(
                classification=c.classification,
                moderation_status=c.moderation_status,
                risk_level=c.risk_level,
                duplicate_status=c.duplicate_status,
                job_type=c.job_type,
                location=c.location,
                contact_phone=c.contact_phone,
                pay_amount=c.pay_amount,
                accommodation=bool(c.accommodation) if c.accommodation is not None else None,
                food=bool(c.food) if c.food is not None else None,
                missing_info=[],
            ))
        text, count, warnings = build_digest(leads)
        return text

    def export_obsidian(self, lead_id: str) -> str:
        lead = self.leads.get_by_lead_id(lead_id)
        if not lead:
            return ""
        return export_lead_to_obsidian(lead)
