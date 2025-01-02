import queue
import threading
import time
from db import db_functions as db_f

def process_new_bins(db_response_data):
    for search_frame in db_response_data:
        print(search_frame['search']['min_price'])
        for listing in search_frame['payload']:
            print(listing['url'])

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


if __name__ == "__main__":
    process_new_bins()