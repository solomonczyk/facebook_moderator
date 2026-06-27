"""Google Forms → Structured Intake Bridge.

Secure endpoints: POST /api/intake/google-forms/employer-offer
                  POST /api/intake/google-forms/worker-search

Requires GOOGLE_FORMS_INTAKE_TOKEN from env.
Maps Google Form field labels to existing structured intake.
Idempotency via external_submission_id.
"""

import os
import hashlib
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

logger = logging.getLogger("sezonski.google_forms_bridge")

router = APIRouter(prefix="/api/intake/google-forms", tags=["google-forms-bridge"])

# Dedup store — simple in-memory + persistent fallback
_seen_submissions: set[str] = set()


# ── Security ─────────────────────────────────────────────────────────────────

def _get_token() -> str:
    return os.getenv("GOOGLE_FORMS_INTAKE_TOKEN", "").strip()


def _verify_token(request: Request) -> None:
    token = _get_token()
    if not token:
        raise HTTPException(status_code=503, detail="Bridge not configured")

    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        auth = auth[7:]
    elif auth.startswith("Token "):
        auth = auth[6:]

    if not auth or auth != token:
        logger.warning(f"Invalid bridge token attempt from {request.client}")
        raise HTTPException(status_code=401, detail="Invalid token")


# ── Idempotency ─────────────────────────────────────────────────────────────

def _submission_id(form_type: str, row_data: dict) -> str:
    """Deterministic submission ID from form type, timestamp, row number, phone."""
    ts = row_data.get("Timestamp", row_data.get("timestamp", ""))
    row = row_data.get("Row", row_data.get("row", ""))
    phone = row_data.get("Kontakt telefon", row_data.get("contact", ""))
    raw = f"{form_type}|{ts}|{row}|{phone}"
    return hashlib.sha256(raw.encode()).hexdigest()[:24]


def _is_duplicate(submission_id: str) -> bool:
    """Check in-memory + persistent store for duplicates."""
    if submission_id in _seen_submissions:
        return True

    # Check persistent queue for same submission
    try:
        from ..runtime_agent.persistent_queue import get_persistent_queue
        pq = get_persistent_queue()
        all_items = pq.get_all()
        for item in all_items:
            raw = item.get("raw_json", {}) or {}
            if raw.get("external_submission_id") == submission_id:
                _seen_submissions.add(submission_id)
                return True
    except Exception:
        pass

    return False


def _mark_seen(submission_id: str) -> None:
    _seen_submissions.add(submission_id)
    if len(_seen_submissions) > 1000:
        # Keep last 500
        items = list(_seen_submissions)
        _seen_submissions.clear()
        _seen_submissions.update(items[-500:])


# ── Request Schema ──────────────────────────────────────────────────────────

class GoogleFormsPayload(BaseModel):
    """Flexible payload — accepts all Google Form fields as a flat dict."""
    Timestamp: str = ""
    Row: str = ""
    # Employer fields
    employer_name: str = ""
    work_location: str = ""
    job_type: str = ""
    workers_needed: str = ""
    start_date: str = ""
    pay_amount: str = ""
    pay_type: str = ""
    working_hours_or_norm: str = ""
    housing_provided: str = ""
    food_provided: str = ""
    payment_frequency: str = ""
    contact: str = ""
    # Worker fields
    worker_name: str = ""
    current_location: str = ""
    people_count: str = ""
    desired_job_type: str = ""
    available_from: str = ""
    housing_needed: str = ""
    food_needed: str = ""
    experience: str = ""
    languages: str = ""
    has_transport: str = ""
    preferred_location: str = ""
    additional_info: str = ""
    # Consent fields
    publication_consent: str = ""  # "Da" or "Ne"
    phone_consent: str = ""         # "Da" or "Ne"
    # Catch-all for unmapped fields
    extra_fields: dict = {}

    class Config:
        extra = "allow"


# ── Response Schema ──────────────────────────────────────────────────────────

class BridgeResponse(BaseModel):
    success: bool = True
    lead_id: str = ""
    item_id: str = ""
    status: str = ""
    action_type: str = ""
    classification: str = ""
    risk_level: str = ""
    duplicate: bool = False
    consent_blocked: bool = False
    missing_fields: list[str] = []
    message: str = ""


# ── Employer Mapping ─────────────────────────────────────────────────────────

EMPLOYER_FIELD_MAP = {
    # Google Form label → EmployerOfferIntake field
    "Ime / naziv poslodavca": "employer_name",
    "Mesto rada / lokacija": "work_location",
    "Vrsta posla": "job_type",
    "Broj radnika": "workers_needed",
    "Kada / datum početka": "start_date",
    "Datum početka": "start_date",
    "Plata / dnevnica / cena po kg": "pay_type",
    "Radno vreme ili norma": "working_hours_or_norm",
    "Smeštaj": "housing_provided",
    "Hrana": "food_provided",
    "Učestalost isplate": "payment_frequency",
    "Kontakt telefon": "contact",
    "Dodatne informacije": "additional_info",
    # Amount is often in pay_type field combined, or separate
    "Iznos plate / dnevnice": "pay_amount",
    "Iznos / dnevnica": "pay_amount",
}

WORKER_FIELD_MAP = {
    "Ime / nadimak": "worker_name",
    "Mesto gde se nalazite": "current_location",
    "Koji posao tražite": "desired_job_type",
    "Koliko osoba traži posao": "people_count",
    "Kada možete početi": "available_from",
    "Iskustvo": "experience",
    "Da li vam treba smeštaj": "housing_needed",
    "Da li vam treba hrana": "food_needed",
    "Kontakt telefon": "contact",
    "Jezici koje govorite": "languages",
    "Da li imate prevoz": "has_transport",
    "Dodatne informacije": "additional_info",
}


def _map_fields(raw: dict, field_map: dict) -> dict:
    """Map Google Form field labels to internal field names."""
    mapped = {}
    # First: try direct field names from the Pydantic model
    for key in ["employer_name", "work_location", "job_type", "workers_needed",
                "start_date", "pay_amount", "pay_type", "working_hours_or_norm",
                "housing_provided", "food_provided", "payment_frequency", "contact",
                "worker_name", "current_location", "people_count", "desired_job_type",
                "available_from", "housing_needed", "food_needed", "experience",
                "languages", "has_transport", "preferred_location", "additional_info"]:
        val = raw.get(key, "")
        if val:
            mapped[key] = str(val).strip()

    # Second: map Google Form labels to internal fields
    for form_label, internal_name in field_map.items():
        val = raw.get(form_label, "")
        if val and internal_name not in mapped:
            mapped[internal_name] = str(val).strip()

    # Extract amount from pay_type if it contains numbers
    if "pay_type" in mapped and "pay_amount" not in mapped:
        import re
        pt = mapped.get("pay_type", "")
        match = re.search(r'(\d[\d\s]*)\s*(rsd|din|€|e|eur)?', pt.lower())
        if match:
            mapped["pay_amount"] = match.group(1).strip()
            # Clean pay_type
            mapped["pay_type"] = re.sub(r'\d[\d\s]*\s*(rsd|din|€|e|eur)?', '', pt, flags=re.IGNORECASE).strip()

    # Normalize da/ne fields
    for f in ["housing_provided", "food_provided", "housing_needed", "food_needed"]:
        v = mapped.get(f, "").lower()
        if v in ("da", "yes", "има", "да"):
            mapped[f] = "da"
        elif v in ("ne", "no", "нема", "нет"):
            mapped[f] = "ne"

    return mapped


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/employer-offer", response_model=BridgeResponse)
async def google_forms_employer(payload: GoogleFormsPayload, request: Request):
    _verify_token(request)

    raw = payload.model_dump()
    # Extract all extra fields
    if payload.extra_fields:
        raw.update(payload.extra_fields)

    # Idempotency
    sub_id = _submission_id("employer", raw)
    if _is_duplicate(sub_id):
        return BridgeResponse(
            success=True, duplicate=True,
            message="Submission already processed",
        )

    # Map fields
    mapped = _map_fields(raw, EMPLOYER_FIELD_MAP)

    # Consent check
    pub_consent = raw.get("publication_consent", raw.get("Da li dozvoljavate objavu", ""))
    phone_consent_val = raw.get("phone_consent", raw.get("Da li dozvoljavate objavu kontakt telefona", ""))

    from .structured_intake import EmployerOfferIntake, process_employer_offer

    offer = EmployerOfferIntake(
        employer_name=mapped.get("employer_name", ""),
        work_location=mapped.get("work_location", ""),
        job_type=mapped.get("job_type", ""),
        workers_needed=mapped.get("workers_needed", ""),
        start_date=mapped.get("start_date", ""),
        pay_amount=mapped.get("pay_amount", ""),
        pay_type=mapped.get("pay_type", ""),
        working_hours_or_norm=mapped.get("working_hours_or_norm", ""),
        housing_provided=mapped.get("housing_provided", ""),
        food_provided=mapped.get("food_provided", ""),
        payment_frequency=mapped.get("payment_frequency", ""),
        contact=mapped.get("contact", ""),
        additional_info=mapped.get("additional_info", ""),
    )

    result = process_employer_offer(offer)

    # Consent overrides
    if pub_consent and pub_consent.lower() in ("ne", "no", "нет"):
        result["status"] = "risk_review"
        result["action_type"] = "request_operator_review"
        result["reason"] += " | Consent: publication=Ne"
    if phone_consent_val and phone_consent_val.lower() in ("ne", "no", "нет"):
        # Remove phone from publishable text
        result["suggested_text"] = result.get("suggested_text", "").replace(
            f"📞 Kontakt: {offer.contact}", "📞 Kontakt: (nije za objavu)"
        )

    # Tag with submission ID for dedup
    result["raw_json"]["external_submission_id"] = sub_id
    result["raw_json"]["source_form"] = "google_forms_employer"

    _add_to_queue_and_notify(request, result)
    _mark_seen(sub_id)

    return BridgeResponse(
        lead_id=result["lead_id"],
        item_id=result["item_id"],
        status=result["status"],
        action_type=result["action_type"],
        classification=result["classification"],
        risk_level=result["risk_level"],
        missing_fields=result["missing_info"],
        consent_blocked=(pub_consent and pub_consent.lower() in ("ne", "no", "нет")),
        message="Employer offer received",
    )


@router.post("/worker-search", response_model=BridgeResponse)
async def google_forms_worker(payload: GoogleFormsPayload, request: Request):
    _verify_token(request)

    raw = payload.model_dump()
    if payload.extra_fields:
        raw.update(payload.extra_fields)

    sub_id = _submission_id("worker", raw)
    if _is_duplicate(sub_id):
        return BridgeResponse(
            success=True, duplicate=True,
            message="Submission already processed",
        )

    mapped = _map_fields(raw, WORKER_FIELD_MAP)

    pub_consent = raw.get("publication_consent", raw.get("Da li dozvoljavate objavu", ""))
    phone_consent_val = raw.get("phone_consent", raw.get("Da li dozvoljavate objavu kontakt telefona", ""))

    from .structured_intake import WorkerSearchIntake, process_worker_search

    worker = WorkerSearchIntake(
        worker_name=mapped.get("worker_name", ""),
        current_location=mapped.get("current_location", ""),
        people_count=mapped.get("people_count", ""),
        desired_job_type=mapped.get("desired_job_type", ""),
        available_from=mapped.get("available_from", ""),
        housing_needed=mapped.get("housing_needed", ""),
        food_needed=mapped.get("food_needed", ""),
        contact=mapped.get("contact", ""),
        experience=mapped.get("experience", ""),
        languages=mapped.get("languages", ""),
        has_transport=mapped.get("has_transport", ""),
        additional_info=mapped.get("additional_info", ""),
    )

    result = process_worker_search(worker)

    if pub_consent and pub_consent.lower() in ("ne", "no", "нет"):
        result["status"] = "risk_review"
        result["action_type"] = "request_operator_review"
        result["reason"] += " | Consent: publication=Ne"
    if phone_consent_val and phone_consent_val.lower() in ("ne", "no", "нет"):
        result["suggested_text"] = result.get("suggested_text", "").replace(
            f"📞 Kontakt: {worker.contact}", "📞 Kontakt: (nije za objavu)"
        )

    result["raw_json"]["external_submission_id"] = sub_id
    result["raw_json"]["source_form"] = "google_forms_worker"

    _add_to_queue_and_notify(request, result)
    _mark_seen(sub_id)

    return BridgeResponse(
        lead_id=result["lead_id"],
        item_id=result["item_id"],
        status=result["status"],
        action_type=result["action_type"],
        classification=result["classification"],
        risk_level=result["risk_level"],
        missing_fields=result["missing_info"],
        consent_blocked=(pub_consent and pub_consent.lower() in ("ne", "no", "нет")),
        message="Worker search received",
    )


@router.get("/health")
async def bridge_health(request: Request):
    """Health check — does NOT require token."""
    token_configured = bool(_get_token())
    return {
        "bridge": "google-forms",
        "token_configured": token_configured,
        "endpoints": ["/api/intake/google-forms/employer-offer",
                      "/api/intake/google-forms/worker-search"],
    }


# ── Helpers ──────────────────────────────────────────────────────────────────

def _add_to_queue_and_notify(request: Request, result: dict):
    """Add to runtime queue + persist + Telegram notify."""
    try:
        agent = getattr(request.app.state, "runtime_agent", None)
        if agent:
            from ..runtime_agent.action_queue import QueueItem, ActionType
            atype_map = {
                "publish_own_group_post": ActionType.PUBLISH_OWN_GROUP_POST,
                "ask_for_missing_info": ActionType.ASK_FOR_MISSING_INFO,
                "request_operator_review": ActionType.REQUEST_OPERATOR_REVIEW,
            }
            item = QueueItem(
                item_id=result["item_id"],
                action_type=atype_map.get(result["action_type"], ActionType.REQUEST_OPERATOR_REVIEW),
                suggested_text=result.get("suggested_text", ""),
                reason=result.get("reason", ""),
                operator_approval_required=True,
            )
            agent.queue.add(item)
    except Exception as e:
        logger.warning(f"Runtime queue add failed: {e}")

    # Telegram notification
    try:
        from ..telegram_bot.notifier import send_notification
        send_notification(result)
    except Exception as e:
        logger.warning(f"Telegram notify failed: {e}")
