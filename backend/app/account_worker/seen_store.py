"""Seen store: deduplicates content by SHA256 hash."""

from collections import OrderedDict


class SeenStore:
    def __init__(self, max_items: int = 1000):
        self._hashes: OrderedDict[str, str] = OrderedDict()  # hash -> item_id
        self.max_items = max_items

    def is_new(self, content_hash: str) -> bool:
        return content_hash not in self._hashes

    def mark_seen(self, content_hash: str, item_id: str) -> None:
        if len(self._hashes) >= self.max_items:
            self._hashes.popitem(last=False)
        self._hashes[content_hash] = item_id

    def filter_new(self, items: list) -> list:
        """Return only items whose hashes haven't been seen."""
        new_items = []
        for item in items:
            if self.is_new(item.content_hash):
                new_items.append(item)
                self.mark_seen(item.content_hash, item.item_id)
        return new_items

    @property
    def count(self) -> int:
        return len(self._hashes)

    def recent(self, n: int = 20) -> list[dict]:
        items = list(self._hashes.items())[-n:]
        return [{"hash": h, "item_id": iid} for h, iid in items]
