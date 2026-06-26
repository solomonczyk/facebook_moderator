"""Universal LLM client — Anthropic-compatible protocol. Provider-agnostic."""

import time
import json
import logging
from .config import LLMConfig
from .provider import LLMResponse
from .cache import LLMCache
from .validator import extract_json
from .retry import with_retry

logger = logging.getLogger("sezonski.llm.client")

ANTHROPIC_AVAILABLE = False
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    pass


class LLMClient:
    """Provider-agnostic LLM client. Works with any Anthropic-compatible API."""

    def __init__(self, config: LLMConfig | None = None):
        self.config = config or LLMConfig()
        self.config.load_from_env()
        self.cache = LLMCache()
        self._client = None

    @property
    def available(self) -> bool:
        return ANTHROPIC_AVAILABLE and self.config.available

    @property
    def client(self):
        if self._client is None and self.available:
            self._client = anthropic.Anthropic(
                api_key=self.config.api_key,
                base_url=self.config.base_url,
            )
        return self._client

    def generate(self, system_prompt: str, user_message: str) -> LLMResponse:
        """Generate a response. Checks cache first."""
        if not self.available:
            return LLMResponse(success=False, error="LLM not configured")

        # Check cache
        cached = self.cache.get(system_prompt, user_message)
        if cached is not None:
            logger.debug(f"Cache hit: {cached.key[:16]}")
            return LLMResponse(
                success=True,
                parsed_json=cached.response_json,
                model=cached.model,
                tokens_used=cached.tokens_used,
                latency_ms=0.0,
                cache_hit=True,
            )

        # Call LLM
        start = time.time()

        def call_fn(temperature: float = 0.2):
            try:
                resp = self.client.messages.create(
                    model=self.config.model,
                    max_tokens=self.config.max_tokens,
                    temperature=temperature,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_message}],
                )
                raw = ""
                for block in resp.content:
                    if hasattr(block, 'text'):
                        raw += block.text
                tokens = resp.usage.input_tokens + resp.usage.output_tokens if hasattr(resp, 'usage') else 0
                latency = (time.time() - start) * 1000
                return LLMResponse(
                    success=True,
                    raw_text=raw,
                    model=self.config.model,
                    tokens_used=tokens,
                    latency_ms=latency,
                )
            except Exception as e:
                return LLMResponse(
                    success=False,
                    error=str(e),
                    latency_ms=(time.time() - start) * 1000,
                )

        result = with_retry(call_fn, extract_json)

        if result["success"]:
            # Cache successful result
            self.cache.set(
                system_prompt, user_message,
                result["parsed"], result.get("model", ""),
                result.get("tokens_used", 0),
            )
            return LLMResponse(
                success=True,
                raw_text=result.get("raw_text", ""),
                parsed_json=result["parsed"],
                model=result.get("model", ""),
                tokens_used=result.get("tokens_used", 0),
                latency_ms=result.get("latency_ms", 0),
                retry_count=result.get("retry_count", 0),
            )

        return LLMResponse(
            success=False,
            error=result.get("error", "Unknown"),
            raw_text=result.get("raw_text", ""),
            latency_ms=result.get("latency_ms", 0),
            retry_count=result.get("retry_count", 0),
        )

    def get_status(self) -> dict:
        return {
            "provider": self.config.provider,
            "model": self.config.model,
            "available": self.available,
            "cache_size": self.cache.size,
            "cache_hit_rate": round(self.cache.hit_rate, 3),
        }
