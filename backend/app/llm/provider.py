"""LLM Provider abstraction — Anthropic-compatible protocol."""

from dataclasses import dataclass


@dataclass
class LLMResponse:
    success: bool
    raw_text: str = ""
    parsed_json: dict | None = None
    error: str = ""
    model: str = ""
    tokens_used: int = 0
    latency_ms: float = 0.0
    cache_hit: bool = False
    retry_count: int = 0
