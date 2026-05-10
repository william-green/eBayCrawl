from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SearchPagePayload:
    """One search-results page worth of data from any backend."""

    # Raw HTML from site scraping (requests / selenium).
    html: str | None = None
    # Browse API item summaries when using official API (parallel to one results page).
    api_items: list[dict[str, Any]] | None = None
