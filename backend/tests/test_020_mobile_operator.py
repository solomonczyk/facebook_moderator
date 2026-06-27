"""TASK 020 — Mobile Operator Support Mode tests."""

import sys, os
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

    # ── Command handlers defined in bot.py ───────────────────────────────
    bot_path = os.path.join(os.path.dirname(__file__), "..", "app", "telegram_bot", "bot.py")
    with open(bot_path, "r", encoding="utf-8") as f:
        src = f.read()

    commands = ["reply", "fb_post", "fb_comment", "fb_question", "fb_review",
                "fb_member", "capture", "today", "links", "evening",
                "digest_next", "fb_help"]
    for cmd in commands:
        check(f"/{cmd} handler defined", f"async def {cmd}_cmd" in src or f"async def {cmd}_cmd" in src)
        check(f"/{cmd} registered", f'CommandHandler("{cmd}"' in src)

    # ── /reply classification ────────────────────────────────────────────
    from app.operator_mvp.mvp_api import _classify_rule_based

    cls_spam, _ = _classify_rule_based("ONLINE KAZINO! 500e bonusa!")
    check("/reply detects spam", cls_spam == "spam")

    cls_job, _ = _classify_rule_based("Tražimo 5 radnika za berbu malina Arilje")
    check("/reply detects job_offer", cls_job == "job_offer")

    cls_worker, _ = _classify_rule_based("Tražim posao u poljoprivredi")
    check("/reply detects worker_search", cls_worker == "worker_search")

    cls_warn, _ = _classify_rule_based("Čuvajte se poslodavca iz Surčina! Ne plaća!")
    check("/reply detects warning", cls_warn == "employer_warning")

    # ── Persistent queue integration ─────────────────────────────────────
    import tempfile
    from app.runtime_agent.persistent_queue import PersistentQueueStore
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        pq = PersistentQueueStore(db_path)
        import uuid
        iid = f"q_{uuid.uuid4().hex[:12]}"
        pq.add({"item_id": iid, "status": "pending",
                "action_type": "request_operator_review",
                "raw_json": {"source_type": "fb_post_manual", "classification": "job_offer"}})
        got = pq.get(iid)
        check("captured item stored", got is not None)
        check("captured item has source_type", "fb_post_manual" in str(got.get("raw_json", {})))

        # External capture
        iid2 = f"q_{uuid.uuid4().hex[:12]}"
        pq.add({"item_id": iid2, "status": "pending",
                "action_type": "request_operator_review",
                "raw_json": {"source_type": "external_group_capture"}})
        # Simulate /digest_next filtering
        all_items = pq.get_all()
        captures = [i for i in all_items
                    if "external_group_capture" in str(i.get("raw_json", {}).get("source_type", ""))
                    or "fb_post_manual" in str(i.get("raw_json", {}).get("source_type", ""))]
        check("/digest_next finds captures", len(captures) >= 2)
        pq.close()
    finally:
        os.unlink(db_path)

    # ── No Facebook auto-publish ─────────────────────────────────────────
    check("no FB auto-publish in bot source",
          "facebook_auto_post" not in src or "False" in src.split("facebook_auto_post")[1][:30])

    print(f"\n{'=' * 50}")
    print(f"RESULTS: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    ok = run_tests()
    sys.exit(0 if ok else 1)
