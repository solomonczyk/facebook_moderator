"""Pydantic schema for Runtime Manager Agent output. Handles validation and clamping."""

from pydantic import BaseModel, Field, field_validator
from typing import Optional


class ExtractedFields(BaseModel):
    job_type: Optional[str] = None
    location: Optional[str] = None
    workers_needed: Optional[int] = None
    start_date: Optional[str] = None
    pay: Optional[str] = None
    payment_type: Optional[str] = None
    accommodation: Optional[str] = None
    food: Optional[str] = None
    transport: Optional[str] = None
    working_hours: Optional[str] = None
    contact: Optional[str] = None
    language: Optional[str] = None


VALID_CLASSIFICATIONS = {
    "employer_job_post", "worker_request", "worker_group_available",
    "review_experience", "question", "spam", "suspicious",
    "irrelevant", "unclear",
}
VALID_ACTIONS = {
    "approve", "approve_with_edits", "reject", "ask_missing_info",
    "mark_spam", "escalate",
}
VALID_RISK_LEVELS = {"low", "medium", "high"}
FORBIDDEN_WORDS = {"provereno", "sigurno", "garantovano", "najbolji poslodavac"}


class AgentDecision(BaseModel):
    classification: str = "unclear"
    confidence: float = 0.0
    risk_level: str = "medium"
    recommended_action: str = "escalate"
    digest_candidate: bool = False
    public_post_allowed: bool = False
    fields: ExtractedFields = Field(default_factory=ExtractedFields)
    missing_info: list[str] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)
    operator_summary: str = ""
    prepared_public_text: str = ""
    prepared_reply_to_author: str = ""
    reason: str = ""

    def model_post_init(self, __context) -> None:
        # Clamp and validate after construction
        self.confidence = max(0.0, min(1.0, self.confidence))
        if self.classification not in VALID_CLASSIFICATIONS:
            self.classification = "unclear"
        if self.recommended_action not in VALID_ACTIONS:
            self.recommended_action = "escalate"
        if self.risk_level not in VALID_RISK_LEVELS:
            self.risk_level = "medium"

    def has_forbidden_words(self) -> list[str]:
        found = []
        texts = [self.prepared_public_text, self.prepared_reply_to_author, self.operator_summary]
        for text in texts:
            for word in FORBIDDEN_WORDS:
                if word.lower() in (text or "").lower():
                    found.append(word)
        return found

    def to_queue_dict(self) -> dict:
        return {
            "classification": self.classification,
            "confidence": self.confidence,
            "risk_level": self.risk_level,
            "recommended_action": self.recommended_action,
            "digest_candidate": self.digest_candidate,
            "fields": self.fields.model_dump(),
            "missing_info": self.missing_info,
            "risk_flags": self.risk_flags,
            "operator_summary": self.operator_summary,
            "prepared_public_text": self.prepared_public_text,
            "prepared_reply_to_author": self.prepared_reply_to_author,
            "reason": self.reason,
        }
