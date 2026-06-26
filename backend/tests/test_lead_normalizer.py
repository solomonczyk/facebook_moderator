"""Tests for lead normalizer."""

import sys
sys.path.insert(0, '.')

from app.aggregator.lead_normalizer import (
    extract_phones, extract_pay, normalize_phone, normalize_location,
    normalize_lead, compute_missing_info,
)
from app.aggregator.models import JobLead, SourceType, Language


def test_extract_phones():
    text = "Kontakt: 064 123 45 67 i 060/304-1690"
    phones = extract_phones(text)
    assert len(phones) == 2


def test_extract_pay_kg():
    text = "140 RSD/kg + smeštaj"
    assert extract_pay(text) == "140 RSD/kg"


def test_extract_pay_daily():
    text = "dnevnica 5000 din"
    result = extract_pay(text)
    assert result is not None and "5000" in result


def test_normalize_phone():
    assert normalize_phone("0641234567") == "+381641234567"
    assert normalize_phone("+381641234567") == "+381641234567"


def test_normalize_location():
    assert normalize_location("okolina Arilja") == "Arilja"
    assert normalize_location("selo Močioci") == "Močioci"


def test_normalize_lead_basic():
    lead = normalize_lead(
        "Radnici za branje malina, smeštaj i hrana, 064 515 7933",
        source_type=SourceType.FACEBOOK_OPERATOR_SCREENSHOT,
        source_name="Malinari Srbija",
        location="okolina Bajine Bašte",
        job_type="branje malina",
    )
    assert lead.job_type == "branje malina"
    assert lead.location == "Bajine Bašte"
    assert lead.contact_phone is not None
    assert "064" in lead.contact_phone


def test_compute_missing_info():
    lead = JobLead(location="Arilje", job_type="branje malina")
    lead.missing_info = compute_missing_info(lead)
    assert len(lead.missing_info) > 0
    assert "plata / dnevnica" in lead.missing_info


if __name__ == '__main__':
    test_extract_phones()
    test_extract_pay_kg()
    test_extract_pay_daily()
    test_normalize_phone()
    test_normalize_location()
    test_normalize_lead_basic()
    test_compute_missing_info()
    print("[PASS]  All normalizer tests passed")
