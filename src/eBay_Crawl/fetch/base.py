from __future__ import annotations

from typing import Protocol

from .models import SearchPagePayload


class PageFetcher(Protocol):
    """Fetches search results for URLs in lockstep order (one payload per URL)."""

    def fetch_pages(self, urls: list[str]) -> list[SearchPagePayload]:
        ...
