from util.get_abs_path import get_abs_path
from util.page_loader import parallel_page_loader
from util.bin_listing import Bin_listing
import time
from bs4 import BeautifulSoup
from db import db_functions as db_f
from search.search import Search
import sqlite3
from util.get_abs_path import get_abs_path
from util.listing_parser import parse_listing_entry
import re

path = get_abs_path()


#maximum number of pages of search results to iterate per search
max_search_pages = 5

def all_searches_complete(searches) -> bool:
    #no searches implies all complete
    if len(searches) == 0:
        return True
    
    #check if any searches are incomplete state
    for search in searches:
        if not search.get_complete():
            return False
    #all searches complete
    return True

def get_listing_id_from_url(listing_url):
    listing_id_group = re.search(r"/itm/(\d+)", listing_url)
    if(listing_id_group):
        listing_id = listing_id_group.group(1)
    else:
        raise ValueError("listing url contains no item id")
    return int(listing_id)

def check_listing_id(listing_url, newest_listing_id):
    listing_id = get_listing_id_from_url(listing_url)
    return listing_id == newest_listing_id

#from listing entry from main search page, determines if a listing accepts best offer
def listing_accepts_best_offer(listing_entry_code) -> bool:
    accepts_best_offer = False
    try:
        accepts_best_offer = len(listing_entry_code.select(".s-item__formatBestOfferEnabled")) > 0
    except:
        pass
    return accepts_best_offer

#from listing entry from main search page, finds the total price (price + shipping)
def get_listing_price(listing_entry_code) -> float:
    base_price = 0
    shipping_price = 0
    try:
        #base price
        #print(listing_entry_code.prettify())
        base_price_str = (listing_entry_code.select(".s-item__price")[0].text).replace(",","")
        base_price = float(base_price_str[1:])
        
        #shipping cost
        shipping_price_str = (listing_entry_code.select(".s-item__shipping s-item__logisticsCost")[0].text).replace(",","")
        #assume free shipping
        shipping_price = 0
        match = re.findall(r"\d+\.\d+", shipping_price_str)
        if match:
            shipping_price = float(match[0])
            print(shipping_price)
    except Exception as e:
        print(f"issue capturing listing price {e}")
        pass
    print(base_price)
    print(shipping_price)
    return base_price + shipping_price

def listing_poll_loop():
    while True:
        #get active searches from database
        db_searches = db_f.get_active_searches()
        searches = []
        for search in db_searches:
            #create new search objects for each db search item
            searches.append(Search(search, max_pages=max_search_pages))

        #iterate through all searches and get the newest recorded listing for each
        for search in searches:
            search_type = search.get_search_type()
            search_id = search.get_search_id()
            if search_type == 'bin':
                newest_listing = db_f.get_newest_bin_listing_ebay_id(search_id)
            elif search_type == 'auction':
                newest_listing = db_f.get_newest_auction_listing_ebay_id(search_id)
            else:
                raise TypeError("Search type is other than bin or auction.")
            print(newest_listing)

        #fetch next set of results
        while not all_searches_complete(searches):
            urls = [search.get_next_page_url() for search in searches]
            search_pages = parallel_page_loader(urls)

            #grabbing links from search page
            listing_urls = []
            #terminate state to break from nested loop
            terminate = False
            for search, search_page in zip(searches, search_pages):
                #check if page is blank
                if search_page == '':
                    continue
                #parsing
                soup = BeautifulSoup(search_page, 'html.parser')
                listing_entries = soup.select(".srp-results")[0].select(".s-item")
                for listing_entry in listing_entries:
                    listing_url = listing_entry.select(".s-item__link")[0]['href']

                    if check_listing_id(listing_url, newest_listing):
                        #listing has already been crawled. terminate search
                        #break and continue
                        print("reached end. break")
                        terminate = True
                        break
                    else:
                        #insert listing into database
                        listing_id = get_listing_id_from_url(listing_url)
                        if(search.get_search_type() == 'bin'):
                            #db_f.insert_bin_listing(search, listing_id)
                            #print("insert listing")

                            #def __init__(self, search_id: int, ebay_listing_id, url: str, accepts_best_offer: bool, price: float):
                            listing_obj = Bin_listing(search_id=search.get_search_id(), ebay_listing_id=listing_id, url=listing_url, accepts_best_offer = listing_accepts_best_offer(listing_entry), price=get_listing_price(listing_entry))
                            db_f.insert_bin_listing(listing_obj)
                        elif(search.get_search_type() == 'auction'):
                            print('insert auction listing into database')
                    listing_urls.append(listing_url)
                if terminate:
                    search.set_complete()
                    continue
            #for listing_url in listing_urls:
            #    print(listing_url)
            listing_pages = parallel_page_loader(listing_urls)
            parse_listing_entry(listing_pages)
            time.sleep(1)
        
        time.sleep(10)

def main():
    #for testing purposes, create the searches
    """
    conn = sqlite3.connect(path+"db/app_data.db")
    cur = conn.cursor()
    cur.execute(
        '''
        INSERT INTO Searches (name, min_price, max_price, type, url, is_active) VALUES (
            '3ds consoles',
            40.00,
            80.00,
            'bin',
            'https://www.ebay.com/sch/i.html?_from=R40&_nkw=3ds+console&_sacat=0&LH_BIN=1&_sop=1',
            1
        )
        '''
    )
    conn.commit()
    conn.close()
    """

    """
    conn = sqlite3.connect(path+"db/app_data.db")
    cur = conn.cursor()
    cur.execute(
        '''
        INSERT INTO Searches (name, min_price, max_price, type, url, is_active) VALUES (
            'iPod 5th Gen',
            20.00,
            80.00,
            'bin',
            'https://www.ebay.com/sch/i.html?_from=R40&_trksid=p2334524.m570.l1313&_nkw=ipod+5th+generation&_sacat=0&_odkw=ipod&_osacat=0&LH_BIN=1&_sop=10',
            1
        )
        '''
        #https://www.ebay.com/sch/i.html?_from=R40&_trksid=p2334524.m570.l1313&_nkw=ipod+5th+generation&_sacat=0&_odkw=ipod&_osacat=0&LH_BIN=1&_sop=10
    )
    conn.commit()
    conn.close()
    """

    listing_poll_loop()

if __name__ == "__main__":
    main()