"""Facebook Group Runtime Manager Agent V1.

LLM-powered agent for managing the "Sezonski rad Srbija" Facebook group.
Uses Claude API for classification, field extraction, and text generation.
Falls back to rule-based classifier when LLM is unavailable.
"""

import os
import logging
from datetime import datetime

from ..services.llm_client import LLMClient, LLMResponse
from ..schemas.runtime_manager import AgentDecision, ExtractedFields
from ..runtime_agent.brain import classify as rule_classify
from ..runtime_agent.brain import ContentClass

logger = logging.getLogger("sezonski.manager")

# Load system prompt at module level
PROMPT_PATH = os.path.join(os.path.dirname(__file__), "prompts", "facebook_runtime_manager.md")
_SYSTEM_PROMPT: str | None = None


def _load_prompt() -> str:
    global _SYSTEM_PROMPT
    if _SYSTEM_PROMPT is None:
        try:
            with open(PROMPT_PATH, "r", encoding="utf-8") as f:
                _SYSTEM_PROMPT = f.read()
        except FileNotFoundError:
            _SYSTEM_PROMPT = "You are the AI manager for Sezonski rad Srbija Facebook group. Return valid JSON."
    return _SYSTEM_PROMPT


class FacebookGroupRuntimeManagerAgent:
    def __init__(self):
        self.llm = LLMClient()
        self._decisions_count = 0

    @property
    def llm_available(self) -> bool:
        return self.llm.available

    def analyze(self, input_data: dict) -> AgentDecision:
        """Main analysis pipeline: LLM -> validate -> fallback if needed."""
        raw_text = input_data.get("raw_text", "")
        source_label = input_data.get("source_label", "")
        operator_note = input_data.get("operator_note", "")

        # Build user message
        user_msg = f"Analyze this post for the Sezonski rad Srbija Facebook group:\n\n"
        if source_label:
            user_msg += f"Source: {source_label}\n"
        if operator_note:
            user_msg += f"Operator note: {operator_note}\n"
        user_msg += f"\nPOST TEXT:\n{raw_text}\n\nReturn valid JSON only."

        decision = None

        # Try LLM first
        if self.llm_available:
            response = self.llm.call(_load_prompt(), user_msg)
            if response.success and response.parsed_json:
                decision = self._validate_llm_response(response)
            else:
                logger.warning(f"LLM failed: {response.error}. Falling back to rule-based.")
        else:
            logger.info("LLM not available. Using rule-based classifier.")

        # Fallback to rule-based
        if decision is None:
            decision = self._rule_based_fallback(input_data)

        self._decisions_count += 1
        return decision

    def _validate_llm_response(self, response: LLMResponse) -> AgentDecision | None:
        """Validate and clean LLM JSON output. Returns None if invalid."""
        try:
            data = response.parsed_json
            if not isinstance(data, dict):
                return None

            # Ensure fields dict exists
            fields_data = data.get("fields", {})
            if not isinstance(fields_data, dict):
                fields_data = {}

            decision = AgentDecision(
                classification=str(data.get("classification", "unclear")),
                confidence=float(data.get("confidence", 0.5)),
                risk_level=str(data.get("risk_level", "medium")),
                recommended_action=str(data.get("recommended_action", "escalate")),
                digest_candidate=bool(data.get("digest_candidate", False)),
                public_post_allowed=bool(data.get("public_post_allowed", False)),
                fields=ExtractedFields(**{k: v for k, v in fields_data.items() if k in ExtractedFields.model_fields}),
                missing_info=data.get("missing_info", []) if isinstance(data.get("missing_info"), list) else [],
                risk_flags=data.get("risk_flags", []) if isinstance(data.get("risk_flags"), list) else [],
                operator_summary=str(data.get("operator_summary", ""))[:500],
                prepared_public_text=str(data.get("prepared_public_text", ""))[:2000],
                prepared_reply_to_author=str(data.get("prepared_reply_to_author", ""))[:1000],
                reason=str(data.get("reason", ""))[:300],
            )

            # Check forbidden words
            forbidden = decision.has_forbidden_words()
            if forbidden:
                decision.risk_flags.append(f"forbidden_words: {','.join(forbidden)}")
                # Clean the text
                for word in forbidden:
                    decision.prepared_public_text = decision.prepared_public_text.replace(word, "[UKLONJENO]")
                    decision.prepared_reply_to_author = decision.prepared_reply_to_author.replace(word, "[UKLONJENO]")

            return decision
        except Exception as e:
            logger.error(f"LLM response validation failed: {e}")
            return None

    def _rule_based_fallback(self, input_data: dict) -> AgentDecision:
        """Rule-based fallback when LLM is unavailable. Sets low confidence."""
        raw_text = input_data.get("raw_text", "")
        result = rule_classify(raw_text)

        # Map ContentClass to our classification
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

        # Extract entities
        entities = result.extracted_entities
        fields = ExtractedFields(
            job_type="sezonski rad" if classification == "employer_job_post" else None,
            location=entities.get("locations", [None])[0] if entities.get("locations") else None,
            workers_needed=entities.get("workers_count"),
            accommodation="da" if entities.get("accommodation") else None,
            food="da" if entities.get("food") else None,
            contact=input_data.get("raw_text", "") if entities.get("contact_status") == "present" else None,
        )

        missing = []
        if not fields.pay:
            missing.append("plata / dnevnica")
        if not fields.accommodation:
            missing.append("smeštaj")
        if not fields.food:
            missing.append("hrana")
        if not fields.working_hours:
            missing.append("radno vreme")
        if not fields.contact:
            missing.append("kontakt")

        is_spam = classification == "spam"
        is_suspicious = classification == "suspicious"

        return AgentDecision(
            classification=classification,
            confidence=0.45,  # Low confidence — fallback mode
            risk_level="high" if (is_spam or is_suspicious) else "medium",
            recommended_action="escalate",  # Always escalate in fallback
            digest_candidate=not is_spam and not is_suspicious and bool(fields.location),
            public_post_allowed=not is_spam and not is_suspicious,
            fields=fields,
            missing_info=missing,
            risk_flags=["fallback_mode", "low_confidence"],
            operator_summary=f"[FALLBACK] {classification}. Tekst: {raw_text[:100]}...",
            prepared_public_text=result.suggested_reply or result.suggested_public_post or "",
            prepared_reply_to_author=result.suggested_reply or "",
            reason=f"Fallback rule-based classification. LLM unavailable. Confidence: 0.45",
        )

    def get_status(self) -> dict:
        return {
            "llm_available": self.llm_available,
            "llm_model": self.llm._model if self.llm_available else "none",
            "fallback_active": not self.llm_available,
            "decisions_made": self._decisions_count,
            "regex_only_mode": not self.llm_available,
        }
