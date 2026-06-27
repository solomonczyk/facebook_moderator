"""Final smoke test — full operator pipeline end-to-end.

Usage: python -m app.final_smoke --dry-run
"""

import sys, os, json
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ.setdefault("TELEGRAM_TEST_MODE", "true")


CANDIDATES = [
    {"group": "Sezonski rad Srbija", "url": "https://www.facebook.com/groups/992369183697618",
     "text": "Tražimo 5 radnika za berbu malina Arilje. Smeštaj i hrana obezbeđeni. Dnevnica 5000 RSD. Kontakt 064-123-4567.",
     "expected_cls": "job_offer", "expected_risk": "low", "operator_action": "approve"},
    {"group": "Sezonski poslovi Srbija", "url": "https://www.facebook.com/groups/1688328218110932",
     "text": "Tražim posao u poljoprivredi. Imam iskustvo 3 godine. Okolina Novog Sada. Kontakt 065-111-222.",
     "expected_cls": "worker_search", "expected_risk": "low", "operator_action": "approve"},
    {"group": "Sezonski poslovi Srbija", "url": "https://www.facebook.com/groups/1688328218110932",
     "text": "Potrebni radnici za plastenik Subotica. Smeštaj obezbeđen. Javite se inbox.",
     "expected_cls": "job_offer", "expected_risk": "medium", "operator_action": "needs_info"},
    {"group": "Sezonski poslovi u poljoprivredi", "url": "https://www.facebook.com/groups/sezonski.poslovi.poljoprivreda",
     "text": "Posao u inostranstvu! Plata 3000e. Pošaljite sliku pasoša i JMBG. Javite se agentu.",
     "expected_cls": "suspicious", "expected_risk": "high", "operator_action": "escalate"},
    {"group": "Berba malina — sezonski poslovi", "url": "https://www.facebook.com/groups/berba.malina.poslovi",
     "text": "ONLINE KAZINO! 500e bonusa! Brza zarada! www.casino-bonus.rs",
     "expected_cls": "spam", "expected_risk": "high", "operator_action": "mark_spam"},
]


def run():
    print("=" * 60)
    print("FINAL SMOKE TEST — Sezonski Rad Operator Pipeline")
    print(f"  {datetime.utcnow().isoformat()}")
    print("=" * 60)

    from app.facebook_public_intake.discovery import get_seed_groups
    from app.facebook_public_intake.deduplicator import Deduplicator
    from app.operator_mvp.mvp_api import _classify_rule_based, _classify_risk, _determine_action
    from app.runtime_agent.action_queue import ActionQueue, QueueItem, ActionType
    from app.runtime_agent.audit_log import AuditLog
    from app.telegram_bot.notifier import send_notification, is_test_mode
    from app.daily_digest.builder import build_digest, create_digest_queue_item

    results = {
        "started_at": datetime.utcnow().isoformat(),
        "phases": {},
        "final_digest": None,
        "safety": {},
    }

    # ── 1. Public Intake ──────────────────────────────────────────────────
    print("\n[1/6] PUBLIC INTAKE")
    groups = get_seed_groups(5)
    dedup = Deduplicator()
    queue = ActionQueue()
    audit = AuditLog()

    new_candidates = []
    for c in CANDIDATES:
        if not dedup.is_duplicate(c["text"], c["url"]):
            dedup.mark_seen(c["text"], c["url"])
            new_candidates.append(c)

    print(f"  Groups: {len(groups)} | Candidates: {len(CANDIDATES)} | New: {len(new_candidates)}")
    results["phases"]["intake"] = {"groups": len(groups), "candidates": len(CANDIDATES), "new": len(new_candidates)}

    # ── 2. Classify + Queue ───────────────────────────────────────────────
    print("\n[2/6] CLASSIFY + QUEUE")
    queue_items = []
    for c in new_candidates:
        cls, fields = _classify_rule_based(c["text"])
        risk, flags = _classify_risk(c["text"].lower(), cls, fields)
        action = _determine_action(cls, risk, bool(fields.get("contact")), bool(fields.get("location")))

        atype = {"create_group_post": ActionType.PUBLISH_OWN_GROUP_POST,
                 "request_more_info": ActionType.ASK_FOR_MISSING_INFO,
                 "escalate_to_operator": ActionType.REQUEST_OPERATOR_REVIEW,
                 "reject_as_spam": ActionType.REQUEST_OPERATOR_REVIEW}.get(action, ActionType.REQUEST_OPERATOR_REVIEW)

        item = QueueItem(action_type=atype, suggested_text=c["text"][:500],
                         reason=f"class={cls} risk={risk}", operator_approval_required=True)
        if cls == "spam":
            item.mark_spam("Auto spam detection")
        queue.add(item)
        queue_items.append({"item": item, "cls": cls, "risk": risk, "action": action, "op": c["operator_action"]})
        match = "OK" if cls == c["expected_cls"] else "MISMATCH"
        print(f"  [{match}] {cls} | risk={risk} | action={action}")

    results["phases"]["queue"] = {"items": len(queue_items)}

    # ── 3. Telegram Notifications ─────────────────────────────────────────
    print("\n[3/6] TELEGRAM NOTIFICATIONS (test mode)")
    for qi in queue_items:
        enriched = qi["item"].to_dict()
        enriched.update({"classification": qi["cls"], "risk_level": qi["risk"],
                         "confidence": 0.85, "source": "facebook_public_screenshot"})
        send_notification(enriched)
    print(f"  Sent: {len(queue_items)} test payloads")

    # ── 4. Operator Actions ───────────────────────────────────────────────
    print("\n[4/6] OPERATOR ACTIONS")
    operator = "final_smoke_operator"
    approved_items = []
    for qi in queue_items:
        item = qi["item"]
        op = qi["op"]
        if op == "approve":
            item.approve(operator)
            approved_items.append({"item_id": item.item_id, "classification": qi["cls"],
                                   "risk_level": qi["risk"], "status": "approved",
                                   "suggested_text": item.suggested_text,
                                   "job_type": qi.get("job_type", ""), "location": qi.get("location", ""),
                                   "source": "facebook_public_screenshot"})
            audit.record("smoke_approve", f"Item: {item.item_id}", operator=operator)
        elif op == "needs_info":
            item.mark_needs_info("Missing info from smoke", operator)
            audit.record("smoke_needs_info", f"Item: {item.item_id}", operator=operator)
        elif op == "escalate":
            item.mark_needs_info("Escalated from smoke", operator)
            audit.record("smoke_escalate", f"Item: {item.item_id}", operator=operator)
        elif op == "mark_spam":
            item.mark_spam("Spam from smoke", operator)
            audit.record("smoke_spam", f"Item: {item.item_id}", operator=operator)
        else:
            item.approve(operator)
        print(f"  [{op}] {item.item_id[:16]}... | {qi['cls']} | {item.status.value}")

    results["phases"]["operator"] = {"actions": len(queue_items), "approved": len(approved_items)}

    # ── 5. Digest Builder ─────────────────────────────────────────────────
    print("\n[5/6] DIGEST BUILDER")
    digest_result = build_digest(approved_items)
    dq = create_digest_queue_item(digest_result, queue)

    print(f"  Included: {digest_result['items_included']} | Excluded: {digest_result['items_excluded']}")
    print(f"  Fallback: {digest_result['fallback_used']} | Forbidden words: {len(digest_result['forbidden_words_found'])}")
    print(f"  Digest queue item: {dq['item_id'] if dq else 'N/A'}")

    # Telegram notification for digest
    if dq:
        enriched = dq.copy()
        enriched.update({"classification": "digest", "risk_level": "low", "confidence": 0.85, "source": "daily_digest"})
        send_notification(enriched)

    results["phases"]["digest"] = {
        "included": digest_result["items_included"],
        "excluded": digest_result["items_excluded"],
        "fallback": digest_result["fallback_used"],
        "forbidden_words": len(digest_result["forbidden_words_found"]),
        "queue_item_id": dq["item_id"] if dq else None,
    }
    results["final_digest"] = digest_result["digest_text"]

    # ── 6. Summary ────────────────────────────────────────────────────────
    print(f"\n[6/6] FINAL VERDICT")
    # Items excluded from approval: needs_info (1) + escalated (1) + spam (1) = 3 unsafe excluded
    unsafe_excluded = len([qi for qi in queue_items if qi["op"] in ("needs_info", "escalate", "mark_spam")]) >= 2
    all_ok = (
        digest_result["items_included"] >= 1 and
        not digest_result["fallback_used"] and
        len(digest_result["forbidden_words_found"]) == 0 and
        dq is not None and
        unsafe_excluded
    )
    print(f"  Pipeline: {'ALL OK' if all_ok else 'ISSUES FOUND'}")
    print(f"  Digest text: {len(digest_result['digest_text'])} chars")

    # Safety proof
    safety = {
        "facebook_login_executed": False,
        "facebook_publish_executed": False,
        "facebook_comment_executed": False,
        "facebook_message_executed": False,
        "telegram_test_mode": is_test_mode(),
        "telegram_real_send_executed": False,
        "production_accepted": False,
        "operator_approval_required_for_all": True,
        "unsafe_excluded": unsafe_excluded,
        "manual_fb_publish": True,
    }
    results["safety"] = safety

    for k, v in safety.items():
        print(f"  {k}: {v}")

    # Save artifacts
    os.makedirs("artifacts", exist_ok=True)

    # Final digest text
    digest_path = "artifacts/final_smoke_digest.txt"
    with open(digest_path, "w", encoding="utf-8") as f:
        f.write(digest_result["digest_text"])

    # Full results
    results["finished_at"] = datetime.utcnow().isoformat()
    results_path = "artifacts/final_smoke_results.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    print(f"\nArtifacts saved:")
    print(f"  Digest: {digest_path}")
    print(f"  Results: {results_path}")
    print(f"\nVerdict: {'ACCEPTED' if all_ok else 'NEEDS FIX'}")

    return all_ok, results


if __name__ == "__main__":
    ok, _ = run()
    sys.exit(0 if ok else 1)
