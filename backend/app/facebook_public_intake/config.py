"""Configuration and safety gates for public Facebook intake."""

from dataclasses import dataclass, field


@dataclass
class PublicIntakeConfig:
    # Safety gates — ALL restrictive by default
    dry_run: bool = True
    max_groups_per_run: int = 5
    max_screenshots_per_group: int = 3
    max_scroll_attempts: int = 2
    screenshot_dir: str = "artifacts/screenshots"
    extracted_dir: str = "artifacts/extracted"

    # Rate limits
    min_delay_between_groups_seconds: float = 5.0
    min_delay_between_screenshots_seconds: float = 2.0
    page_load_timeout_seconds: int = 15

    # NEVER login, NEVER use cookies
    allow_login: bool = False
    allow_cookies: bool = False
    allow_session_restore: bool = False

    # Hard forbidden
    HARD_FORBIDDEN: list = field(default_factory=lambda: [
        "facebook_login",
        "facebook_cookies",
        "facebook_session",
        "facebook_comment",
        "facebook_post",
        "facebook_message",
        "facebook_like",
        "facebook_share",
        "profile_scraping",
        "friend_request",
    ])

    def can_proceed(self) -> tuple[bool, str]:
        """Pre-flight safety check."""
        if self.allow_login:
            return False, "LOGIN FORBIDDEN — allow_login must be False"
        if self.allow_cookies:
            return False, "COOKIES FORBIDDEN — allow_cookies must be False"
        if self.allow_session_restore:
            return False, "SESSION FORBIDDEN — allow_session_restore must be False"
        return True, "ok"

    def to_dict(self) -> dict:
        return {
            "dry_run": self.dry_run,
            "max_groups_per_run": self.max_groups_per_run,
            "max_screenshots_per_group": self.max_screenshots_per_group,
            "allow_login": self.allow_login,
            "allow_cookies": self.allow_cookies,
            "production_mode": False,
        }
