"""Batch capture — split messy multi-post text, extract fields, deduplicate, persist."""

import re
import uuid
import hashlib
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger("sezonski.batch_capture")


# ── Text splitting ──────────────────────────────────────────────────────────

def split_posts(raw_text: str) -> list[str]:
    """Split messy multi-post text into individual posts.

    Handles: numbered lists, double newlines, dashes separators, emoji separators.
    """
    # Normalize line endings
    text = raw_text.replace("\r\n", "\n").replace("\r", "\n")

    # Try splitting by common separators
    separators = [
        r"\n\d+[.)]\s*\n",      # "1.\n" or "2)\n"
        r"\n-{3,}\n",            # "---" line
        r"\n_{3,}\n",            # "___" line
        r"\n•\s*",               # bullet points
        r"\n🔹\s*",              # emoji bullets
        r"\n📌\s*",
        r"\n\n\n+",              # 3+ newlines
    ]

    for sep in separators:
        parts = re.split(sep, text)
        if len(parts) > 1:
            # Filter out empty/short parts
            posts = [p.strip() for p in parts if len(p.strip()) > 30]
            if len(posts) >= 2:
                return posts[:20]  # max 20 posts

    # Fallback: split by double newline
    parts = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 30]
    if parts:
        return parts[:20]

    return [text.strip()] if len(text.strip()) > 30 else []


# ── Field extraction from a single post ─────────────────────────────────────

def extract_post_fields(text: str) -> dict:
    """Extract fields from a single post text.

    Returns dict with: location, job_type, workers_needed, pay, housing,
    food, work_hours, contact, source_author, risk_flags, classification.
    """
    t = text.lower()
    fields: dict = {
        "location": None, "job_type": None, "workers_needed": None,
        "pay": None, "pay_type": None, "housing": None, "food": None,
        "work_hours": None, "contact": None, "source_author": None,
        "risk_flags": [],
    }

    # Phone — Serbian formats 064-123-4567, 064-123-456, 064/123-456, +381...
    phone_patterns = [
        r'(0\d{2})[\s/-]?(\d{2,4})[\s/-]?(\d{2,4})(?:[\s/-]?(\d{2,4}))?',  # flexible 3+3+3 or 3+4+4 or 3+4+3+4
        r'\+\d{2,3}[\s/-]?\d{2,3}[\s/-]?\d{2,3}[\s/-]?\d{2,4}',
    ]
    for pat in phone_patterns:
        phone = re.search(pat, text)
        if phone:
            fields["contact"] = phone.group(0).strip()
            break

    # Location (match root of location name, e.g. "Arilje" matches "Arilju", "Arilja")
    locations = [("Arilj", "Arilje"), ("Ivanjic", "Ivanjica"), ("Čačak", "Čačak"),
                 ("Užic", "Užice"), ("Subotic", "Subotica"),
                 ("Novi Sad", "Novi Sad"), ("Beograd", "Beograd"),
                 ("Smederev", "Smederevo"), ("Srem", "Srem"), ("Vojvodin", "Vojvodina"),
                 ("Valjev", "Valjevo"), ("Kraljev", "Kraljevo"), ("Leskovac", "Leskovac"),
                 ("Bajina Bašt", "Bajina Bašta"),
                 ("Sivac", "Sivac"), ("Šabac", "Šabac"), ("Sombor", "Sombor"),
                 ("Prije", "Prijepolje"),
                 ("okolin", "okolina"), ("Šumadij", "Šumadija")]
    found_locs = []
    for root, display in locations:
        if root.lower() in t:
            found_locs.append(display)
    if found_locs:
        fields["location"] = ", ".join(found_locs[:2])

    # Job type — match both "berba malina" and "berbu malina"
    t_mod = t.replace("berbu", "berba").replace("berbe", "berba").replace("berbi", "berba")
    jobs = ["berba malina", "berba višanja", "berba jabuka", "berba jagoda",
            "berba borovnica", "berba kupina", "branje", "berba šljiva",
            "plastenik", "farma", "hladnjača", "pakovanje", "sortiranje",
            "građevina", "poljoprivreda", "sezonski rad"]
    found_jobs = [j for j in jobs if j.lower() in t_mod]
    if found_jobs:
        fields["job_type"] = found_jobs[0]

    # Workers needed
    w = re.search(r'(\d+)\s*(radnika|radnice|radnik|berača|berači)', t)
    if w:
        fields["workers_needed"] = w.group(1)

    # Pay
    pay = re.search(r'(dnevnica|plata|po kg|po kilogramu|po satu|mesečno)\s*:?\s*(\d[\d\s]*)', t)
    if pay:
        fields["pay"] = pay.group(0).strip()[:50]
        fields["pay_type"] = pay.group(1)

    # Housing
    if "smeštaj" in t:
        fields["housing"] = "da" if "obezbeđen" in t else "nepoznato"
    # Food
    if "hrana" in t:
        fields["food"] = "da" if "obezbeđen" in t else "nepoznato"
    # Work hours
    wh = re.search(r'(\d+)\s*(sati|h|časova)', t)
    if wh:
        fields["work_hours"] = wh.group(0)

    # Classification
    spam_signals = ["kazino", "casino", "crypto", "forex", "kladionica"]
    if any(s in t for s in spam_signals):
        fields["classification"] = "spam"
    elif any(w in t for w in ["tražim posao", "treba mi posao"]):
        fields["classification"] = "worker_search"
    elif any(w in t for w in ["tražimo", "potrebni", "zapošljavamo", "berba",
                                "treba nam", "radnici za"]):
        fields["classification"] = "job_offer"
    elif any(w in t for w in ["čuvajte se", "ne plaća", "upozorenje"]):
        fields["classification"] = "employer_warning"
    else:
        fields["classification"] = "unknown"

    # Risk flags
    if not fields.get("pay"):
        fields["risk_flags"].append("missing_pay")
    if not fields.get("location"):
        fields["risk_flags"].append("missing_location")
    if not fields.get("contact"):
        fields["risk_flags"].append("no_contact")
    if "inbox" in t:
        fields["risk_flags"].append("inbox_only")
    if re.search(r'\d{4,5}€|\d{4,5}e\b|2000€', t) and not re.search(r'dnevnica|plata', t):
        fields["risk_flags"].append("too_good_to_be_true")

    return fields


def compute_risk_level(fields: dict) -> str:
    """Low/medium/high from extracted fields and risk flags."""
    flags = fields.get("risk_flags", [])
    if not fields.get("contact"):
        return "high"
    if len(flags) >= 3:
        return "high"
    if len(flags) >= 1:
        return "medium"
    return "low"


def dedup_key(text: str, contact: str = "") -> str:
    """Deterministic dedup key from text prefix + phone."""
    normalized = " ".join(text.lower().split())[:100]
    phone = contact.replace(" ", "").replace("-", "") if contact else ""
    raw = f"{normalized}|{phone}"
    return hashlib.sha256(raw.encode()).hexdigest()[:24]


def process_batch(raw_text: str, source_group: str = "", source_author: str = "") -> list[dict]:
    """Full batch pipeline: split → extract → dedup → queue-ready items.

    Returns list of queue-ready item dicts.
    """
    posts = split_posts(raw_text)
    if not posts:
        return []

    seen: set[str] = set()
    items = []

    for post in posts:
        fields = extract_post_fields(post)
        risk = compute_risk_level(fields)
        dkey = dedup_key(post, fields.get("contact") or "")

        if dkey in seen:
            continue
        seen.add(dkey)

        classification = fields.get("classification", "unknown")

        # Build suggested Serbian text
        lines = []
        if classification == "job_offer":
            emp = fields.get("source_author") or source_author or "Poslodavac"
            lines.append(f"🔹 {emp}")
            if fields.get("job_type"):
                lines.append(f"💼 {fields['job_type']}")
            if fields.get("location"):
                lines.append(f"📍 {fields['location']}")
            if fields.get("workers_needed"):
                lines.append(f"👥 {fields['workers_needed']} radnika")
            if fields.get("pay"):
                lines.append(f"💰 {fields['pay']}")
            if fields.get("work_hours"):
                lines.append(f"🕐 {fields['work_hours']}")
            if fields.get("housing"):
                lines.append(f"🏠 Smeštaj: {fields['housing']}")
            if fields.get("food"):
                lines.append(f"🍽 Hrana: {fields['food']}")
            if fields.get("contact"):
                lines.append(f"📞 {fields['contact']}")
            if source_group:
                lines.append(f"📎 Izvor: {source_group}")
        elif classification == "worker_search":
            lines.append(f"👷 Radnik traži posao")
            if fields.get("job_type"):
                lines.append(f"💼 {fields['job_type']}")
            if fields.get("location"):
                lines.append(f"📍 {fields['location']}")
            if fields.get("contact"):
                lines.append(f"📞 {fields['contact']}")
        else:
            lines.append(f"📋 {post[:200]}")

        suggested_text = "\n".join(lines)

        now = datetime.utcnow().isoformat()
        item_id = f"q_{uuid.uuid4().hex[:12]}"

        # Determine action_type
        if classification in ("spam",):
            status = "spam_candidate"
            action_type = "request_operator_review"
        elif risk == "high":
            status = "risk_review"
            action_type = "request_operator_review"
        else:
            status = "pending"
            action_type = "publish_own_group_post"

        items.append({
            "item_id": item_id,
            "action_type": action_type,
            "status": status,
            "classification": classification,
            "risk_level": risk,
            "suggested_text": suggested_text[:1000],
            "reason": f"batch_capture: {classification}, risk={risk}, flags={fields['risk_flags']}",
            "operator_approval_required": True,
            "source": "external_batch_capture",
            "missing_info": fields.get("risk_flags", []),
            "risk_flags": fields.get("risk_flags", []),
            "raw_json": {
                "original": post[:500],
                "dedup_key": dkey,
                "source_group": source_group,
                "source_author": source_author,
                "captured_at": now,
                "fields": {k: v for k, v in fields.items() if v and k != "risk_flags"},
            },
            "created_at": now,
        })

    return items


def build_morning_digest(captured_items: list[dict]) -> str:
    """Build a Serbian morning digest from captured external leads.

    Includes only non-spam, non-high-risk items.
    """
    date_str = datetime.utcnow().strftime("%d.%m.%Y")
    safe = [i for i in captured_items
            if i.get("status") not in ("spam_candidate", "spam")
            and i.get("risk_level") != "high"]

    if not safe:
        return (
            f"📌 Jutarnji pregled eksternih oglasa — {date_str}\n\n"
            "Nema novih oglasa za danas. "
            "Ako vidite zanimljive objave u drugim grupama, "
            "pošaljite ih putem /capture_batch."
        )

    lines = [f"📌 Jutarnji pregled eksternih oglasa — {date_str}", ""]
    lines.append("Oglasi su prikupljeni iz javnih FB grupa. "
                  "Pre odlaska proverite uslove direktno.")
    lines.append("")

    for i, item in enumerate(safe[:10], 1):
        text = item.get("suggested_text", "")
        if text:
            lines.append(f"{i}. {text[:600]}")
            lines.append("")

    lines.append("---")
    lines.append("Napomena: Grupa nije poslodavac i ne garantuje uslove.")

    return "\n".join(lines)
