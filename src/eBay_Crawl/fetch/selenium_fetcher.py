"""Fetch search result HTML using Selenium (browser) instead of raw HTTP."""

from __future__ import annotations

import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions

from .models import SearchPagePayload


class SeleniumPageFetcher:
    """
    Loads each URL in order with a single WebDriver (stable for automation).

    Requires Chrome/Chromium and a matching ChromeDriver on PATH or Selenium Manager.
    """

    def __init__(self, page_load_wait_s: float | None = None) -> None:
        self._driver: webdriver.Chrome | None = None
        raw = page_load_wait_s
        if raw is None:
            raw = float(os.environ.get("EBAY_SELENIUM_WAIT_S", "2.0"))
        self._wait_s = raw

    def _ensure_driver(self) -> webdriver.Chrome:
        if self._driver is None:
            opts = ChromeOptions()
            if os.environ.get("EBAY_SELENIUM_HEADLESS", "1").strip() not in ("0", "false", "False"):
                opts.add_argument("--headless=new")
            opts.add_argument("--no-sandbox")
            opts.add_argument("--disable-dev-shm-usage")
            opts.add_argument("--disable-gpu")
            opts.add_argument("--window-size=1920,1080")
            ua = os.environ.get("EBAY_SELENIUM_USER_AGENT")
            if ua:
                opts.add_argument(f"--user-agent={ua}")
            self._driver = webdriver.Chrome(options=opts)
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
