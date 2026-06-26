"""Browser session: manages visible browser for own-group content reading.

This is a DESIGN module. The actual browser automation (Selenium/Playwright)
is NOT implemented here to avoid accidental Facebook automation.
Instead, this module provides the interface and safety checks.

In production, operator manually opens Facebook in their browser.
The browser extension (TASK 005B) captures selected text.
This worker reads from the extension/intake pipeline.
"""

from .config import WorkerConfig


class BrowserSession:
    """Stub browser session. Real implementation requires operator's explicit
    approval and a local Selenium/Playwright driver with visible mode only."""

    def __init__(self, config: WorkerConfig):
        self.config = config
        self._connected: bool = False
        self._visible: bool = True
        self._headless: bool = False  # NEVER set to True

    @property
    def is_connected(self) -> bool:
        return self._connected

    def connect(self) -> tuple[bool, str]:
        """Stub: in production, connects to a visible browser instance."""
        if self._headless:
            return False, "Headless mode is FORBIDDEN"
        if self.config.stealth_browser_enabled:
            return False, "Stealth browser is FORBIDDEN"
        # In production: attach to existing visible browser or launch new visible instance
        self._connected = True
        return True, "Connected (stub)"

    def disconnect(self) -> None:
        self._connected = False

    def read_visible_page(self, url: str) -> list[str]:
        """Stub: reads visible text from the current page.
        In production, reads from the browser's current viewport.
        Returns list of text blocks."""
        if not self.config.is_own_group(url) and "facebook.com/groups/" in url:
            return []  # Reject external groups
        # In production: read visible DOM text blocks
        return []

    def to_dict(self) -> dict:
        return {
            "connected": self._connected,
            "visible": self._visible,
            "headless": self._headless,
        }
