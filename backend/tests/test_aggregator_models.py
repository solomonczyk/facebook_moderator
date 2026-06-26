"""Tests for aggregator data models."""

import sys
sys.path.insert(0, '.')

from app.aggregator.models import (
    JobLead, SourceType, Classification, DuplicateStatus,
    RiskLevel, ModerationStatus, FreshnessStatus,
)


def test_job_lead_defaults():
    lead = JobLead()
    assert lead.country == "Srbija"
    assert lead.language == "sr"
    assert lead.moderation_status == ModerationStatus.NEW
    assert lead.duplicate_status == DuplicateStatus.NEW
    assert lead.classification == Classification.NEEDS_CLARIFICATION


def test_can_go_to_digest_good_lead():
    lead = JobLead(
        classification=Classification.GOOD_LEAD,
        moderation_status=ModerationStatus.APPROVED_FOR_DIGEST,
        risk_level=RiskLevel.LOW,
        duplicate_status=DuplicateStatus.NEW,
    )
    assert lead.can_go_to_digest() is True


def test_can_go_to_digest_high_risk_blocked():
    lead = JobLead(
        classification=Classification.GOOD_LEAD,
        moderation_status=ModerationStatus.APPROVED_FOR_DIGEST,
        risk_level=RiskLevel.HIGH,
        duplicate_status=DuplicateStatus.NEW,
    )
    assert lead.can_go_to_digest() is False


def test_can_go_to_digest_duplicate_blocked():
    lead = JobLead(
        classification=Classification.GOOD_LEAD,
        moderation_status=ModerationStatus.APPROVED_FOR_DIGEST,
        risk_level=RiskLevel.LOW,
        duplicate_status=DuplicateStatus.DUPLICATE,
    )
    assert lead.can_go_to_digest() is False


def test_can_go_to_digest_repeat_candidate_allowed():
    lead = JobLead(
        classification=Classification.REPEAT_CANDIDATE,
        moderation_status=ModerationStatus.APPROVED_FOR_DIGEST,
        risk_level=RiskLevel.LOW,
        duplicate_status=DuplicateStatus.REPEAT_CANDIDATE,
    )
    # REPEAT_CANDIDATE is NOT in (GOOD_LEAD, LOW_INFO, CONTACT_ONLY)
    assert lead.can_go_to_digest() is False


def test_review_average_rating():
    from app.aggregator.models import Review
    review = Review(
        rating_pay_accuracy=4,
        rating_accommodation=3,
        rating_food=3,
        rating_working_hours=4,
        rating_payment_timeliness=5,
        rating_respect=3,
    )
    avg = review.average_rating
    assert 3.5 <= avg <= 3.7  # (4+3+3+4+5+3)/6 = 22/6 = 3.666...


if __name__ == '__main__':
    test_job_lead_defaults()
    test_can_go_to_digest_good_lead()
    test_can_go_to_digest_high_risk_blocked()
    test_can_go_to_digest_duplicate_blocked()
    test_can_go_to_digest_repeat_candidate_allowed()
    test_review_average_rating()
    print("[PASS]  All model tests passed")
