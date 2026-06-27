"""Deduplication for public intake candidates.

SHA256-based dedup. Checks text similarity to avoid re-processing.
"""

import hashlib
import logging
from datetime import datetime

logger = logging.getLogger("sezonski.public_intake.dedup")


class Deduplicator:
    """Tracks seen candidates to prevent duplicate processing."""

    def __init__(self):
        self._seen_hashes: set[str] = set()
        self._seen_prefixes: list[str] = []  # Recent text prefixes for similarity check
        self._seen_urls: set[str] = set()
        self._duplicates_skipped: int = 0

    def is_duplicate(self, text: str, source_url: str = "") -> bool:
        """Check if this text+URL combination has been seen before."""
        normalized = " ".join(text.lower().split())
        content_hash = hashlib.sha256(
            (normalized + source_url).encode()
        ).hexdigest()

        # Check exact match
        if content_hash in self._seen_hashes:
            self._duplicates_skipped += 1
            logger.debug(f"Duplicate skipped (hash: {content_hash[:12]}...)")
            return True

        # Check text similarity (first 150 chars) against recent entries
        prefix = normalized[:150]
        if len(prefix) >= 80:
            for seen_prefix in list(self._seen_prefixes)[-500:]:
                if prefix == seen_prefix:
                    self._duplicates_skipped += 1
                    logger.debug(f"Duplicate text skipped (prefix match)")
                    return True

        return False

    def mark_seen(self, text: str, source_url: str = "") -> str:
        """Mark a candidate as seen. Returns the hash."""
        normalized = " ".join(text.lower().split())
        content_hash = hashlib.sha256(
            (normalized + source_url).encode()
        ).hexdigest()
        self._seen_hashes.add(content_hash)
        prefix = normalized[:150]
        if len(prefix) >= 80:
            self._seen_prefixes.append(prefix)
            if len(self._seen_prefixes) > 500:
                self._seen_prefixes = self._seen_prefixes[-500:]
        if source_url:
            self._seen_urls.add(source_url)
        return content_hash

    def mark_seen_by_hash(self, text_hash: str) -> None:
        """Mark a hash as seen (used for ExtractedCandidate.text_hash)."""
        self._seen_hashes.add(text_hash)

    @property
    def seen_count(self) -> int:
        return len(self._seen_hashes)

    @property
    def duplicates_skipped(self) -> int:
        return self._duplicates_skipped
