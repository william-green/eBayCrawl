from ..fetch.factory import get_page_fetcher
from ..structs.search import Search
from .search_page_processor import (
    process_api_search_items,
    process_html_search_page,
)
import time
from ..db import db_functions as db_f

# maximum number of pages of search results to iterate per search
max_search_pages = 5

# deep search enables analysis and logging of listing pages in addition to search results page
deep_search = False


def all_searches_complete(searches) -> bool:
    if len(searches) == 0:
        return True
    for search in searches:
        if not search.get_complete():
            return False
    return True


def listing_poll_loop(db_lock):
    fetcher = get_page_fetcher()
    db_lock.acquire()
    has_lock = True
    while True:
        db_searches = db_f.get_active_searches()
        searches = []
        for search in db_searches:
            searches.append(Search(search, max_pages=max_search_pages))

        new_listings_inserted = False

        while not all_searches_complete(searches):
            urls = [search.get_next_page_url() for search in searches]

            if new_listings_inserted:
                has_lock = False
                db_lock.release()

            payloads = fetcher.fetch_pages(urls)

            if not has_lock:
                db_lock.acquire()
                has_lock = True

            for search, payload in zip(searches, payloads):
                if payload.api_items is not None:
                    inserted, _ = process_api_search_items(search, payload.api_items, db_f)
                elif payload.html is not None:
                    inserted, _ = process_html_search_page(search, payload.html, db_f)
                else:
                    inserted = False
                if inserted:
                    new_listings_inserted = True

            time.sleep(1)

        time.sleep(10)


def main():
    listing_poll_loop()


if __name__ == "__main__":
    main()
