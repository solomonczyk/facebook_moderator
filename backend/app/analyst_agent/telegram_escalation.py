"""Telegram escalation: sends risky/high-confidence items to operator for review."""

import os
import logging

logger = logging.getLogger("sezonski.analyst.escalation")

TELEGRAM_AVAILABLE = False
try:
    import httpx
    TELEGRAM_AVAILABLE = True
except ImportError:
    pass


def _get_bot_token() -> str:
    return os.getenv("TELEGRAM_BOT_TOKEN", "").strip()


def _get_operator_chat_id() -> str:
    return os.getenv("TELEGRAM_OPERATOR_CHAT_ID", "").strip()


def send_escalation(decision_result: dict) -> bool:
    """Send an escalation card to the operator via Telegram."""
    token = _get_bot_token()
    chat_id = _get_operator_chat_id()

    if not token or not chat_id or token == "REPLACE_ME":
        logger.info("Telegram escalation skipped: token/chat_id not configured")
        return False

    if not TELEGRAM_AVAILABLE:
        logger.warning("httpx not available for Telegram escalation")
        return False

    action = decision_result.get("action", "unknown")
    confidence = decision_result.get("confidence", 0)
    risk = decision_result.get("risk_level", "medium")
    reasoning = decision_result.get("reasoning", "")
    item_id = decision_result.get("queue_item_id", "")[:16]

    risk_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴", "reject": "⛔"}.get(risk, "⚪")

    message = (
        f"{risk_emoji} *Analyst Escalation*\n\n"
        f"Action: `{action}`\n"
        f"Risk: {risk} | Confidence: {confidence:.0%}\n"
        f"Item: `{item_id}...`\n\n"
        f"_{reasoning}_\n\n"
        f"Use /queue to review and approve/reject."
    )

    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        resp = httpx.post(url, json={
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown",
        }, timeout=10)
        return resp.status_code == 200
    except Exception as e:
        logger.error(f"Telegram escalation failed: {e}")
        return False


def send_analyst_summary(summary: dict) -> bool:
    """Send daily analyst summary to operator."""
    token = _get_bot_token()
    chat_id = _get_operator_chat_id()
    if not token or not chat_id or token == "REPLACE_ME":
        return False

    message = (
        f"🤖 *Analyst Daily Summary*\n\n"
        f"Processed: {summary.get('processed', 0)}\n"
        f"Autonomous: {summary.get('executed', 0)}\n"
        f"Escalated: {summary.get('escalated', 0)}\n"
        f"Blocked: {summary.get('blocked', 0)}"
    )

    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        resp = httpx.post(url, json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}, timeout=10)
        return resp.status_code == 200
    except Exception:
        return False
