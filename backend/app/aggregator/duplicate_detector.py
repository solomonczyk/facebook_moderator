"""Duplicate detector: finds duplicate leads by phone, location+job, text similarity."""

from difflib import SequenceMatcher
from .models import JobLead, DuplicateStatus


def _clean_phone(phone: str | None) -> str:
    if not phone:
        return ""
    return ''.join(c for c in phone if c.isdigit())


def _text_similarity(a: str | None, b: str | None) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def is_duplicate(new_lead: JobLead, existing_leads: list[JobLead]) -> tuple[DuplicateStatus, JobLead | None]:
    """
    Check if new_lead is a duplicate of any existing lead.
    Returns (status, matched_lead_or_None).
    """
    new_phone = _clean_phone(new_lead.contact_phone)
    new_loc = (new_lead.location or '').lower()
    new_job = (new_lead.job_type or '').lower()

    for existing in existing_leads:
        # Exact match by source URL
        if new_lead.source_url and new_lead.source_url == existing.source_url:
            return DuplicateStatus.DUPLICATE, existing

        # Exact phone match
        exist_phone = _clean_phone(existing.contact_phone)
        if new_phone and exist_phone and new_phone == exist_phone:
            return DuplicateStatus.DUPLICATE, existing

        # Same phone prefix (last 6 digits) + same location
        if new_phone and exist_phone:
            if new_phone[-6:] == exist_phone[-6:] and new_loc and new_loc == (existing.location or '').lower():
                return DuplicateStatus.POSSIBLE_DUPLICATE, existing

        # Same location + same job type + same employer name
        if new_loc and new_job:
            exist_loc = (existing.location or '').lower()
            exist_job = (existing.job_type or '').lower()
            if new_loc == exist_loc and new_job == exist_job:
                if new_lead.employer_name and existing.employer_name:
                    if new_lead.employer_name.lower() == existing.employer_name.lower():
                        return DuplicateStatus.POSSIBLE_DUPLICATE, existing

        # High text similarity (80%+)
        similarity = _text_similarity(new_lead.raw_text, existing.raw_text)
        if similarity > 0.80 and new_loc == (existing.location or '').lower():
            return DuplicateStatus.POSSIBLE_DUPLICATE, existing

    return DuplicateStatus.NEW, None
