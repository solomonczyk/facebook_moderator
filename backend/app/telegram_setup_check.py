"""Telegram setup check — verifies env vars without revealing secrets.

Usage: python -m app.telegram_setup_check
"""

import sys, os, json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.env_loader import load_env, _mask
load_env()  # Load .env from project root before checking vars


def mask(value: str) -> str:
    if not value or len(value) < 8:
        return "[NOT SET]"
    return value[:4] + "****" + value[-4:] if len(value) > 8 else "****"


def check() -> dict:
    from app.env_loader import load_env, _mask
    env_diag = load_env()

    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_OPERATOR_CHAT_ID", "")
    test_mode = os.getenv("TELEGRAM_TEST_MODE", "true").lower() == "true"
    allowed = os.getenv("TELEGRAM_ALLOWED_CHAT_IDS", "")

    results = {
        "env_file_found": env_diag["env_file_found"],
        "env_file_path": env_diag["env_file_path"],
        "bot_token_configured": bool(token and token != "REPLACE_ME"),
        "bot_token_masked": mask(token),
        "operator_chat_id_configured": bool(chat_id and chat_id != "REPLACE_ME"),
        "operator_chat_id_masked": mask(chat_id),
        "test_mode": test_mode,
        "can_real_send": not test_mode and bool(token) and bool(chat_id),
        "allowed_chat_ids": allowed if allowed else "(none — operator only)",
        "production_accepted": False,
        "checked_at": __import__("datetime").datetime.utcnow().isoformat(),
    }

    # Warnings
    warnings = []
    if not token or token == "REPLACE_ME":
        warnings.append("TELEGRAM_BOT_TOKEN not configured — real send impossible")
    if not chat_id or chat_id == "REPLACE_ME":
        warnings.append("TELEGRAM_OPERATOR_CHAT_ID not configured — real send impossible")
    if test_mode:
        warnings.append("TELEGRAM_TEST_MODE=true — all sends go to disk, not Telegram")
    if not test_mode and token and chat_id:
        warnings.append("Real send mode active — messages WILL be sent to operator")

    results["warnings"] = warnings

    return results


def main():
    print("=" * 55)
    print("TELEGRAM SETUP CHECK")
    print("=" * 55)

    r = check()
    print(f"  .env file:      {'FOUND' if r.get('env_file_found') else 'NOT FOUND'} ({r.get('env_file_path', '?')})")
    print(f"  Bot token:      {r['bot_token_masked']}")
    print(f"  Operator chat:  {r['operator_chat_id_masked']}")
    print(f"  Test mode:      {r['test_mode']}")
    print(f"  Can real send:  {r['can_real_send']}")
    print(f"  Allowed chats:  {r['allowed_chat_ids']}")

    for w in r["warnings"]:
        prefix = "WARNING" if "not configured" in w else "INFO"
        print(f"  [{prefix}] {w}")

    # Save sanitized output
    os.makedirs("artifacts", exist_ok=True)
    out = {k: v for k, v in r.items() if k != "warnings_raw"}
    with open("artifacts/telegram_setup_check.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"\nSanitized output: artifacts/telegram_setup_check.json")
    print("No secrets exposed.")


if __name__ == "__main__":
    main()
