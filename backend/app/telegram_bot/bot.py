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


# ── /reply — smart reply drafter ──────────────────────────────────────────

async def reply_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_operator(update):
        await _reject_unknown(update, context)
        return

    text = update.message.text or ""
    msg_text = text.removeprefix("/reply").strip()
    if not msg_text:
        await update.message.reply_text("Upotreba: /reply <tekst poruke>\n\nBot analizira poruku i predlaže odgovor.")
        return

    # Quick classification
    t = msg_text.lower()
    if any(w in t for w in ["kazino", "casino", "crypto", "forex", "kladionica", "brza zarada"]):
        intent, risk, reply = "spam", "high", "Ova objava je uklonjena jer krši pravila grupe. Dozvoljen sadržaj: sezonski rad u Srbiji."
    elif any(w in t for w in ["čuvajte se", "ne plaća", "prevarant", "lopov"]):
        intent, risk = "upozorenje", "high"
        reply = "Hvala na informaciji. Administrator će pregledati i preduzeti odgovarajuće korake."
    elif any(w in t for w in ["tražim posao", "treba mi posao"]):
        intent, risk = "traži posao", "low"
        reply = "Hvala! Popunite formu za radnike: https://forms.gle/UvbaekC86m8EE5X87 — administrator proverava podatke pre objave."
    elif any(w in t for w in ["tražimo", "potrebni", "zapošljavamo", "berba"]):
        intent, risk = "ponuda posla", "low"
        reply = "Hvala na objavi! Da bismo je objavili, popunite formu: https://forms.gle/KovE1kMFxMF7nq8w5"
    elif "?" in t or "pitanje" in t or "da li" in t:
        intent, risk = "pitanje", "low"
        reply = "Hvala na pitanju. Administrator će odgovoriti uskoro."
    else:
        intent, risk = "nepoznato", "medium"
        reply = "Hvala. Administrator će pregledati poruku."

    # Store as queue item
    from ..runtime_agent.persistent_queue import get_persistent_queue
    import uuid
    item_id = f"q_{uuid.uuid4().hex[:12]}"
    pq = get_persistent_queue()
    pq.add({
        "item_id": item_id, "action_type": "request_operator_review",
        "status": "pending", "suggested_text": reply,
        "reason": f"/reply: {intent}, risk={risk}",
        "operator_approval_required": True,
        "raw_json": {"intent": intent, "risk": risk, "original": msg_text[:200]},
        "created_at": __import__("datetime").datetime.utcnow().isoformat(),
    })

    await update.message.reply_text(
        f"📋 Analiza poruke\n\n"
        f"Tip: {intent}\n"
        f"Rizik: {risk}\n\n"
        f"Predlog odgovora:\n{reply}\n\n"
        f"Sledeći korak: kopirajte odgovor i pošaljite ručno u Facebook.",
    )


# ── /fb_post — capture Facebook post ─────────────────────────────────────

async def fb_post_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_operator(update):
        await _reject_unknown(update, context)
        return
    text = update.message.text or ""
    post = text.removeprefix("/fb_post").strip()
    if not post:
        await update.message.reply_text("Upotreba: /fb_post <tekst kopiran sa Facebook-a>")
        return
    await _capture_text(update, post, "fb_post_manual")


# ── /fb_comment — capture Facebook comment ────────────────────────────────

async def fb_comment_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_operator(update):
        await _reject_unknown(update, context)
        return
    text = update.message.text or ""
    comment = text.removeprefix("/fb_comment").strip()
    if not comment:
        await update.message.reply_text("Upotreba: /fb_comment Author: ime\nPost: tekst\nComment: tekst")
        return
    await _capture_text(update, comment, "fb_comment_manual")


# ── /capture — external group capture ─────────────────────────────────────

async def capture_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_operator(update):
        await _reject_unknown(update, context)
        return
    text = update.message.text or ""
    content = text.removeprefix("/capture").strip()
    if not content:
        await update.message.reply_text("Upotreba: /capture\nGroup: <ime grupe>\nAuthor: <ime>\nText: <tekst>")
        return
    await _capture_text(update, content, "external_group_capture")


# ── /fb_question, /fb_review, /fb_member aliases ─────────────────────────

async def fb_question_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_operator(update): await _reject_unknown(update, context); return
    q = (update.message.text or "").removeprefix("/fb_question").strip()
    if not q: await update.message.reply_text("Upotreba: /fb_question <tekst pitanja>"); return
    await _capture_text(update, q, "fb_question_manual")

async def fb_review_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_operator(update): await _reject_unknown(update, context); return
    r = (update.message.text or "").removeprefix("/fb_review").strip()
    if not r: await update.message.reply_text("Upotreba: /fb_review <tekst iskustva>"); return
    await _capture_text(update, r, "fb_review_manual")

async def fb_member_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_operator(update): await _reject_unknown(update, context); return
    m = (update.message.text or "").removeprefix("/fb_member").strip()
    if not m: await update.message.reply_text("Upotreba: /fb_member Name: ime\nNote: opis"); return
    await _capture_text(update, m, "fb_member_manual")


async def _capture_text(update, text: str, source_type: str):
    """Shared capture: classify, persist, return draft reply."""
    import uuid, re
    from ..runtime_agent.persistent_queue import get_persistent_queue
    from ..operator_mvp.mvp_api import _classify_rule_based, _classify_risk, _determine_action

    cls, fields = _classify_rule_based(text)
    risk, flags = _classify_risk(text.lower(), cls, fields)
    action = _determine_action(cls, risk, bool(fields.get("contact")), bool(fields.get("location")))

    # Build Serbian reply
    if cls == "spam":
        reply = "Ova objava je uklonjena jer krši pravila grupe."
    elif cls == "employer_warning":
        reply = "Hvala na informaciji. Administrator će pregledati."
    elif cls == "job_offer" and risk == "low":
        reply = "Hvala! Popunite formu za poslodavce: https://forms.gle/KovE1kMFxMF7nq8w5"
    elif cls == "worker_search":
        reply = "Hvala! Popunite formu za radnike: https://forms.gle/UvbaekC86m8EE5X87"
    elif action == "request_more_info":
        reply = "Hvala. Da bismo objavu pripremili, molimo vas da navedete više informacija."
    else:
        reply = "Hvala. Administrator će pregledati i odgovoriti."

    item_id = f"q_{uuid.uuid4().hex[:12]}"
    pq = get_persistent_queue()
    pq.add({
        "item_id": item_id, "action_type": "request_operator_review",
        "status": "pending", "suggested_text": reply,
        "reason": f"{source_type}: {cls}, risk={risk}",
        "operator_approval_required": True,
        "raw_json": {"source_type": source_type, "classification": cls,
                     "risk": risk, "original": text[:500]},
        "created_at": __import__("datetime").datetime.utcnow().isoformat(),
    })

    await update.message.reply_text(
        f"📋 {source_type}\n"
        f"Klasifikacija: {cls}\n"
        f"Rizik: {risk} | Akcija: {action}\n\n"
        f"Predlog odgovora:\n{reply}\n\n"
        f"✅ Sačuvano. Objavite ručno u Facebook.",
    )


# ── /today — daily operator checklist ─────────────────────────────────────

async def today_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_operator(update): await _reject_unknown(update, context); return

    from ..runtime_agent.persistent_queue import get_persistent_queue
    pq = get_persistent_queue()
    all_items = pq.get_all()

    new = [i for i in all_items if i["status"] in ("pending", "approved")]
    questions = [i for i in new if "question" in str(i.get("raw_json", {}).get("source_type", ""))]
    spam = [i for i in all_items if i["status"] in ("spam", "spam_candidate")]

    msg = "📅 *Današnji pregled*\n\n"
    msg += f"📰 Novi draft-ovi: {len(new)}\n"
    msg += f"❓ Pitanja: {len(questions)}\n"
    msg += f"🚫 Spam/rizik: {len(spam)}\n\n"

    msg += "*Za uraditi danas:*\n"
    msg += "1. Pregledaj /drafts\n"
    msg += "2. Odgovori na pitanja\n"
    msg += "3. Proveri /spam\n"
    msg += "4. Pokreni /digest\n"
    msg += "5. Objavi ručno u FB grupu\n\n"

    msg += "Forme:\n"
    msg += "Poslodavci: https://forms.gle/KovE1kMFxMF7nq8w5\n"
    msg += "Radnici: https://forms.gle/UvbaekC86m8EE5X87"

    await update.message.reply_text(msg, parse_mode="Markdown")


# ── /links — form links + Serbian copy-paste ──────────────────────────────

async def links_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_operator(update): await _reject_unknown(update, context); return

    await update.message.reply_text(
        "📋 *Linkovi*\n\n"
        "*Za poslodavce:*\n"
        "https://forms.gle/KovE1kMFxMF7nq8w5\n\n"
        "✂️ Kopiraj za FB:\n"
        "Ako tražite sezonske radnike, popunite ovu formu. "
        "Administrator proverava podatke pre objave:\n"
        "https://forms.gle/KovE1kMFxMF7nq8w5\n\n"
        "*Za radnike:*\n"
        "https://forms.gle/UvbaekC86m8EE5X87\n\n"
        "✂️ Kopiraj za FB:\n"
        "Ako tražite sezonski posao, popunite ovu formu. "
        "Administrator proverava podatke pre objave:\n"
        "https://forms.gle/UvbaekC86m8EE5X87",
        parse_mode="Markdown",
    )


# ── /evening — end-of-day actionable items ────────────────────────────────

async def evening_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_operator(update): await _reject_unknown(update, context); return

    from ..runtime_agent.persistent_queue import get_persistent_queue
    pq = get_persistent_queue()
    all_items = pq.get_all()

    # Group by priority
    high = [i for i in all_items if i.get("status") in ("risk_review",) or
            "high" in str(i.get("raw_json", {}).get("risk", ""))]
    questions = [i for i in all_items if "question" in str(i.get("raw_json", {}).get("source_type", ""))
                 and i["status"] == "pending"]
    offers = [i for i in all_items if i["status"] == "pending"
              and i.get("action_type") == "publish_own_group_post"]
    spam = [i for i in all_items if i["status"] in ("spam", "spam_candidate")]

    msg = "🌙 *Večernji pregled*\n\n"

    if high:
        msg += f"🔴 *Prioritet 1 — Rizik:* {len(high)}\n"
        for h in high[:3]:
            msg += f"  `{h['item_id'][:12]}...` {h.get('reason', '')[:80]}\n"
    if questions:
        msg += f"\n🟡 *Pitanja:* {len(questions)}\n"
    if offers:
        msg += f"\n🟢 *Ponude:* {len(offers)}\n"
    if spam:
        msg += f"\n⚫ *Spam:* {len(spam)}\n"

    if not any([high, questions, offers, spam]):
        msg += "✅ Nema stavki za večeras."

    msg += "\n✂️ Svi odgovori su spremni u /drafts. Kopiraj i objavi ručno."

    await update.message.reply_text(msg, parse_mode="Markdown")


# ── /digest_next — next-day digest from external captures ─────────────────

async def digest_next_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_operator(update): await _reject_unknown(update, context); return

    from ..runtime_agent.persistent_queue import get_persistent_queue
    pq = get_persistent_queue()
    all_items = pq.get_all()

    # Collect external captures
    captures = [i for i in all_items
                if "external_group_capture" in str(i.get("raw_json", {}).get("source_type", ""))
                or "fb_post_manual" in str(i.get("raw_json", {}).get("source_type", ""))]
    captures = [c for c in captures if c["status"] not in ("spam", "spam_candidate", "rejected")]

    if not captures:
        await update.message.reply_text("Nema captures za digest. Koristite /capture za dodavanje.")
        return

    date_str = __import__("datetime").datetime.utcnow().strftime("%d.%m.%Y")
    lines = [f"📌 Pregled sezonskih poslova — {date_str}", "",
             "Oglasi prikupljeni iz javnih izvora. Proverite uslove direktno.", ""]

    for i, c in enumerate(captures[:10], 1):
        raw = c.get("raw_json", {}) or {}
        original = raw.get("original", c.get("suggested_text", ""))[:150]
        lines.append(f"{i}. {original}")
        lines.append("")

    lines.append("---")
    lines.append("Napomena: Grupa nije poslodavac i ne garantuje uslove.")
    lines.append("Objava pripremljena za ručnu proveru, nije automatski objavljena.")

    digest = "\n".join(lines)

    # Save as queue item
    import uuid
    pq.add({
        "item_id": f"q_{uuid.uuid4().hex[:12]}",
        "action_type": "create_digest_post",
        "status": "pending", "suggested_text": digest,
        "reason": "digest_next from external captures",
        "operator_approval_required": True,
        "created_at": __import__("datetime").datetime.utcnow().isoformat(),
    })

    await update.message.reply_text(
        f"📌 *Digest za sutra*\n\n{digest[:1000]}"
        f"\n\n✅ {len(captures)} stavki. Objavite ručno u FB.",
        parse_mode="Markdown",
    )


# ── /fb_help — mobile mode help ───────────────────────────────────────────

async def fb_help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_operator(update): await _reject_unknown(update, context); return
    await update.message.reply_text(
        "📱 *Mobilni režim — komande*\n\n"
        "/fb_post <tekst> — kopirani FB post\n"
        "/fb_comment <tekst> — kopirani FB komentar\n"
        "/fb_question <tekst> — pitanje\n"
        "/fb_review <tekst> — iskustvo/recenzija\n"
        "/fb_member <tekst> — profil člana\n"
        "/capture <tekst> — post iz druge grupe\n"
        "/reply <tekst> — analiza i predlog odgovora\n"
        "/today — današnji pregled\n"
        "/links — forme (copy-paste)\n"
        "/evening — večernji pregled\n"
        "/digest_next — digest za sutra",
        parse_mode="Markdown",
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

async def handle_text_or_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle non-command text: edit mode first, then natural language assistant."""
    if not update.message or not update.message.text:
        return

    editing_item_id = context.user_data.get("editing_item_id")
    if editing_item_id:
        await handle_text_for_edit(update, context)
        return

    # ── Natural Language Assistant Mode ──────────────────────────────────
    await _natural_language_assistant(update, context)


async def _natural_language_assistant(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Detect intent from natural language and respond helpfully."""
    if not _is_operator(update):
        await update.message.reply_text("Access denied.")
        return

    text = (update.message.text or "").strip()
    t = text.lower()
    resp = None

    # Intent: daily summary
    if any(w in t for w in ["что у меня", "на сегодня", "сегодня", "дневной", "dnevni", "pregled",
                              "шта има", "шта треба", "šta ima", "šta treba"]):
        await today_cmd(update, context)
        return

    # Intent: forms / links
    if any(w in t for w in ["forma", "formu", "link", "линк", "ссылк", "анкет"]):
        await links_cmd(update, context)
        return

    # Intent: digest capture (add to next digest)
    if any(w in t for w in ["добавь", "дайджест", "digest", "додај", "dodaj",
                              "треба радника", "tražimo", "potrebni", "zapošljavamo"]):
        await _capture_text(update, text, "natural_language_capture")
        return

    # Intent: draft reply — contains Serbian question-like text
    if any(w in t for w in ["что ответить", "шта одговорити", "kako da odgovorim",
                              "ответ", "odgovor", "odgovori", "reply", "da li", "kako"]):
        await reply_cmd(update, context)
        return

    # Intent: classify text (looks like FB post/comment)
    serbian_markers = ["tražim", "tražimo", "potrebni", "berba", "branje", "plastenik",
                       "dnevnica", "smeštaj", "hrana", "kontakt", "posao", "radnici",
                       "čuvajte", "iskustvo", "radio sam", "radila sam"]
    russian_markers = ["ищу", "требуются", "работа", "вакансия", "опыт"]

    if any(m in t for m in serbian_markers + russian_markers):
        from ..operator_mvp.mvp_api import _classify_rule_based, _classify_risk, _determine_action
        cls, fields = _classify_rule_based(text)
        risk, flags = _classify_risk(t, cls, fields)
        action = _determine_action(cls, risk, bool(fields.get("contact")), bool(fields.get("location")))

        # Build Serbian reply draft
        if cls == "spam":
            draft = "Ova objava je uklonjena jer krši pravila grupe."
        elif cls == "employer_warning":
            draft = "Hvala na informaciji. Administrator će pregledati."
        elif cls == "job_offer":
            draft = "Hvala na objavi! Popunite formu za poslodavce: https://forms.gle/KovE1kMFxMF7nq8w5"
        elif cls == "worker_search":
            draft = "Hvala! Popunite formu za radnike: https://forms.gle/UvbaekC86m8EE5X87"
        else:
            draft = "Hvala. Administrator će pregledati i odgovoriti."

        resp = (f"📋 *Analiza*\n"
                f"Tip: {cls} | Rizik: {risk} | Akcija: {action}\n\n"
                f"*Predlog odgovora:*\n{draft}\n\n"
                f"✂️ Kopirajte i pošaljite ručno u Facebook.")

    # Fallback: help
    if resp is None:
        resp = ("🤖 *Asistent*\n\n"
                "Pošaljite tekst za analizu ili:\n"
                "/fb_post — FB post\n"
                "/reply — predlog odgovora\n"
                "/today — današnji pregled\n"
                "/links — forme\n"
                "/evening — večernji pregled\n"
                "/help — sve komande")

    await update.message.reply_text(resp, parse_mode="Markdown")


async def handle_text_for_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages that are edit replies."""
    if not update.message or not update.message.text:
        return

    editing_item_id = context.user_data.get("editing_item_id")
    if not editing_item_id:
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
    app.add_handler(CommandHandler("reply", reply_cmd))
    app.add_handler(CommandHandler("fb_post", fb_post_cmd))
    app.add_handler(CommandHandler("fb_comment", fb_comment_cmd))
    app.add_handler(CommandHandler("fb_question", fb_question_cmd))
    app.add_handler(CommandHandler("fb_review", fb_review_cmd))
    app.add_handler(CommandHandler("fb_member", fb_member_cmd))
    app.add_handler(CommandHandler("capture", capture_cmd))
    app.add_handler(CommandHandler("today", today_cmd))
    app.add_handler(CommandHandler("links", links_cmd))
    app.add_handler(CommandHandler("evening", evening_cmd))
    app.add_handler(CommandHandler("digest_next", digest_next_cmd))
    app.add_handler(CommandHandler("fb_help", fb_help_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_or_edit))

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
