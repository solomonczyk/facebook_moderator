"""TASK 023 — Image Post Generator tests."""

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
    from app.image_poster import generate_image_post, generate_image_pack, PILLOW_AVAILABLE

    check("Pillow available", PILLOW_AVAILABLE)

    # Generate from simple text
    img = generate_image_post("Test text only")
    check("image generated", img is not None)
    check("is PNG bytes", img[:4] == b'\x89PNG' if img else False)
    check("PNG size > 1KB", len(img) > 1000 if img else False)

    # Generate from Serbian text
    sr_text = "Tražimo 5 radnika za berbu malina, Arilje, dnevnica 5000 RSD, smeštaj i hrana obezbeđeni."
    img2 = generate_image_post(sr_text)
    check("Serbian text generates", img2 is not None)
    check("Serbian PNG > 1KB", len(img2) > 1000 if img2 else False)

    # Generate from long text
    long_text = (
        "Poslodavac: Gazdinstvo Petrović. Mesto rada: Arilje. "
        "Vrsta posla: berba malina. Potrebno: 5 radnika. "
        "Dnevnica: 5000 RSD. Radno vreme: 8h dnevno. "
        "Smeštaj: obezbeđen. Hrana: 3 obroka. "
        "Prevoz: organizovan. Početak: 1. jul. "
        "Kontakt: 064-123-4567. Prijava: obavezna."
    )
    img3 = generate_image_post(long_text)
    check("long text generates", img3 is not None)
    check("long PNG > 1KB", len(img3) > 1000 if img3 else False)

    # Check text shortening
    very_long = "word " * 500
    from app.image_poster import _shorten_text
    shortened = _shorten_text(very_long, 200)
    check("shorten reduces length", len(shortened) < len(very_long))
    check("shorten keeps ending with ...", shortened.endswith("...") or len(shortened) == 200)

    # Generating from empty text
    img4 = generate_image_post("")
    check("empty text doesn't crash", img4 is None or len(img4) > 0)

    # Image pack from items
    items = [
        {"suggested_text": "Job offer 1", "risk_level": "low", "status": "approved"},
        {"suggested_text": "Job offer 2", "risk_level": "low", "status": "pending"},
        {"suggested_text": "High risk", "risk_level": "high", "status": "pending"},
    ]
    packs = generate_image_pack(items, max_cards=3)
    check("imagepack excludes high risk", len(packs) <= 2)  # third is high risk
    check("imagepack includes safe items", len(packs) >= 1)
    for p in packs:
        check("pack item is PNG", p[:4] == b'\x89PNG', str(p[:4]) if p else "None")

    # Verify handlers exist in bot.py
    bot_path = os.path.join(os.path.dirname(__file__), "..", "app", "telegram_bot", "bot.py")
    with open(bot_path, "r", encoding="utf-8") as f:
        src = f.read()
    check("/imagepost handler defined", "async def imagepost_cmd" in src)
    check("/imagepack handler defined", "async def imagepack_cmd" in src)
    check("/imagepost registered", 'CommandHandler("imagepost"' in src)
    check("/imagepack registered", 'CommandHandler("imagepack"' in src)

    # No FB automation
    poster_path = os.path.join(os.path.dirname(__file__), "..", "app", "image_poster.py")
    if os.path.exists(poster_path):
        poster_src = open(poster_path, encoding="utf-8").read().lower()
        check("no FB auto-publish in image_poster",
              "facebook" not in poster_src or "no facebook" in poster_src)
    else:
        check("image_poster.py exists", os.path.exists(poster_path))

    print(f"\n{'=' * 50}")
    print(f"RESULTS: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    ok = run_tests()
    sys.exit(0 if ok else 1)
