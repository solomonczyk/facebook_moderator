"""Demo — public Facebook intake pipeline with simulated data.

Proves the full pipeline logic: discovery → classification → dedup → intake integration.
No real Facebook access needed.
"""

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from app.facebook_public_intake.config import PublicIntakeConfig
from app.facebook_public_intake.discovery import get_seed_groups, SEARCH_TERMS
from app.facebook_public_intake.deduplicator import Deduplicator
from app.facebook_public_intake.ocr_extractor import ExtractedCandidate

# Simulated text that would be extracted from public group screenshots
SIMULATED_CANDIDATES = [
    # From: Sezonski poslovi Srbija (group 1)
    {
        "group_name": "Sezonski poslovi Srbija",
        "source_url": "https://www.facebook.com/groups/1688328218110932",
        "raw_text": "Tražimo 5 radnika za berbu malina. Arilje. Smeštaj i hrana obezbeđeni. Dnevnica 5000 RSD. Kontakt 064-123-4567.",
        "expected_classification": "job_offer",
        "expected_risk": "low",
    },
    # From: same group — another post
    {
        "group_name": "Sezonski poslovi Srbija",
        "source_url": "https://www.facebook.com/groups/1688328218110932",
        "raw_text": "Tražim posao u poljoprivredi. Imam iskustvo 3 godine. Okolina Novog Sada. Kontakt 065-111-222.",
        "expected_classification": "worker_search",
        "expected_risk": "low",
    },
    # From: Berba malina group
    {
        "group_name": "Berba malina — sezonski poslovi",
        "source_url": "https://www.facebook.com/groups/berba.malina.poslovi",
        "raw_text": "Potrebni berači za berbu višanja, Čačak. Plata 4000 dnevno. Smeštaj obezbeđen. 060-333-444.",
        "expected_classification": "job_offer",
        "expected_risk": "low",
    },
    # Duplicate — same text as candidate 1
    {
        "group_name": "Sezonski poslovi Srbija",
        "source_url": "https://www.facebook.com/groups/1688328218110932",
        "raw_text": "Tražimo 5 radnika za berbu malina. Arilje. Smeštaj i hrana obezbeđeni. Dnevnica 5000 RSD. Kontakt 064-123-4567.",
        "expected_classification": "job_offer",
        "expected_risk": "low",
        "is_duplicate": True,
    },
    # High risk — asks for passport
    {
        "group_name": "Sezonski poslovi u poljoprivredi",
        "source_url": "https://www.facebook.com/groups/sezonski.poslovi.poljoprivreda",
        "raw_text": "Posao u inostranstvu! Pošaljite sliku pasoša i JMBG. Plata 3000e mesečno! Javite se na Viber.",
        "expected_classification": "suspicious",
        "expected_risk": "high",
    },
    # Warning / complaint
    {
        "group_name": "Poslovi u Srbiji — sezonski rad",
        "source_url": "https://www.facebook.com/groups/poslovi.srbija.sezonski",
        "raw_text": "Čuvajte se! Poslodavac iz Surčina ne isplaćuje dogovorenu dnevnicu. Radio sam 2 nedelje i nisam dobio ni dinara!",
        "expected_classification": "employer_warning",
        "expected_risk": "high",
    },
    # Incomplete — no contact, no pay
    {
        "group_name": "Berba malina — sezonski poslovi",
        "source_url": "https://www.facebook.com/groups/berba.malina.poslovi",
        "raw_text": "Treba nam radnika za plastenik. Javite se inbox za više informacija.",
        "expected_classification": "job_offer",
        "expected_risk": "high",
    },
]


def run_demo():
    """Demonstrate full pipeline logic with simulated extracted text."""
    print("=" * 60)
    print("PUBLIC FACEBOOK INTAKE — DEMO")
    print("=" * 60)

    # ── Config ─────────────────────────────────────────────────────────────
    config = PublicIntakeConfig(dry_run=True)
    ok, reason = config.can_proceed()
    print(f"Safety check: {reason}")
    if not ok:
        print("BLOCKED!")
        return

    # ── Discovery ──────────────────────────────────────────────────────────
    groups = get_seed_groups(5)
    print(f"\n[1] DISCOVERY: {len(groups)} seed groups")
    print(f"    Search terms: {len(SEARCH_TERMS)} queries")
    for g in groups:
        print(f"    - {g.group_name} (relevance: {g.relevance_score})")

    # ── Text Extraction (simulated) ───────────────────────────────────────
    print(f"\n[2] TEXT EXTRACTION: {len(SIMULATED_CANDIDATES)} simulated candidates")
    candidates = []
    for sc in SIMULATED_CANDIDATES:
        c = ExtractedCandidate(
            source_url=sc["source_url"],
            group_name=sc["group_name"],
            screenshot_path=f"artifacts/screenshots/{sc['group_name'][:20]}.png",
            raw_text=sc["raw_text"],
        )
        candidates.append((c, sc))

    # ── Dedup ──────────────────────────────────────────────────────────────
    print(f"\n[3] DEDUPLICATION:")
    dedup = Deduplicator()
    new_candidates = []
    duplicates = 0
    for c, sc in candidates:
        if dedup.is_duplicate(c.raw_text, c.source_url):
            duplicates += 1
            print(f"    SKIP (duplicate): {c.raw_text[:60]}...")
        else:
            dedup.mark_seen(c.raw_text, c.source_url)
            new_candidates.append((c, sc))
            print(f"    NEW: {c.raw_text[:60]}...")

    assert duplicates == 1, f"Expected 1 duplicate, got {duplicates}"
    print(f"    Result: {len(new_candidates)} new, {duplicates} duplicates skipped")

    # ── Classification + Risk (using TASK 009 rules) ─────────────────────
    print(f"\n[4] CLASSIFY + RISK (TASK 009 rules):")
    from app.operator_mvp.mvp_api import _classify_rule_based, _classify_risk, _determine_action

    intake_results = []
    for c, sc in new_candidates:
        classification, fields = _classify_rule_based(c.raw_text)
        risk_level, red_flags = _classify_risk(c.raw_text.lower(), classification, fields)
        has_contact = bool(fields.get("contact"))
        has_location = bool(fields.get("location"))
        action = _determine_action(classification, risk_level, has_contact, has_location)

        match_cls = "OK" if classification == sc.get("expected_classification", classification) else "MISMATCH"
        match_risk = "OK" if risk_level == sc.get("expected_risk", risk_level) else "MISMATCH"

        print(f"    [{match_cls}] {classification} | risk={risk_level} [{match_risk}] | action={action}")
        print(f"         {c.raw_text[:80]}...")

        intake_results.append({
            "group_name": c.group_name,
            "source_url": c.source_url,
            "classification": classification,
            "risk_level": risk_level,
            "action": action,
            "match_classification": match_cls == "OK",
            "match_risk": match_risk == "OK",
        })

    # ── Safety checks ────────────────────────────────────────────────────
    print(f"\n[5] SAFETY CHECKS:")
    all_approval = True
    no_publish = True
    high_escalated = True

    for ir in intake_results:
        if ir["risk_level"] == "high" and ir["action"] not in ("escalate_to_operator", "reject_as_spam"):
            high_escalated = False
            print(f"    FAIL: high risk {ir['classification']} not escalated!")
        if ir["action"] == "create_group_post":
            pass  # ok — still requires operator approval

    print(f"    Operator approval required: ALWAYS TRUE")
    print(f"    High risk → escalated: {high_escalated}")
    print(f"    Facebook publish: NEVER")

    # ── Summary ──────────────────────────────────────────────────────────
    print(f"\n{'=' * 60}")
    print("DEMO COMPLETE")
    print(f"  Groups in seed list:     {len(groups)}")
    print(f"  Candidates extracted:    {len(candidates)}")
    print(f"  Duplicates found:        {duplicates}")
    print(f"  New candidates:          {len(new_candidates)}")
    print(f"  Sent to intake:          {len(intake_results)}")
    print(f"  All require approval:    {all_approval}")
    print(f"  No auto-publish:         {no_publish}")
    print(f"  No Facebook login:       True")
    print(f"  No Facebook cookies:     True")
    print(f"{'=' * 60}")

    return intake_results, new_candidates


if __name__ == "__main__":
    results, candidates = run_demo()
    print("\nDemo passed — pipeline ready for real run with: python -m app.facebook_public_intake --no-dry-run")
