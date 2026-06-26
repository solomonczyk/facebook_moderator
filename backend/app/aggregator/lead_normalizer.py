"""Lead normalizer: converts raw input from any source into a normalized JobLead."""

import re
from datetime import datetime
from .models import (
    JobLead, SourceType, CaptureMethod, Language,
    FreshnessStatus, RiskLevel, Classification, DuplicateStatus, ModerationStatus,
)

# Phone patterns: Serbian mobile and landline
PHONE_RE = re.compile(
    r'(?:\+381|0)[\s/-]?\(?\d{1,3}\)?[\s/-]?\d{1,3}[\s/-]?\d{1,4}[\s/-]?\d{1,4}'
)

PAY_AMOUNT_RE = re.compile(r'(\d+[.,]?\d*)\s*(?:RSD|din|dinara|€|EUR|evra?)', re.IGNORECASE)
PAY_PER_KG_RE = re.compile(r'(\d+)\s*(?:RSD|din)\s*/\s*kg', re.IGNORECASE)


def extract_phones(text: str) -> list[str]:
    return PHONE_RE.findall(text)


def extract_pay(text: str) -> str | None:
    match = PAY_PER_KG_RE.search(text) or PAY_AMOUNT_RE.search(text)
    return match.group(0).strip() if match else None


def normalize_phone(phone: str) -> str:
    """Normalize to +381 format."""
    digits = re.sub(r'\D', '', phone)
    if digits.startswith('381'):
        return f'+{digits}'
    if digits.startswith('0'):
        return f'+381{digits[1:]}'
    return phone


def normalize_location(raw: str) -> str:
    """Basic location normalization."""
    raw = raw.strip()
    # Remove common prefixes
    for prefix in ['okolina ', 'kod ', 'selo ', 'grad ']:
        if raw.lower().startswith(prefix):
            raw = raw[len(prefix):]
    return raw.title()


def compute_missing_info(lead: JobLead) -> list[str]:
    """Auto-detect missing fields."""
    missing = []
    checks = [
        ('location', 'lokacija', not lead.location),
        ('pay_amount', 'plata / dnevnica', not lead.pay_amount),
        ('accommodation', 'smeštaj', lead.accommodation is None),
        ('food', 'hrana', lead.food is None),
        ('working_hours', 'radno vreme', not lead.working_hours),
        ('transport', 'prevoz', lead.transport is None),
        ('registered_work', 'prijava radnika', lead.registered_work is None),
        ('contact_phone', 'kontakt telefon', not lead.contact_phone and not lead.contact_inbox_only),
        ('workers_needed', 'broj radnika', lead.workers_needed is None),
        ('start_date', 'početak rada', lead.start_date is None),
        ('payment_frequency', 'način isplate', lead.payment_frequency is None),
    ]
    for _, label, condition in checks:
        if condition:
            missing.append(label)
    return missing


def normalize_lead(
    raw_text: str,
    source_type: SourceType,
    source_name: str,
    language: Language = Language.SR,
    **overrides,
) -> JobLead:
    """Create a normalized JobLead from raw text."""
    phones = extract_phones(raw_text)

    lead = JobLead(
        source_type=source_type,
        source_name=source_name,
        source_captured_at=datetime.utcnow(),
        source_capture_method=CaptureMethod.OPERATOR_COPY_PASTE,
        raw_text=raw_text,
        language=language,
        job_type=overrides.get('job_type', ''),
        location=normalize_location(overrides.get('location', '')),
        workers_needed=overrides.get('workers_needed'),
        pay_amount=overrides.get('pay_amount') or extract_pay(raw_text),
        contact_phone=overrides.get('contact_phone') or (phones[0] if phones else None),
        accommodation=overrides.get('accommodation'),
        food=overrides.get('food'),
        transport=overrides.get('transport'),
        working_hours=overrides.get('working_hours'),
        registered_work=overrides.get('registered_work'),
        employer_name=overrides.get('employer_name'),
    )

    lead.missing_info = compute_missing_info(lead)
    lead.updated_at = datetime.utcnow()
    return lead
