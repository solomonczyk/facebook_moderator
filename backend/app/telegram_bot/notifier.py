"""Queue notification dispatcher — auto-notifies operator on new queue items.

Supports test mode: saves notification payloads to disk instead of sending.
"""

import os, sys
import json
import logging
from datetime import datetime

# Ensure .env is loaded when notifier is imported
try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
    from app.env_loader import load_env
    load_env()
except ImportError:
    pass

logger = logging.getLogger("sezonski.telegram.notifier")

# Module-level test mode flag
_test_mode: bool | None = None


def is_test_mode() -> bool:
    """Check if Telegram test mode is active. Cached after first check."""
    global _test_mode
    if _test_mode is None:
        _test_mode = os.getenv("TELEGRAM_TEST_MODE", "true").lower() == "true"
        logger.info(f"Telegram test mode: {_test_mode}")
    return _test_mode


def get_token() -> str:
    return os.getenv("TELEGRAM_BOT_TOKEN", "").strip()


def get_chat_id() -> str:
    return os.getenv("TELEGRAM_OPERATOR_CHAT_ID", "").strip()


def is_available() -> bool:
    """Check if Telegram is available (token + chat_id configured)."""
    token = get_token()
    chat_id = get_chat_id()
    if not token or token == "REPLACE_ME":
        return False
    if not chat_id or chat_id == "REPLACE_ME":
        return False
    return True


def build_notification_message(item: dict) -> tuple[str, dict]:
    """Build a formatted notification message and inline keyboard for a queue item.

    Returns (message_text, keyboard_dict).
    """
    action_type = item.get("action_type", "unknown")
    classification = item.get("classification", "N/A")
    risk_level = item.get("risk_level", "N/A")
    confidence = item.get("confidence", 0.0)
    source = item.get("source", "unknown")
    suggested_text = item.get("suggested_text", "")[:300]
    reason = item.get("reason", "")
    missing = item.get("missing_info", [])
    item_id = item.get("item_id", "")

    # Emoji for action
    action_emoji = {
        "publish_own_group_post": "📰",
        "create_digest_post": "📌",
        "reply_to_comment": "💬",
        "reply_to_post": "📝",
        "ask_for_missing_info": "❓",
        "request_operator_review": "🔍",
        "save_worker_lead": "👷",
        "save_employer_lead": "🏢",
        "review_moderation_needed": "⚠️",
    }.get(action_type, "📋")

    # Risk emoji
    risk_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴"}.get(risk_level, "⚪")

    msg = (
        f"{action_emoji} <b>New Queue Item</b>\n\n"
        f"<b>Action:</b> {action_type.replace('_', ' ').title()}\n"
        f"<b>Classification:</b> <code>{classification}</code>\n"
        f"<b>Risk:</b> {risk_emoji} {risk_level.upper()}\n"
        f"<b>Confidence:</b> {confidence:.0%}\n"
        f"<b>Source:</b> {source}\n"
    )

    if reason:
        msg += f"\n<b>Reason:</b> {reason[:200]}\n"

    if missing:
        msg += f"\n<b>Missing:</b> {', '.join(missing[:5])}\n"

    if suggested_text:
        msg += f"\n<b>Suggested text:</b>\n{suggested_text[:300]}\n"

    msg += f"\nID: <code>{item_id[:16]}...</code>"

    # Build inline keyboard
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "✅ Approve", "callback_data": f"approve:{item_id}"},
                {"text": "❌ Reject", "callback_data": f"reject:{item_id}"},
            ],
            [
                {"text": "✏️ Edit", "callback_data": f"edit:{item_id}"},
                {"text": "❓ Request Info", "callback_data": f"needs_info:{item_id}"},
            ],
            [
                {"text": "⚠️ Escalate", "callback_data": f"escalate:{item_id}"},
                {"text": "🚫 Spam", "callback_data": f"mark_spam:{item_id}"},
            ],
        ]
    }

    # Safety: high risk items should have big warning
    if risk_level == "high":
        msg = "⚠️ <b>HIGH RISK ITEM</b> ⚠️\n" + msg

    return msg, keyboard


def send_notification(item: dict) -> bool:
    """Send a queue item notification to the operator.

    In test mode: saves payload to artifacts/test_telegram_payloads/.
    In real mode: sends via Telegram API.
    Returns True if notification was dispatched (or saved in test mode).
    """
    if not is_available() and not is_test_mode():
        logger.debug("Telegram not available and not in test mode — skipping notification")
        return False

    msg, keyboard = build_notification_message(item)
    item_id = item.get("item_id", "unknown")

    # ── PERSIST to SQLite BEFORE sending Telegram ──────────────────────
    _persist_item(item)

    if is_test_mode():
        return _save_test_payload(item_id, msg, keyboard)

    # Real send via Telegram API
    return _send_real(msg, keyboard)


def _persist_item(item: dict) -> None:
    """Save item to persistent SQLite queue before Telegram notification."""
    try:
        # Use absolute path for server compatibility
        db_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "persistent_queue.db"
        )
        db_path = os.path.abspath(db_path)

        from ..runtime_agent.persistent_queue import get_persistent_queue
        pq = get_persistent_queue(db_path)
        pq.add(item)
        logger.debug(f"Persisted item {item.get('item_id', '?')[:16]} to {db_path}")
    except Exception as e:
        logger.warning(f"Failed to persist item to SQLite: {e}")


def _save_test_payload(item_id: str, msg: str, keyboard: dict) -> bool:
    """Save notification payload to disk for test verification."""
    test_dir = "artifacts/test_telegram_payloads"
    os.makedirs(test_dir, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_id = item_id.replace("/", "_").replace("\\", "_")[:16]
    filepath = os.path.join(test_dir, f"notify_{safe_id}_{timestamp}.json")

    payload = {
        "item_id": item_id,
        "chat_id": get_chat_id() or "TEST_MODE",
        "text": msg,
        "parse_mode": "HTML",
        "reply_markup": keyboard,
        "test_mode": True,
        "saved_at": datetime.utcnow().isoformat(),
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    logger.info(f"[TEST MODE] Notification saved to {filepath}")
    return True


def _send_real(msg: str, keyboard: dict) -> bool:
    """Send real Telegram message to operator."""
    try:
        import httpx

        token = get_token()
        chat_id = get_chat_id()

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": msg,
            "parse_mode": "HTML",
            "reply_markup": json.dumps(keyboard),
        }

        resp = httpx.post(url, json=payload, timeout=10)
        if resp.status_code == 200:
            logger.info("Notification sent to operator")
            return True
        else:
            logger.error(f"Telegram send failed: {resp.status_code} {resp.text[:200]}")
            return False
    except Exception as e:
        logger.error(f"Telegram send error: {e}")
        return False


def get_test_payloads(limit: int = 20) -> list[dict]:
    """Retrieve saved test payloads for verification."""
    test_dir = "artifacts/test_telegram_payloads"
    if not os.path.isdir(test_dir):
        return []

    payloads = []
    for fname in sorted(os.listdir(test_dir), reverse=True)[:limit]:
        if fname.endswith(".json"):
            try:
                with open(os.path.join(test_dir, fname), "r", encoding="utf-8") as f:
                    payloads.append(json.load(f))
            except Exception:
                pass
    return payloads
