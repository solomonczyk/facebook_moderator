"""Tests for duplicate detector."""

import sys
sys.path.insert(0, '.')

from app.aggregator.duplicate_detector import is_duplicate
from app.aggregator.models import JobLead, DuplicateStatus


def test_same_phone_is_duplicate():
    lead1 = JobLead(contact_phone="064-988-5113", location="Arilje", job_type="branje malina")
    lead2 = JobLead(contact_phone="0649885113", location="Arilje", job_type="branje malina")
    status, matched = is_duplicate(lead2, [lead1])
    assert status == DuplicateStatus.DUPLICATE


def test_different_phone_is_new():
    lead1 = JobLead(contact_phone="064-111-1111", location="Arilje")
    lead2 = JobLead(contact_phone="064-222-2222", location="Beograd")
    status, _ = is_duplicate(lead2, [lead1])
    assert status == DuplicateStatus.NEW


def test_same_url_is_duplicate():
    lead1 = JobLead(source_url="https://021.rs/oglasi/123")
    lead2 = JobLead(source_url="https://021.rs/oglasi/123")
    status, _ = is_duplicate(lead2, [lead1])
    assert status == DuplicateStatus.DUPLICATE


def test_same_location_job_employer_is_possible_duplicate():
    lead1 = JobLead(
        location="Arilje", job_type="branje malina",
        employer_name="Voćarstvo Jović",
    )
    lead2 = JobLead(
        location="Arilje", job_type="branje malina",
        employer_name="Voćarstvo Jović",
    )
    status, _ = is_duplicate(lead2, [lead1])
    assert status == DuplicateStatus.POSSIBLE_DUPLICATE


def test_high_text_similarity_same_location():
    lead1 = JobLead(
        raw_text="Radnici za branje malina u okolini Arilja. Smeštaj i hrana obezbeđeni.",
        location="Arilje",
    )
    lead2 = JobLead(
        raw_text="Radnici za branje malina u okolini Arilja. Smeštaj i hrana obezbeđeni. Kontakt 064-123-4567.",
        location="Arilje",
    )
    status, _ = is_duplicate(lead2, [lead1])
    assert status == DuplicateStatus.POSSIBLE_DUPLICATE


if __name__ == '__main__':
    test_same_phone_is_duplicate()
    test_different_phone_is_new()
    test_same_url_is_duplicate()
    test_same_location_job_employer_is_possible_duplicate()
    test_high_text_similarity_same_location()
    print("[PASS]  All duplicate detector tests passed")
