"""Selenium-based screenshot capture — public Facebook pages only, NO login, NO cookies."""

import os
import time
import logging
from datetime import datetime
from pathlib import Path

from .config import PublicIntakeConfig

logger = logging.getLogger("sezonski.public_intake.screenshotter")


class ScreenshotResult:
    def __init__(self, path: str, url: str, text_content: str = "", success: bool = False, error: str = ""):
        self.path = path
        self.url = url
        self.text_content = text_content
        self.success = success
        self.error = error
        self.taken_at = datetime.utcnow().isoformat()

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "url": self.url,
            "text_length": len(self.text_content),
            "success": self.success,
            "error": self.error,
            "taken_at": self.taken_at,
        }


class PublicScreenshotter:
    """Captures screenshots of public Facebook pages WITHOUT login or cookies.

    Uses Selenium Chrome in visible mode. No stealth. No session storage.
    Each page is loaded fresh with incognito-like settings.
    """

    def __init__(self, config: PublicIntakeConfig | None = None):
        self.config = config or PublicIntakeConfig()
        self._driver = None
        self._screenshots_taken: int = 0

    def _get_driver(self):
        """Lazy-init Selenium driver with NO cookies, NO profile, NO session."""
        if self._driver is not None:
            return self._driver

        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service

            opts = Options()
            # Essential: NO user data, NO profile, NO session persistence
            opts.add_argument("--incognito")
            opts.add_argument("--disable-session-crashed-bubble")
            opts.add_argument("--disable-save-password-bubble")
            opts.add_argument("--disable-permissions-api")
            opts.add_argument("--no-first-run")
            opts.add_argument("--no-default-browser-check")

            # Prevent cookie/session storage
            opts.add_argument("--disable-features=PasswordImport,PasswordGeneration")
            opts.add_experimental_option("excludeSwitches", ["enable-logging"])
            opts.add_experimental_option("prefs", {
                "profile.default_content_setting_values.cookies": 2,  # Block all cookies
                "profile.default_content_setting_values.notifications": 2,
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False,
            })

            # Headless NOT allowed — we need visible for screenshots
            # opts.add_argument("--headless")  # EXPLICITLY NOT USED

            driver = webdriver.Chrome(options=opts)
            driver.set_page_load_timeout(self.config.page_load_timeout_seconds)
            driver.set_window_size(1280, 900)

            self._driver = driver
            logger.info("Selenium driver initialized (incognito, no cookies, no profile)")
            return driver
        except Exception as e:
            logger.error(f"Failed to create Selenium driver: {e}")
            return None

    def capture(self, url: str, group_name: str, max_screenshots: int = 3) -> list[ScreenshotResult]:
        """Capture screenshots of a public Facebook group page. NO login.

        Returns up to max_screenshots results with extracted text content.
        """
        results: list[ScreenshotResult] = []
        if self.config.dry_run:
            logger.info(f"[DRY RUN] Would capture {url} ({group_name})")
            return [ScreenshotResult(
                path=f"[DRY RUN] {url}",
                url=url,
                text_content="[DRY RUN — no actual screenshot taken]",
                success=True,
            )]

        driver = self._get_driver()
        if driver is None:
            return [ScreenshotResult(url=url, success=False, error="No Selenium driver available")]

        os.makedirs(self.config.screenshot_dir, exist_ok=True)

        try:
            # Load the page — public, no login
            logger.info(f"Loading public page: {url}")
            driver.get(url)
            time.sleep(3)  # Let the page render (Facebook is JS-heavy)

            # Check if we got a login wall
            page_source = driver.page_source.lower()
            if "login" in page_source and "password" in page_source and "you must log in" in page_source:
                logger.warning(f"Login wall detected for {url} — marking as login_required")
                return [ScreenshotResult(url=url, success=False, error="login_required")]

            # Take screenshots at different scroll positions
            for i in range(max_screenshots):
                if i > 0:
                    # Scroll down a bit for next screenshot
                    driver.execute_script(f"window.scrollBy(0, {400 * i});")
                    time.sleep(self.config.min_delay_between_screenshots_seconds)

                timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                safe_name = "".join(c if c.isalnum() else "_" for c in group_name)[:40]
                filename = f"{safe_name}_{timestamp}_{i+1}.png"
                filepath = os.path.join(self.config.screenshot_dir, filename)

                driver.save_screenshot(filepath)
                self._screenshots_taken += 1

                # Extract visible text from the page DOM
                text_content = self._extract_visible_text(driver)

                result = ScreenshotResult(
                    path=filepath,
                    url=url,
                    text_content=text_content,
                    success=True,
                )
                results.append(result)
                logger.info(f"Screenshot {i+1}/{max_screenshots} saved: {filepath} ({len(text_content)} chars text)")

        except Exception as e:
            logger.error(f"Screenshot capture failed for {url}: {e}")
            results.append(ScreenshotResult(url=url, success=False, error=str(e)))

        return results

    def _extract_visible_text(self, driver) -> str:
        """Extract visible text content from the page DOM.

        Avoids script/style content. Focuses on post/feed content areas.
        """
        try:
            # Try to find Facebook post content areas first
            scripts = [
                # Facebook post containers (various selectors that work on public pages)
                "return Array.from(document.querySelectorAll('div[data-ad-preview], div[data-pagelet], [role=\"article\"], .userContent, .story_body_container, [data-ft]')).map(el => el.innerText).filter(t => t && t.length > 20).join('\\n---\\n')",
                # Fallback: get all visible text from body
                "return document.body ? document.body.innerText : ''",
            ]

            for script in scripts:
                try:
                    text = driver.execute_script(script)
                    if text and len(text.strip()) > 50:
                        # Truncate to reasonable size
                        return text[:5000]
                except Exception:
                    continue

            return ""
        except Exception as e:
            logger.warning(f"Text extraction failed: {e}")
            return ""

    def close(self):
        """Close the browser driver."""
        if self._driver is not None:
            try:
                self._driver.quit()
            except Exception:
                pass
            self._driver = None
            logger.info("Selenium driver closed")

    @property
    def screenshots_taken(self) -> int:
        return self._screenshots_taken
