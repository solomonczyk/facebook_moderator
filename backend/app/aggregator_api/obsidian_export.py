"""Obsidian markdown export for leads, workers, and digests."""

import json
from datetime import date


def _bool_emoji(val: bool | None) -> str:
    if val is True:
        return "da"
    if val is False:
        return "ne"
    return "Nepoznato"


def export_lead_to_obsidian(lead) -> str:
    """Export a single lead as Obsidian-compatible markdown with YAML frontmatter."""
    missing = json.loads(lead.missing_info_json) if lead.missing_info_json else []
    missing_str = "\n".join(f"  - {m}" for m in missing) if missing else "none"

    return f"""---
type: vacancy
status: {lead.moderation_status}
source: {lead.source_type}
source_group: {lead.source_group or ''}
source_url: {lead.source_url or ''}
date_added: {lead.created_at.strftime('%Y-%m-%d') if lead.created_at else date.today().isoformat()}
location: {lead.location}
job_type: {lead.job_type}
employer_name: {lead.employer_name or 'Nepoznat'}
contact_public: {lead.contact_phone or 'Nepoznato'}
workers_needed: {lead.workers_needed or 'Nepoznato'}
pay_amount: {lead.pay_amount or 'Nepoznato'}
accommodation: {_bool_emoji(bool(lead.accommodation) if lead.accommodation is not None else None)}
food: {_bool_emoji(bool(lead.food) if lead.food is not None else None)}
transport: {_bool_emoji(bool(lead.transport) if lead.transport is not None else None)}
working_hours: {lead.working_hours or 'Nepoznato'}
registered_work: {_bool_emoji(bool(lead.registered_work) if lead.registered_work is not None else None)}
risk_level: {lead.risk_level}
classification: {lead.classification}
freshness: {lead.freshness_status}
operator_verified: {'true' if lead.operator_verified else 'false'}
posted_to_group: false
missing_info:
{missing_str}
notes: >
  Auto-exported from aggregator. Lead ID: {lead.lead_id}.
  Source: {lead.source_name}.
---

# {lead.job_type} — {lead.location}

Izvor: {lead.source_name}

Kontakt: {lead.contact_phone or 'Nepoznato'}

{'Smeštaj: ' + _bool_emoji(bool(lead.accommodation) if lead.accommodation is not None else None)}
{'Hrana: ' + _bool_emoji(bool(lead.food) if lead.food is not None else None)}
{'Plata: ' + (lead.pay_amount or 'Nepoznato')}

Nedostaje: {', '.join(missing) if missing else 'ništa'}
"""


def export_leads_to_obsidian(leads: list) -> dict:
    """Export multiple leads. Returns a dict of filename -> content."""
    result = {}
    for lead in leads:
        slug = f"{lead.location.lower().replace(' ', '-')}-{lead.job_type.lower().replace(' ', '-')[:20]}"
        filename = f"vacancies/{lead.created_at.strftime('%Y-%m-%d') if lead.created_at else date.today().isoformat()}-{slug}.md"
        result[filename] = export_lead_to_obsidian(lead)
    return {"files": list(result.keys()), "count": len(result)}
