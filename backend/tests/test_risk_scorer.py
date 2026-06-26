"""Tests for risk scorer."""

import sys
sys.path.insert(0, '.')

from app.aggregator.risk_scorer import score_risk
from app.aggregator.models import JobLead, RiskLevel, RiskFlag


def test_clean_lead_low_risk():
    lead = JobLead(
        location="Arilje",
        job_type="branje malina",
        contact_phone="064-123-4567",
        pay_amount="5000 RSD dnevno",
    )
    level, flags = score_risk(lead)
    assert level == RiskLevel.LOW
    assert len(flags) == 0


def test_no_contact_flag():
    lead = JobLead(location="Arilje", job_type="branje malina")
    _, flags = score_risk(lead)
    assert RiskFlag.NO_CONTACT in flags
    assert RiskFlag.NO_PAY_INFO in flags


def test_spam_keywords():
    lead = JobLead(raw_text="BRZA ZARADA! Laka zarada, klikni!")
    level, flags = score_risk(lead)
    assert RiskFlag.SPAM_KEYWORDS in flags
    assert level == RiskLevel.REJECT


def test_asks_for_payment():
    lead = JobLead(
        raw_text="Potrebna uplata od 50€ za rezervaciju mesta.",
        location="Arilje",
        contact_phone="064-111-1111",
    )
    _, flags = score_risk(lead)
    assert RiskFlag.ASKS_FOR_PAYMENT in flags


def test_asus_for_documents():
    lead = JobLead(
        raw_text="Pošaljite sliku pasoša i JMBG u inbox.",
    )
    _, flags = score_risk(lead)
    assert RiskFlag.ASKS_FOR_DOCUMENTS in flags


def test_too_good_to_be_true():
    lead = JobLead(
        raw_text="Zaradite 100€ dnevno bez iskustva!",
        location="Beograd",
    )
    _, flags = score_risk(lead)
    assert RiskFlag.TOO_GOOD_TO_BE_TRUE in flags


def test_multiple_flags_high_risk():
    lead = JobLead(raw_text="Brza zarada, pošaljite dokumenta!")
    level, flags = score_risk(lead)
    assert len(flags) >= 3
    assert level in (RiskLevel.HIGH, RiskLevel.REJECT)


if __name__ == '__main__':
    test_clean_lead_low_risk()
    test_no_contact_flag()
    test_spam_keywords()
    test_asks_for_payment()
    test_asus_for_documents()
    test_too_good_to_be_true()
    test_multiple_flags_high_risk()
    print("[PASS]  All risk scorer tests passed")
