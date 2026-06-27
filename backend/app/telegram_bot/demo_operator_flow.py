"""Demo — Telegram operator approval flow with 3 items.

Proves: queue item creation → notification → operator approve/reject/escalate → queue update.
All in test mode (no real Telegram send).
"""

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

# Force test mode
os.environ["TELEGRAM_TEST_MODE"] = "true"

from app.runtime_agent.action_queue import ActionQueue, QueueItem, ActionType, QueueStatus
from app.runtime_agent.audit_log import AuditLog
from app.telegram_bot.notifier import (
    send_notification,
    build_notification_message,
    is_test_mode,
    get_test_payloads,
)

DEMO_ITEMS = [
    {
        "id": "demo_item_001",
        "name": "Low-risk job offer → approve",
        "item": {
            "item_id": "q_demo_001",
            "action_type": "publish_own_group_post",
            "status": "pending",
            "suggested_text": "Tražimo 5 radnika za berbu malina Arilje. Smeštaj i hrana obezbeđeni. Dnevnica 5000 RSD. Kontakt 064-123-4567.\n\nNapomena: Grupa nije poslodavac i ne garantuje uslove...",
            "reason": "Complete employer post. Safe to publish.",
            "classification": "job_offer",
            "risk_level": "low",
            "confidence": 0.92,
            "source": "facebook_manual",
            "missing_info": ["work hours", "start date"],
            "operator_approval_required": True,
        },
        "expected_action": "approve",
        "expected_final_status": "approved",
    },
    {
        "id": "demo_item_002",
        "name": "Medium-risk incomplete job → request_info",
        "item": {
            "item_id": "q_demo_002",
            "action_type": "publish_own_group_post",
            "status": "pending",
            "suggested_text": "Potrebni radnici za plastenik. Javite se inbox.",
            "reason": "Incomplete: no pay, no location, no phone.",
            "classification": "job_offer",
            "risk_level": "medium",
            "confidence": 0.65,
            "source": "facebook_public_screenshot",
            "missing_info": ["pay", "location", "contact"],
            "operator_approval_required": True,
        },
        "expected_action": "needs_info",
        "expected_final_status": "needs_info",
    },
    {
        "id": "demo_item_003",
        "name": "High-risk warning → escalate",
        "item": {
            "item_id": "q_demo_003",
            "action_type": "request_operator_review",
            "status": "pending",
            "suggested_text": "Čuvajte se poslodavca iz Surčina! Ne isplaćuje dogovorenu dnevnicu!",
            "reason": "Employer warning with serious accusation. Must be escalated.",
            "classification": "employer_warning",
            "risk_level": "high",
            "confidence": 0.78,
            "source": "facebook_manual",
            "missing_info": ["employer verification", "evidence"],
            "operator_approval_required": True,
        },
        "expected_action": "escalate",
        "expected_final_status": "needs_info",  # escalate → needs_info
    },
]


def run_demo():
    """Run the Telegram operator approval flow demo."""
    print("=" * 60)
    print("TELEGRAM OPERATOR APPROVAL FLOW — DEMO")
    print(f"  Test mode: {is_test_mode()}")
    print(f"  Items: {len(DEMO_ITEMS)}")
    print("=" * 60)

    queue = ActionQueue()
    audit = AuditLog()
    results = []
    passed = 0

    for demo in DEMO_ITEMS:
        item_data = demo["item"]
        item_id = item_data["item_id"]
        print(f"\n--- {demo['name']} ---")
        print(f"  ID: {item_id}")

        # Step 1: Create queue item
        item = QueueItem(
            item_id=item_id,
            action_type=ActionType(item_data["action_type"]),
            suggested_text=item_data["suggested_text"],
            reason=item_data["reason"],
            operator_approval_required=True,
        )
        queue.add(item)

        # Step 2: Build notification
        enriched = item.to_dict()
        enriched.update({
            "classification": item_data.get("classification", "N/A"),
            "risk_level": item_data["risk_level"],
            "confidence": item_data["confidence"],
            "source": item_data.get("source", "unknown"),
            "missing_info": item_data.get("missing_info", []),
        })

        msg, keyboard = build_notification_message(enriched)
        print(f"  Notification message length: {len(msg)} chars")

        # Verify notification content
        assert item_data["risk_level"].upper() in msg, "Risk level not in notification"
        assert item_data["classification"] in msg, "Classification not in notification"
        assert item_id[:16] in msg, "Item ID not in notification"
        print(f"  [OK] Notification contains: classification, risk, item_id")

        # Verify keyboard has expected buttons
        buttons = [b["text"] for row in keyboard["inline_keyboard"] for b in row]
        expected_buttons = ["Approve", "Reject", "Edit", "Request Info", "Escalate", "Spam"]
        for btn in expected_buttons:
            assert any(btn in b for b in buttons), f"Missing button: {btn}"
        print(f"  [OK] All 6 inline buttons present: {', '.join(expected_buttons)}")

        # Step 3: Send notification (test mode)
        sent = send_notification(enriched)
        assert sent, "Notification send failed"
        print(f"  [OK] Notification sent (test mode): payload saved")

        # Step 4: Apply operator action
        action = demo["expected_action"]
        operator = "test_operator"

        if action == "approve":
            item.approve(operator)
            audit.record("telegram_approve", f"Item: {item_id}", new_state="approved", operator=operator)
        elif action == "reject":
            item.reject("Test rejection", operator)
            audit.record("telegram_reject", f"Item: {item_id}", new_state="rejected", operator=operator)
        elif action == "needs_info":
            item.mark_needs_info("Missing info flagged", operator)
            audit.record("telegram_needs_info", f"Item: {item_id}", new_state="needs_info", operator=operator)
        elif action == "escalate":
            item.mark_needs_info(f"Escalated by {operator}", operator)
            audit.record("telegram_escalate", f"Item: {item_id}", new_state="needs_info", operator=operator)

        # Step 5: Verify final status
        final_status = item.status.value
        expected = demo["expected_final_status"]
        assert final_status == expected, f"Status mismatch: expected {expected}, got {final_status}"
        print(f"  [OK] Status transition: pending → {final_status}")

        # Step 6: Safety rules
        if item_data["risk_level"] == "high":
            # High risk should NOT be approved for publish
            if action != "escalate":
                print(f"  [WARNING] High risk approved without escalation!")
            else:
                print(f"  [OK] High risk → escalated (not auto-published)")
        elif item_data["risk_level"] == "low":
            if action == "approve":
                print(f"  [OK] Low risk → approved (ready for manual FB publish)")

        # Step 7: Verify operator_approval_required remains True
        assert item.operator_approval_required, "Approval requirement removed!"
        print(f"  [OK] operator_approval_required = True (always)")

        results.append({
            "item_id": item_id,
            "name": demo["name"],
            "risk_level": item_data["risk_level"],
            "action_applied": action,
            "final_status": final_status,
            "notification_sent": sent,
            "passed": True,
        })
        passed += 1
        print(f"  PASSED")

    # Summary
    print(f"\n{'=' * 60}")
    print("DEMO COMPLETE")
    print(f"  Items processed: {len(DEMO_ITEMS)}")
    print(f"  Passed: {passed}/{len(DEMO_ITEMS)}")
    print(f"  Test payloads saved: {len(get_test_payloads())}")
    print(f"  Audit entries: {audit.count}")
    print(f"  No real Telegram send: True")
    print(f"  No Facebook action: True")
    print(f"{'=' * 60}")

    # Verify test payloads exist
    payloads = get_test_payloads()
    assert len(payloads) >= len(DEMO_ITEMS), f"Expected >= {len(DEMO_ITEMS)} test payloads, got {len(payloads)}"
    print(f"\nTest payloads verified: {len(payloads)} files in artifacts/test_telegram_payloads/")

    # Verify each payload has required fields
    for p in payloads[:len(DEMO_ITEMS)]:
        assert "text" in p, "Payload missing text"
        assert "reply_markup" in p, "Payload missing reply_markup"
        assert p["test_mode"] == True, "Payload not marked as test mode"
    print("All payloads have required fields: text, reply_markup, test_mode")

    return results, passed


if __name__ == "__main__":
    results, passed = run_demo()
    if passed != len(DEMO_ITEMS):
        print(f"\nFAIL: {len(DEMO_ITEMS) - passed} items failed")
        sys.exit(1)
    else:
        print(f"\nALL {passed}/{len(DEMO_ITEMS)} DEMO ITEMS PASSED")
        sys.exit(0)
