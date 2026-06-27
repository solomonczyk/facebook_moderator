"""TASK 017 — Persistent Queue tests."""

import sys, os, tempfile, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

passed = 0
failed = 0


def check(name: str, condition: bool, detail: str = ""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  [PASS] {name}")
    else:
        failed += 1
        print(f"  [FAIL] {name}: {detail}")


def run_tests():
    global passed, failed
    from app.runtime_agent.persistent_queue import PersistentQueueStore

    # Use temp file for clean test
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    try:
        # ── Create store ─────────────────────────────────────────────────
        store = PersistentQueueStore(db_path)
        check("store created", store is not None)

        # ── Add item ─────────────────────────────────────────────────────
        item = {
            "item_id": "q_test_001",
            "action_type": "publish_own_group_post",
            "status": "pending",
            "suggested_text": "Test job offer text",
            "reason": "Test reason",
            "operator_approval_required": True,
        }
        item_id = store.add(item)
        check("add returns item_id", item_id == "q_test_001")

        # ── Get item ─────────────────────────────────────────────────────
        got = store.get("q_test_001")
        check("get returns item", got is not None)
        check("item has correct action_type", got["action_type"] == "publish_own_group_post")
        check("item has pending status", got["status"] == "pending")
        check("item has suggested_text", got["suggested_text"] == "Test job offer text")
        check("operator_approval_required", got["operator_approval_required"] == True)

        # ── Update status → approved ────────────────────────────────────
        ok = store.update_status("q_test_001", "approved", "test_operator")
        check("update_status returns True", ok)
        got = store.get("q_test_001")
        check("status changed to approved", got["status"] == "approved")
        check("operator recorded", got["operator"] == "test_operator")

        # ── Update status → rejected ────────────────────────────────────
        store.update_status("q_test_001", "rejected", "op2", "Not good")
        got = store.get("q_test_001")
        check("status changed to rejected", got["status"] == "rejected")
        check("reason recorded", got["reason"] == "Not good")

        # ── Update status → needs_info ──────────────────────────────────
        store.update_status("q_test_001", "needs_info")
        got = store.get("q_test_001")
        check("status changed to needs_info", got["status"] == "needs_info")

        # ── Update status → spam ────────────────────────────────────────
        store.update_status("q_test_001", "spam", "op3", "Test spam")
        got = store.get("q_test_001")
        check("status changed to spam", got["status"] == "spam")

        # ── Edit text ───────────────────────────────────────────────────
        store.update_text("q_test_001", "Edited text content", "operator_editor")
        got = store.get("q_test_001")
        check("status is edited after text update", got["status"] == "edited")
        check("edited_text saved", got["edited_text"] == "Edited text content")

        # ── Unknown item ────────────────────────────────────────────────
        unknown = store.get("q_nonexistent")
        check("unknown item returns None", unknown is None)
        ok = store.update_status("q_nonexistent", "approved")
        check("update unknown returns False", not ok)

        # ── Multiple items ──────────────────────────────────────────────
        store.add({"item_id": "q_test_002", "status": "pending", "action_type": "reply_to_post"})
        store.add({"item_id": "q_test_003", "status": "approved", "action_type": "create_digest_post"})
        all_items = store.get_all()
        check("get_all returns list", isinstance(all_items, list))
        check("get_all count >= 3", len(all_items) >= 3)

        pending = store.get_all("pending")
        check("get_all pending filter works", len(pending) >= 1)
        check("pending item is q_test_002", any(i["item_id"] == "q_test_002" for i in pending))

        count = store.get_pending_count()
        check("get_pending_count >= 1", count >= 1)

        # ── RESTART SIMULATION ──────────────────────────────────────────
        store.close()
        store2 = PersistentQueueStore(db_path)
        got = store2.get("q_test_001")
        check("RESTART: item survives restart", got is not None)
        check("RESTART: status preserved after restart", got["status"] == "edited")
        check("RESTART: edited_text preserved", got["edited_text"] == "Edited text content")

        ok = store2.update_status("q_test_001", "approved", "post_restart_op")
        check("RESTART: update after restart works", ok)
        got = store2.get("q_test_001")
        check("RESTART: status after restart update", got["status"] == "approved")

        # ── All 4 status transitions ────────────────────────────────────
        transitions = ["approved", "rejected", "needs_info", "spam"]
        for i, t in enumerate(transitions):
            sid = f"q_trans_{i}"
            store2.add({"item_id": sid, "status": "pending", "action_type": "test"})
            store2.update_status(sid, t)
            g = store2.get(sid)
            check(f"transition to {t}", g["status"] == t)

        store2.close()

    finally:
        os.unlink(db_path)

    print(f"\n{'=' * 50}")
    print(f"RESULTS: {passed} passed, {failed} failed")
    print(f"{'=' * 50}")
    return failed == 0


if __name__ == "__main__":
    ok = run_tests()
    sys.exit(0 if ok else 1)
