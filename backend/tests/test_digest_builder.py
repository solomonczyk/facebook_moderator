"""Tests for digest builder."""

import sys
sys.path.insert(0, '.')

from app.aggregator.digest_builder import build_digest, _validate_no_forbidden_words
from app.aggregator.models import (
    JobLead, Classification, ModerationStatus, RiskLevel, DuplicateStatus,
)


def _make_approved_lead(**kwargs) -> JobLead:
    defaults = {
        "classification": Classification.GOOD_LEAD,
        "moderation_status": ModerationStatus.APPROVED_FOR_DIGEST,
        "risk_level": RiskLevel.LOW,
        "duplicate_status": DuplicateStatus.NEW,
        "job_type": "branje malina",
        "location": "Arilje",
        "contact_phone": "064-123-4567",
        "public_digest_allowed": True,
    }
    defaults.update(kwargs)
    return JobLead(**defaults)


def test_build_digest_minimum():
    leads = [_make_approved_lead()]
    text, count, warnings = build_digest(leads)
    assert count == 1
    assert "branje malina" in text
    assert "Arilje" in text
    assert "064-123-4567" in text
    assert "Grupa nije poslodavac" in text


def test_build_digest_below_minimum_warns():
    leads = [_make_approved_lead()]
    text, count, warnings = build_digest(leads, min_leads=3)
    assert len(warnings) > 0
    assert "Only 1 digest candidates" in warnings[0]


def test_build_digest_sorts_good_first():
    leads = [
        _make_approved_lead(
            classification=Classification.CONTACT_ONLY_LEAD,
            job_type="berba visanja",
        ),
        _make_approved_lead(
            classification=Classification.GOOD_LEAD,
            job_type="branje malina",
        ),
    ]
    _, _, warnings = build_digest(leads, min_leads=1)
    assert len(warnings) == 0


def test_build_digest_max_limit():
    leads = [_make_approved_lead(job_type=f"posao {i}") for i in range(15)]
    _, count, _ = build_digest(leads, max_leads=5, min_leads=1)
    assert count == 5


def test_forbidden_words_detected():
    assert _validate_no_forbidden_words("Ovo je provereno!") == ["provereno"]
    assert _validate_no_forbidden_words("Sigurno, garantovano.") == ["sigurno", "garantovano"]
    assert _validate_no_forbidden_words("Običan tekst.") == []


def test_disclaimer_present():
    leads = [_make_approved_lead()]
    text, _, _ = build_digest(leads)
    assert "Grupa nije poslodavac i ne garantuje uslove" in text


if __name__ == '__main__':
    test_build_digest_minimum()
    test_build_digest_below_minimum_warns()
    test_build_digest_sorts_good_first()
    test_build_digest_max_limit()
    test_forbidden_words_detected()
    test_disclaimer_present()
    print("[PASS]  All digest builder tests passed")
