"""Retry logic for LLM calls with exponential backoff."""

import time
import logging

logger = logging.getLogger("sezonski.llm.retry")

MAX_RETRIES = 1
RETRY_DELAY_SECONDS = 0.5


def with_retry(call_fn, validator_fn, max_retries: int = MAX_RETRIES) -> dict:
    """Call LLM, validate JSON, retry once if invalid. Returns result dict."""
    last_error = ""
    last_raw = ""

    for attempt in range(max_retries + 1):
        response = call_fn(temperature=0.2 if attempt == 0 else 0.1)

        if not response.success:
            last_error = response.error
            if attempt < max_retries:
                time.sleep(RETRY_DELAY_SECONDS)
            continue

        # Try to extract JSON
        parsed = validator_fn(response.raw_text)
        if parsed is not None:
            return {
                "success": True,
                "parsed": parsed,
                "raw_text": response.raw_text,
                "model": response.model,
                "tokens_used": response.tokens_used,
                "latency_ms": response.latency_ms,
                "retry_count": attempt,
            }

        last_error = "Invalid JSON in response"
        last_raw = response.raw_text
        if attempt < max_retries:
            time.sleep(RETRY_DELAY_SECONDS)

    return {
        "success": False,
        "error": last_error,
        "raw_text": last_raw,
        "retry_count": max_retries,
    }
