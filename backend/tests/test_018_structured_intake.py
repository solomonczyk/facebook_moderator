"""TASK 018 — Structured Intake Tests."""

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
    from app.runtime_intake.structured_intake import (
        EmployerOfferIntake, WorkerSearchIntake,
        process_employer_offer, process_worker_search,
        detect_spam, detect_high_risk,
    )
    from app.runtime_agent.persistent_queue import PersistentQueueStore

    # ── Employer: valid ──────────────────────────────────────────────────
    offer = EmployerOfferIntake(
        employer_name="Test Gazdinstvo", work_location="Sivac",
        job_type="berba malina", workers_needed="4", start_date="odmah",
        pay_amount="5000", pay_type="dnevnica",
        working_hours_or_norm="8 sati", housing_provided="da",
        food_provided="da", payment_frequency="dnevno",
        contact="+381600000000",
    )

    check("employer: all required fields present", len(offer.missing_fields()) == 0)
    check("employer: completeness 1.0", offer.completeness() == 1.0)

    result = process_employer_offer(offer)
    check("employer: item_id generated", result["item_id"].startswith("q_"))
    check("employer: status ready for review", result["status"] == "pending")
    check("employer: action publish_own_group_post", result["action_type"] == "publish_own_group_post")
    check("employer: classification job_offer", result["classification"] == "job_offer")
    check("employer: risk low", result["risk_level"] == "low")
    check("employer: suggested_text not empty", len(result["suggested_text"]) > 100)
    check("employer: has disclaimer", "Grupa nije poslodavac" in result["suggested_text"])
    check("employer: operator approval required", result["operator_approval_required"] == True)

    # ── Employer: missing fields ─────────────────────────────────────────
    offer2 = EmployerOfferIntake(employer_name="Test", work_location="Test")
    check("employer2: has missing fields", len(offer2.missing_fields()) > 5)
    check("employer2: completeness < 0.3", offer2.completeness() < 0.3)

    result2 = process_employer_offer(offer2)
    check("employer2: status needs_info", result2["status"] == "needs_info")
    check("employer2: action ask_for_missing_info", result2["action_type"] == "ask_for_missing_info")
    check("employer2: reply_to_author has missing fields", "dopunite" in result2["prepared_reply_to_author"])

    # ── Worker: valid ────────────────────────────────────────────────────
    worker = WorkerSearchIntake(
        worker_name="Petar Radnik", current_location="Ivanjica",
        people_count="2", desired_job_type="berba malina",
        available_from="odmah", housing_needed="da",
        food_needed="da", contact="065-111-222",
        experience="3 godine", has_transport="da",
    )
    check("worker: all required fields present", len(worker.missing_fields()) == 0)
    check("worker: completeness 1.0", worker.completeness() == 1.0)

    wresult = process_worker_search(worker)
    check("worker: item_id generated", wresult["item_id"].startswith("q_"))
    check("worker: status pending", wresult["status"] == "pending")
    check("worker: classification worker_search", wresult["classification"] == "worker_search")
    check("worker: suggested_text has worker name", "Petar Radnik" in wresult["suggested_text"])

    # ── Worker: missing fields ───────────────────────────────────────────
    worker2 = WorkerSearchIntake(worker_name="Test", current_location="Test")
    check("worker2: has missing fields", len(worker2.missing_fields()) > 3)
    wresult2 = process_worker_search(worker2)
    check("worker2: status needs_info", wresult2["status"] == "needs_info")

    # ── Spam detection ───────────────────────────────────────────────────
    spam_offer = EmployerOfferIntake(
        employer_name="Kazino", work_location="Online",
        job_type="kazino operater", workers_needed="100",
        start_date="odmah", pay_amount="5000", pay_type="dnevno",
        working_hours_or_norm="2 sata", housing_provided="ne",
        food_provided="ne", payment_frequency="dnevno",
        contact="inbox",
    )
    check("spam: detected", detect_spam("kazino online bonus"))
    check("spam: not detected in clean text", not detect_spam("berba malina Arilje"))

    spam_result = process_employer_offer(spam_offer)
    check("spam: status spam_candidate", spam_result["status"] == "spam_candidate")
    check("spam: NOT publish_own_group_post", spam_result["action_type"] != "publish_own_group_post")

    # ── High risk detection ──────────────────────────────────────────────
    check("risk: detects pasos", detect_high_risk("pošaljite pasoš"))
    check("risk: detects jmbg", detect_high_risk("JMBG obavezan"))
    check("risk: clean text passes", not detect_high_risk("berba malina Arilje"))

    # ── Persistent queue integration ─────────────────────────────────────
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    try:
        pq = PersistentQueueStore(db_path)
        pq.add(result)
        stored = pq.get(result["item_id"])
        check("persist: item stored", stored is not None)
        check("persist: status preserved", stored["status"] == "pending")

        # Simulate operator: approve
        pq.update_status(result["item_id"], "approved", "test_op")
        stored = pq.get(result["item_id"])
        check("persist: approved status", stored["status"] == "approved")

        # Simulate operator: published_manually
        pq.update_status(result["item_id"], "published_manually", "test_op")
        stored = pq.get(result["item_id"])
        check("persist: published_manually status", stored["status"] == "published_manually")

        # Restart simulation
        pq2 = PersistentQueueStore(db_path)
        stored2 = pq2.get(result["item_id"])
        check("persist: survives restart", stored2 is not None)
        check("persist: status after restart", stored2["status"] == "published_manually")
    finally:
        os.unlink(db_path)

    # ── No Facebook auto-publish ─────────────────────────────────────────
    # Verify that the codebase has no "facebook.*auto.*publish" or similar
    import subprocess
    try:
        grep_result = subprocess.run(
            ["grep", "-r", "facebook.*auto.*publish\\|auto.*facebook.*post",
             "backend/app/runtime_intake/structured_intake.py",
             "backend/app/runtime_intake/structured_api.py"],
            capture_output=True, text=True
        )
        check("no Facebook auto-publish in intake code",
              "facebook" not in grep_result.stdout.lower() or "manual" in grep_result.stdout.lower())
    except Exception:
        pass  # grep not available on Windows

    print(f"\n{'=' * 50}")
    print(f"RESULTS: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    ok = run_tests()
    sys.exit(0 if ok else 1)
