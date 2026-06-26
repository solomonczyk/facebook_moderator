"""FB Group Runtime Manager Agent V2 — DeepSeek-powered primary brain.

Multi-step pipeline:
  1. Preprocess — normalize text, detect language
  2. Analyze — DeepSeek LLM call (primary) or rule-based (fallback)
  3. Validate — JSON schema check, business rules, forbidden words
  4. Normalize — clamp confidence, fix invalid fields, final checks
  5. Queue — create queue item with full decision
"""

import os
import logging
from datetime import datetime

from ..llm.client import LLMClient
from ..llm.config import LLMConfig
from ..schemas.runtime_manager import AgentDecision, ExtractedFields, FORBIDDEN_WORDS
from ..runtime_agent.brain import classify as rule_classify
from ..runtime_agent.brain import ContentClass

logger = logging.getLogger("sezonski.manager")

PROMPT_PATH = os.path.join(os.path.dirname(__file__), "prompts", "facebook_runtime_manager.md")
_SYSTEM_PROMPT: str | None = None


def _load_prompt() -> str:
    global _SYSTEM_PROMPT
    if _SYSTEM_PROMPT is None:
        try:
            with open(PROMPT_PATH, "r", encoding="utf-8") as f:
                _SYSTEM_PROMPT = f.read()
        except FileNotFoundError:
            _SYSTEM_PROMPT = "You are the AI manager for Sezonski rad Srbija. Return valid JSON only."
    return _SYSTEM_PROMPT


class FacebookGroupRuntimeManagerAgent:
    """LLM-first runtime manager. Falls back to rule-based only if LLM fails."""

    def __init__(self, config: LLMConfig | None = None):
        self.llm = LLMClient(config)
        self._decisions_count: int = 0
        self._llm_used_count: int = 0
        self._fallback_count: int = 0
        self._cache_hits: int = 0

    @property
    def llm_available(self) -> bool:
        return self.llm.available

    # ── Public API ──────────────────────────────────────────────────────────

    def analyze(self, input_data: dict) -> AgentDecision:
        """Main entry point: preprocess -> analyze -> validate -> normalize."""
        raw_text = input_data.get("raw_text", "")
        source_label = input_data.get("source_label", "")
        operator_note = input_data.get("operator_note", "")

        # Step 1: Preprocess
        preprocessed = self._preprocess(raw_text)

        # Step 2: Primary analysis (LLM first, fallback if needed)
        decision = self._analyze_llm(preprocessed, source_label, operator_note)
        if decision is None:
            self._fallback_count += 1
            decision = self._analyze_fallback(input_data)
        else:
            self._llm_used_count += 1

        # Step 3: Validate business rules
        decision = self._validate_business_rules(decision)

        # Step 4: Normalize
        decision = self._normalize(decision)

        self._decisions_count += 1
        return decision

    # ── Pipeline Steps ──────────────────────────────────────────────────────

    def _preprocess(self, text: str) -> str:
        """Normalize text, strip excessive whitespace, basic cleanup."""
        return text.strip()

    def _analyze_llm(self, text: str, source_label: str, operator_note: str) -> AgentDecision | None:
        """Call DeepSeek/LLM for primary analysis."""
        if not self.llm.available:
            return None

        user_msg = f"Analyze this post for the Sezonski rad Srbija Facebook group:\n\n"
        if source_label:
            user_msg += f"Source: {source_label}\n"
        if operator_note:
            user_msg += f"Operator note: {operator_note}\n"
        user_msg += f"\nPOST TEXT:\n{text}\n\nReturn valid JSON only."

        response = self.llm.generate(_load_prompt(), user_msg)

        if response.cache_hit:
            self._cache_hits += 1

        if not response.success or response.parsed_json is None:
            logger.warning(
                f"LLM failed: {response.error}, retries={response.retry_count}, "
                f"latency={response.latency_ms:.0f}ms"
            )
            return None

        try:
            data = response.parsed_json
            fields_data = data.get("fields", {}) if isinstance(data.get("fields"), dict) else {}

            decision = AgentDecision(
                classification=str(data.get("classification", "unclear")),
                confidence=float(data.get("confidence", 0.7)),
                risk_level=str(data.get("risk_level", "medium")),
                recommended_action=str(data.get("recommended_action", "escalate")),
                digest_candidate=bool(data.get("digest_candidate", False)),
                public_post_allowed=bool(data.get("public_post_allowed", False)),
                fields=ExtractedFields(
                    **{k: v for k, v in fields_data.items() if k in ExtractedFields.model_fields}
                ),
                missing_info=data.get("missing_info", []) if isinstance(data.get("missing_info"), list) else [],
                risk_flags=data.get("risk_flags", []) if isinstance(data.get("risk_flags"), list) else [],
                operator_summary=str(data.get("operator_summary", ""))[:500],
                prepared_public_text=str(data.get("prepared_public_text", ""))[:2000],
                prepared_reply_to_author=str(data.get("prepared_reply_to_author", ""))[:1000],
                reason=str(data.get("reason", ""))[:300],
            )
            return decision
        except Exception as e:
            logger.error(f"Failed to construct AgentDecision from LLM output: {e}")
            return None

    def _analyze_fallback(self, input_data: dict) -> AgentDecision:
        """Rule-based fallback when LLM is unavailable."""
        raw_text = input_data.get("raw_text", "")
        result = rule_classify(raw_text)

        class_map = {
            ContentClass.EMPLOYER_JOB_POST: "employer_job_post",
            ContentClass.WORKER_LOOKING_FOR_JOB: "worker_request",
            ContentClass.WORKER_GROUP_AVAILABLE: "worker_group_available",
            ContentClass.EXPERIENCE_REVIEW: "review_experience",
            ContentClass.WORKER_QUESTION: "question",
            ContentClass.EMPLOYER_QUESTION: "question",
            ContentClass.SPAM: "spam",
            ContentClass.SUSPICIOUS: "suspicious",
            ContentClass.IRRELEVANT: "irrelevant",
            ContentClass.NEEDS_OPERATOR_REVIEW: "unclear",
        }
        classification = class_map.get(result.classification, "unclear")
        entities = result.extracted_entities

        fields = ExtractedFields(
            job_type="sezonski rad" if classification == "employer_job_post" else None,
            location=entities.get("locations", [None])[0] if entities.get("locations") else None,
            workers_needed=entities.get("workers_count"),
            accommodation="da" if entities.get("accommodation") else None,
            food="da" if entities.get("food") else None,
            contact=input_data.get("raw_text", "") if entities.get("contact_status") == "present" else None,
        )

        missing = [f for f in ["plata / dnevnica", "smeštaj", "hrana", "radno vreme", "kontakt"]
                   if not getattr(fields, f.replace(" / ", "_").replace("plata", "pay"), None)]

        is_spam = classification == "spam"
        is_suspicious = classification == "suspicious"

        return AgentDecision(
            classification=classification,
            confidence=0.45,
            risk_level="high" if (is_spam or is_suspicious) else "medium",
            recommended_action="escalate",
            digest_candidate=not is_spam and not is_suspicious and bool(fields.location),
            public_post_allowed=not is_spam and not is_suspicious,
            fields=fields,
            missing_info=missing,
            risk_flags=["fallback_mode", "low_confidence"],
            operator_summary=f"[FALLBACK] {classification}. Tekst: {raw_text[:100]}...",
            prepared_public_text=result.suggested_reply or "",
            prepared_reply_to_author=result.suggested_reply or "",
            reason="Fallback rule-based (LLM unavailable)",
        )

    def _validate_business_rules(self, decision: AgentDecision) -> AgentDecision:
        """Apply business rules: forbidden words, disclaimer, confidence thresholds."""
        # Check forbidden words
        forbidden = decision.has_forbidden_words()
        if forbidden:
            decision.risk_flags.append(f"forbidden_words:{','.join(forbidden)}")
            for word in forbidden:
                decision.prepared_public_text = decision.prepared_public_text.replace(word, "[UKLONJENO]")
                decision.prepared_reply_to_author = decision.prepared_reply_to_author.replace(word, "[UKLONJENO]")

        # Spam/Suspicious NEVER publish
        if decision.classification in ("spam", "suspicious"):
            decision.digest_candidate = False
            decision.public_post_allowed = False

        # Ensure disclaimer for publishable content
        if decision.public_post_allowed and "Grupa nije poslodavac" not in decision.prepared_public_text:
            decision.prepared_public_text += (
                "\n\nNapomena: Grupa nije poslodavac i ne garantuje uslove. "
                "Oglasi su pronađeni kao javne objave ili su prosleđeni grupi. "
                "Pre odlaska obavezno proverite platu, smeštaj, hranu, radno vreme, "
                "prevoz i način isplate direktno sa osobom iz oglasa."
            )

        return decision

    def _normalize(self, decision: AgentDecision) -> AgentDecision:
        """Final normalization: confidence thresholds, missing info cleanup."""
        # Confidence < 0.60 -> escalate
        if decision.confidence < 0.60:
            decision.recommended_action = "escalate"
            decision.risk_flags.append("low_confidence_escalated")

        return decision

    def get_status(self) -> dict:
        llm_status = self.llm.get_status()
        return {
            **llm_status,
            "llm_primary": self.llm_available,
            "fallback_active": not self.llm_available,
            "regex_only_mode": not self.llm_available,
            "decisions_made": self._decisions_count,
            "llm_used": self._llm_used_count,
            "fallback_used": self._fallback_count,
            "cache_hits": self._cache_hits,
        }
