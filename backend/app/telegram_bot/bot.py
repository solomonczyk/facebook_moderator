"""Telegram bot for mobile operator approval of runtime action queue items.

Uses polling mode. Backend stays on 127.0.0.1. No public webhook required.
"""

import os
import logging
from datetime import datetime

logger = logging.getLogger("sezonski.telegram")

# Suppress httpx URL logging — prevents token leakage in journal
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

# Optional import — bot is active only when token is configured
try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import (
        Application, CommandHandler, CallbackQueryHandler, ContextTypes,
    )
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False


# ── Auth ────────────────────────────────────────────────────────────────────

def _get_operator_chat_id() -> str:
    return os.getenv("TELEGRAM_OPERATOR_CHAT_ID", "")


def _is_operator(update: Update) -> bool:
    chat_id = str(update.effective_chat.id) if update.effective_chat else ""
    allowed = _get_operator_chat_id()
    return chat_id == allowed


async def _reject_unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat:
        logger.warning(f"Rejected unknown chat_id: {update.effective_chat.id}")
    await update.message.reply_text("Access denied.")


# ── Queue Helpers ───────────────────────────────────────────────────────────

def _get_queue():
    """Get the runtime agent queue from the bot's application context."""
    import sys
    return sys.modules.get("app.telegram_bot.bot", {})


# We store agent reference at module level (set during init)
_runtime_agent = None


def set_runtime_agent(agent):
    global _runtime_agent
    _runtime_agent = agent


def _get_agent():
    return _runtime_agent


def _format_queue_card(item: dict, index: int) -> str:
    action_type = item.get("action_type", "unknown")
    suggested = item.get("suggested_text", "")[:300]
    item_id = item.get("item_id", "")

    emoji = {
        "reply_to_comment": "💬",
        "reply_to_post": "📝",
        "create_digest_post": "📌",
        "publish_own_group_post": "📰",
        "ask_for_missing_info": "❓",
        "request_operator_review": "🔍",
        "review_moderation_needed": "⚠️",
    }.get(action_type, "📋")

    return (
        f"{emoji} *{action_type.replace('_', ' ').title()}*\n"
        f"ID: `{item_id[:16]}...`\n"
        f"{suggested}\n"
    )


def _build_inline_keyboard(item_id: str) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"approve:{item_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject:{item_id}"),
        ],
        [
            InlineKeyboardButton("✏️ Edit", callback_data=f"edit:{item_id}"),
            InlineKeyboardButton("✅ Executed", callback_data=f"mark_executed:{item_id}"),
        ],
        [
            InlineKeyboardButton("🔒 Closed", callback_data=f"mark_closed:{item_id}"),
            InlineKeyboardButton("📋 Duplicate", callback_data=f"mark_duplicate:{item_id}"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


# ── Command Handlers ────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_operator(update):
        await _reject_unknown(update, context)
        return
    await update.message.reply_text(
        "🤖 *Sezonski Runtime Agent*\n\n"
        "Mobile approval bot ready.\n\n"
        "Commands:\n"
        "/status — Runtime health\n"
        "/queue — Pending action items\n"
        "/digest — Generate daily digest draft\n"
        "/help — This message",
        parse_mode="Markdown",
    )


async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_operator(update):
        await _reject_unknown(update, context)
        return

    agent = _get_agent()
    if not agent:
        await update.message.reply_text("Runtime agent not initialized.")
        return

    agent_status = agent.get_status()
    qs = agent_status.get("queue_summary", {})
    cfg = agent_status.get("config", {})

    msg = (
        "📊 *Sezonski Runtime Agent*\n\n"
        f"Runtime: ok\n"
        f"Queue pending: {qs.get('total_pending', 0)}\n"
        f"Pending replies: {qs.get('pending_replies', 0)}\n"
        f"Pending posts: {qs.get('pending_posts', 0)}\n"
        f"Audit entries: {agent_status.get('audit_entries', 0)}\n\n"
        "*Safety Gates:*\n"
        f"Telegram approval: enabled\n"
        f"Facebook auto-post: {cfg.get('facebook_auto_post_enabled', False)}\n"
        f"Facebook auto-comment: {cfg.get('facebook_auto_comment_enabled', False)}\n"
        f"Facebook auto-message: {cfg.get('facebook_auto_message_enabled', False)}\n"
        f"Account worker: {cfg.get('facebook_account_worker_enabled', False)}\n"
        f"Backend public: false (127.0.0.1)\n"
        f"Production: {cfg.get('production_accepted', False)}"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")


async def queue_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_operator(update):
        await _reject_unknown(update, context)
        return

    agent = _get_agent()
    if not agent:
        await update.message.reply_text("Runtime agent not initialized.")
        return

    pending = agent.queue.get_all()
    if not pending:
        await update.message.reply_text("✅ No pending items in queue.")
        return

    await update.message.reply_text(f"📋 *{len(pending)} pending item(s)*", parse_mode="Markdown")

    for i, item in enumerate(pending[:5]):  # Max 5 cards per message
        card = _format_queue_card(item.to_dict(), i)
        keyboard = _build_inline_keyboard(item.item_id)
        await update.message.reply_text(card, parse_mode="Markdown", reply_markup=keyboard)


async def digest_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_operator(update):
        await _reject_unknown(update, context)
        return

    agent = _get_agent()
    if not agent:
        await update.message.reply_text("Runtime agent not initialized.")
        return

    result = agent.run_daily_digest()
    if result.get("success"):
        preview = result.get("digest_preview", "")[:500]
        await update.message.reply_text(
            f"📌 *Digest draft created*\nQueue ID: `{result.get('queue_item_id', '?')}`\n\n{preview}",
            parse_mode="Markdown",
        )
    else:
        await update.message.reply_text(f"Digest not run: {result.get('reason', 'unknown')}")


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_operator(update):
        await _reject_unknown(update, context)
        return
    await update.message.reply_text(
        "/status — Runtime health & gates\n"
        "/queue — Pending action items with approve/reject buttons\n"
        "/digest — Generate daily digest draft\n"
        "/help — This help"
    )


# ── Callback Handlers ──────────────────────────────────────────────────────

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query:
        return

    if not _is_operator(update):
        await query.answer("Access denied.")
        return

    data = query.data or ""
    await query.answer()

    agent = _get_agent()
    if not agent:
        await query.edit_message_text("Runtime agent not initialized.")
        return

    try:
        action, item_id = data.split(":", 1)
    except ValueError:
        await query.edit_message_text(f"Invalid action: {data}")
        return

    item = agent.queue.get(item_id)
    if not item:
        await query.edit_message_text(f"Queue item not found: {item_id}")
        return

    operator = update.effective_user.username or str(update.effective_chat.id)

    if action == "approve":
        item.approve(operator)
        agent.audit.record("telegram_approve", f"Item: {item_id}", new_state="approved", operator=operator)
        await query.edit_message_text(f"✅ Approved\nID: `{item_id[:16]}...`", parse_mode="Markdown")

    elif action == "reject":
        item.reject("Rejected from Telegram", operator)
        agent.audit.record("telegram_reject", f"Item: {item_id}", new_state="rejected", operator=operator)
        await query.edit_message_text(f"❌ Rejected\nID: `{item_id[:16]}...`", parse_mode="Markdown")

    elif action == "mark_executed":
        item.mark_executed(operator)
        agent.audit.record("telegram_executed", f"Item: {item_id}", new_state="executed_manually", operator=operator)
        await query.edit_message_text(f"✅ Executed manually\nID: `{item_id[:16]}...`", parse_mode="Markdown")

    elif action == "mark_closed":
        item.status = type(item.status)("cancelled")
        agent.audit.record("telegram_closed", f"Item: {item_id}", new_state="cancelled", operator=operator)
        await query.edit_message_text(f"🔒 Closed\nID: `{item_id[:16]}...`", parse_mode="Markdown")

    elif action == "mark_duplicate":
        agent.audit.record("telegram_marked_duplicate", f"Item: {item_id}", operator=operator)
        await query.edit_message_text(f"📋 Marked duplicate\nID: `{item_id[:16]}...`", parse_mode="Markdown")

    elif action == "edit":
        await query.edit_message_text(
            f"✏️ Edit requested for `{item_id[:16]}...`\n"
            "Use operator console or API to edit the suggested text.",
            parse_mode="Markdown",
        )

    else:
        await query.edit_message_text(f"Unknown action: {action}")


# ── Bot Runner ──────────────────────────────────────────────────────────────

_bot_app: Application | None = None


def start_bot():
    """Start Telegram bot in polling mode. Runs in a background thread."""
    global _bot_app

    if not TELEGRAM_AVAILABLE:
        logger.warning("python-telegram-bot not installed. Telegram bot disabled.")
        return None

    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token or token == "REPLACE_ME":
        logger.warning("TELEGRAM_BOT_TOKEN not configured. Telegram bot disabled.")
        return None

    chat_id = _get_operator_chat_id()
    if not chat_id or chat_id == "REPLACE_ME":
        logger.warning("TELEGRAM_OPERATOR_CHAT_ID not configured. Telegram bot disabled.")
        return None

    logger.info(f"Starting Telegram bot in polling mode. Operator chat_id: {chat_id}")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status_cmd))
    app.add_handler(CommandHandler("queue", queue_cmd))
    app.add_handler(CommandHandler("digest", digest_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CallbackQueryHandler(handle_callback))

    import threading, asyncio
    def run_polling():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        logger.info("Telegram bot polling started")
        loop.run_until_complete(app.initialize())
        loop.run_until_complete(app.updater.start_polling(drop_pending_updates=True))
        loop.run_until_complete(app.start())
        loop.run_forever()

    thread = threading.Thread(target=run_polling, daemon=True, name="telegram-bot")
    thread.start()

    _bot_app = app
    return app


def stop_bot():
    global _bot_app
    if _bot_app:
        _bot_app.stop()
        _bot_app = None
        logger.info("Telegram bot stopped")
