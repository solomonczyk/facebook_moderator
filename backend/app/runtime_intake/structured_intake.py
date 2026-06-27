"""Structured intake: employer offer and worker search schemas, validation, queue."""

import uuid
import logging
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger("sezonski.structured_intake")


# ── Schemas ──────────────────────────────────────────────────────────────────

@dataclass
class EmployerOfferIntake:
    # Required
    employer_name: str = ""
    work_location: str = ""
    job_type: str = ""
    workers_needed: str = ""
    start_date: str = ""
    pay_amount: str = ""
    pay_type: str = ""           # dnevnica, po kg, po satu, mesečno
    working_hours_or_norm: str = ""
    housing_provided: str = ""   # da, ne, nepoznato
    food_provided: str = ""      # da, ne, nepoznato
    payment_frequency: str = ""  # dnevno, nedeljno, mesečno
    contact: str = ""

    # Optional
    transport: str = ""
    experience_required: str = ""
    gender_or_age_constraints: str = ""
    additional_info: str = ""
    source_url: str = ""
    source_group: str = ""
    language: str = "sr"

    def required_fields(self) -> list[str]:
        return ["employer_name", "work_location", "job_type", "workers_needed",
                "start_date", "pay_amount", "pay_type", "working_hours_or_norm",
                "housing_provided", "food_provided", "payment_frequency", "contact"]

    def missing_fields(self) -> list[str]:
        missing = []
        for f in self.required_fields():
            if not getattr(self, f, "").strip():
                missing.append(self._field_label(f))
        return missing

    def completeness(self) -> float:
        required = len(self.required_fields())
        missing = len(self.missing_fields())
        return (required - missing) / required if required > 0 else 0.0

    def _field_label(self, field_name: str) -> str:
        labels = {
            "employer_name": "ime poslodavca / firme",
            "work_location": "mesto rada",
            "job_type": "vrsta posla",
            "workers_needed": "broj radnika",
            "start_date": "datum početka",
            "pay_amount": "iznos plate / dnevnice",
            "pay_type": "način plaćanja (dnevnica, po kg, po satu)",
            "working_hours_or_norm": "radno vreme ili norma",
            "housing_provided": "smeštaj (da/ne)",
            "food_provided": "hrana (da/ne)",
            "payment_frequency": "isplata (dnevno/nedeljno/mesečno)",
            "contact": "kontakt telefon",
        }
        return labels.get(field_name, field_name)


@dataclass
class WorkerSearchIntake:
    # Required
    worker_name: str = ""
    current_location: str = ""
    people_count: str = ""
    desired_job_type: str = ""
    available_from: str = ""
    housing_needed: str = ""     # da, ne
    food_needed: str = ""         # da, ne
    contact: str = ""

    # Optional
    experience: str = ""
    languages: str = ""
    has_transport: str = ""
    preferred_location: str = ""
    additional_info: str = ""
    source_url: str = ""
    source_group: str = ""
    language: str = "sr"

    def required_fields(self) -> list[str]:
        return ["worker_name", "current_location", "people_count",
                "desired_job_type", "available_from", "housing_needed",
                "food_needed", "contact"]

    def missing_fields(self) -> list[str]:
        missing = []
        for f in self.required_fields():
            if not getattr(self, f, "").strip():
                missing.append(self._field_label(f))
        return missing

    def completeness(self) -> float:
        required = len(self.required_fields())
        missing = len(self.missing_fields())
        return (required - missing) / required if required > 0 else 0.0

    def _field_label(self, field_name: str) -> str:
        labels = {
            "worker_name": "ime radnika",
            "current_location": "trenutna lokacija",
            "people_count": "broj ljudi",
            "desired_job_type": "željena vrsta posla",
            "available_from": "dostupan od",
            "housing_needed": "smeštaj potreban (da/ne)",
            "food_needed": "hrana potrebna (da/ne)",
            "contact": "kontakt telefon",
        }
        return labels.get(field_name, field_name)


# ── Risk / Spam detection ────────────────────────────────────────────────────

SPAM_SIGNALS = [
    "kazino", "casino", "crypto", "bitcoin", "forex", "kladionica",
    "brza zarada", "laka zarada", "mlm", "online kazino",
]

HIGH_RISK_SIGNALS = [
    "pasoš", "jmbg", "lična karta", "dokumenta unapred",
    "uplata unapred", "depozit", "inostranstvo",
]


def detect_spam(text: str) -> bool:
    t = text.lower()
    return any(s in t for s in SPAM_SIGNALS)


def detect_high_risk(text: str) -> bool:
    t = text.lower()
    return any(s in t for s in HIGH_RISK_SIGNALS)


# ── Intake Processor ─────────────────────────────────────────────────────────

def process_employer_offer(offer: EmployerOfferIntake) -> dict:
    """Process structured employer offer → queue item dict."""
    lead_id = f"lead_{uuid.uuid4().hex[:12]}"
    item_id = f"q_{uuid.uuid4().hex[:12]}"
    now = datetime.utcnow().isoformat()

    combined_text = (
        f"{offer.employer_name} traži {offer.workers_needed} radnika "
        f"za {offer.job_type}, {offer.work_location}. "
        f"Plata: {offer.pay_amount} {offer.pay_type}. "
        f"Smeštaj: {offer.housing_provided}. Hrana: {offer.food_provided}. "
        f"Kontakt: {offer.contact}."
    )

    missing = offer.missing_fields()
    completeness = offer.completeness()
    is_spam = detect_spam(combined_text)
    is_high_risk = detect_high_risk(combined_text)

    # Determine status
    if is_spam:
        status = "spam_candidate"
        action_type = "request_operator_review"
    elif is_high_risk:
        status = "risk_review"
        action_type = "request_operator_review"
    elif completeness >= 1.0:
        status = "pending"
        action_type = "publish_own_group_post"
    else:
        status = "needs_info"
        action_type = "ask_for_missing_info"

    # Build Serbian messages
    if missing:
        missing_list = "\n".join(f"- {m}" for m in missing)
        reply_to_author = (
            f"Hvala na informacijama. Da bismo objavu pripremili, "
            f"molimo vas da dopunite:\n{missing_list}"
        )
    else:
        reply_to_author = ""

    # Build draft for manual FB publish
    if status == "pending" and action_type == "publish_own_group_post":
        fb_draft = _build_employer_facebook_draft(offer)
    else:
        fb_draft = ""

    # Russian operator summary
    op_summary = (
        f"Работодатель: {offer.employer_name}. "
        f"Локация: {offer.work_location}. "
        f"Работа: {offer.job_type}. "
        f"Оплата: {offer.pay_amount} {offer.pay_type}. "
        f"Полнота: {completeness:.0%}. "
        f"Пропущено: {len(missing)} полей."
    )

    return {
        "lead_id": lead_id,
        "item_id": item_id,
        "intake_type": "employer_offer",
        "action_type": action_type,
        "status": status,
        "suggested_text": fb_draft,
        "reason": f"Structured employer intake. Completeness: {completeness:.0%}.",
        "operator_approval_required": True,
        "classification": "job_offer",
        "risk_level": "high" if is_high_risk else ("medium" if missing else "low"),
        "confidence": completeness,
        "source": "structured_intake_api",
        "missing_info": missing,
        "risk_flags": (["spam_signal"] if is_spam else []) + (["high_risk_signal"] if is_high_risk else []),
        "operator_summary": op_summary,
        "prepared_reply_to_author": reply_to_author,
        "raw_json": {
            "employer_name": offer.employer_name,
            "work_location": offer.work_location,
            "job_type": offer.job_type,
            "pay_amount": offer.pay_amount,
            "pay_type": offer.pay_type,
            "housing_provided": offer.housing_provided,
            "food_provided": offer.food_provided,
            "contact": offer.contact,
        },
        "created_at": now,
    }


def process_worker_search(worker: WorkerSearchIntake) -> dict:
    """Process structured worker search → queue item dict."""
    lead_id = f"lead_{uuid.uuid4().hex[:12]}"
    item_id = f"q_{uuid.uuid4().hex[:12]}"
    now = datetime.utcnow().isoformat()

    combined_text = (
        f"{worker.worker_name} traži posao: {worker.desired_job_type}. "
        f"Ljudi: {worker.people_count}. Lokacija: {worker.current_location}. "
        f"Dostupan od: {worker.available_from}. "
        f"Smeštaj potreban: {worker.housing_needed}. "
        f"Kontakt: {worker.contact}."
    )

    missing = worker.missing_fields()
    completeness = worker.completeness()
    is_spam = detect_spam(combined_text)
    is_high_risk = detect_high_risk(combined_text)

    if is_spam:
        status = "spam_candidate"
        action_type = "request_operator_review"
    elif is_high_risk:
        status = "risk_review"
        action_type = "request_operator_review"
    elif completeness >= 1.0:
        status = "pending"
        action_type = "publish_own_group_post"
    else:
        status = "needs_info"
        action_type = "ask_for_missing_info"

    if missing:
        missing_list = "\n".join(f"- {m}" for m in missing)
        reply_to_author = (
            f"Hvala. Da bismo objavu pripremili, molimo vas da dopunite:\n{missing_list}"
        )
    else:
        reply_to_author = ""

    if status == "pending" and action_type == "publish_own_group_post":
        fb_draft = _build_worker_facebook_draft(worker)
    else:
        fb_draft = ""

    op_summary = (
        f"Работник: {worker.worker_name}. "
        f"Ищет: {worker.desired_job_type}. "
        f"Людей: {worker.people_count}. "
        f"Локация: {worker.current_location}. "
        f"Полнота: {completeness:.0%}."
    )

    return {
        "lead_id": lead_id,
        "item_id": item_id,
        "intake_type": "worker_search",
        "action_type": action_type,
        "status": status,
        "suggested_text": fb_draft,
        "reason": f"Structured worker intake. Completeness: {completeness:.0%}.",
        "operator_approval_required": True,
        "classification": "worker_search",
        "risk_level": "high" if is_high_risk else ("medium" if missing else "low"),
        "confidence": completeness,
        "source": "structured_intake_api",
        "missing_info": missing,
        "risk_flags": (["spam_signal"] if is_spam else []) + (["high_risk_signal"] if is_high_risk else []),
        "operator_summary": op_summary,
        "prepared_reply_to_author": reply_to_author,
        "raw_json": {
            "worker_name": worker.worker_name,
            "current_location": worker.current_location,
            "people_count": worker.people_count,
            "desired_job_type": worker.desired_job_type,
            "contact": worker.contact,
        },
        "created_at": now,
    }


# ── Facebook Draft Builders ──────────────────────────────────────────────────

def _build_employer_facebook_draft(offer: EmployerOfferIntake) -> str:
    lines = [
        f"🔹 Poslodavac: {offer.employer_name}",
        f"📍 Mesto rada: {offer.work_location}",
        f"💼 Vrsta posla: {offer.job_type}",
        f"👥 Broj radnika: {offer.workers_needed}",
        f"📅 Početak: {offer.start_date}",
        f"💰 Plata: {offer.pay_amount} {offer.pay_type} ({offer.payment_frequency})",
        f"🕐 Radno vreme: {offer.working_hours_or_norm}",
        f"🏠 Smeštaj: {offer.housing_provided}",
        f"🍽️ Hrana: {offer.food_provided}",
    ]
    if offer.transport:
        lines.append(f"🚗 Prevoz: {offer.transport}")
    if offer.contact:
        lines.append(f"📞 Kontakt: {offer.contact}")
    if offer.additional_info:
        lines.append(f"📝 {offer.additional_info}")

    lines.append("")
    lines.append("Napomena: Grupa nije poslodavac i ne garantuje uslove. "
                  "Pre odlaska obavezno proverite platu, smeštaj, hranu, "
                  "radno vreme, prevoz i način isplate direktno sa osobom iz oglasa.")

    return "\n".join(lines)


def _build_worker_facebook_draft(worker: WorkerSearchIntake) -> str:
    lines = [
        f"👷 Traži posao: {worker.worker_name}",
        f"📍 Lokacija: {worker.current_location}",
        f"👥 Broj ljudi: {worker.people_count}",
        f"💼 Željeni posao: {worker.desired_job_type}",
        f"📅 Dostupan od: {worker.available_from}",
        f"🏠 Smeštaj potreban: {worker.housing_needed}",
        f"🍽️ Hrana potrebna: {worker.food_needed}",
    ]
    if worker.experience:
        lines.append(f"⭐ Iskustvo: {worker.experience}")
    if worker.has_transport:
        lines.append(f"🚗 Prevoz: {worker.has_transport}")
    if worker.contact:
        lines.append(f"📞 Kontakt: {worker.contact}")

    lines.append("")
    lines.append("Napomena: Grupa ne garantuje poslodavce. "
                  "Proverite uslove direktno.")

    return "\n".join(lines)
