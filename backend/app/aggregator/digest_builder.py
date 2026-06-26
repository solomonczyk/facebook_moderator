"""Digest builder: assembles the daily public digest from approved leads."""

from datetime import date
from .models import JobLead, Classification, FreshnessStatus

DISCLAIMER = (
    "Napomena: Grupa nije poslodavac i ne garantuje uslove. "
    "Oglasi su pronađeni kao javne objave ili su prosleđeni grupi. "
    "Pre odlaska obavezno proverite platu, smeštaj, hranu, radno vreme, "
    "prevoz i način isplate direktno sa osobom iz oglasa."
)

FORBIDDEN_WORDS = ['provereno', 'sigurno', 'garantovano', 'najbolji poslodavac']


def _validate_no_forbidden_words(text: str) -> list[str]:
    found = []
    for word in FORBIDDEN_WORDS:
        if word in text.lower():
            found.append(word)
    return found


def _format_lead_for_digest(lead: JobLead, index: int) -> str:
    lines = [
        f"{index}. {lead.job_type} — {lead.location}",
    ]
    if lead.contact_phone:
        lines.append(f"Kontakt iz javnog oglasa: {lead.contact_phone}")
    if lead.contact_inbox_only:
        lines.append("Kontakt: samo preko Facebook inboxa (nema telefon)")
    if lead.accommodation:
        lines.append(f"Smeštaj: obezbeđen" + (f" ({lead.accommodation_details})" if lead.accommodation_details else ""))
    if lead.food:
        lines.append(f"Hrana: obezbeđena" + (f" ({lead.food_details})" if lead.food_details else ""))
    if lead.pay_amount:
        lines.append(f"Plata: {lead.pay_amount}")
    else:
        lines.append("Dnevnica nije navedena. Proverite direktno kod poslodavca.")
    if lead.missing_info:
        lines.append(f"Nedostaje: {', '.join(lead.missing_info[:5])}")
    lines.append("")
    return "\n".join(lines)


def build_digest(
    leads: list[JobLead],
    digest_date: date | None = None,
    max_leads: int = 10,
    min_leads: int = 3,
) -> tuple[str, int, list[str]]:
    """
    Build a daily digest markdown string from approved leads.
    Returns (digest_text, lead_count, warnings).
    """
    warnings: list[str] = []

    # Filter: only digest-approved leads
    candidates = [
        lead for lead in leads
        if lead.can_go_to_digest()
        and lead.classification
        in (
            Classification.GOOD_LEAD,
            Classification.LOW_INFO_LEAD,
            Classification.CONTACT_ONLY_LEAD,
        )
    ]

    # Sort: good_lead first, then low_info, then contact_only
    sort_order = {
        Classification.GOOD_LEAD: 0,
        Classification.LOW_INFO_LEAD: 1,
        Classification.CONTACT_ONLY_LEAD: 2,
    }
    candidates.sort(key=lambda l: sort_order.get(l.classification, 99))

    # Limit
    selected = candidates[:max_leads]

    if len(selected) < min_leads:
        warnings.append(
            f"Only {len(selected)} digest candidates (minimum {min_leads} required). "
            "Consider adding more leads or using repeat_candidate leads."
        )

    # Check for forbidden words
    for lead in selected:
        if lead.raw_text:
            forbidden = _validate_no_forbidden_words(lead.raw_text)
            if forbidden:
                warnings.append(
                    f"Lead {lead.lead_id}: forbidden words found: {', '.join(forbidden)}"
                )

    # Build digest
    today = digest_date or date.today()
    lines = [
        f"📌 Dnevni pregled javnih oglasa za sezonski posao — {today.strftime('%d.%m.%Y.')}",
        "",
    ]

    for i, lead in enumerate(selected, 1):
        lines.append(_format_lead_for_digest(lead, i))

    lines.append("---")
    lines.append(DISCLAIMER)

    return "\n".join(lines), len(selected), warnings
