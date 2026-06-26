"""Own group visible intake adapter — guarded, disabled by default."""

from .config import IntakeConfig


class OwnGroupVisibleAdapter:
    def __init__(self, config: IntakeConfig):
        self.config = config

    @property
    def enabled(self) -> bool:
        return self.config.own_group_visible_intake_enabled

    def capture(self, page_url: str, source_group: str, text_blocks: list[str]) -> dict:
        if not self.enabled:
            return {"success": False, "error": "own_group_visible_intake is disabled"}

        if not text_blocks:
            return {"success": False, "error": "no text blocks provided"}

        return {
            "success": True,
            "capture_method": "own_group_visible_intake",
            "page_url": page_url,
            "source_group": source_group,
            "visible_text_blocks": text_blocks,
            "block_count": len(text_blocks),
            "warning": "All captured content goes to action queue. No auto-posting.",
        }

    def get_warning(self) -> str:
        return (
            "OWN GROUP VISIBLE INTAKE IS ENABLED. "
            "This mode reads visible text from the current Facebook tab. "
            "No auto-scrolling. No auto-posting. Operator must click to capture. "
            "All content goes to action queue for manual review."
        )
