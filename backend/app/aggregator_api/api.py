"""FastAPI router for the Lead Intake API."""

import json
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .database import get_db
from .service import LeadService
from .repositories import LeadRepository

router = APIRouter(prefix="/api/aggregator", tags=["aggregator"])


# ── Schemas ─────────────────────────────────────────────────────────────────

class LeadIntakeRequest(BaseModel):
    source_type: str = "manual_admin_entry"
    source_name: str = ""
    source_group: Optional[str] = None
    source_url: Optional[str] = None
    source_post_url: Optional[str] = None
    raw_text: Optional[str] = None
    raw_image_path: Optional[str] = None
    source_capture_method: str = "operator_copy_paste"
    language: str = "sr"
    job_type: Optional[str] = None
    location: Optional[str] = None
    workers_needed: Optional[int] = None
    pay_amount: Optional[str] = None
    accommodation: Optional[bool] = None
    food: Optional[bool] = None
    transport: Optional[bool] = None
    working_hours: Optional[str] = None
    registered_work: Optional[bool] = None
    employer_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_inbox_only: bool = False
    post_date: Optional[str] = None
    operator_confirmed_active: bool = False


class ModerateRequest(BaseModel):
    action: str
    reason: str = ""
    operator: str = ""


class LeadResponse(BaseModel):
    lead_id: str
    source_type: str
    source_name: str
    job_type: str
    location: str
    contact_phone: Optional[str] = None
    classification: str
    freshness_status: str
    risk_level: str
    duplicate_status: str
    moderation_status: str
    public_digest_allowed: bool
    operator_verified: bool
    missing_info: list = []
    created_at: Optional[str] = None


# ── Endpoints ───────────────────────────────────────────────────────────────

@router.post("/leads/intake", response_model=LeadResponse)
def intake_lead(request: LeadIntakeRequest, db: Session = Depends(get_db)):
    service = LeadService(db)
    result = service.intake(request.model_dump())
    return LeadResponse(**result)


@router.get("/leads", response_model=list[LeadResponse])
def list_leads(
    classification: Optional[str] = Query(None),
    freshness_status: Optional[str] = Query(None),
    risk_level: Optional[str] = Query(None),
    moderation_status: Optional[str] = Query(None),
    public_digest_allowed: Optional[bool] = Query(None),
    source_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    repo = LeadRepository(db)
    filters = {}
    if classification:
        filters["classification"] = classification
    if freshness_status:
        filters["freshness_status"] = freshness_status
    if risk_level:
        filters["risk_level"] = risk_level
    if moderation_status:
        filters["moderation_status"] = moderation_status
    if public_digest_allowed is not None:
        filters["public_digest_allowed"] = 1 if public_digest_allowed else 0
    if source_type:
        filters["source_type"] = source_type
    leads = repo.get_all(**filters)
    return [LeadService._to_dict(lead) for lead in leads]


@router.get("/leads/{lead_id}", response_model=LeadResponse)
def get_lead(lead_id: str, db: Session = Depends(get_db)):
    repo = LeadRepository(db)
    lead = repo.get_by_lead_id(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return LeadService._to_dict(lead)


@router.post("/leads/{lead_id}/moderate")
def moderate_lead(lead_id: str, request: ModerateRequest, db: Session = Depends(get_db)):
    service = LeadService(db)
    result = service.moderate(lead_id, request.action, request.reason, request.operator)
    if result is None:
        raise HTTPException(status_code=400, detail="Invalid moderation action or lead not found")
    return result


@router.get("/digest/candidates")
def get_digest_candidates(db: Session = Depends(get_db)):
    service = LeadService(db)
    candidates = service.get_digest_candidates()
    return {"candidates": candidates, "count": len(candidates)}


@router.post("/export/obsidian")
def export_obsidian(lead_ids: list[str], db: Session = Depends(get_db)):
    from .obsidian_export import export_leads_to_obsidian
    repo = LeadRepository(db)
    leads = []
    for lid in lead_ids:
        lead = repo.get_by_lead_id(lid)
        if lead:
            leads.append(lead)
    result = export_leads_to_obsidian(leads)
    return result


@router.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}
