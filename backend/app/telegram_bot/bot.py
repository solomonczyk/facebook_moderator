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
        Application, CommandHandler, CallbackQueryHandler, MessageHandler,
        filters, ContextTypes,
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
            InlineKeyboardButton("✅ Executed", callback_data=f"mark_executed:{item_id}"),
            InlineKeyboardButton("❓ Needs Info", callback_data=f"needs_info:{item_id}"),
        ],
        [
            InlineKeyboardButton("🚫 Spam", callback_data=f"mark_spam:{item_id}"),
            InlineKeyboardButton("📋 Duplicate", callback_data=f"mark_duplicate:{item_id}"),
        ],
        [
            InlineKeyboardButton("🔒 Closed", callback_data=f"mark_closed:{item_id}"),
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

    from ..runtime_agent.action_queue import QueueStatus
    pending = agent.queue.get_all(QueueStatus.PENDING)
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


async def addlead_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_operator(update):
        await _reject_unknown(update, context)
        return

    text = update.message.text or ""
    # Remove the /addlead command prefix
    lead_text = text.removeprefix("/addlead").strip()
    if not lead_text:
        await update.message.reply_text(
            "Usage: /addlead <text>\n\n"
            "Example:\n"
            "/addlead Tražimo 5 radnika za berbu malina Arilje, smeštaj i hrana, 064-123-4567"
        )
        return

    # Send to runtime manager
    try:
        from ..agents.facebook_runtime_manager import FacebookGroupRuntimeManagerAgent
        manager = FacebookGroupRuntimeManagerAgent()
        decision = manager.analyze({
            "source_type": "telegram_lead",
            "source_label": "Telegram /addlead",
            "raw_text": lead_text,
            "operator_note": f"From Telegram, operator: {update.effective_user.username or 'unknown'}",
        })

        msg = (
            f"📌 *Lead analyzed*\n\n"
            f"Classification: `{decision.classification}`\n"
            f"Risk: {decision.risk_level} | Confidence: {decision.confidence:.0%}\n"
            f"Action: `{decision.recommended_action}`\n"
            f"Digest candidate: {'Yes' if decision.digest_candidate else 'No'}\n\n"
            f"*Operator summary:*\n{decision.operator_summary}\n\n"
            f"*Prepared FB text:*\n{decision.prepared_public_text[:500]}\n\n"
            f"*Missing:* {', '.join(decision.missing_info) if decision.missing_info else 'none'}"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"Error analyzing lead: {e}")


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_operator(update):
        await _reject_unknown(update, context)
        return
    await update.message.reply_text(
        "/status — Runtime health & gates\n"
        "/queue — Pending action items with buttons\n"
        "/digest — Generate daily digest draft\n"
        "/addlead <text> — Analyze a lead from text\n"
        "/forms — Structured intake forms\n"
        "/drafts — Pending manual-publish drafts\n"
        "/spam — Spam quarantine items\n"
        "/help — This help"
    )


# ── /forms — structured intake links ─────────────────────────────────────

async def forms_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_operator(update):
        await _reject_unknown(update, context)
        return
    await update.message.reply_text(
        "📋 *Strukturirani unos*\n\n"
        "*Za poslodavce:*\n"
        "`POST /api/intake/employer-offer`\n"
        "Obavezna polja: employer_name, work_location, job_type, workers_needed, "
        "start_date, pay_amount, pay_type, working_hours_or_norm, "
        "housing_provided, food_provided, payment_frequency, contact\n\n"
        "*Za radnike:*\n"
        "`POST /api/intake/worker-search`\n"
        "Obavezna polja: worker_name, current_location, people_count, "
        "desired_job_type, available_from, housing_needed, food_needed, contact\n\n"
        "Primer:\n"
        "`curl -X POST http://127.0.0.1:8000/api/intake/employer-offer "
        "-H \"Content-Type: application/json\" "
        "-d '{\"employer_name\":\"Test\",\"work_location\":\"Sivac\",...}'`",
        parse_mode="Markdown",
    )


# ── /drafts — pending manual-publish items ────────────────────────────────

async def drafts_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_operator(update):
        await _reject_unknown(update, context)
        return

    from ..runtime_agent.persistent_queue import get_persistent_queue
    pq = get_persistent_queue()

    # Show: pending items ready for manual publish
    pending = pq.get_all("pending")
    approved = pq.get_all("approved")

    drafts = [i for i in pending + approved if i.get("action_type") == "publish_own_group_post"]

    if not drafts:
        drafts = [i for i in pending if i["status"] == "pending"]

    if not drafts:
        await update.message.reply_text("✅ Nema draft-ova za ručno objavljivanje.")
        return

    await update.message.reply_text(f"📰 *Draft-ovi za ručno objavljivanje:* {len(drafts)}", parse_mode="Markdown")
    for d in drafts[:5]:
        text = d.get("suggested_text", "")[:300]
        sid = d.get("item_id", "")[:16]
        status = d.get("status", "?")
        msg = f"`{sid}...` [{status}]\n{text}"
        await update.message.reply_text(msg, parse_mode="Markdown")


# ── /spam — spam quarantine ───────────────────────────────────────────────

async def spam_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_operator(update):
        await _reject_unknown(update, context)
        return

    from ..runtime_agent.persistent_queue import get_persistent_queue
    pq = get_persistent_queue()

    spam_items = pq.get_all("spam_candidate") + pq.get_all("spam")

    if not spam_items:
        await update.message.reply_text("✅ Spam karantin prazan.")
        return

    await update.message.reply_text(f"🚫 *Spam karantin:* {len(spam_items)}", parse_mode="Markdown")
    for s in spam_items[:5]:
        sid = s.get("item_id", "")[:16]
        reason = s.get("reason", "")[:100]
        await update.message.reply_text(f"`{sid}...`\n{reason}", parse_mode="Markdown")


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
    _pq_store = None

    if not item:
        # Fallback: persistent SQLite queue (survives restarts)
        try:
            from ..runtime_agent.persistent_queue import get_persistent_queue
            _pq_store = get_persistent_queue()
            item_p = _pq_store.get(item_id)
            if not item_p:
                await query.edit_message_text(f"Queue item not found: {item_id}")
                return
            # Wrap persistent dict into object-like interface
            class _PQWrapper:
                def __init__(self, d): self.__dict__.update(d)
                approve = lambda s, op: _pq_store.update_status(item_id, "approved", op)
                reject = lambda s, r, op: _pq_store.update_status(item_id, "rejected", op, r)
                mark_spam = lambda s, r, op: _pq_store.update_status(item_id, "spam", op, r)
                mark_needs_info = lambda s, r, op: _pq_store.update_status(item_id, "needs_info", op, r)
                mark_executed = lambda s, op: _pq_store.update_status(item_id, "executed_manually", op)
                mark_closed = lambda s, op: _pq_store.update_status(item_id, "closed", op)
                mark_duplicate = lambda s, op: _pq_store.update_status(item_id, "duplicate", op)
                def edit(self, new_text, op):
                    _pq_store.update_text(item_id, new_text, op)
                @property
                def suggested_text(self): return item_p.get("suggested_text", "")
                @property
                def operator_approval_required(self): return item_p.get("operator_approval_required", True)
            item = _PQWrapper(item_p)
            item.item_id = item_id
            item.status = type('S', (), {'value': item_p['status']})()
            item.to_dict = lambda: item_p
        except Exception:
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
        item.mark_closed(operator)
        agent.audit.record("telegram_closed", f"Item: {item_id}", new_state="closed", operator=operator)
        await query.edit_message_text(f"🔒 Closed\nID: `{item_id[:16]}...`", parse_mode="Markdown")

    elif action == "mark_duplicate":
        item.mark_duplicate(operator)
        agent.audit.record("telegram_marked_duplicate", f"Item: {item_id}", new_state="duplicate", operator=operator)
        await query.edit_message_text(f"📋 Duplicate\nID: `{item_id[:16]}...`", parse_mode="Markdown")

    elif action == "mark_spam":
        item.mark_spam("Marked spam from Telegram", operator)
        agent.audit.record("telegram_spam", f"Item: {item_id}", new_state="spam", operator=operator)
        await query.edit_message_text(f"🚫 Spam\nID: `{item_id[:16]}...`", parse_mode="Markdown")

    elif action == "needs_info":
        item.mark_needs_info("Missing info flagged from Telegram", operator)
        agent.audit.record("telegram_needs_info", f"Item: {item_id}", new_state="needs_info", operator=operator)
        await query.edit_message_text(f"❓ Needs info\nID: `{item_id[:16]}...`", parse_mode="Markdown")

    elif action == "edit":
        # Edit flow: prompt operator to send new text
        context.user_data["editing_item_id"] = item_id
        await query.edit_message_text(
            f"✏️ *Edit Mode*\n\n"
            f"Item: `{item_id[:16]}...`\n"
            f"Original text:\n```\n{item.suggested_text[:200]}\n```\n\n"
            f"Reply to this chat with the new text to save the edit.\n"
            f"After editing, use /queue to approve or reject.",
            parse_mode="Markdown",
        )

    elif action == "escalate":
        # Escalation: flag item for deeper operator review
        item.mark_needs_info(f"Escalated by operator: {operator}", operator)
        agent.audit.record("telegram_escalate", f"Item: {item_id}", new_state="needs_info", operator=operator)
        await query.edit_message_text(
            f"⚠️ *Escalated for operator review*\n\n"
            f"ID: `{item_id[:16]}...`\n"
            f"Action: This item requires manual operator review.\n"
            f"Check the full context and decide: publish, edit, or reject.",
            parse_mode="Markdown",
        )

    else:
        await query.edit_message_text(f"Unknown action: {action}")


# ── Edit Text Handler ─────────────────────────────────────────────────────

async def handle_text_for_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages that may be edit replies."""
    if not update.message or not update.message.text:
        return

    editing_item_id = context.user_data.get("editing_item_id")
    if not editing_item_id:
        # Not editing — could be a command; let other handlers process
        return

    if not _is_operator(update):
        await update.message.reply_text("Access denied.")
        return

    agent = _get_agent()
    if not agent:
        await update.message.reply_text("Runtime agent not initialized.")
        return

    item = agent.queue.get(editing_item_id)
    if not item:
        await update.message.reply_text(f"Queue item not found: {editing_item_id}")
        context.user_data.pop("editing_item_id", None)
        return

    new_text = update.message.text.strip()
    operator = update.effective_user.username or str(update.effective_chat.id)

    # Save edited text
    item.edit(new_text, operator)
    agent.audit.record(
        "telegram_edit_text",
        f"Item: {editing_item_id}, new_text_len={len(new_text)}",
        new_state="edited",
        operator=operator,
    )
    context.user_data.pop("editing_item_id", None)

    await update.message.reply_text(
        f"✏️ *Edit saved*\n\n"
        f"Item: `{editing_item_id[:16]}...`\n"
        f"New text:\n```\n{new_text[:200]}\n```\n\n"
        f"Use /queue to approve or reject.",
        parse_mode="Markdown",
    )


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
    app.add_handler(CommandHandler("addlead", addlead_cmd))
    app.add_handler(CommandHandler("forms", forms_cmd))
    app.add_handler(CommandHandler("drafts", drafts_cmd))
    app.add_handler(CommandHandler("spam", spam_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_for_edit))

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
