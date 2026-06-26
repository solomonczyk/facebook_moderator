"""Short-term memory for conversation context."""

from collections import OrderedDict


class AgentMemory:
    def __init__(self, max_items: int = 100):
        self._storage: OrderedDict[str, dict] = OrderedDict()
        self.max_items = max_items

    def remember(self, key: str, data: dict) -> None:
        if len(self._storage) >= self.max_items:
            self._storage.popitem(last=False)
        self._storage[key] = data

    def recall(self, key: str) -> dict | None:
        return self._storage.get(key)

    def forget(self, key: str) -> None:
        self._storage.pop(key, None)

    def recent(self, n: int = 10) -> list[dict]:
        return list(self._storage.values())[-n:]
