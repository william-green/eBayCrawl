import threading
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
            pass