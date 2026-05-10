"""Parse eBay `/sch/i.html` URLs into Browse API search parameters."""

from __future__ import annotations

from urllib.parse import parse_qs, unquote_plus, urlparse


def parse_ebay_search_url(url: str) -> tuple[str, int, int, list[str]]:
    """
    From a search results URL, derive keyword, offset, limit, and filter fragments.

    Returns (keyword, offset, limit, filter_fragments).
    """
    limit = 50
    if not url.strip():
        return "", 0, limit, []

    parsed = urlparse(url)
    qs = parse_qs(parsed.query)

    raw_kw = qs.get("_nkw", [""])[0]
    keyword = unquote_plus(raw_kw.replace("+", " "))

    pgn_raw = qs.get("_pgn", ["1"])[0] or "1"
    try:
        page = max(1, int(pgn_raw))
    except ValueError:
        page = 1
    offset = (page - 1) * limit

    filters: list[str] = []
    if qs.get("LH_BIN", [""])[0] == "1":
        filters.append("buyingOptions:{FIXED_PRICE}")

    return keyword, offset, limit, filters
