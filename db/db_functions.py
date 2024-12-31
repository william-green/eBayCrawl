
import sqlite3
from util.get_abs_path import get_abs_path
from search.search import Search

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

def get_newest_bin_listing(search_id):
    conn = sqlite3.connect(path+"db/app_data.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM bin_listings WHERE search_id = ? ORDER BY date_created DESC LIMIT 1", (search_id,))
    rows = cur.fetchall()
    conn.commit()
    conn.close()
    return rows

def get_newest_auction_listing(search_id):
    conn = sqlite3.connect(path+"db/app_data.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM auction_listings WHERE search_id = ? ORDER BY date_created DESC LIMIT 1", (search_id,))
    rows = cur.fetchall()
    conn.commit()
    conn.close()
    return rows

def insert_bin_listing(search, listing_id, accepts_best_offer, price):
    '''search_id = search.get_search_id()
    ebay_listing_id = listing_id
    accepts_best_offer = 
    conn = sqlite3.connect(path+"db/app_data.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute()
    conn.commit()
    conn.close()'''
    print(listing_id)
    print(type(listing_id))