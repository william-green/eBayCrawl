"""Parse search results and write listings — independent of how HTML/API data was fetched."""

from __future__ import annotations

import re
from typing import Any

from bs4 import BeautifulSoup

from ..db import db_functions as db_f
from ..structs.bin_listing import Bin_listing
from ..structs.search import Search


def get_listing_id_from_url(listing_url: str) -> int:
    listing_id_group = re.search(r"/itm/(\d+)", listing_url)
    if listing_id_group:
        return int(listing_id_group.group(1))
    raise ValueError("listing url contains no item id")


def check_listing_id(listing_url: str, newest_listing_id: int | None) -> bool:
    listing_id = get_listing_id_from_url(listing_url)
    return listing_id == newest_listing_id


def listing_accepts_best_offer(listing_entry_code) -> bool:
    try:
        return len(listing_entry_code.select(".s-item__formatBestOfferEnabled")) > 0
    except Exception:
        return False


def get_listing_price(listing_entry_code) -> float:
    base_price = 0.0
    shipping_price = 0.0
    try:
        base_price_str = (listing_entry_code.select(".s-item__price")[0].text).replace(",", "")
        base_price = float(base_price_str[1:])
        shipping_price_str = (
            listing_entry_code.select(".s-item__shipping s-item__logisticsCost")[0].text
        ).replace(",", "")
        shipping_price = 0.0
        match = re.findall(r"\d+\.\d+", shipping_price_str)
        if match:
            shipping_price = float(match[0])
            print(shipping_price)
    except Exception:
        pass
    return base_price + shipping_price


def process_html_search_page(search: Search, search_page: str, db_mod=db_f) -> tuple[bool, bool]:
    """
    Process one HTML search results page for one Search.

    Returns (new_listings_inserted, terminate_outer_hint).
    Caller should call search.set_complete() when terminate_outer_hint is True.
    """
    search_type = search.get_search_type()
    search_id = search.get_search_id()
    if search_type == "bin":
        newest_listing = db_mod.get_newest_bin_listing_ebay_id(search_id)
    elif search_type == "auction":
        newest_listing = db_mod.get_newest_auction_listing_ebay_id(search_id)
    else:
        raise TypeError("Search type is other than bin or auction.")

    print(newest_listing)

    new_listings_inserted = False
    terminate = False

    if search_page == "":
        return False, False

    soup = BeautifulSoup(search_page, "html.parser")
    results = soup.select(".srp-results")
    if not results:
        return False, False
    listing_entries = results[0].select(".s-item")

    for listing_entry in listing_entries:
        listing_url = listing_entry.select(".s-item__link")[0]["href"]

        if check_listing_id(listing_url, newest_listing):
            if len(listing_entry.select(".s-wl38509_s-gk45084")) == 0:
                print("reached end. break")
                terminate = True
                search.set_complete()
                break
            print("promoted listing")
            continue

        listing_id = get_listing_id_from_url(listing_url)
        if search.get_search_type() == "bin":
            listing_obj = Bin_listing(
                search_id=search.get_search_id(),
                ebay_listing_id=listing_id,
                url=listing_url,
                accepts_best_offer=listing_accepts_best_offer(listing_entry),
                price=get_listing_price(listing_entry),
            )
            db_mod.insert_bin_listing(listing_obj)
            new_listings_inserted = True
        elif search.get_search_type() == "auction":
            print("insert auction listing into database")
            new_listings_inserted = True

    if terminate:
        print("terminating")
        search.set_complete()

    return new_listings_inserted, terminate


def _parse_api_item_id(item_id_raw: str | int) -> int:
    s = str(item_id_raw)
    if "|" in s:
        parts = s.split("|")
        return int(parts[1])
    return int(s)


def _api_item_best_offer(item: dict[str, Any]) -> bool:
    opts = item.get("buyingOptions") or []
    return any("BEST_OFFER" in str(o).upper() for o in opts)


def process_api_search_items(
    search: Search, items: list[dict[str, Any]], db_mod=db_f
) -> tuple[bool, bool]:
    """Process Browse API item summaries for one Search (same return shape as HTML)."""
    search_type = search.get_search_type()
    search_id = search.get_search_id()
    if search_type == "bin":
        newest_listing = db_mod.get_newest_bin_listing_ebay_id(search_id)
    elif search_type == "auction":
        newest_listing = db_mod.get_newest_auction_listing_ebay_id(search_id)
    else:
        raise TypeError("Search type is other than bin or auction.")

    new_listings_inserted = False
    terminate = False

    for item in items:
        listing_url = item.get("itemWebUrl") or ""
        if not listing_url:
            continue

        item_id_raw = item.get("itemId")
        if item_id_raw is None:
            continue
        listing_id = _parse_api_item_id(item_id_raw)

        if check_listing_id(listing_url, newest_listing):
            terminate = True
            search.set_complete()
            break

        price_block = item.get("price") or {}
        try:
            price_val = float(price_block.get("value", 0))
        except (TypeError, ValueError):
            price_val = 0.0

        if search.get_search_type() == "bin":
            listing_obj = Bin_listing(
                search_id=search.get_search_id(),
                ebay_listing_id=listing_id,
                url=listing_url,
                accepts_best_offer=_api_item_best_offer(item),
                price=price_val,
            )
            db_mod.insert_bin_listing(listing_obj)
            new_listings_inserted = True
        elif search.get_search_type() == "auction":
            print("insert auction listing into database")
            new_listings_inserted = True

    if terminate:
        print("terminating")
        search.set_complete()

    return new_listings_inserted, terminate
