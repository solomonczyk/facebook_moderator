"""Policy engine: enforces dangerous gates and safety rules."""

from .config import RuntimeConfig


class PolicyEngine:
    def __init__(self, config: RuntimeConfig):
        self.config = config

    def can_auto_post(self) -> bool:
        return self.config.is_gate_enabled("facebook_auto_post_enabled")

    def can_auto_reply(self) -> bool:
        return self.config.is_gate_enabled("facebook_auto_reply_enabled")

    def can_auto_comment(self) -> bool:
        return self.config.is_gate_enabled("facebook_auto_comment_enabled")

    def can_auto_message(self) -> bool:
        return self.config.is_gate_enabled("facebook_auto_message_enabled")

    def requires_operator_approval(self, action_type: str) -> bool:
        always_require = [
            "publish_own_group_post", "reply_to_comment", "reply_to_post",
            "create_digest_post", "review_moderation_needed",
        ]
        if action_type in always_require:
            return True
        return self.config.operator_approval_required

    def is_hard_forbidden(self, action: str) -> bool:
        return action in self.config.HARD_FORBIDDEN

    def validate_action(self, action_type: str) -> tuple[bool, str]:
        """Returns (allowed, reason)."""
        if self.is_hard_forbidden(action_type):
            return False, f"Hard forbidden: {action_type}"
        if action_type == "auto_post" and not self.can_auto_post():
            return False, "Auto-posting is disabled"
        if action_type == "auto_reply" and not self.can_auto_reply():
            return False, "Auto-reply is disabled"
        if action_type == "auto_comment" and not self.can_auto_comment():
            return False, "Auto-comment is disabled"
        return True, "Allowed"
