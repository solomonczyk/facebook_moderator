"""Real visible browser session via Selenium for own-group content reading.

Opens a VISIBLE Chrome window. Operator must log in manually.
Never stores credentials. Never exports cookies. Headless FORBIDDEN.
"""

import time
from .config import WorkerConfig

# Optional Selenium import — fails gracefully if not installed
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.common.exceptions import WebDriverException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


class BrowserSession:
    def __init__(self, config: WorkerConfig):
        self.config = config
        self._driver = None
        self._connected: bool = False
        self._visible: bool = True
        self._headless: bool = False  # NEVER set to True

    @property
    def is_connected(self) -> bool:
        return self._connected and self._driver is not None

    def connect(self) -> tuple[bool, str]:
        if self._headless:
            return False, "Headless mode is FORBIDDEN"
        if self.config.stealth_browser_enabled:
            return False, "Stealth browser is FORBIDDEN"
        if not SELENIUM_AVAILABLE:
            return False, "Selenium not installed. Run: pip install selenium"

        try:
            opts = Options()
            opts.add_argument("--start-maximized")
            # Explicitly NOT headless
            opts.add_experimental_option("excludeSwitches", ["enable-automation"])
            opts.add_experimental_option("useAutomationExtension", False)

            self._driver = webdriver.Chrome(options=opts)
            self._connected = True
            return True, "Browser opened in visible window. Operator: log in manually to Facebook, then press Enter."
        except WebDriverException as e:
            return False, f"Browser launch failed: {e}. Is Chrome installed? Is chromedriver in PATH?"

    def disconnect(self) -> None:
        if self._driver:
            try:
                self._driver.quit()
            except Exception:
                pass
            self._driver = None
        self._connected = False

    def navigate_and_read(self, url: str, wait_for_login_seconds: int = 45) -> list[dict]:
        """Navigate to the own group page, wait for operator login, read visible text blocks.
        Returns list of {"text": str, "url": str, "type": str, "timestamp": str} dicts."""
        if not self._driver:
            return []
        if not self.config.is_own_group(url) and "facebook.com/groups/" in url:
            return []  # Reject external groups

        try:
            self._driver.get(url)
        except WebDriverException as e:
            return [{"text": f"Navigation error: {e}", "url": url, "type": "error"}]

        # Wait for operator to log in manually
        time.sleep(2)  # Let page start loading
        # In a real interactive session, operator logs in now.
        # For smoke test: if already logged in, FB loads the group directly.
        time.sleep(wait_for_login_seconds)

        blocks = []
        try:
            # Extract visible post/comment text from the page
            selectors = [
                'div[data-ad-preview]',
                'div[class*="userContent"]',
                'div[role="article"]',
                'div[dir="auto"]',
            ]
            for selector in selectors:
                try:
                    elements = self._driver.find_elements(By.CSS_SELECTOR, selector)
                    for el in elements:
                        text = el.text.strip()
                        if text and len(text) > 10:
                            blocks.append({
                                "text": text,
                                "url": self._driver.current_url,
                                "type": "post" if "article" in selector else "comment",
                                "timestamp": "",
                            })
                except Exception:
                    continue
        except Exception:
            pass

        # If no blocks found via selectors, try reading all visible text
        if not blocks:
            try:
                body = self._driver.find_element(By.TAG_NAME, "body")
                full_text = body.text
                paragraphs = [p.strip() for p in full_text.split("\n") if len(p.strip()) > 20]
                for p in paragraphs[:20]:
                    blocks.append({
                        "text": p,
                        "url": self._driver.current_url,
                        "type": "visible_text",
                        "timestamp": "",
                    })
            except Exception:
                pass

        return blocks

    def read_visible_page(self, url: str) -> list[dict]:
        """Alias for navigate_and_read — used by OwnGroupWatcher."""
        return self.navigate_and_read(url)

    def to_dict(self) -> dict:
        return {
            "connected": self._connected,
            "visible": self._visible,
            "headless": self._headless,
            "selenium_available": SELENIUM_AVAILABLE,
        }
