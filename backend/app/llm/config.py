"""LLM configuration from environment variables. Provider-agnostic."""

import os
from dataclasses import dataclass


@dataclass
class LLMConfig:
    provider: str = "deepseek"
    base_url: str = "https://api.deepseek.com/anthropic"
    model: str = "DeepSeek-V4-Pro"
    api_key: str = ""
    max_tokens: int = 2000
    temperature: float = 0.2
    timeout_seconds: int = 15

    def load_from_env(self) -> None:
        self.provider = os.getenv("LLM_PROVIDER", self.provider)
        self.base_url = os.getenv("LLM_BASE_URL", self.base_url)
        self.model = os.getenv("LLM_MODEL", self.model)
        self.api_key = os.getenv("LLM_API_KEY", os.getenv("ANTHROPIC_API_KEY", ""))
        self.max_tokens = int(os.getenv("LLM_MAX_TOKENS", str(self.max_tokens)))
        self.temperature = float(os.getenv("LLM_TEMPERATURE", str(self.temperature)))
        self.timeout_seconds = int(os.getenv("LLM_TIMEOUT", str(self.timeout_seconds)))

    @property
    def available(self) -> bool:
        return bool(self.api_key)
