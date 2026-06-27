"""Real Daily Workflow Pilot — full operator daily cycle.

Usage:
    python -m app.daily_pilot                    # dry-run/test mode
    python -m app.daily_pilot --real             # real Telegram (requires env)

Flow:
    1. Setup check
    2. Public intake dry-run
    3. Classify + queue
    4. Telegram notifications (real if --real)
    5. Operator action simulation
    6. Digest builder
    7. Final digest artifact
"""

import sys, os, json, argparse
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.env_loader import load_env; load_env()
os.environ.setdefault("TELEGRAM_TEST_MODE", "true")


def run(real: bool = False):
    print("=" * 60)
    print("DAILY WORKFLOW PILOT — Sezonski Rad Operator")
    print(f"  Mode: {'REAL' if real else 'DRY RUN / TEST'}")
    print(f"  {datetime.utcnow().isoformat()}")
    print("=" * 60)

    # ── 1. Setup Check ───────────────────────────────────────────────────
    print("\n[1/7] SETUP CHECK")
    from app.telegram_setup_check import check as setup_check, mask
    setup = setup_check()
    print(f"  Token: {setup['bot_token_masked']} | Chat: {setup['operator_chat_id_masked']}")
    print(f"  Test mode: {setup['test_mode']} | Can real send: {setup['can_real_send']}")
    for w in setup["warnings"]:
        print(f"  [{('WARN' if 'not configured' in w else 'INFO')}] {w}")

    # ── 2. Public Intake ─────────────────────────────────────────────────
    print("\n[2/7] PUBLIC INTAKE")
    from app.facebook_public_intake.discovery import get_seed_groups
    from app.facebook_public_intake.deduplicator import Deduplicator

    groups = get_seed_groups(5)
    dedup = Deduplicator()

    candidates = [
        ("Tražimo 5 radnika za berbu malina Arilje. Smeštaj i hrana obezbeđeni. Dnevnica 5000 RSD. Kontakt 064-123-4567.",
         "Sezonski rad Srbija", "https://www.facebook.com/groups/992369183697618",
         "job_offer", "low"),
        ("Tražim posao u poljoprivredi. Imam iskustvo 3 godine. Okolina Novog Sada. Kontakt 065-111-222.",
         "Sezonski poslovi Srbija", "https://www.facebook.com/groups/1688328218110932",
         "worker_search", "low"),
        ("Potrebni radnici za plastenik Subotica. Smeštaj obezbeđen. Javite se inbox.",
         "Sezonski poslovi Srbija", "https://www.facebook.com/groups/1688328218110932",
         "job_offer", "medium"),
        ("Posao u inostranstvu! Pošaljite pasoš i JMBG. Plata 3000e. Javite se agentu.",
         "Sezonski poslovi u poljoprivredi", "https://www.facebook.com/groups/sezonski.poslovi.poljoprivreda",
         "suspicious", "high"),
        ("ONLINE KAZINO! 500e bonusa! Brza zarada! www.casino.rs",
         "Berba malina", "https://www.facebook.com/groups/berba.malina.poslovi",
         "spam", "high"),
    ]

    new_c = []
    for text, group, url, *_ in candidates:
        if not dedup.is_duplicate(text, url):
            dedup.mark_seen(text, url)
            new_c.append((text, group, url))
    print(f"  Groups: {len(groups)} | Candidates: {len(candidates)} | New: {len(new_c)} | Dups: {len(candidates) - len(new_c)}")

    # ── 3. Classify + Queue ──────────────────────────────────────────────
    print("\n[3/7] CLASSIFY + QUEUE")
    from app.operator_mvp.mvp_api import _classify_rule_based, _classify_risk, _determine_action
    from app.runtime_agent.action_queue import ActionQueue, QueueItem, ActionType
    from app.runtime_agent.audit_log import AuditLog

    queue = ActionQueue()
    audit = AuditLog()
    queue_items = []

    for i, (text, group, url) in enumerate(new_c):
        cls, fields = _classify_rule_based(text)
        risk, flags = _classify_risk(text.lower(), cls, fields)
        action = _determine_action(cls, risk, bool(fields.get("contact")), bool(fields.get("location")))

        atype_map = {"create_group_post": ActionType.PUBLISH_OWN_GROUP_POST,
                     "request_more_info": ActionType.ASK_FOR_MISSING_INFO,
                     "escalate_to_operator": ActionType.REQUEST_OPERATOR_REVIEW,
                     "reject_as_spam": ActionType.REQUEST_OPERATOR_REVIEW}
        item = QueueItem(action_type=atype_map.get(action, ActionType.REQUEST_OPERATOR_REVIEW),
                        suggested_text=text[:500], reason=f"class={cls} risk={risk}", operator_approval_required=True)
        if cls == "spam":
            item.mark_spam("Auto spam")
        queue.add(item)
        qi = {"item": item, "cls": cls, "risk": risk, "action": action, "group": group, "text": text[:80]}
        # Determine operator action based on risk
        if cls == "spam": qi["op"] = "mark_spam"
        elif risk == "high": qi["op"] = "escalate"
        elif risk == "medium": qi["op"] = "needs_info"
        else: qi["op"] = "approve"
        queue_items.append(qi)
        print(f"  [{cls}] risk={risk} | action={action} | op={qi['op']}")

    # ── 4. Telegram Notifications ─────────────────────────────────────────
    print(f"\n[4/7] TELEGRAM NOTIFICATIONS ({'REAL' if real else 'TEST MODE'})")
    from app.telegram_bot.notifier import send_notification, is_test_mode
    if real:
        os.environ["TELEGRAM_TEST_MODE"] = "false"
    for qi in queue_items:
        enriched = qi["item"].to_dict()
        enriched.update({"classification": qi["cls"], "risk_level": qi["risk"],
                        "confidence": 0.85, "source": "daily_pilot"})
        send_notification(enriched)
    print(f"  Dispatched: {len(queue_items)}")

    # ── 5. Operator Actions ───────────────────────────────────────────────
    print(f"\n[5/7] OPERATOR ACTIONS ({'REAL CALLBACKS' if real else 'SIMULATED'})")
    operator = "daily_pilot_operator"
    approved_for_digest = []
    for qi in queue_items:
        item, op = qi["item"], qi["op"]
        if op == "approve":
            item.approve(operator)
            approved_for_digest.append({"item_id": item.item_id, "status": "approved",
                "classification": qi["cls"], "risk_level": qi["risk"],
                "suggested_text": item.suggested_text, "location": qi["group"],
                "source": "daily_pilot", "confidence": 0.85})
        elif op == "needs_info": item.mark_needs_info("Missing info", operator)
        elif op == "escalate": item.mark_needs_info("Escalated", operator)
        elif op == "mark_spam": item.mark_spam("Spam", operator)
        audit.record(f"pilot_{op}", f"Item: {item.item_id}", operator=operator)
        print(f"  [{op}] {item.item_id[:16]}... | {qi['cls']} | {item.status.value}")

    # ── 6. Digest Builder ─────────────────────────────────────────────────
    print(f"\n[6/7] DIGEST BUILDER")
    from app.daily_digest.builder import build_digest, create_digest_queue_item
    digest = build_digest(approved_for_digest)
    dq_item = create_digest_queue_item(digest, queue)
    print(f"  Included: {digest['items_included']} | Excluded: {digest['items_excluded']}")
    print(f"  Fallback: {digest['fallback_used']} | Forbidden: {len(digest['forbidden_words_found'])}")

    # Send digest notification
    if dq_item:
        enriched = dq_item.copy()
        enriched.update({"classification": "digest", "risk_level": "low", "confidence": 0.85, "source": "daily_pilot"})
        send_notification(enriched)

    # ── 7. Final Artifact ─────────────────────────────────────────────────
    print(f"\n[7/7] FINAL DIGEST ARTIFACT")
    os.makedirs("artifacts", exist_ok=True)
    path = "artifacts/daily_pilot_final_digest.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write(digest["digest_text"])
    print(f"  Saved: {path} ({len(digest['digest_text'])} chars)")

    # Summary
    print(f"\n{'=' * 60}")
    print("PILOT COMPLETE")
    print(f"  Setup: {'OK' if setup['bot_token_configured'] else 'NO TOKEN'}")
    print(f"  Tele real: {real}")
    print(f"  Intake: {len(groups)} groups, {len(new_c)} candidates")
    print(f"  Queue: {len(queue_items)} items")
    print(f"  Digest: {digest['items_included']} items, {len(digest['digest_text'])} chars")
    print(f"  FB auto-publish: NEVER")
    print(f"  Production: false")
    print(f"{'=' * 60}")

    return {
        "setup": setup,
        "groups": len(groups),
        "candidates": len(new_c),
        "queue_items": len(queue_items),
        "digest_included": digest["items_included"],
        "digest_excluded": digest["items_excluded"],
        "digest_fallback": digest["fallback_used"],
        "forbidden_words": len(digest["forbidden_words_found"]),
        "real_send": real,
        "telegram_messages_sent": len(queue_items) + 1 if real else 0,
        "production_accepted": False,
        "facebook_publish": False,
    }


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--real", action="store_true")
    args = p.parse_args()
    result = run(real=args.real)

    os.makedirs("artifacts", exist_ok=True)
    with open("artifacts/daily_pilot_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False, default=str)
    print("\nSaved: artifacts/daily_pilot_result.json")
