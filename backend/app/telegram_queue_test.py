"""Telegram queue notification real test — sends one queue item to operator.

Usage:
    python -m app.telegram_queue_test              # dry-run
    python -m app.telegram_queue_test --real       # real send
"""

import sys, os, json, argparse
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.env_loader import load_env; load_env()
os.environ.setdefault("TELEGRAM_TEST_MODE", "true")


def test_queue_notify(real: bool = False) -> dict:
    from app.telegram_bot.notifier import is_test_mode, is_available, send_notification
    from app.runtime_agent.action_queue import ActionQueue, QueueItem, ActionType

    if real and is_test_mode():
        return {"sent": False, "error": "TEST_MODE blocks real send. Set TELEGRAM_TEST_MODE=false."}
    if real and not is_available():
        return {"sent": False, "error": "Bot token or chat ID not configured."}

    # Override test mode for real send
    if real:
        os.environ["TELEGRAM_TEST_MODE"] = "false"

    # Create safe demo queue item
    queue = ActionQueue()
    item = QueueItem(
        action_type=ActionType.PUBLISH_OWN_GROUP_POST,
        suggested_text="Test queue item: Tražimo 3 radnika za berbu malina, Arilje. Smeštaj i hrana obezbeđeni. Dnevnica 5000 RSD. Kontakt 064-123-4567.",
        reason="Telegram queue test — safe demo item",
        operator_approval_required=True,
    )
    queue.add(item)

    # Send notification
    enriched = item.to_dict()
    enriched.update({
        "classification": "job_offer",
        "risk_level": "low",
        "confidence": 0.92,
        "source": "telegram_queue_test",
        "missing_info": ["work hours"],
    })
    sent = send_notification(enriched)

    return {
        "sent": sent,
        "real": real,
        "test_mode": os.environ.get("TELEGRAM_TEST_MODE", "?"),
        "item_id": item.item_id,
        "action_type": item.action_type.value,
        "classification": "job_offer",
        "risk_level": "low",
        "operator_approval_required": item.operator_approval_required,
        "sent_at": datetime.utcnow().isoformat(),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--real", action="store_true")
    args = p.parse_args()

    print("=" * 55)
    print("TELEGRAM QUEUE NOTIFICATION TEST")
    print(f"  Mode: {'REAL' if args.real else 'DRY RUN / TEST MODE'}")
    print("=" * 55)

    result = test_queue_notify(real=args.real)

    print(f"  Sent: {result['sent']}")
    print(f"  Item ID: {result['item_id']}")
    print(f"  Classification: {result['classification']}")
    print(f"  Risk: {result['risk_level']}")
    print(f"  Approval required: {result['operator_approval_required']}")

    if result["sent"]:
        print(f"\n  Operator should now see the item in Telegram.")
        print(f"  Buttons: [Approve] [Reject] [Edit] [Request Info] [Escalate] [Spam]")
        print(f"  Press Approve → queue status changes to 'approved'.")
        print(f"  Press Reject → queue status changes to 'rejected'.")

    print(f"\n  No Facebook actions. No secrets exposed. production_accepted=false.")

    os.makedirs("artifacts", exist_ok=True)
    out = {k: v for k, v in result.items()}
    with open("artifacts/telegram_queue_test_result.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False, default=str)


if __name__ == "__main__":
    main()
