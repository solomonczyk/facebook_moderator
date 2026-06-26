"""LLM client for the Runtime Manager Agent. Uses Anthropic Claude API."""

import os
import json
import logging
from dataclasses import dataclass

logger = logging.getLogger("sezonski.llm")

ANTHROPIC_AVAILABLE = False
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    pass


@dataclass
class LLMResponse:
    success: bool
    raw_text: str = ""
    parsed_json: dict | None = None
    error: str = ""
    model: str = ""
    tokens_used: int = 0


class LLMClient:
    def __init__(self):
        self._client = None
        self._model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
        self._max_tokens = int(os.getenv("ANTHROPIC_MAX_TOKENS", "2000"))

    @property
    def available(self) -> bool:
        return ANTHROPIC_AVAILABLE and bool(os.getenv("ANTHROPIC_API_KEY"))

    @property
    def client(self):
        if self._client is None and self.available:
            self._client = anthropic.Anthropic(
                api_key=os.getenv("ANTHROPIC_API_KEY"),
            )
        return self._client

    def call(self, system_prompt: str, user_message: str,
             temperature: float = 0.3) -> LLMResponse:
        """Call the LLM and return parsed JSON response."""
        if not self.available:
            return LLMResponse(
                success=False,
                error="LLM not available. Set ANTHROPIC_API_KEY or install anthropic package.",
            )

        try:
            response = self.client.messages.create(
                model=self._model,
                max_tokens=self._max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
            )

            raw_text = ""
            for block in response.content:
                if hasattr(block, 'text'):
                    raw_text += block.text

            # Parse JSON from response
            parsed = self._extract_json(raw_text)

            if parsed is None:
                # One retry with stricter prompt
                retry_msg = user_message + "\n\nIMPORTANT: Return ONLY valid JSON. No markdown. No extra text."
                response2 = self.client.messages.create(
                    model=self._model,
                    max_tokens=self._max_tokens,
                    temperature=0.1,
                    system=system_prompt,
                    messages=[{"role": "user", "content": retry_msg}],
                )
                raw_text2 = ""
                for block in response2.content:
                    if hasattr(block, 'text'):
                        raw_text2 += block.text
                parsed = self._extract_json(raw_text2)
                if parsed is None:
                    return LLMResponse(
                        success=False,
                        raw_text=raw_text2,
                        error="LLM returned invalid JSON after retry",
                        model=self._model,
                    )
                raw_text = raw_text2

            return LLMResponse(
                success=True,
                raw_text=raw_text,
                parsed_json=parsed,
                model=self._model,
                tokens_used=response.usage.input_tokens + response.usage.output_tokens if hasattr(response, 'usage') else 0,
            )

        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return LLMResponse(success=False, error=str(e))

    @staticmethod
    def _extract_json(text: str) -> dict | None:
        """Extract JSON object from LLM response text."""
        text = text.strip()
        # Remove markdown fences
        if text.startswith("```"):
            lines = text.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines)

        # Find first { and last }
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except json.JSONDecodeError:
                pass
        return None
