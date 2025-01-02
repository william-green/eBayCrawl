from find_listings import listing_poll_loop as find_listings
from data_processing.post_process import post_process_data
from notifs.telegram_server import init_telegram_bot
import threading
#from multiprocessing import Manager
import time
from threading import Lock
#from concurrent.futures import ThreadPoolExecutor

def main():

    db_lock = Lock()
    #sleep between starting threads to avoid thread lock contention

    #run the listing poll loop as a daemon so that the thread is terminated
    #if main thread has an interrupt
    find_listings_thread = threading.Thread(target=find_listings, args=(db_lock,), daemon=True)
    find_listings_thread.start()
    time.sleep(1)
    post_process_data_thread = threading.Thread(target=post_process_data, args=(db_lock,), daemon=True)
    post_process_data_thread.start()

    init_telegram_bot()

    #keep the main thread running for as long as child thread is
    #except in the case of an interrupt
    find_listings_thread.join()
    post_process_data_thread.join()
if __name__ == "__main__":
    main()