"""Fetch search result HTML via undetected_chromedriver (Chrome)."""

from __future__ import annotations

import os
import time
from typing import Any

import undetected_chromedriver as uc

from .models import SearchPagePayload


class SeleniumPageFetcher:
    """
    Loads each URL in order with a single Chrome session.

    Uses ``undetected_chromedriver`` so the browser matches a normal Chrome fingerprint
    more closely than raw Selenium. Requires a Chrome/Chromium install compatible with
    the bundled ChromeDriver resolution logic.
    """

    def __init__(self, page_load_wait_s: float | None = None) -> None:
        self._driver: Any | None = None
        raw = page_load_wait_s
        if raw is None:
            raw = float(os.environ.get("EBAY_SELENIUM_WAIT_S", "2.0"))
        self._wait_s = raw

    def _ensure_driver(self) -> Any:
        if self._driver is None:
            opts = uc.ChromeOptions()
            opts.add_argument("--no-sandbox")
            opts.add_argument("--disable-dev-shm-usage")
            opts.add_argument("--disable-gpu")
            opts.add_argument("--window-size=1920,1080")
            ua = os.environ.get("EBAY_SELENIUM_USER_AGENT")
            if ua:
                opts.add_argument(f"--user-agent={ua}")

            headless = os.environ.get("EBAY_SELENIUM_HEADLESS", "1").strip() not in (
                "0",
                "false",
                "False",
            )

            chrome_kw: dict[str, Any] = {"options": opts, "headless": headless}

            browser_bin = os.environ.get("EBAY_CHROME_BINARY")
            if browser_bin:
                chrome_kw["browser_executable_path"] = browser_bin

            vm = os.environ.get("EBAY_CHROME_VERSION_MAIN")
            if vm and vm.isdigit():
                chrome_kw["version_main"] = int(vm)

            self._driver = uc.Chrome(**chrome_kw)
        return self._driver

    def fetch_pages(self, urls: list[str]) -> list[SearchPagePayload]:
        driver = self._ensure_driver()
        out: list[SearchPagePayload] = []
        for url in urls:
            if not url.strip():
                out.append(SearchPagePayload(html=""))
                continue
            try:
                driver.get(url)
                time.sleep(self._wait_s)
                out.append(SearchPagePayload(html=driver.page_source))
            except Exception as e:
                print(f"Selenium fetch failed for {url[:80]}...: {e}")
                out.append(SearchPagePayload(html=""))
        return out

    def close(self) -> None:
        if self._driver is not None:
            try:
                self._driver.quit()
            except Exception:
                pass
            self._driver = None

    def __del__(self) -> None:
        self.close()
