
import sqlite3
from util.get_abs_path import get_abs_path
from search.search import Search
from util.bin_listing import Bin_listing

path = get_abs_path()


def get_active_searches():
    conn = sqlite3.connect(path+"db/app_data.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM Searches WHERE is_active=1")
    rows = cur.fetchall()
    conn.commit()
    conn.close()
    return rows

def get_newest_bin_listing_ebay_id(search_id):
    conn = sqlite3.connect(path+"db/app_data.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM bin_listings WHERE search_id = ? ORDER BY date_created DESC LIMIT 1", (search_id,))
    row = cur.fetchone()
    conn.commit()
    conn.close()
    if row is None:
        return None
    else:
        return row['ebay_listing_id']

def get_newest_auction_listing_ebay_id(search_id):
    conn = sqlite3.connect(path+"db/app_data.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM auction_listings WHERE search_id = ? ORDER BY date_created DESC LIMIT 1", (search_id,))
    row = cur.fetchone()
    conn.commit()
    conn.close()
    if row is None:
        return None
    else:
        return row['ebay_listing_id']

#inserts the listing into database if it does not already exist (constrained by ebay_listing_id)
def insert_bin_listing(listing: Bin_listing):
    conn = sqlite3.connect(path+"db/app_data.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    #check if listing is already entered
    cur.execute("SELECT COUNT(ebay_listing_id) FROM bin_listings WHERE ebay_listing_id=?",(listing.get_ebay_listing_id(),))
    existing_entry = cur.fetchone()[0] != 0
    if not existing_entry:
        cur.execute("INSERT INTO bin_listings (search_id, ebay_listing_id, url, accepts_best_offer, price) VALUES (?, ?, ?, ?, ?)", (listing.get_search_id(), listing.get_ebay_listing_id(), listing.get_listing_url(), listing.get_accepts_best_offer(), listing.get_price(),))
    conn.commit()
    conn.close()

def get_unprocessed_bin_listings():
    conn = sqlite3.connect(path+"db/app_data.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    #fetch all listings from bin_listings that do not exist in bin_notifications

    #start with fetching the search ids corresponding to the listings that have not been processed yet
    cur.execute("SELECT DISTINCT l.search_id FROM bin_listings AS l LEFT JOIN bin_notifications AS r ON l.id = r.bin_listing_id WHERE r.id IS NULL AND l.processed=0;")
    db_search_ids = cur.fetchall()

    #[{"search":search_data, "payload":[{row_object},{row_object}...]},{...},]
    payload = []
    for db_search_id in db_search_ids:
        search_id = db_search_id['search_id']
        search_payload = []
        cur.execute("SELECT * FROM bin_listings WHERE search_id=? AND processed=0", (search_id,))
        db_bin_payload = cur.fetchall()
        for db_listing in db_bin_payload:
            search_payload.append(db_listing)
        cur.execute("SELECT * FROM Searches WHERE id=?", (search_id,))
        search = cur.fetchone()

        payload_item = {
            "search": search,
            "payload": search_payload
        }
        payload.append(payload_item)
    #pretty bad for update anomalies
    cur.execute("UPDATE bin_listings SET processed=1")
    conn.commit()
    conn.close()
    return payload