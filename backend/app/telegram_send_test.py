"""Telegram real send test — sends one safe message to operator.

Usage:
    python -m app.telegram_send_test              # dry-run (safe)
    python -m app.telegram_send_test --real       # real send (requires env)
"""

import sys, os, json, argparse
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.env_loader import load_env; load_env()

TEST_MESSAGE = "FB Moderator: Telegram operator channel connected. Test message only. Operator approval flow ready."


def send_test(real: bool = False) -> dict:
    from app.telegram_bot.notifier import is_test_mode, is_available, get_token, get_chat_id

    if real and is_test_mode():
        return {"sent": False, "error": "TELEGRAM_TEST_MODE=true blocks real send. Set TELEGRAM_TEST_MODE=false."}

    if real and not is_available():
        return {"sent": False, "error": "TELEGRAM_BOT_TOKEN or TELEGRAM_OPERATOR_CHAT_ID not configured."}

    if not real:
        # Dry run — save payload
        test_dir = "artifacts/test_telegram_payloads"
        os.makedirs(test_dir, exist_ok=True)
        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(test_dir, f"test_message_{ts}.json")
        payload = {
            "chat_id": get_chat_id() or "[NOT SET]",
            "text": TEST_MESSAGE,
            "parse_mode": "Markdown",
            "test_mode": True,
            "dry_run": True,
            "saved_at": datetime.utcnow().isoformat(),
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        return {"sent": False, "dry_run": True, "payload_path": filepath, "message": TEST_MESSAGE[:50] + "..."}

    # Real send — single message to operator only
    import httpx
    token = get_token()
    chat_id = get_chat_id()
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    try:
        resp = httpx.post(url, json={
            "chat_id": chat_id,
            "text": TEST_MESSAGE,
            "parse_mode": "Markdown",
        }, timeout=10)
        ok = resp.status_code == 200
        return {
            "sent": ok,
            "real": True,
            "http_status": resp.status_code,
            "chat_id_masked": chat_id[:4] + "****" if len(chat_id) > 4 else "****",
            "message": TEST_MESSAGE[:50] + "...",
            "sent_at": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        return {"sent": False, "real": True, "error": str(e)}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--real", action="store_true")
    args = p.parse_args()

    print("=" * 55)
    print("TELEGRAM SEND TEST")
    print(f"  Mode: {'REAL' if args.real else 'DRY RUN'}")
    print("=" * 55)

    result = send_test(real=args.real)

    if result.get("dry_run"):
        print(f"  Dry run — payload saved to: {result['payload_path']}")
        print(f"  Message: {result['message']}")
    elif result["sent"]:
        print(f"  SENT to operator chat {result.get('chat_id_masked', '****')}")
        print(f"  HTTP {result['http_status']}")
        print(f"  Message: {result['message']}")
    else:
        print(f"  NOT SENT: {result.get('error', 'unknown error')}")

    print(f"  No Facebook actions. production_accepted=false.")
    print(f"  No secrets exposed.")

    os.makedirs("artifacts", exist_ok=True)
    out = {k: v for k, v in result.items()}
    with open("artifacts/telegram_send_test_result.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False, default=str)


if __name__ == "__main__":
    main()
