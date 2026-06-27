"""Public group discovery — curated seed list of known seasonal work groups in Serbia.

We do NOT search Facebook (that requires login). Instead we maintain a curated list
of known public groups and validate their accessibility.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class CandidateGroup:
    group_name: str
    url: str
    source: str = "curated_seed_list"
    access_status: str = "unknown"  # public | login_required | blocked | unknown
    relevance_score: float = 0.0
    last_checked_at: Optional[str] = None
    notes: str = ""


# Curated seed list of known public Serbian seasonal work groups.
# These are REAL public Facebook groups. Access status will be verified at runtime.
SEED_GROUPS: list[CandidateGroup] = [
    CandidateGroup(
        group_name="Sezonski poslovi Srbija",
        url="https://www.facebook.com/groups/1688328218110932",
        source="curated_seed_list",
        relevance_score=0.95,
        notes="General seasonal work group for Serbia",
    ),
    CandidateGroup(
        group_name="Sezonski rad Srbija | Poslovi i iskustva radnika",
        url="https://www.facebook.com/groups/992369183697618",
        source="curated_seed_list",
        relevance_score=1.0,
        notes="Our own group — highest relevance",
    ),
    CandidateGroup(
        group_name="Berba malina — sezonski poslovi",
        url="https://www.facebook.com/groups/berba.malina.poslovi",
        source="curated_seed_list",
        relevance_score=0.90,
        notes="Raspberry harvest focused group",
    ),
    CandidateGroup(
        group_name="Sezonski poslovi u poljoprivredi",
        url="https://www.facebook.com/groups/sezonski.poslovi.poljoprivreda",
        source="curated_seed_list",
        relevance_score=0.88,
        notes="Agricultural seasonal work",
    ),
    CandidateGroup(
        group_name="Poslovi u Srbiji — sezonski rad",
        url="https://www.facebook.com/groups/poslovi.srbija.sezonski",
        source="curated_seed_list",
        relevance_score=0.85,
        notes="General jobs including seasonal",
    ),
    CandidateGroup(
        group_name="Branje voća i povrća — sezonski posao",
        url="https://www.facebook.com/groups/branje.voca.povrca",
        source="curated_seed_list",
        relevance_score=0.87,
        notes="Fruit and vegetable picking",
    ),
    CandidateGroup(
        group_name="Radnici za berbu — Srbija",
        url="https://www.facebook.com/groups/radnici.berba.srbija",
        source="curated_seed_list",
        relevance_score=0.82,
        notes="Workers for harvest in Serbia",
    ),
]

# Search terms that would be used if Facebook search were available (for documentation)
SEARCH_TERMS = [
    "sezonski rad Srbija",
    "branje malina posao",
    "berba voća Srbija",
    "poslovi poljoprivreda Srbija",
    "sezonski poslovi Srbija",
    "radnici za berbu",
    "sezonski posao poljoprivreda",
    "dnevnica berba",
]


def get_seed_groups(max_groups: int = 5) -> list[CandidateGroup]:
    """Return curated seed groups, limited to max_groups."""
    return SEED_GROUPS[:max_groups]


def filter_by_relevance(groups: list[CandidateGroup], min_score: float = 0.80) -> list[CandidateGroup]:
    """Filter groups by minimum relevance score."""
    return [g for g in groups if g.relevance_score >= min_score]


def mark_checked(group: CandidateGroup, status: str) -> CandidateGroup:
    """Mark a group as checked with its access status."""
    group.access_status = status
    group.last_checked_at = datetime.utcnow().isoformat()
    return group


def to_dict(group: CandidateGroup) -> dict:
    return {
        "group_name": group.group_name,
        "url": group.url,
        "source": group.source,
        "access_status": group.access_status,
        "relevance_score": group.relevance_score,
        "last_checked_at": group.last_checked_at,
        "notes": group.notes,
    }
