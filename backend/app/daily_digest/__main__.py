"""CLI for daily digest builder.

Usage:
    python -m app.daily_digest --dry-run
    python -m app.daily_digest --date 2026-06-27
"""

import sys, os, json, argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
os.environ.setdefault("TELEGRAM_TEST_MODE", "true")

from datetime import datetime
from app.daily_digest.builder import build_digest, create_digest_queue_item
from app.runtime_agent.action_queue import ActionQueue, QueueStatus
from app.runtime_agent.audit_log import AuditLog
from app.telegram_bot.notifier import send_notification, is_test_mode


def main():
    parser = argparse.ArgumentParser(description="Daily digest builder")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--date", type=str, default=None)
    args = parser.parse_args()

    date_str = args.date or datetime.utcnow().strftime("%d.%m.%Y")
    dry_run = args.dry_run

    print("=" * 55)
    print(f"DAILY DIGEST BUILDER — {date_str}")
    print(f"  Dry run: {dry_run}")
    print(f"  Test mode: {is_test_mode()}")
    print("=" * 55)

    # Simulated approved items from previous pipeline runs
    source_items = _load_demo_items()

    # Build digest
    result = build_digest(source_items, date_str)

    print(f"\n[FILTER] {len(source_items)} total, {result['items_included']} included, {result['items_excluded']} excluded")
    for reason in result.get("excluded_reasons", []):
        print(f"  EXCLUDED: {reason}")
    if result["fallback_used"]:
        print("  FALLBACK DIGEST USED (not enough items)")

    print(f"\n[DIGEST TEXT] ({len(result['digest_text'])} chars)")
    print(result["digest_text"][:500])
    if len(result["digest_text"]) > 500:
        print("...")

    # Forbidden words check
    if result["forbidden_words_found"]:
        print(f"\n  FORBIDDEN WORDS FOUND: {result['forbidden_words_found']}")
    else:
        print(f"\n  No forbidden words found")

    # Create queue item
    queue = ActionQueue()
    audit = AuditLog()
    queue_item = create_digest_queue_item(result, queue)

    if queue_item:
        print(f"\n[QUEUE] Digest queue item: {queue_item['item_id']}")
        print(f"  Action: {queue_item['action_type']}")
        print(f"  Approval required: {queue_item['operator_approval_required']}")

        # Telegram notification
        enriched = queue_item.copy()
        enriched.update({
            "classification": "digest_candidate",
            "risk_level": "low",
            "confidence": 0.85,
            "source": "daily_digest_builder",
            "missing_info": [],
        })
        sent = send_notification(enriched)
        print(f"  Telegram notification: {'sent (test mode)' if sent else 'failed'}")

    print(f"\nSAFETY: no Facebook publish, no real Telegram send")

    # Save output
    os.makedirs("artifacts", exist_ok=True)
    output = {
        "date": date_str,
        "items_included": result["items_included"],
        "items_excluded": result["items_excluded"],
        "excluded_reasons": result["excluded_reasons"],
        "digest_text": result["digest_text"],
        "fallback_used": result["fallback_used"],
        "forbidden_words_found": result["forbidden_words_found"],
        "queue_item": queue_item,
        "source_ids": result["source_item_ids"],
    }
    outpath = f"artifacts/digest_{date_str.replace('.', '-')}.json"
    with open(outpath, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\nSaved: {outpath}")


def _load_demo_items() -> list[dict]:
    """Load simulated approved items (mirrors TASK 012 E2E results)."""
    return [
        {
            "item_id": "q_demo_001",
            "status": "approved",
            "classification": "job_offer",
            "risk_level": "low",
            "confidence": 0.92,
            "source": "facebook_public_screenshot",
            "suggested_text": "Tražimo 5 radnika za berbu malina Arilje...",
            "job_type": "berba malina",
            "location": "Arilje",
            "pay": "5000 RSD dnevno",
            "accommodation": "da (smeštaj obezbeđen)",
            "food": "da (3 obroka)",
            "contact": "064-123-4567",
        },
        {
            "item_id": "q_demo_002",
            "status": "approved",
            "classification": "worker_search",
            "risk_level": "low",
            "confidence": 0.88,
            "source": "facebook_manual",
            "suggested_text": "Tražim posao u poljoprivredi...",
            "job_type": "poljoprivreda",
            "location": "okolina Novog Sada",
            "contact": "065-111-222",
        },
        {
            "item_id": "q_demo_003",
            "status": "needs_info",
            "classification": "job_offer",
            "risk_level": "medium",
            "confidence": 0.65,
            "source": "facebook_public_screenshot",
            "suggested_text": "Potrebni radnici za plastenik...",
            "missing_info": ["pay", "contact"],
        },
        {
            "item_id": "q_demo_004",
            "status": "needs_info",
            "classification": "suspicious",
            "risk_level": "high",
            "confidence": 0.78,
            "source": "facebook_public_screenshot",
            "suggested_text": "Posao u inostranstvu! Pošaljite pasoš...",
        },
        {
            "item_id": "q_demo_005",
            "status": "needs_info",
            "classification": "employer_warning",
            "risk_level": "high",
            "confidence": 0.82,
            "source": "facebook_manual",
            "suggested_text": "Čuvajte se poslodavca iz Surčina!",
        },
        {
            "item_id": "q_demo_006",
            "status": "spam",
            "classification": "spam",
            "risk_level": "high",
            "confidence": 0.99,
            "source": "facebook_public_screenshot",
            "suggested_text": "ONLINE KAZINO! Dobijate 500e bonusa!",
        },
    ]


if __name__ == "__main__":
    main()
