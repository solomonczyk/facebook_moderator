"""OCR and text extraction from screenshots.

Primary: Direct DOM text extraction (done during screenshot capture).
Fallback: pytesseract OCR on saved screenshot images.
"""

import os
import hashlib
import logging
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional

from .config import PublicIntakeConfig

logger = logging.getLogger("sezonski.public_intake.ocr")


@dataclass
class ExtractedCandidate:
    source_url: str
    group_name: str
    screenshot_path: str
    raw_text: str
    extracted_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    status: str = "unverified_public_source"
    text_hash: str = ""
    candidate_id: str = ""

    def __post_init__(self):
        if not self.text_hash:
            self.text_hash = hashlib.sha256(
                (self.raw_text.strip() + self.source_url).encode()
            ).hexdigest()[:16]
        if not self.candidate_id:
            self.candidate_id = f"pub_{self.text_hash[:12]}"

    def to_dict(self) -> dict:
        return {
            "candidate_id": self.candidate_id,
            "source_url": self.source_url,
            "group_name": self.group_name,
            "screenshot_path": self.screenshot_path,
            "raw_text": self.raw_text[:500],
            "raw_text_length": len(self.raw_text),
            "extracted_at": self.extracted_at,
            "status": self.status,
            "text_hash": self.text_hash,
        }


class OCRExtractor:
    """Extracts text candidates from screenshots and DOM text content."""

    def __init__(self, config: PublicIntakeConfig | None = None):
        self.config = config or PublicIntakeConfig()

    def extract_from_screenshots(
        self, screenshot_results: list, group_name: str, source_url: str
    ) -> list[ExtractedCandidate]:
        """Extract text candidates from screenshot results.

        Uses DOM-extracted text (already captured during screenshot).
        Falls back to OCR on the image file if needed.
        """
        candidates: list[ExtractedCandidate] = []

        for sr in screenshot_results:
            if not sr.success:
                continue

            # Primary: use DOM-extracted text from the screenshotter
            if sr.text_content and len(sr.text_content.strip()) > 50:
                # Split long text into individual post candidates
                posts = self._split_into_posts(sr.text_content)
                for post_text in posts:
                    if len(post_text.strip()) > 30:
                        candidate = ExtractedCandidate(
                            source_url=source_url,
                            group_name=group_name,
                            screenshot_path=sr.path,
                            raw_text=post_text.strip(),
                        )
                        candidates.append(candidate)
            else:
                # Fallback: OCR the image
                ocr_text = self._ocr_image(sr.path)
                if ocr_text and len(ocr_text.strip()) > 20:
                    candidate = ExtractedCandidate(
                        source_url=source_url,
                        group_name=group_name,
                        screenshot_path=sr.path,
                        raw_text=ocr_text.strip(),
                    )
                    candidates.append(candidate)

        return candidates

    def _split_into_posts(self, text: str) -> list[str]:
        """Split page text into individual post candidates."""
        # Split by common Facebook post separators
        separators = ["\n---\n", "\n——\n", "\n___\n", "\n\n\n"]
        for sep in separators:
            if sep in text:
                parts = [p.strip() for p in text.split(sep) if p.strip()]
                if len(parts) > 1:
                    return parts

        # If no clear separators, split by double newlines
        # but keep chunks reasonably sized
        chunks = text.split("\n\n")
        if len(chunks) <= 1:
            return [text]

        result = []
        current = ""
        for chunk in chunks:
            if len(current) + len(chunk) < 1000:
                current += "\n" + chunk if current else chunk
            else:
                if current.strip():
                    result.append(current.strip())
                current = chunk
        if current.strip():
            result.append(current.strip())

        return result if result else [text]

    def _ocr_image(self, image_path: str) -> str:
        """Fallback OCR using pytesseract on saved screenshot."""
        try:
            from PIL import Image
            import pytesseract

            img = Image.open(image_path)
            # Convert to grayscale for better OCR
            img = img.convert("L")
            text = pytesseract.image_to_string(img, lang="srp+eng+rus")
            return text
        except ImportError:
            logger.debug("pytesseract not available for OCR fallback")
            return ""
        except Exception as e:
            logger.warning(f"OCR failed for {image_path}: {e}")
            return ""

    def save_candidates(self, candidates: list[ExtractedCandidate]) -> str:
        """Save extracted candidates to JSON file. Returns file path."""
        import json
        os.makedirs(self.config.extracted_dir, exist_ok=True)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(self.config.extracted_dir, f"candidates_{timestamp}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump([c.to_dict() for c in candidates], f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(candidates)} candidates to {filepath}")
        return filepath
