"""Simple image-post generation for manual Facebook publishing.

1080x1080 PNG with gradient background, centered Serbian text, footer.
No Facebook automation.
"""

import os
import math
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger("sezonski.image_poster")

try:
    from PIL import Image, ImageDraw, ImageFont
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

CANVAS_W = 1080
CANVAS_H = 1080
MAX_LINES = 8

# Colors
BG_TOP = (71, 131, 191)      # soft blue
BG_BOTTOM = (43, 87, 135)    # darker blue
TEXT_COLOR = (255, 255, 255)
FOOTER_COLOR = (200, 220, 240)


def _make_gradient(draw):
    """Draw vertical gradient background."""
    for y in range(CANVAS_H):
        r = BG_TOP[0] + (BG_BOTTOM[0] - BG_TOP[0]) * y // CANVAS_H
        g = BG_TOP[1] + (BG_BOTTOM[1] - BG_TOP[1]) * y // CANVAS_H
        b = BG_TOP[2] + (BG_BOTTOM[2] - BG_TOP[2]) * y // CANVAS_H
        draw.line([(0, y), (CANVAS_W, y)], fill=(r, g, b))


def _get_font(size):
    """Try to load a font, fallback to default."""
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
        "/usr/local/share/fonts/DejaVuSans.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def _wrap_text(text: str, font, max_width: int, draw) -> list[str]:
    """Wrap text to fit within max_width. Returns list of lines."""
    words = text.split()
    lines = []
    current = ""
    for w in words:
        test = f"{current} {w}".strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        w_w = bbox[2] - bbox[0]
        if w_w <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines[:MAX_LINES]


def _shorten_text(text: str, max_chars: int = 400) -> str:
    """Shorten long text safely."""
    if len(text) <= max_chars:
        return text
    cutoff = text.rfind(" ", 0, max_chars - 3)
    return text[:cutoff] + "..."


def generate_image_post(text: str, footer: str = "Sezonski rad Srbija") -> Optional[bytes]:
    """Generate a 1080x1080 PNG with the given text centered on gradient background.

    Returns PNG bytes, or None if Pillow is unavailable.
    """
    if not PILLOW_AVAILABLE:
        logger.warning("Pillow not available — cannot generate image")
        return None

    img = Image.new("RGB", (CANVAS_W, CANVAS_H))
    draw = ImageDraw.Draw(img)

    # Background
    _make_gradient(draw)

    # Shorten text
    display_text = _shorten_text(text)

    # Try font sizes
    font_size = 70
    font = _get_font(font_size)
    margin = 80
    max_text_w = CANVAS_W - margin * 2

    # Find best font size
    while font_size > 28:
        font = _get_font(font_size)
        wrapped = _wrap_text(display_text, font, max_text_w, draw)
        total_h = len(wrapped) * (font_size + 12)
        if total_h < CANVAS_H * 0.7 and len(wrapped) <= MAX_LINES:
            break
        font_size -= 4

    # Draw text
    wrapped = _wrap_text(display_text, font, max_text_w, draw)
    total_h = len(wrapped) * (font_size + 12)
    start_y = (CANVAS_H - total_h) // 2 - 30

    for i, line in enumerate(wrapped):
        bbox = draw.textbbox((0, 0), line, font=font)
        line_w = bbox[2] - bbox[0]
        x = (CANVAS_W - line_w) // 2
        y = start_y + i * (font_size + 12)
        # Shadow for readability
        draw.text((x + 2, y + 2), line, font=font, fill=(0, 0, 0, 80))
        draw.text((x, y), line, font=font, fill=TEXT_COLOR)

    # Footer
    footer_font = _get_font(30)
    f_bbox = draw.textbbox((0, 0), footer, font=footer_font)
    f_w = f_bbox[2] - f_bbox[0]
    f_x = (CANVAS_W - f_w) // 2
    f_y = CANVAS_H - 80
    draw.text((f_x, f_y), footer, font=footer_font, fill=FOOTER_COLOR)

    # Return PNG bytes
    import io
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.getvalue()


def generate_image_pack(items: list[dict], max_cards: int = 3) -> list[bytes]:
    """Generate image cards from safe queue items.

    Each item dict should have:
        - suggested_text or raw_json.original
        - classification
        - risk_level (exclude high risk)

    Returns list of PNG bytes (max max_cards).
    """
    safe = [i for i in items
            if i.get("risk_level") != "high"
            and i.get("status") not in ("spam_candidate", "spam")]
    images = []
    for i in safe[:max_cards]:
        text = i.get("suggested_text") or i.get("raw_json", {}).get("original", "")
        if text:
            img = generate_image_post(text)
            if img:
                images.append(img)
    return images
