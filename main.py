from find_listings import listing_poll_loop as find_listings
import threading
#from concurrent.futures import ThreadPoolExecutor

def main():
    #run the listing poll loop as a daemon so that the thread is terminated
    #if main thread has an interrupt
    find_listings_thread = threading.Thread(target=find_listings, daemon=True)
    find_listings_thread.start()

    #keep the main thread running for as long as child thread is
    #except in the case of an interrupt
    find_listings_thread.join()
if __name__ == "__main__":
    main()

"""import threading
import json
import search.searchFixed as searchFixed
import search.searchAuction as searchAuction
import queueManager
import os

def parseConf():
    if os.path.isfile("../conf.json"):
        with open("../conf.json") as confFile:
            print(confFile.read())
    else:
        with open("../settings.json",'w') as confFile:
            print('conf file not configured; creating file')

if __name__ == "__main__":
    profiles = open("./profiles/profiles.json","r")
    searchItems = json.load(profiles)
    for searchItem in searchItems:
        try:
            if searchItem['searchType'] == 'auction':
                print('starting threads')
                searchThread = threading.Thread(target=searchAuction.search,kwargs={'searchPrefs':searchItem})
                searchThread.start()
                queueManagerThread = threading.Thread(target=queueManager.queueManager,kwargs={'searchPrefs':searchItem})
                queueManagerThread.start()
            if searchItem['searchType'] == 'fixed':
                searchThread = threading.Thread(target=searchFixed.search,kwargs={'searchPrefs':searchItem})
                searchThread.start()
        except:
            pass"""