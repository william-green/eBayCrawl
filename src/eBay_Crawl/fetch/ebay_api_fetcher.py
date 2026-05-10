"""Fetch listing summaries via eBay Browse API instead of scraping HTML."""

from __future__ import annotations

import base64
import os
import time

import requests

from .ebay_search_url import parse_ebay_search_url
from .models import SearchPagePayload

_TOKEN: str | None = None
_TOKEN_EXPIRES_AT: float = 0.0


def _application_access_token(client_id: str, client_secret: str) -> str:
    global _TOKEN, _TOKEN_EXPIRES_AT
    now = time.time()
    if _TOKEN and now < _TOKEN_EXPIRES_AT:
        return _TOKEN

    auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    resp = requests.post(
        "https://api.ebay.com/identity/v1/oauth2/token",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {auth}",
        },
        data={
            "grant_type": "client_credentials",
            "scope": "https://api.ebay.com/oauth/api_scope",
        },
        timeout=30,
    )
    resp.raise_for_status()
    body = resp.json()
    _TOKEN = body["access_token"]
    _TOKEN_EXPIRES_AT = now + float(body.get("expires_in", 3600)) - 60.0
    return _TOKEN


def _browse_search(
    token: str,
    marketplace_id: str,
    keyword: str,
    offset: int,
    limit: int,
    filter_fragments: list[str],
) -> list[dict]:
    if not keyword.strip():
        return []

    params: dict[str, str | int] = {
        "q": keyword,
        "limit": min(limit, 200),
        "offset": offset,
    }
    if filter_fragments:
        params["filter"] = ",".join(filter_fragments)

    headers = {
        "Authorization": f"Bearer {token}",
        "X-EBAY-C-MARKETPLACE-ID": marketplace_id,
    }
    resp = requests.get(
        "https://api.ebay.com/buy/browse/v1/item_summary/search",
        headers=headers,
        params=params,
        timeout=30,
    )
    if resp.status_code != 200:
        print(f"Browse API error {resp.status_code}: {resp.text[:500]}")
        return []
    data = resp.json()
    return list(data.get("itemSummaries") or [])


class EbayBrowseApiFetcher:
    """One Browse API call per stored search URL (pagination via ``_pgn`` → offset)."""

    def __init__(self) -> None:
        cid = os.environ.get("EBAY_CLIENT_ID")
        secret = os.environ.get("EBAY_CLIENT_SECRET")
        if not cid or not secret:
            raise RuntimeError(
                "EBAY_CLIENT_ID and EBAY_CLIENT_SECRET must be set for EBAY_FETCH_BACKEND=ebay_api"
            )
        self._client_id = cid
        self._client_secret = secret
        self._marketplace = os.environ.get("EBAY_MARKETPLACE_ID", "EBAY_US")

    def fetch_pages(self, urls: list[str]) -> list[SearchPagePayload]:
        token = _application_access_token(self._client_id, self._client_secret)
        out: list[SearchPagePayload] = []
        for url in urls:
            if not url.strip():
                out.append(SearchPagePayload(api_items=[]))
                continue
            keyword, offset, limit, filters = parse_ebay_search_url(url)
            items = _browse_search(
                token, self._marketplace, keyword, offset, limit, filters
            )
            out.append(SearchPagePayload(api_items=items))
        return out
