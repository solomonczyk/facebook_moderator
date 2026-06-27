"""TASK 019 — Telegram Commands + Dry-Run Tests."""

import sys, os, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

passed = 0
failed = 0

def check(name, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1; print(f"  [PASS] {name}")
    else:
        failed += 1; print(f"  [FAIL] {name}: {detail}")


def run_tests():
    global passed, failed

    # ── /forms /drafts /spam handlers exist in bot.py ────────────────────
    import inspect
    bot_path = os.path.join(os.path.dirname(__file__), "..", "app", "telegram_bot", "bot.py")
    with open(bot_path, "r", encoding="utf-8") as f:
        bot_source = f.read()
    check("/forms handler defined in bot.py", "async def forms_cmd" in bot_source)
    check("/drafts handler defined in bot.py", "async def drafts_cmd" in bot_source)
    check("/spam handler defined in bot.py", "async def spam_cmd" in bot_source)
    check("/forms registered as handler", "CommandHandler(\"forms\"" in bot_source)
    check("/drafts registered as handler", "CommandHandler(\"drafts\"" in bot_source)
    check("/spam registered as handler", "CommandHandler(\"spam\"" in bot_source)

    # ── Persistent queue filtering for /drafts ────────────────────────────
    from app.runtime_agent.persistent_queue import PersistentQueueStore
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    try:
        pq = PersistentQueueStore(db_path)

        # Add items in different states
        pq.add({"item_id": "q_draft_001", "status": "pending",
                 "action_type": "publish_own_group_post",
                 "suggested_text": "Test draft 1 — employer offer"})
        pq.add({"item_id": "q_draft_002", "status": "approved",
                 "action_type": "publish_own_group_post",
                 "suggested_text": "Test draft 2 — worker search"})
        pq.add({"item_id": "q_spam_001", "status": "spam_candidate",
                 "action_type": "request_operator_review",
                 "suggested_text": "SPAM: kazino online"})
        pq.add({"item_id": "q_pending_misc", "status": "pending",
                 "action_type": "ask_for_missing_info",
                 "suggested_text": "Missing info item"})

        # /drafts: should find publish_own_group_post items in pending/approved
        pending = pq.get_all("pending")
        approved = pq.get_all("approved")
        drafts = [i for i in pending + approved
                  if i.get("action_type") == "publish_own_group_post"]
        check("/drafts finds pending publish item", len(drafts) >= 1)
        check("/drafts finds approved publish item",
              any(d["item_id"] == "q_draft_002" for d in drafts))

        # /spam: spam_candidate items
        spam_items = pq.get_all("spam_candidate") + pq.get_all("spam")
        check("/spam finds spam_candidate", len(spam_items) >= 1)
        check("/spam does NOT include normal items",
              not any(s["item_id"] == "q_draft_001" for s in spam_items))

        # Pending count for /queue
        pending_count = pq.get_pending_count()
        check("pending count > 0", pending_count >= 1)

        pq.close()
    finally:
        os.unlink(db_path)

    # ── Structured intake produces item ───────────────────────────────────
    from app.runtime_intake.structured_intake import (
        EmployerOfferIntake, process_employer_offer,
        WorkerSearchIntake, process_worker_search,
    )

    offer = EmployerOfferIntake(
        employer_name="Test", work_location="Sivac", job_type="berba malina",
        workers_needed="4", start_date="odmah", pay_amount="5000",
        pay_type="dnevnica", working_hours_or_norm="8h", housing_provided="da",
        food_provided="da", payment_frequency="dnevno", contact="+381600000000",
    )
    result = process_employer_offer(offer)
    check("employer offer: item_id", result["item_id"].startswith("q_"))
    check("employer offer: status pending", result["status"] == "pending")
    check("employer offer: not spam", result["status"] != "spam_candidate")

    worker = WorkerSearchIntake(
        worker_name="Marko", current_location="Ivanjica", people_count="3",
        desired_job_type="berba", available_from="odmah", housing_needed="da",
        food_needed="da", contact="065-111-222",
    )
    wresult = process_worker_search(worker)
    check("worker search: item_id", wresult["item_id"].startswith("q_"))
    check("worker search: status pending", wresult["status"] == "pending")

    # ── No Facebook automation in code ───────────────────────────────────
    import subprocess
    try:
        r = subprocess.run(
            ["grep", "-r", "facebook.*auto.*publish\\|auto.*facebook.*post",
             "backend/app/telegram_bot/", "backend/app/runtime_intake/structured_api.py"],
            capture_output=True, text=True
        )
        check("no FB auto-publish in Telegram/intake code",
              "facebook_auto_post_enabled" not in r.stdout or "False" in r.stdout)
    except Exception:
        pass

    print(f"\n{'=' * 50}")
    print(f"RESULTS: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    ok = run_tests()
    sys.exit(0 if ok else 1)
