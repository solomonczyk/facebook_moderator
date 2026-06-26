"""Intake configuration and dangerous gates."""

from dataclasses import dataclass


@dataclass
class IntakeConfig:
    # Safe modes — enabled by default
    manual_paste_enabled: bool = True
    clipboard_intake_enabled: bool = True
    selected_text_extension_enabled: bool = True

    # Guarded modes — disabled by default
    own_group_visible_intake_enabled: bool = False
    external_group_visible_intake_enabled: bool = False
    facebook_account_worker_enabled: bool = False

    # Dangerous — disabled
    auto_reply_enabled: bool = False
    auto_post_enabled: bool = False
    auto_comment_enabled: bool = False
    auto_message_enabled: bool = False
    captcha_bypass_enabled: bool = False
    stealth_browser_enabled: bool = False
    fake_account_enabled: bool = False
    production_accepted: bool = False

    # Safety defaults
    operator_approval_required: bool = True
    draft_only_by_default: bool = True
    localhost_only: bool = True

    def to_dict(self) -> dict:
        return {
            "manual_paste_enabled": self.manual_paste_enabled,
            "clipboard_intake_enabled": self.clipboard_intake_enabled,
            "selected_text_extension_enabled": self.selected_text_extension_enabled,
            "own_group_visible_intake_enabled": self.own_group_visible_intake_enabled,
            "external_group_visible_intake_enabled": self.external_group_visible_intake_enabled,
            "auto_reply_enabled": self.auto_reply_enabled,
            "auto_post_enabled": self.auto_post_enabled,
            "auto_comment_enabled": self.auto_comment_enabled,
            "auto_message_enabled": self.auto_message_enabled,
            "operator_approval_required": self.operator_approval_required,
            "draft_only_by_default": self.draft_only_by_default,
        }
