"""JSON validator for LLM responses. Extracts and validates structured output."""

import json
import re
import logging

logger = logging.getLogger("sezonski.llm.validator")


def extract_json(text: str) -> dict | None:
    """Extract the first valid JSON object from LLM output text."""
    text = text.strip()

    # Remove markdown fences
    if text.startswith("```"):
        lines = text.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines)

    # Find JSON boundaries
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end <= start:
        return None

    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        pass

    # Try fixing common issues
    try:
        cleaned = re.sub(r',\s*}', '}', text[start:end + 1])
        cleaned = re.sub(r',\s*]', ']', cleaned)
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    return None


def validate_schema(data: dict, required_fields: list[str] | None = None) -> list[str]:
    """Validate that required fields exist. Returns list of missing fields."""
    if required_fields is None:
        required_fields = ["classification", "risk_level", "recommended_action"]
    return [f for f in required_fields if f not in data]
