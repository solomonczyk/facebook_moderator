"""Analyst agent configuration: kill switch, thresholds, gates."""

from dataclasses import dataclass


@dataclass
class AnalystConfig:
    # Kill switch
    analyst_enabled: bool = False
    autonomous_mode_enabled: bool = False

    # Confidence thresholds
    min_confidence_for_autonomous: float = 0.85
    min_confidence_for_escalation: float = 0.50

    # Risk thresholds
    max_risk_for_autonomous: str = "medium"  # low/medium ok, high/reject -> escalate

    # Rate limits
    max_autonomous_decisions_per_hour: int = 30

    # Dangerous — ALL must be false
    facebook_auto_post_enabled: bool = False
    facebook_auto_comment_enabled: bool = False
    facebook_auto_message_enabled: bool = False
    production_accepted: bool = False

    def can_operate(self) -> tuple[bool, str]:
        if not self.analyst_enabled:
            return False, "analyst_enabled is false"
        if self.facebook_auto_post_enabled:
            return False, "facebook_auto_post_enabled must be false"
        if self.facebook_auto_comment_enabled:
            return False, "facebook_auto_comment_enabled must be false"
        if self.facebook_auto_message_enabled:
            return False, "facebook_auto_message_enabled must be false"
        return True, "OK"

    def to_dict(self) -> dict:
        return {
            "analyst_enabled": self.analyst_enabled,
            "autonomous_mode_enabled": self.autonomous_mode_enabled,
            "min_confidence_for_autonomous": self.min_confidence_for_autonomous,
            "max_risk_for_autonomous": self.max_risk_for_autonomous,
            "max_autonomous_decisions_per_hour": self.max_autonomous_decisions_per_hour,
        }
