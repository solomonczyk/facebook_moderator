"""Account worker configuration and safety gates."""

import os
from dataclasses import dataclass, field


@dataclass
class WorkerConfig:
    # Gated mode
    own_group_worker_enabled: bool = False
    own_group_url: str = ""

    # Dangerous gates — ALL must be false for worker to start
    external_group_worker_enabled: bool = False
    auto_post_enabled: bool = False
    auto_comment_enabled: bool = False
    auto_message_enabled: bool = False
    captcha_bypass_enabled: bool = False
    stealth_browser_enabled: bool = False
    fake_account_enabled: bool = False

    # Safety defaults
    read_only: bool = True
    draft_only: bool = True
    operator_approval_required: bool = True
    production_accepted: bool = False

    # Rate limits
    max_items_per_run: int = 20
    max_scrolls_per_run: int = 2
    min_seconds_between_scrolls: int = 15
    max_runs_per_hour: int = 3

    def load_from_env(self) -> None:
        url = os.getenv("OWN_FACEBOOK_GROUP_URL", "")
        if url:
            self.own_group_url = url

    def can_start(self) -> tuple[bool, list[str]]:
        """Check if worker is allowed to start. Returns (allowed, reasons)."""
        blockers = []

        if self.auto_post_enabled:
            blockers.append("auto_post_enabled must be false")
        if self.auto_comment_enabled:
            blockers.append("auto_comment_enabled must be false")
        if self.auto_message_enabled:
            blockers.append("auto_message_enabled must be false")
        if self.captcha_bypass_enabled:
            blockers.append("captcha_bypass_enabled must be false")
        if self.stealth_browser_enabled:
            blockers.append("stealth_browser_enabled must be false")
        if self.fake_account_enabled:
            blockers.append("fake_account_enabled must be false")
        if not self.own_group_worker_enabled:
            blockers.append("own_group_worker_enabled must be true")
        if not self.own_group_url:
            blockers.append("own_group_url is not configured")

        return len(blockers) == 0, blockers

    def is_own_group(self, url: str) -> bool:
        if not self.own_group_url:
            return False
        own_id = self._extract_group_id(self.own_group_url)
        check_id = self._extract_group_id(url)
        return own_id and check_id and own_id == check_id

    @staticmethod
    def _extract_group_id(url: str) -> str:
        if "groups/" in url:
            parts = url.split("groups/")
            if len(parts) > 1:
                return parts[1].split("/")[0].split("?")[0]
        return ""

    def to_dict(self) -> dict:
        return {
            "own_group_worker_enabled": self.own_group_worker_enabled,
            "own_group_url_configured": bool(self.own_group_url),
            "read_only": self.read_only,
            "draft_only": self.draft_only,
            "operator_approval_required": self.operator_approval_required,
            "auto_post_enabled": self.auto_post_enabled,
            "auto_comment_enabled": self.auto_comment_enabled,
            "auto_message_enabled": self.auto_message_enabled,
        }
