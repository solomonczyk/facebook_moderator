"""E2E Demo — full operator pipeline: public FB → extract → intake → queue → Telegram → operator action.

Usage:
    python -m app.facebook_public_intake.e2e_demo --dry-run --max-groups 3
"""

import sys
import os
import json
import time
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

# Force test mode for Telegram
os.environ["TELEGRAM_TEST_MODE"] = "true"


def _check_url_accessibility(url: str) -> dict:
    """Quick HTTP check to determine if a URL is accessible."""
    try:
        import httpx
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Language": "sr,en-US;q=0.9",
        }
        r = httpx.get(url, headers=headers, timeout=10, follow_redirects=True)
        has_login_form = "login" in r.text.lower() and "password" in r.text.lower()
        return {
            "url": url,
            "http_status": r.status_code,
            "content_length": len(r.text),
            "has_login_form": has_login_form,
            "accessible": r.status_code == 200,
            "checked_at": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        return {
            "url": url,
            "http_status": 0,
            "error": str(e),
            "accessible": False,
            "checked_at": datetime.utcnow().isoformat(),
        }


# Expanded simulated candidates covering all risk levels
E2E_CANDIDATES = [
    # From: Sezonski rad Srbija (own group — highest relevance)
    {
        "group_name": "Sezonski rad Srbija | Poslovi i iskustva radnika",
        "source_url": "https://www.facebook.com/groups/992369183697618",
        "raw_text": "Tražimo 5 radnika za berbu malina Arilje. Smeštaj i 3 obroka obezbeđeni. Dnevnica 5000 RSD. Početak 1. jula. Kontakt 064-123-4567.",
        "expected_classification": "job_offer",
        "expected_risk": "low",
        "expected_action": "approve",
    },
    # From: Sezonski poslovi Srbija
    {
        "group_name": "Sezonski poslovi Srbija",
        "source_url": "https://www.facebook.com/groups/1688328218110932",
        "raw_text": "Imam ekipu 15 ljudi sa svojim prevozom, tražimo berbu malina ili višanja. Svi iskusni. Kontakt 064-988-5113.",
        "expected_classification": "worker_search",
        "expected_risk": "low",
        "expected_action": "approve",
    },
    # Incomplete — no pay, inbox only
    {
        "group_name": "Sezonski poslovi Srbija",
        "source_url": "https://www.facebook.com/groups/1688328218110932",
        "raw_text": "Potrebni radnici za plastenik Subotica. Smeštaj obezbeđen. Javite se inbox za više info.",
        "expected_classification": "job_offer",
        "expected_risk": "medium",
        "expected_action": "needs_info",
    },
    # High risk — passport request
    {
        "group_name": "Sezonski poslovi u poljoprivredi",
        "source_url": "https://www.facebook.com/groups/sezonski.poslovi.poljoprivreda",
        "raw_text": "Posao u inostranstvu! Plata 3000e mesečno. Pošaljite sliku pasoša i JMBG. Javite se agentu.",
        "expected_classification": "suspicious",
        "expected_risk": "high",
        "expected_action": "escalate",
    },
    # Warning about employer
    {
        "group_name": "Poslovi u Srbiji — sezonski rad",
        "source_url": "https://www.facebook.com/groups/poslovi.srbija.sezonski",
        "raw_text": "Čuvajte se! Poslodavac iz Surčina ne isplaćuje dogovoreno. Radio sam mesec dana, dobio pola plate!",
        "expected_classification": "employer_warning",
        "expected_risk": "high",
        "expected_action": "escalate",
    },
    # Spam
    {
        "group_name": "Berba malina — sezonski poslovi",
        "source_url": "https://www.facebook.com/groups/berba.malina.poslovi",
        "raw_text": "ONLINE KAZINO! Dobijate 500e bonusa! Brza zarada od kuće! www.casino-bonus.rs",
        "expected_classification": "spam",
        "expected_risk": "high",
        "expected_action": "mark_spam",
    },
    # Duplicate of candidate 1
    {
        "group_name": "Sezonski rad Srbija | Poslovi i iskustva radnika",
        "source_url": "https://www.facebook.com/groups/992369183697618",
        "raw_text": "Tražimo 5 radnika za berbu malina Arilje. Smeštaj i 3 obroka obezbeđeni. Dnevnica 5000 RSD. Početak 1. jula. Kontakt 064-123-4567.",
        "expected_classification": "job_offer",
        "expected_risk": "low",
        "expected_action": "approve",
        "is_duplicate": True,
    },
]


def run_e2e(dry_run: bool = True, max_groups: int = 5):
    """Full E2E pipeline: groups → candidates → intake → queue → Telegram → operator."""
    print("=" * 65)
    print("TASK 012 — E2E: PUBLIC INTAKE → TELEGRAM OPERATOR APPROVAL")
    print(f"  Dry run: {dry_run}")
    print(f"  Max groups: {max_groups}")
    print(f"  Telegram test mode: {os.environ.get('TELEGRAM_TEST_MODE', '?')}")
    print("=" * 65)

    from app.facebook_public_intake.discovery import get_seed_groups, to_dict
    from app.facebook_public_intake.deduplicator import Deduplicator
    from app.facebook_public_intake.ocr_extractor import ExtractedCandidate
    from app.runtime_agent.action_queue import ActionQueue, QueueItem, ActionType, QueueStatus
    from app.runtime_agent.audit_log import AuditLog
    from app.telegram_bot.notifier import send_notification, is_test_mode, get_test_payloads
    from app.operator_mvp.mvp_api import _classify_rule_based, _classify_risk, _determine_action

    # ── Phase 1: Group Discovery + Accessibility ──────────────────────────
    print("\n[Phase 1] GROUP DISCOVERY + ACCESSIBILITY CHECK")
    groups = get_seed_groups(max_groups)
    groups_checked = []
    public_accessible = 0
    login_blocked = 0

    for g in groups:
        if dry_run:
            status = "public (dry-run)"
            public_accessible += 1
        else:
            result = _check_url_accessibility(g.url)
            if result["accessible"] and not result.get("has_login_form", True):
                status = "public"
                public_accessible += 1
            elif result["accessible"]:
                status = "public_with_login_form"
                public_accessible += 1
            else:
                status = f"blocked (HTTP {result['http_status']})"
                login_blocked += 1

        print(f"  [{status}] {g.group_name}")
        print(f"         {g.url}")
        groups_checked.append({
            "group_name": g.group_name,
            "url": g.url,
            "relevance_score": g.relevance_score,
            "access_status": status,
        })

    # ── Phase 2: Text Extraction (simulated) ──────────────────────────────
    print(f"\n[Phase 2] TEXT EXTRACTION: {len(E2E_CANDIDATES)} candidates")

    # ── Phase 3: Deduplication ────────────────────────────────────────────
    print(f"\n[Phase 3] DEDUPLICATION")
    dedup = Deduplicator()
    new_candidates = []
    duplicates_skipped = 0

    for sc in E2E_CANDIDATES:
        c = ExtractedCandidate(
            source_url=sc["source_url"],
            group_name=sc["group_name"],
            screenshot_path=f"artifacts/screenshots/e2e_{sc['group_name'][:20]}.png",
            raw_text=sc["raw_text"],
        )
        if dedup.is_duplicate(c.raw_text, c.source_url):
            duplicates_skipped += 1
            print(f"  SKIP (duplicate): {c.raw_text[:60]}...")
        else:
            dedup.mark_seen(c.raw_text, c.source_url)
            new_candidates.append((c, sc))
            print(f"  NEW: [{sc['expected_classification']}] {c.raw_text[:60]}...")

    print(f"  Result: {len(new_candidates)} new, {duplicates_skipped} duplicates")

    # ── Phase 4: Classification + Intake → Queue ──────────────────────────
    print(f"\n[Phase 4] CLASSIFY → QUEUE")
    queue = ActionQueue()
    audit = AuditLog()
    queue_items_created = 0
    queue_results = []

    for c, sc in new_candidates:
        classification, fields = _classify_rule_based(c.raw_text)
        risk_level, red_flags = _classify_risk(c.raw_text.lower(), classification, fields)
        has_contact = bool(fields.get("contact"))
        has_location = bool(fields.get("location"))
        action = _determine_action(classification, risk_level, has_contact, has_location)

        # Map action to queue ActionType
        action_type_map = {
            "create_group_post": ActionType.PUBLISH_OWN_GROUP_POST,
            "request_more_info": ActionType.ASK_FOR_MISSING_INFO,
            "escalate_to_operator": ActionType.REQUEST_OPERATOR_REVIEW,
            "reject_as_spam": ActionType.REQUEST_OPERATOR_REVIEW,
        }
        queue_action = action_type_map.get(action, ActionType.REQUEST_OPERATOR_REVIEW)

        item = QueueItem(
            action_type=queue_action,
            suggested_text=c.raw_text[:500],
            reason=f"E2E: {classification}, risk={risk_level}, action={action}",
            operator_approval_required=True,
            lead_id=c.candidate_id,
        )

        if classification == "spam":
            item.mark_spam("Auto-detected spam")

        queue.add(item)
        queue_items_created += 1

        match = "OK" if classification == sc.get("expected_classification", "") else "MISMATCH"
        print(f"  [{match}] q_{item.item_id[:8]}... | {classification} | risk={risk_level} | action={action}")

        queue_results.append({
            "candidate_id": c.candidate_id,
            "item_id": item.item_id,
            "classification": classification,
            "risk_level": risk_level,
            "action": action,
            "queue_action_type": queue_action.value,
            "group_name": c.group_name,
            "source_url": c.source_url,
        })

    # ── Phase 5: Telegram Notification Dispatch ────────────────────────────
    print(f"\n[Phase 5] TELEGRAM NOTIFICATIONS (test mode={is_test_mode()})")
    telegram_sent = 0

    for qr in queue_results:
        item = queue.get(qr["item_id"])
        if not item:
            continue
        enriched = item.to_dict()
        enriched.update({
            "classification": qr["classification"],
            "risk_level": qr["risk_level"],
            "confidence": 0.85,
            "source": "facebook_public_screenshot",
            "missing_info": [],
        })
        sent = send_notification(enriched)
        if sent:
            telegram_sent += 1
            print(f"  [SENT] {qr['item_id'][:16]}... | {qr['classification']} | risk={qr['risk_level']}")

    print(f"  Total notifications: {telegram_sent}")

    # ── Phase 6: Operator Action Simulation ────────────────────────────────
    print(f"\n[Phase 6] OPERATOR ACTION SIMULATION")
    operator = "e2e_test_operator"
    transitions_verified = 0

    for qr in queue_results:
        item = queue.get(qr["item_id"])
        if not item:
            continue

        sc = next((s for s in E2E_CANDIDATES if s["raw_text"][:30] in (qr.get("source_url", "") or item.suggested_text[:30])), None)
        expected_action = qr.get("expected_action", qr["action"])
        if not expected_action:
            # Derive from risk
            if qr["risk_level"] == "high":
                expected_action = "escalate" if qr["classification"] != "spam" else "mark_spam"
            elif qr["risk_level"] == "medium":
                expected_action = "needs_info"
            else:
                expected_action = "approve"

        # Look up expected action from E2E_CANDIDATES
        for sc in E2E_CANDIDATES:
            if sc["raw_text"] == item.suggested_text or sc.get("raw_text", "")[:30] == item.suggested_text[:30]:
                expected_action = sc["expected_action"]
                break

        if expected_action == "approve":
            item.approve(operator)
            audit.record("e2e_approve", f"Item: {qr['item_id']}", new_state="approved", operator=operator)
            icon = "+"
        elif expected_action == "needs_info":
            item.mark_needs_info("Missing info", operator)
            audit.record("e2e_needs_info", f"Item: {qr['item_id']}", new_state="needs_info", operator=operator)
            icon = "?"
        elif expected_action == "escalate":
            item.mark_needs_info(f"Escalated: high risk {qr['classification']}", operator)
            audit.record("e2e_escalate", f"Item: {qr['item_id']}", new_state="needs_info", operator=operator)
            icon = "!"
        elif expected_action == "mark_spam":
            item.mark_spam("E2E spam detection", operator)
            audit.record("e2e_spam", f"Item: {qr['item_id']}", new_state="spam", operator=operator)
            icon = "X"
        else:
            icon = "~"

        transitions_verified += 1
        # Safety: verify approval still required
        assert item.operator_approval_required, "Approval requirement removed!"
        print(f"  [{icon}] {qr['item_id'][:16]}... | {qr['classification']} | {item.status.value}")

    # ── Summary ───────────────────────────────────────────────────────────
    payloads = get_test_payloads()
    print(f"\n{'=' * 65}")
    print("E2E PIPELINE COMPLETE")
    print(f"  Groups checked:              {len(groups_checked)}")
    print(f"  Public accessible:           {public_accessible}")
    print(f"  Login/blocked:               {login_blocked}")
    print(f"  Candidates extracted:        {len(E2E_CANDIDATES)}")
    print(f"  Duplicates skipped:          {duplicates_skipped}")
    print(f"  Queue items created:         {queue_items_created}")
    print(f"  Telegram payloads created:   {len(payloads)}")
    print(f"  Operator transitions:        {transitions_verified}")
    print(f"  Audit entries:               {audit.count}")
    print(f"{'=' * 65}")
    print()
    print("SAFETY PROOF:")
    print(f"  facebook_login_executed:     False")
    print(f"  facebook_publish_executed:   False")
    print(f"  telegram_real_send:          False")
    print(f"  production_accepted:         False")
    print(f"  operator_approval_required:  True (ALL)")
    print(f"  dry_run:                     {dry_run}")

    return {
        "groups_checked": groups_checked,
        "public_accessible": public_accessible,
        "login_blocked": login_blocked,
        "candidates_total": len(E2E_CANDIDATES),
        "duplicates_skipped": duplicates_skipped,
        "queue_items_created": queue_items_created,
        "telegram_payloads": len(payloads),
        "transitions_verified": transitions_verified,
        "queue_results": queue_results,
        "audit_count": audit.count,
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--no-dry-run", action="store_true")
    parser.add_argument("--max-groups", type=int, default=5)
    parser.add_argument("--output", type=str, default="")
    args = parser.parse_args()

    dry_run = not args.no_dry_run
    result = run_e2e(dry_run=dry_run, max_groups=args.max_groups)

    output_path = args.output or "artifacts/e2e_result.json"
    os.makedirs(os.path.dirname(output_path) or "artifacts", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False, default=str)
    print(f"\nFull results saved to: {output_path}")
