"""Policy engine: action allowlist, forbidden list, validation.

This is the FINAL authority on what actions can execute.
Even if the brain/LLM suggests an action, the policy engine
MUST validate it against the allowlist before execution.
"""

from dataclasses import dataclass

# ── Autonomous Allowed Actions ──────────────────────────────────────────────

AUTONOMOUS_ALLOWED = {
    "save_worker_lead",
    "save_job_lead",
    "mark_duplicate",
    "mark_spam_candidate",
    "ask_missing_info_draft",
    "approve_for_digest",
    "generate_digest_draft",
    "escalate_to_operator",
    "archive_closed_lead",
    "update_missing_info",
}

# ── Forbidden (Hard Block) ──────────────────────────────────────────────────

HARD_FORBIDDEN = {
    "facebook_auto_post",
    "facebook_auto_comment",
    "facebook_auto_message",
    "facebook_delete_content",
    "facebook_ban_user",
    "facebook_approve_member",
    "facebook_reject_member",
    "publish_review",
    "publish_employer_rating",
    "label_employer_scammer",
    "label_worker_fraud",
    "access_secrets",
    "read_env_file",
    "change_config",
    "shell_command",
    "cookie_access",
    "session_access",
    "credential_read",
    "credential_write",
    "database_drop",
    "database_truncate",
    "disable_audit_log",
    "disable_kill_switch",
    "modify_policy",
}


@dataclass
class PolicyDecision:
    allowed: bool
    action: str
    reason: str
    requires_operator: bool = False
    blocked_reason: str = ""


class PolicyEngine:
    def validate(self, action: str, risk_level: str = "low",
                 confidence: float = 1.0,
                 autonomous_mode: bool = False) -> PolicyDecision:
        """Validate an action against the policy. Returns a PolicyDecision."""

        # Hard forbidden check FIRST
        if action in HARD_FORBIDDEN:
            return PolicyDecision(
                allowed=False,
                action=action,
                reason="Hard forbidden",
                blocked_reason=f"Action '{action}' is on the permanent blocklist",
            )

        # Is this an autonomous allowed action?
        if action not in AUTONOMOUS_ALLOWED:
            # Unknown action — escalate
            return PolicyDecision(
                allowed=False,
                action=action,
                reason="Not in allowlist",
                requires_operator=True,
                blocked_reason=f"Action '{action}' is not in the autonomous allowlist. Escalate.",
            )

        # Autonomous mode: check risk and confidence
        if autonomous_mode:
            if risk_level in ("high", "reject"):
                return PolicyDecision(
                    allowed=False,
                    action=action,
                    reason="Risk too high for autonomous",
                    requires_operator=True,
                    blocked_reason=f"Risk level '{risk_level}' exceeds autonomous threshold. Escalate.",
                )

            if confidence < 0.50:
                return PolicyDecision(
                    allowed=False,
                    action=action,
                    reason="Confidence too low",
                    requires_operator=True,
                    blocked_reason=f"Confidence {confidence:.2f} below minimum (0.50). Escalate.",
                )

            if confidence < 0.85 and risk_level == "medium":
                return PolicyDecision(
                    allowed=False,
                    action=action,
                    reason="Medium risk + medium confidence -> escalate",
                    requires_operator=True,
                    blocked_reason="Medium risk with confidence < 0.85. Escalate.",
                )

        return PolicyDecision(
            allowed=True,
            action=action,
            reason="Approved" if autonomous_mode else "Approved (manual mode)",
            requires_operator=not autonomous_mode,
        )

    @staticmethod
    def sanitize_content(text: str) -> str:
        """Defense against prompt injection in user content."""
        # Strip common injection patterns
        dangerous = [
            "ignore previous instructions",
            "ignore all previous",
            "disregard above",
            "system prompt:",
            "you are now",
            "act as",
            "pretend you are",
            "new instructions:",
            "override policy",
            "bypass allowlist",
            "execute shell",
            "sudo ",
            "rm -rf",
            "DROP TABLE",
            "<script",
            "javascript:",
            "eval(",
            "exec(",
            "__import__",
        ]
        result = text
        for pattern in dangerous:
            if pattern.lower() in result.lower():
                # Replace with safe marker
                result = result.replace(pattern, "[FILTERED]")
        return result
