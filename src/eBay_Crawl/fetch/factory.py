"""Select fetch backend via EBAY_FETCH_BACKEND (requests | selenium | ebay_api)."""

from __future__ import annotations

import os

from .base import PageFetcher
from .requests_fetcher import RequestsPageFetcher


def get_page_fetcher() -> PageFetcher:
    mode = os.environ.get("EBAY_FETCH_BACKEND", "requests").strip().lower()
    if mode == "selenium":
        from .selenium_fetcher import SeleniumPageFetcher

        return SeleniumPageFetcher()
    if mode == "ebay_api":
        from .ebay_api_fetcher import EbayBrowseApiFetcher

        return EbayBrowseApiFetcher()
    return RequestsPageFetcher()
