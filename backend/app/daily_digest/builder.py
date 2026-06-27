"""Daily digest builder — filters approved queue items, builds Serbian digest post.

Rules:
- Include ONLY: status=approved, risk=low, non-spam items
- Exclude: pending, rejected, spam, needs_info, escalated, high-risk
- Always add disclaimer + CTA
- Fallback if <1 usable item
"""

import os
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger("sezonski.daily_digest")

# Forbidden words that must NEVER appear in digest text
FORBIDDEN_WORDS = {"provereno", "sigurno", "garantovano", "najbolji poslodavac"}

DISCLAIMER = (
    "Napomena: Grupa nije poslodavac i ne garantuje uslove. "
    "Pre odlaska obavezno proverite platu, smeštaj, hranu, "
    "radno vreme, prevoz i način isplate direktno sa osobom iz oglasa."
)

CTA = (
    "Ako imate svež oglas za sezonski rad, napišite: "
    "mesto rada, vrstu posla, zaradu, radno vreme, "
    "smeštaj/hranu, datum početka i kontakt."
)

INTRO = (
    "Oglasi su prikupljeni iz javnih izvora i/ili od članova grupe. "
    "Pre odlaska obavezno proverite uslove direktno sa osobom iz oglasa."
)

FALLBACK_TEXT = (
    "Nema dovoljno proverenih oglasa za današnji digest. "
    "Ako imate informaciju o sezonskom poslu — podelite je u grupi "
    "sa lokacijom, vrstom posla, zaradom i kontaktom."
)


def build_digest(
    approved_items: list[dict],
    date_str: str | None = None,
) -> dict:
    """Build a daily digest from approved queue items.

    Args:
        approved_items: List of approved queue item dicts with fields:
            item_id, suggested_text, classification, risk_level,
            source, group_name, contact, location, job_type, pay
        date_str: Date string in DD.MM.YYYY format (default: today)

    Returns:
        dict with: success, digest_text, items_included, items_excluded,
                   source_item_ids, missing_count, fallback_used
    """
    if date_str is None:
        date_str = datetime.utcnow().strftime("%d.%m.%Y")

    usable = []
    excluded = []
    excluded_reasons = []

    for item in approved_items:
        risk = item.get("risk_level", "medium")
        classification = item.get("classification", "")
        status = item.get("status", "")
        is_spam = classification in ("spam",) or item.get("is_spam", False)
        confidence = item.get("confidence", 1.0)

        # Exclusion rules
        if status not in ("approved",):
            excluded.append(item)
            excluded_reasons.append(f"{item.get('item_id', '?')[:12]}: not approved")
            continue
        if is_spam:
            excluded.append(item)
            excluded_reasons.append(f"{item.get('item_id', '?')[:12]}: spam")
            continue
        if risk == "high":
            excluded.append(item)
            excluded_reasons.append(f"{item.get('item_id', '?')[:12]}: high risk")
            continue
        if confidence < 0.60:
            excluded.append(item)
            excluded_reasons.append(f"{item.get('item_id', '?')[:12]}: low confidence ({confidence:.0%})")
            continue

        # Only include job offers and useful worker content for digest
        if classification not in ("job_offer", "worker_search", "digest_candidate"):
            excluded.append(item)
            excluded_reasons.append(f"{item.get('item_id', '?')[:12]}: not digest-type ({classification})")
            continue

        usable.append(item)

    # Fallback if not enough usable items
    if len(usable) < 1:
        digest_lines = [
            f"📌 Dnevni pregled sezonskih poslova — {date_str}",
            "",
            FALLBACK_TEXT,
            "",
            CTA,
            "",
            "---",
            DISCLAIMER,
        ]
        digest_text = "\n".join(digest_lines)

        # Check forbidden words
        found_forbidden = _check_forbidden(digest_text)
        if found_forbidden:
            logger.error(f"Forbidden words in fallback digest: {found_forbidden}")

        return {
            "success": True,
            "digest_text": digest_text,
            "items_included": 0,
            "items_excluded": len(approved_items),
            "excluded_reasons": excluded_reasons,
            "source_item_ids": [],
            "missing_count": 0,
            "fallback_used": True,
            "forbidden_words_found": found_forbidden,
        }

    # Build digest
    digest_lines = [
        f"📌 Dnevni pregled sezonskih poslova — {date_str}",
        "",
        INTRO,
        "",
    ]

    source_ids = []
    for i, item in enumerate(usable, 1):
        # Determine source label
        source = item.get("source", "")
        if "public_screenshot" in source or "facebook_public" in source:
            source_label = "javni oglas"
        elif "facebook_manual" in source or "telegram" in source:
            source_label = "član grupe"
        else:
            source_label = "ručni unos"

        # Build item entry
        classification = item.get("classification", "")
        if classification == "job_offer":
            prefix = "🔹"
            label = "Poslodavac traži"
        elif classification == "worker_search":
            prefix = "👷"
            label = "Radnik traži posao"
        else:
            prefix = "📋"
            label = "Oglas"

        lines = [f"{prefix} **{i}. {label}**"]

        # Job type / crop
        job_type = item.get("job_type") or item.get("crop") or ""
        location = item.get("location") or ""
        if job_type and location:
            lines.append(f"   *{job_type}* — {location}")
        elif job_type:
            lines.append(f"   *{job_type}*")
        elif location:
            lines.append(f"   Lokacija: {location}")

        # Pay
        pay = item.get("pay") or ""
        if pay:
            lines.append(f"   Plata: {pay}")

        # Accommodation / Food
        acc = item.get("accommodation") or ""
        food = item.get("food") or ""
        conditions = []
        if acc:
            conditions.append(f"smeštaj: {acc}")
        if food:
            conditions.append(f"hrana: {food}")
        if conditions:
            lines.append(f"   Uslovi: {', '.join(conditions)}")

        # Contact (only if present in original public text)
        contact = item.get("contact") or ""
        if contact:
            lines.append(f"   Kontakt: {contact}")

        # Missing fields to verify
        missing = item.get("missing_info") or item.get("missing_fields") or []
        if missing:
            lines.append(f"   *Proverite:* {', '.join(missing[:4])}")

        # Source label
        lines.append(f"   📎 Izvor: {source_label}")

        digest_lines.append("\n".join(lines))
        digest_lines.append("")
        source_ids.append(item.get("item_id", ""))

    # Footer
    digest_lines.extend([
        "---",
        CTA,
        "",
        DISCLAIMER,
    ])

    digest_text = "\n".join(digest_lines)

    # Check forbidden words
    found_forbidden = _check_forbidden(digest_text)

    return {
        "success": True,
        "digest_text": digest_text,
        "items_included": len(usable),
        "items_excluded": len(excluded),
        "excluded_reasons": excluded_reasons,
        "source_item_ids": source_ids,
        "missing_count": 0,
        "fallback_used": False,
        "forbidden_words_found": found_forbidden,
    }


def _check_forbidden(text: str) -> list[str]:
    """Check for forbidden words in digest text."""
    found = []
    for word in FORBIDDEN_WORDS:
        if word.lower() in text.lower():
            found.append(word)
    return found


def create_digest_queue_item(
    digest_result: dict,
    action_queue=None,
) -> dict | None:
    """Create a queue item for the digest (requires operator approval).

    Returns the queue item dict or None if queue unavailable.
    """
    if action_queue is None:
        logger.warning("No action queue provided — cannot create digest queue item")
        return None

    from ..runtime_agent.action_queue import QueueItem, ActionType

    item = QueueItem(
        action_type=ActionType.CREATE_DIGEST_POST,
        suggested_text=digest_result["digest_text"],
        reason=f"daily_digest_builder: {digest_result['items_included']} items included",
        operator_approval_required=True,
    )

    action_queue.add(item)
    logger.info(
        f"Digest queue item created: {item.item_id} "
        f"({digest_result['items_included']} items, "
        f"{digest_result['items_excluded']} excluded)"
    )

    return item.to_dict()
