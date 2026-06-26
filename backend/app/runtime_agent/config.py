"""Runtime agent configuration and dangerous gates."""

from dataclasses import dataclass, field


@dataclass
class RuntimeConfig:
    # Dangerous gates — ALL disabled by default
    facebook_account_worker_enabled: bool = False
    facebook_external_group_capture_enabled: bool = False
    facebook_own_group_capture_enabled: bool = False
    facebook_auto_reply_enabled: bool = False
    facebook_auto_post_enabled: bool = False
    facebook_auto_comment_enabled: bool = False
    facebook_auto_message_enabled: bool = False
    captcha_bypass_enabled: bool = False
    stealth_browser_enabled: bool = False
    fake_account_enabled: bool = False
    review_auto_publish_enabled: bool = False
    production_accepted: bool = False

    # Safe defaults
    operator_approval_required: bool = True
    draft_only_by_default: bool = True
    max_queue_items_per_run: int = 50

    # Hard forbidden — cannot be changed at runtime
    HARD_FORBIDDEN: list = field(default_factory=lambda: [
        "captcha_bypass",
        "stealth_evasion",
        "fake_accounts",
        "credential_extraction",
        "cookie_export",
        "private_member_data_collection",
        "fake_vacancies",
        "fake_reviews",
    ])

    def is_gate_enabled(self, gate_name: str) -> bool:
        if gate_name in self.HARD_FORBIDDEN:
            return False
        return getattr(self, gate_name, False)

    def to_dict(self) -> dict:
        return {
            "facebook_account_worker_enabled": self.facebook_account_worker_enabled,
            "facebook_auto_reply_enabled": self.facebook_auto_reply_enabled,
            "facebook_auto_post_enabled": self.facebook_auto_post_enabled,
            "facebook_auto_comment_enabled": self.facebook_auto_comment_enabled,
            "facebook_auto_message_enabled": self.facebook_auto_message_enabled,
            "captcha_bypass_enabled": self.captcha_bypass_enabled,
            "stealth_browser_enabled": self.stealth_browser_enabled,
            "fake_account_enabled": self.fake_account_enabled,
            "review_auto_publish_enabled": self.review_auto_publish_enabled,
            "production_accepted": self.production_accepted,
            "operator_approval_required": self.operator_approval_required,
            "draft_only_by_default": self.draft_only_by_default,
            "hard_forbidden": self.HARD_FORBIDDEN,
        }
