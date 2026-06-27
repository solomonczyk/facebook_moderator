"""Unified MVP intake endpoint: text → analyze → queue → response.

POST /api/intake/manual

Accepts raw text, runs through LLM-powered brain (with rule-based fallback),
creates action queue item, returns full decision with queue action ID.
"""

import uuid
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger("sezonski.mvp")

router = APIRouter(prefix="/api/intake", tags=["operator-mvp"])


# ── Request / Response Schemas ────────────────────────────────────────────────

class ManualIntakeRequest(BaseModel):
    source: str = "facebook_manual"
    text: str = ""
    author_name: str | None = None
    source_url: str | None = None
    language: str = "unknown"   # sr | ru | uk | en | unknown


class ExtractedFieldsResponse(BaseModel):
    location: str | None = None
    job_type: str | None = None
    crop: str | None = None
    pay: str | None = None
    pay_unit: str | None = None
    accommodation: str | None = None
    food: str | None = None
    working_hours: str | None = None
    start_date: str | None = None
    contact: str | None = None
    employer_name: str | None = None
    red_flags: list[str] = Field(default_factory=list)
    missing_fields: list[str] = Field(default_factory=list)
    confidence: float = 0.0


class ManualIntakeResponse(BaseModel):
    lead_id: str
    status: str                          # "queued" | "error"
    classification: str                  # job_offer | worker_search | worker_experience | employer_warning | question | digest_candidate | spam | unsafe | unknown
    risk_level: str                      # low | medium | high
    action_type: str                     # create_group_post | ask_clarifying_question | create_digest_item | escalate_to_operator | reject_as_spam | request_more_info
    action_id: str | None = None         # queue item ID
    fields: ExtractedFieldsResponse = Field(default_factory=ExtractedFieldsResponse)
    operator_summary: str = ""           # Russian summary for operator
    suggested_text: str = ""             # prepared safe text
    reason: str = ""                     # why this decision
    operator_approval_required: bool = True


# ── Classification mapping ────────────────────────────────────────────────────

_MVP_CLASSIFICATION_MAP = {
    "employer_job_post": "job_offer",
    "worker_request": "worker_search",
    "worker_group_available": "worker_search",
    "review_experience": "worker_experience",
    "question": "question",
    "spam": "spam",
    "suspicious": "unsafe",
    "irrelevant": "unknown",
    "unclear": "unknown",
}

_ACTION_MAP = {
    "approve": "create_group_post",
    "approve_with_edits": "create_group_post",
    "ask_missing_info": "request_more_info",
    "reject": "reject_as_spam",
    "mark_spam": "reject_as_spam",
    "escalate": "escalate_to_operator",
}

# Risk signals that trigger HIGH risk classification
_HIGH_RISK_SIGNALS = [
    "advance payment", "deposit", "JMBG", "passport photo", "ID card",
    "crypto", "casino", "forex", "betting", "unrealistic pay",
    "no contact", "no location", "document request", "inbox only",
    "suspicious intermediary", "too good to be true", "mlm",
    "quick money", "laka zarada", "brza zarada",
]


# ── MVP Pipeline ──────────────────────────────────────────────────────────────

def _classify_risk(text_lower: str, classification: str, fields: dict) -> tuple[str, list[str]]:
    """Determine risk level and collect red flags."""
    red_flags: list[str] = []

    for signal in _HIGH_RISK_SIGNALS:
        if signal.lower() in text_lower:
            red_flags.append(signal)

    # Additional checks (context-dependent)
    if classification in ("job_offer", "employer_job_post", "unknown") and not fields.get("pay"):
        red_flags.append("unclear payment")
    if not fields.get("location"):
        red_flags.append("no location")
    if not fields.get("contact") and classification != "question":
        red_flags.append("suspicious contact")

    # Determine risk level
    high_triggers = {"advance payment", "deposit", "jmbg", "passport photo",
                     "id card", "crypto", "casino", "forex", "betting",
                     "unrealistic pay", "document request", "suspicious intermediary",
                     "too good to be true", "mlm"}
    found_high = [f for f in red_flags if f.lower() in high_triggers]

    if classification in ("spam", "unsafe", "employer_warning") or len(found_high) >= 1:
        return "high", red_flags
    elif len(red_flags) >= 3:
        return "high", red_flags
    elif len(red_flags) >= 1:
        return "medium", red_flags
    else:
        return "low", red_flags


def _compute_missing(fields: dict) -> list[str]:
    """Compute list of missing fields for operator visibility."""
    missing = []
    key_fields = {
        "pay": "plata / dnevnica",
        "location": "lokacija",
        "contact": "kontakt",
        "job_type": "vrsta posla",
        "accommodation": "smeštaj",
        "food": "hrana",
        "working_hours": "radno vreme",
        "start_date": "datum početka",
        "employer_name": "poslodavac",
    }
    for field_key, label in key_fields.items():
        if not fields.get(field_key):
            missing.append(label)
    return missing


def _determine_action(classification: str, risk_level: str, has_contact: bool, has_location: bool) -> str:
    """Determine recommended action based on classification, risk, and completeness."""
    if classification in ("spam",):
        return "reject_as_spam"
    if classification in ("unsafe",):
        return "escalate_to_operator"
    if risk_level == "high":
        return "escalate_to_operator"
    if classification in ("unknown", "unclear"):
        return "escalate_to_operator"
    if not has_contact and not has_location:
        return "request_more_info"
    if classification in ("job_offer", "employer_job_post"):
        if has_contact and has_location:
            return "create_group_post"
        return "request_more_info"
    if classification in ("worker_search", "worker_request", "worker_group_available"):
        return "create_group_post" if has_contact else "request_more_info"
    if classification in ("worker_experience", "review_experience"):
        return "create_group_post"
    if classification == "question":
        return "create_group_post"
    if classification == "digest_candidate":
        return "create_digest_item"
    return "escalate_to_operator"


def _generate_digest_text(fields: dict, missing: list[str]) -> str:
    """Generate a safe digest entry text."""
    job = fields.get("job_type") or fields.get("crop") or "sezonski posao"
    loc = fields.get("location") or "lokacija nije navedena"
    contact = fields.get("contact") or ""

    lines = [f"📌 {job} — {loc}"]
    if contact:
        lines.append(f"Kontakt: {contact}")
    if missing:
        lines.append(f"Nedostaje: {', '.join(missing)}")
    lines.append("")
    lines.append("Napomena: Grupa nije poslodavac i ne garantuje uslove. "
                  "Pre odlaska obavezno proverite platu, smeštaj, hranu, "
                  "radno vreme, prevoz i način isplate direktno sa osobom iz oglasa.")
    return "\n".join(lines)


def _classify_rule_based(text: str) -> tuple[str, dict]:
    """Deterministic rule-based classification as fallback when LLM unavailable."""
    text_lower = text.lower()

    # Employer job offer signals
    employer_signals = ["tražimo", "potrebni", "zapošljavamo", "firma traži",
                        "hitno potrebno", "berba", "treba nam", "gazdinstvo traži"]
    # Worker search signals
    worker_signals = ["tražim posao", "treba mi posao", "dostupan sam",
                      "imam iskustvo", "radio sam", "radila sam", "tražim sezonski"]
    # Worker group signals
    group_signals = ["imam ekipu", "imamo grupu", "nas je", "grupa radnika",
                     "tražimo poslodavca", "sa svojim prevozom"]
    # Spam signals
    spam_signals = ["kazino", "casino", "crypto", "bitcoin", "forex",
                    "brza zarada", "laka zarada", "kladionica", "online kazino",
                    "klikni", "mlm"]
    # Warning/complaint signals
    warning_signals = ["čuvajte se", "ne preporučujem", "ne plaća", "prevarant",
                       "lopov", "ne idite tamo", "upozorenje"]

    # Determine classification — check worker/group before employer to avoid
    # false positives (e.g. "tražim posao" mentioning "berba" should be worker_search)
    if any(s in text_lower for s in spam_signals):
        classification = "spam"
    elif any(s in text_lower for s in warning_signals):
        classification = "employer_warning"
    elif any(s in text_lower for s in worker_signals):
        classification = "worker_search"
    elif any(s in text_lower for s in group_signals):
        classification = "worker_search"
    elif any(s in text_lower for s in employer_signals):
        classification = "job_offer"
    elif "?" in text or "pitanje" in text_lower or "da li" in text_lower:
        classification = "question"
    else:
        classification = "unknown"

    # Extract fields
    fields: dict = {}

    # Location extraction (common Serbian cities/regions)
    locations = ["Arilje", "Ivanjica", "Ivanjice", "Čačak", "Užice", "Subotica", "Subotice", "Novi Sad", "Novog Sada",
                 "Beograd", "Smederevo", "Srem", "Vojvodina", "Šumadija",
                 "Valjevo", "Kraljevo", "Kragujevac", "Leskovac", "Vranje",
                 "Prijepolje", "Bajina Bašta", "Šabac", "Požarevac", "Surčin", "Surčina",
                 "okolina", "selo", "grad", "opština"]
    found_locations = [loc for loc in locations if loc.lower() in text_lower]
    if found_locations:
        fields["location"] = ", ".join(found_locations[:2])

    # Job type
    jobs = ["berba malina", "berba višanja", "berba jabuka", "berba jagoda",
            "berba borovnica", "berba kupina", "berba šljiva", "branje",
            "plastenik", "farma", "hladnjača", "pakovanje", "sortiranje",
            "građevina", "poljoprivreda", "sezonski rad"]
    found_jobs = [j for j in jobs if j.lower() in text_lower]
    if found_jobs:
        fields["job_type"] = found_jobs[0]
        if found_jobs[0].startswith("berba") or found_jobs[0] == "branje":
            fields["crop"] = found_jobs[0]

    # Contact (phone) — flexible patterns for Serbian formats: 06X-XXX-XXXX, 06X/XXX-XXXX, etc.
    import re
    phone_match = re.search(r'0\d{1,2}[\s/-]?\d{2,3}[\s/-]?\d{2,4}[\s/-]?\d{2,4}', text)
    if not phone_match:
        phone_match = re.search(r'0\d{1,2}[\s/-]?\d{2,3}[\s/-]?\d{2,3}', text)
    if phone_match:
        fields["contact"] = phone_match.group(0)

    # Pay
    pay_match = re.search(r'(dnevnica|plata|po kg|po kilogramu|po satu|mesečno)\s*:?\s*(\d+[\s]*[€e]?(ur|rsd|din)?)', text_lower)
    if pay_match:
        fields["pay"] = pay_match.group(0).strip()
    elif re.search(r'\d{3,4}\s*(rsd|din|€|e)', text_lower):
        pay_match2 = re.search(r'\d{3,4}\s*(rsd|din|€|e)', text_lower)
        if pay_match2:
            fields["pay"] = pay_match2.group(0).strip()

    # Accommodation
    if "smeštaj" in text_lower:
        fields["accommodation"] = "da" if "obezbeđen" in text_lower or "ima" in text_lower else "nepoznato"
    # Food
    if "hrana" in text_lower:
        fields["food"] = "da" if "obezbeđen" in text_lower else "nepoznato"

    return classification, fields


async def _process_intake(request: Request, req: ManualIntakeRequest) -> ManualIntakeResponse:
    """Full MVP pipeline: classify → extract → risk → action → queue."""
    lead_id = f"lead_{uuid.uuid4().hex[:12]}"
    text = req.text.strip()
    text_lower = text.lower()

    if not text:
        return ManualIntakeResponse(
            lead_id=lead_id,
            status="error",
            classification="unknown",
            risk_level="low",
            action_type="escalate_to_operator",
            reason="Empty text received.",
        )

    # ── Step 1: Classify (try LLM, fall back to rule-based) ──────────────────
    classification = "unknown"
    fields: dict = {}
    llm_used = False
    llm_decision = None

    try:
        runtime_mgr = getattr(request.app.state, "runtime_manager", None)
        if runtime_mgr is not None and runtime_mgr.llm_available:
            llm_decision = runtime_mgr.analyze({
                "raw_text": text,
                "source_label": req.source,
                "operator_note": f"Language: {req.language}",
            })
            llm_used = True
    except Exception as e:
        logger.warning(f"LLM analysis failed: {e}")

    if llm_decision is not None:
        # Map canonical classification to MVP classification
        classification = _MVP_CLASSIFICATION_MAP.get(llm_decision.classification, "unknown")

        # Extract fields from LLM decision
        fd = llm_decision.fields
        fields = {
            "location": fd.location,
            "job_type": fd.job_type,
            "crop": fd.job_type if fd.job_type and "berba" in fd.job_type.lower() else None,
            "pay": fd.pay,
            "pay_unit": fd.payment_type,
            "accommodation": fd.accommodation,
            "food": fd.food,
            "working_hours": fd.working_hours,
            "start_date": fd.start_date,
            "contact": fd.contact,
            "employer_name": None,
            "confidence": llm_decision.confidence,
        }

        # Compute risk and action from LLM output
        risk_level = llm_decision.risk_level
        red_flags = llm_decision.risk_flags or []
        missing = llm_decision.missing_info or []
        suggested_text = llm_decision.prepared_public_text or ""
        operator_summary = llm_decision.operator_summary or ""
        reason = llm_decision.reason or ""

        raw_action = llm_decision.recommended_action
        action_type = _ACTION_MAP.get(raw_action, "escalate_to_operator")

    else:
        # Rule-based fallback
        classification, fields = _classify_rule_based(text)

        # Compute missing fields
        missing = _compute_missing(fields)

        # Compute risk
        risk_level, red_flags = _classify_risk(text_lower, classification, fields)

        # Compute action
        has_contact = bool(fields.get("contact"))
        has_location = bool(fields.get("location"))
        action_type = _determine_action(classification, risk_level, has_contact, has_location)

        # Generate safe text
        if classification in ("spam", "unsafe"):
            suggested_text = ""
            operator_summary = f"[FALLBACK] {classification.upper()}. Tekst sadrži rizične signale: {', '.join(red_flags[:3])}. Preporuka: NE objavljivati."
            reason = f"Rule-based classification: {classification}. Risk flags: {', '.join(red_flags[:3])}"
        elif classification == "employer_warning":
            suggested_text = f"⚠️ Upozorenje člana grupe: {text[:300]}"
            operator_summary = f"[FALLBACK] Žalba/upozorenje. Potrebna provera operatora."
            reason = "Employer warning — requires operator verification."
            action_type = "escalate_to_operator"
        elif classification == "question":
            suggested_text = text[:500]
            operator_summary = f"[FALLBACK] Pitanje člana grupe o sezonskom radu."
            reason = "General question about seasonal work."
        elif action_type == "create_group_post":
            suggested_text = _generate_digest_text(fields, missing)
            operator_summary = f"[FALLBACK] {classification}. Lokacija: {fields.get('location', '?')}. Kontakt: {fields.get('contact', '?')}. Nedostaje: {', '.join(missing[:3])}"
            reason = f"Rule-based: {classification} with {'contact' if has_contact else 'no contact'}, {'location' if has_location else 'no location'}. Missing: {len(missing)} fields."
        else:
            suggested_text = text[:300] if classification not in ("spam",) else ""
            operator_summary = f"[FALLBACK] {classification}. {len(missing)} nedostajućih polja. Akcija: {action_type}."
            reason = f"Rule-based classification: {classification}. Action: {action_type}."

        fields["confidence"] = 0.45  # fallback confidence

    # ── Step 2: Apply safety overrides ──────────────────────────────────────
    if classification in ("spam",):
        risk_level = "high"
        action_type = "reject_as_spam"
        if "spam" not in red_flags:
            red_flags.append("spam")

    if risk_level == "high" and action_type not in ("escalate_to_operator", "reject_as_spam"):
        action_type = "escalate_to_operator"

    confidence = fields.get("confidence", 0.45)
    if confidence < 0.60 and action_type not in ("escalate_to_operator", "reject_as_spam", "request_more_info"):
        action_type = "escalate_to_operator"
        if "low_confidence" not in red_flags:
            red_flags.append("low_confidence")

    # ── Step 3: Create queue item ──────────────────────────────────────────
    action_id = None
    try:
        runtime_agent = getattr(request.app.state, "runtime_agent", None)
        if runtime_agent is not None:
            from ..runtime_agent.action_queue import QueueItem, ActionType, QueueStatus

            action_map = {
                "create_group_post": ActionType.PUBLISH_OWN_GROUP_POST,
                "ask_clarifying_question": ActionType.ASK_FOR_MISSING_INFO,
                "create_digest_item": ActionType.CREATE_DIGEST_POST,
                "escalate_to_operator": ActionType.REQUEST_OPERATOR_REVIEW,
                "reject_as_spam": ActionType.REQUEST_OPERATOR_REVIEW,
                "request_more_info": ActionType.ASK_FOR_MISSING_INFO,
            }

            queue_action = action_map.get(action_type, ActionType.REQUEST_OPERATOR_REVIEW)

            item = QueueItem(
                action_type=queue_action,
                suggested_text=suggested_text,
                reason=reason,
                operator_approval_required=True,
                lead_id=lead_id,
            )

            if classification in ("spam", "unsafe") and action_type == "reject_as_spam":
                item.mark_spam(reason=reason)

            runtime_agent.queue.add(item)
            runtime_agent.audit.record(
                "mvp_intake",
                f"lead={lead_id} class={classification} risk={risk_level} action={action_type} llm={llm_used}",
                item.item_id,
            )
            action_id = item.item_id
    except Exception as e:
        logger.error(f"Queue item creation failed: {e}")

    # ── Step 4: Return response ────────────────────────────────────────────
    mvp_fields = ExtractedFieldsResponse(
        location=fields.get("location"),
        job_type=fields.get("job_type"),
        crop=fields.get("crop"),
        pay=fields.get("pay"),
        pay_unit=fields.get("pay_unit"),
        accommodation=fields.get("accommodation"),
        food=fields.get("food"),
        working_hours=fields.get("working_hours"),
        start_date=fields.get("start_date"),
        contact=fields.get("contact"),
        employer_name=fields.get("employer_name"),
        red_flags=red_flags,
        missing_fields=missing,
        confidence=confidence,
    )

    return ManualIntakeResponse(
        lead_id=lead_id,
        status="queued",
        classification=classification,
        risk_level=risk_level,
        action_type=action_type,
        action_id=action_id,
        fields=mvp_fields,
        operator_summary=operator_summary,
        suggested_text=suggested_text,
        reason=reason,
        operator_approval_required=True,
    )


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/manual", response_model=ManualIntakeResponse)
async def manual_intake(req: ManualIntakeRequest, request: Request):
    """Unified manual intake: text → classify → extract → queue → response."""
    return await _process_intake(request, req)


@router.get("/status")
async def mvp_status(request: Request):
    """MVP pipeline status."""
    runtime_mgr = getattr(request.app.state, "runtime_manager", None)
    runtime_agent = getattr(request.app.state, "runtime_agent", None)

    return {
        "mvp_version": "1.0.0",
        "llm_available": runtime_mgr.llm_available if runtime_mgr else False,
        "llm_primary": runtime_mgr.llm_available if runtime_mgr else False,
        "fallback_active": not (runtime_mgr.llm_available if runtime_mgr else False),
        "queue_pending": runtime_agent.queue.get_pending_count() if runtime_agent else 0,
        "production_accepted": False,
        "operator_approval_required": True,
    }
