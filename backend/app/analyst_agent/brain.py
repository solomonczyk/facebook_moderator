"""Analyst brain: deterministic classifier with JSON output format.

In production, this could be replaced with an LLM call that returns
the same JSON schema. The policy engine validates ALL output regardless
of source (rule-based or LLM).
"""

import json
import re
from dataclasses import dataclass, field


# ── JSON Output Schema ─────────────────────────────────────────────────────

@dataclass
class AnalystDecision:
    action: str = "escalate_to_operator"
    confidence: float = 0.0
    risk_level: str = "medium"
    reasoning: str = ""
    extracted_entities: dict = field(default_factory=dict)
    suggested_reply: str = ""
    flags: list[str] = field(default_factory=list)
    requires_operator: bool = True

    def to_json(self) -> str:
        return json.dumps({
            "action": self.action,
            "confidence": self.confidence,
            "risk_level": self.risk_level,
            "reasoning": self.reasoning,
            "extracted_entities": self.extracted_entities,
            "suggested_reply": self.suggested_reply,
            "flags": self.flags,
            "requires_operator": self.requires_operator,
        }, ensure_ascii=False)

    @classmethod
    def from_json(cls, raw: str) -> "AnalystDecision":
        """Parse JSON output. This is the prompt injection defense point:
        we parse structured JSON, not free text commands."""
        try:
            # Strip any markdown fences
            text = raw.strip()
            if text.startswith("```"):
                text = re.sub(r'^```\w*\n?', '', text)
                text = re.sub(r'\n?```$', '', text)
            data = json.loads(text)

            # Validate required fields exist
            decision = cls(
                action=str(data.get("action", "escalate_to_operator")),
                confidence=float(data.get("confidence", 0.0)),
                risk_level=str(data.get("risk_level", "medium")),
                reasoning=str(data.get("reasoning", "")),
                extracted_entities=data.get("extracted_entities", {}),
                suggested_reply=str(data.get("suggested_reply", "")),
                flags=[str(f) for f in data.get("flags", [])],
                requires_operator=bool(data.get("requires_operator", True)),
            )

            # Clamp confidence to [0, 1]
            decision.confidence = max(0.0, min(1.0, decision.confidence))

            # Validate risk_level
            if decision.risk_level not in ("low", "medium", "high", "reject"):
                decision.risk_level = "medium"

            return decision
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            return cls(
                action="escalate_to_operator",
                confidence=0.0,
                risk_level="high",
                reasoning=f"Failed to parse decision JSON: {e}",
                requires_operator=True,
            )


# ── Deterministic Classifier (MVP — replace with LLM in production) ────────

def analyze_queue_item(item: dict) -> AnalystDecision:
    """Analyze a queue item and return a decision. Uses deterministic rules
    for the MVP. The same JSON schema works for LLM-based analysis."""

    action_type = item.get("action_type", "")
    suggested_text = item.get("suggested_text", "")

    # Worker lead detection — check action_type AND text patterns
    worker_text_signals = ["grupu", "grupa", "ekipa", "ljudi sa", "radnika sa", "prevozom"]
    has_worker_signal = (
        "worker" in action_type
        or "worker" in suggested_text.lower()
        or any(s in suggested_text.lower() for s in worker_text_signals)
    )
    if has_worker_signal:
        count = _extract_worker_count(suggested_text)
        has_contact = bool(re.search(r'0\d{1,2}[\s/-]?\d{2,4}', suggested_text))
        has_transport = bool(re.search(r'(?:prevoz|kombi|auto|voz)', suggested_text.lower()))

        missing_count = sum([not has_contact, not has_transport])

        if count and has_contact:
            return AnalystDecision(
                action="save_worker_lead",
                confidence=0.90,
                risk_level="low",
                reasoning=f"Worker group of {count} with contact. Save as lead.",
                extracted_entities={"worker_count": count, "has_contact": True, "has_transport": has_transport},
                suggested_reply=_build_missing_info_reply(missing=["phone" if not has_contact else None, "job_type", "availability"]),
                flags=[],
                requires_operator=False,
            )
        elif count:
            return AnalystDecision(
                action="ask_missing_info_draft",
                confidence=0.75,
                risk_level="low",
                reasoning=f"Worker group of {count} without contact. Draft missing-info reply.",
                extracted_entities={"worker_count": count, "has_contact": False},
                suggested_reply=_build_missing_info_reply(missing=["phone", "job_type", "availability"]),
                flags=["missing_contact"],
                requires_operator=False,
            )

    # Spam detection
    spam_signals = ["brza zarada", "kazino", "kripto", "klikni", "laka zarada"]
    spam_count = sum(1 for s in spam_signals if s in suggested_text.lower())
    if spam_count >= 2:
        return AnalystDecision(
            action="mark_spam_candidate",
            confidence=0.95,
            risk_level="high",
            reasoning=f"Detected {spam_count} spam signals. Mark as spam candidate.",
            flags=["spam_detected"],
            requires_operator=True,
        )

    # Job lead detection
    job_signals = ["tražim", "potrebni", "radnici", "radnice", "zapošljavam", "firma"]
    has_job = any(s in suggested_text.lower() for s in job_signals)
    has_location = bool(re.search(r'(?:Arilje|Ivanjica|Čačak|Beograd|Novi Sad|Subotica|Sombor|Srem|Vojvodina|Šumadija)', suggested_text, re.IGNORECASE))
    has_phone = bool(re.search(r'0\d{1,2}[\s/-]?\d{2,4}', suggested_text))

    if has_job and has_location and has_phone:
        return AnalystDecision(
            action="save_job_lead",
            confidence=0.85,
            risk_level="low",
            reasoning="Job lead with location and contact. Save.",
            extracted_entities={"has_location": True, "has_contact": True},
            flags=[],
            requires_operator=False,
        )
    elif has_job:
        return AnalystDecision(
            action="ask_missing_info_draft",
            confidence=0.70,
            risk_level="low",
            reasoning="Job lead missing location or contact. Draft missing-info.",
            extracted_entities={"has_location": has_location, "has_contact": has_phone},
            flags=["missing_info"] if not has_phone else [],
            requires_operator=False,
        )

    # Digest-related
    if "digest" in action_type:
        return AnalystDecision(
            action="generate_digest_draft",
            confidence=0.90,
            risk_level="low",
            reasoning="Digest-related queue item. Generate draft.",
            flags=[],
            requires_operator=False,
        )

    # Default: escalate
    return AnalystDecision(
        action="escalate_to_operator",
        confidence=0.50,
        risk_level="medium",
        reasoning=f"No clear autonomous path for action_type='{action_type}'. Escalate.",
        flags=["unclear_intent"],
        requires_operator=True,
    )


def _extract_worker_count(text: str) -> int | None:
    match = re.search(r'(\d+)\s*(?:ljudi|radnika|ljude|članova|osoba)', text.lower())
    return int(match.group(1)) if match else None


def _build_missing_info_reply(missing: list) -> str:
    fields = [m for m in missing if m]
    if not fields:
        return ""
    lines = ["Molimo vas da dopunite informacije:"]
    for f in fields:
        lines.append(f"- {f}")
    return "\n".join(lines)
