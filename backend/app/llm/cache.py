"""SHA256 cache for LLM responses. Avoids duplicate API calls."""

import hashlib
from collections import OrderedDict
from dataclasses import dataclass


@dataclass
class CacheEntry:
    key: str
    response_json: dict
    model: str
    tokens_used: int


class LLMCache:
    def __init__(self, max_size: int = 500):
        self._store: OrderedDict[str, CacheEntry] = OrderedDict()
        self.max_size = max_size
        self._hits: int = 0
        self._misses: int = 0

    def _make_key(self, system_prompt: str, user_message: str) -> str:
        combined = system_prompt + "|||" + user_message
        return hashlib.sha256(combined.encode()).hexdigest()

    def get(self, system_prompt: str, user_message: str) -> CacheEntry | None:
        key = self._make_key(system_prompt, user_message)
        entry = self._store.get(key)
        if entry:
            self._hits += 1
            return entry
        self._misses += 1
        return None

    def set(self, system_prompt: str, user_message: str,
            response_json: dict, model: str = "", tokens_used: int = 0) -> None:
        key = self._make_key(system_prompt, user_message)
        if len(self._store) >= self.max_size:
            self._store.popitem(last=False)
        self._store[key] = CacheEntry(
            key=key, response_json=response_json,
            model=model, tokens_used=tokens_used,
        )

    @property
    def hit_rate(self) -> float:
        total = self._hits + self._misses
        return self._hits / total if total > 0 else 0.0

    @property
    def size(self) -> int:
        return len(self._store)
