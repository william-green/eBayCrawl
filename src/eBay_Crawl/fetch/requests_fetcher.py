"""Fetch search HTML via plain HTTP ( urllib / requests )."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

import requests
from requests.exceptions import RequestException
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from .models import SearchPagePayload


@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(2),
    retry=retry_if_exception_type(RequestException),
)
def _fetch_url(url: str) -> str:
    if url == "":
        return ""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.text
        return ""
    except RequestException as e:
        print(f"Failed to retrieve the page: {e}")
        return ""


class RequestsPageFetcher:
    """Parallel HTTP fetch matching legacy parallel_page_loader behavior."""

    def __init__(self, max_workers: int = 12):
        self._max_workers = max_workers

    def fetch_pages(self, urls: list[str]) -> list[SearchPagePayload]:
        with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            html_list = list(executor.map(_fetch_url, urls))
        return [SearchPagePayload(html=h) for h in html_list]
