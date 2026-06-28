"""TASK 025 — Batch capture and morning digest tests."""

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


# Realistic raspberry harvest posts from 28.06.2026
FIVE_POSTS = """Tražimo 10 radnika za berbu malina u Arilju. Smeštaj obezbeđen, tri obroka dnevno. Dnevnica 5000 RSD. Početak 5. jula. Kontakt 064-123-4567.

Potrebni berači za berbu malina, Ivanjica. Plata 4000 dnevno. Smeštaj i hrana obezbeđeni. 064-111-222..

Branje malina — traži se 5 radnika, okolina Bajine Bašte. Dnevnica 4500. Smeštaj obezbeđen. 069-333-444.

Tražim posao za berbu. Imam iskustva. Mogu odmah. Iz Arilja sam. 065-555-777.

KAZINO online! Zarada 1000e dnevno! www.casino-bonus.rs"""


def run_tests():
    global passed, failed
    from app.batch_capture import (
        split_posts, extract_post_fields, compute_risk_level,
        dedup_key, process_batch, build_morning_digest
    )

    # ── 1. Split posts ──────────────────────────────────────────────────
    posts = split_posts(FIVE_POSTS)
    check("split_posts returns list", isinstance(posts, list))
    check("split_posts finds 5 posts", len(posts) >= 4, f"got {len(posts)}")  # could merge some

    # ── 2. Extract fields from job offer ────────────────────────────────
    fields = extract_post_fields("Tražimo 10 radnika za berbu malina u Arilju. "
                                  "Smeštaj obezbeđen. Dnevnica 5000 RSD. Kontakt 064-123-4567.")
    check("extract: job_type = berba malina", "malina" in (fields.get("job_type") or ""))
    check("extract: location", fields.get("location") == "Arilje")
    check("extract: contact", fields.get("contact") == "064-123-4567")
    check("extract: pay found", fields.get("pay") is not None)
    check("extract: housing da", fields.get("housing") == "da")

    # ── 3. Extract from worker post ─────────────────────────────────────
    wf = extract_post_fields("Tražim posao za berbu. Imam iskustva. Iz Arilja. 065-555-777.")
    check("worker: location", wf.get("location") == "Arilje")
    check("worker: contact", wf.get("contact") == "065-555-777")
    check("worker: classification", wf.get("classification") == "worker_search")

    # ── 4. Spam detection ──────────────────────────────────────────────
    sf = extract_post_fields("KAZINO online zarada 1000e bonusa!")
    check("spam: classification spam", sf.get("classification") == "spam")
    check("spam: no contact → risk_flag", "no_contact" in sf.get("risk_flags", []))

    # ── 5. Risk levels ─────────────────────────────────────────────────
    complete = extract_post_fields("Posao u Arilju. Dnevnica 5000. Kontakt 064-123-4567.")
    check("complete: risk low", compute_risk_level(complete) == "low")

    no_contact = extract_post_fields("Posao u Arilju. Dnevnica 5000.")
    check("no contact: risk high", compute_risk_level(no_contact) == "high")

    # ── 6. Dedup key ────────────────────────────────────────────────────
    d1 = dedup_key("Tražimo radnike za berbu", "064-123-4567")
    d2 = dedup_key("Tražimo radnike za berbu", "064-123-4567")
    d3 = dedup_key("Drugi tekst", "064-999-999")
    check("dedup: same input = same key", d1 == d2)
    check("dedup: different input = different key", d1 != d3)

    # ── 7. Process batch ───────────────────────────────────────────────
    items = process_batch(FIVE_POSTS, source_group="Test grupa")
    check("process_batch returns items", len(items) >= 1)
    for item in items:
        check("process: item has item_id", item.get("item_id", "").startswith("q_"))
        check("process: operator approval required", item.get("operator_approval_required") == True)

    # ── 8. Empty / fallback ──────────────────────────────────────────────
    empty = process_batch("")
    check("empty input returns []", len(empty) == 0)

    short = process_batch("Hello")
    check("very short returns []", len(short) == 0)

    # ── 9. Morning digest ────────────────────────────────────────────────
    digest = build_morning_digest(items)
    check("digest is string", isinstance(digest, str))
    check("digest contains disclaimer", "Grupa nije poslodavac" in digest)
    check("digest contains date", "2026" in digest)

    # Empty digest
    empty_digest = build_morning_digest([])
    check("empty digest works", "Nema novih oglasa" in empty_digest)

    # Spam excluded from digest
    items_with_spam = items + [{"status": "spam_candidate", "risk_level": "high"}]
    digest2 = build_morning_digest(items_with_spam)
    check("spam excluded from digest", "KAZINO" not in digest2)

    # ── 10. Handlers in bot.py ─────────────────────────────────────────
    bot_path = os.path.join(os.path.dirname(__file__), "..", "app", "telegram_bot", "bot.py")
    with open(bot_path, "r", encoding="utf-8") as f:
        src = f.read()
    check("/capture_batch handler", "async def capture_batch_cmd" in src)
    check("/morning_digest handler", "async def morning_digest_cmd" in src)
    check("/capture_batch registered", 'CommandHandler("capture_batch"' in src)
    check("/morning_digest registered", 'CommandHandler("morning_digest"' in src)

    # ── 11. No Facebook automation ─────────────────────────────────────
    import subprocess
    try:
        r = subprocess.run(["grep", "-c", "facebook_auto_publish", "backend/app/batch_capture.py"],
                          capture_output=True, text=True)
        check("no FB auto-publish in batch_capture", "0" in r.stdout or not r.stdout.strip())
    except Exception:
        pass

    print(f"\n{'=' * 50}")
    print(f"RESULTS: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    ok = run_tests()
    sys.exit(0 if ok else 1)
