"""
Legacy parallel HTTP loader. Prefer ``eBay_Crawl.fetch`` + ``EBAY_FETCH_BACKEND``.
"""

from ..fetch.requests_fetcher import RequestsPageFetcher


def parallel_page_loader(urls):
    fetcher = RequestsPageFetcher()
    payloads = fetcher.fetch_pages(urls)
    return [p.html or "" for p in payloads]