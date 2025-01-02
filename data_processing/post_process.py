import queue
import threading
#from util.shared import OwnedEvent
import time

#runs when the flag is not set
def post_process_data(db_lock):
    while True:
        time.sleep(1)
        db_lock.acquire()
        #print("post_process: accessing database")
        time.sleep(1)
        db_lock.release()
