"""Content extractor: extracts text, timestamps, and URLs from visible HTML."""

import re
import hashlib
from datetime import datetime
from .worker_models import CapturedItem


def extract_items(html_blocks: list[dict], page_url: str) -> list[CapturedItem]:
    """Extract captured items from HTML text blocks.
    Each block: {"text": "...", "html": "...", "timestamp": "..."}
    """
    items = []
    for i, block in enumerate(html_blocks):
        text = block.get("text", "").strip()
        if not text or len(text) < 10:
            continue

        content_hash = hashlib.sha256(text.encode()).hexdigest()

        items.append(CapturedItem(
            item_id=f"cap_{content_hash[:16]}",
            raw_text=text,
            content_hash=content_hash,
            source_url=block.get("url", page_url),
            page_url=page_url,
            visible_timestamp=block.get("timestamp"),
            item_type=block.get("type", "post"),
            captured_at=datetime.utcnow().isoformat(),
        ))
    return items


def extract_text_from_html(html: str) -> str:
    """Basic HTML-to-text extraction. Strips tags, normalizes whitespace."""
    # Remove script/style
    text = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', html, flags=re.DOTALL | re.IGNORECASE)
    # Remove tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def extract_facebook_blocks(html: str) -> list[dict]:
    """Extract post/comment text blocks from Facebook HTML.
    Looks for common FB post container patterns."""
    blocks = []
    patterns = [
        r'<div[^>]*data-ad-preview[^>]*>(.*?)</div>',
        r'<div[^>]*class="[^"]*userContent[^"]*"[^>]*>(.*?)</div>',
        r'<div[^>]*class="[^"]*comment[^"]*"[^>]*>(.*?)</div>',
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, html, re.DOTALL | re.IGNORECASE):
            text = extract_text_from_html(match.group(1))
            if len(text) > 10:
                blocks.append({"text": text, "html": match.group(1), "type": "post"})
    return blocks
