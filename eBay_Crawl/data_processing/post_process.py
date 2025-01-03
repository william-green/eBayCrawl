import time
from ..db import db_functions as db_f


def process_new_bins(db_response_data):
    for search_frame in db_response_data:
        search_data = search_frame['search']
        for listing in search_frame['payload']:
            print(listing['url'])

            listing_id = listing['id']

            #accepts best offer
            if listing['accepts_best_offer'] == 1:
                db_f.create_bin_notification(listing_id)
                return
            
            if listing['price'] >= search_data['min_price'] and listing['price'] <= search_data['max_price']:
                db_f.create_bin_notification(listing_id)
                return
            
            #to-do add filtering functions to lookup url
            #and filter by listing title, description, condition, etc


#runs when the flag is not set
def post_process_data(db_lock):
    while True:
        time.sleep(1)

        #critical section
        db_lock.acquire()
        db_response_data = db_f.get_unprocessed_bin_listings()
        time.sleep(1)
        db_lock.release()

        process_new_bins(db_response_data)