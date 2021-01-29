import threading
import json
import search.searchFixed as searchFixed
import search.searchAuction as searchAuction
import queueManager
import os
import time
from requests_html import HTMLSession
session = HTMLSession()
import sys

'''
def parseConf():
    if os.path.isfile("../conf.json"):
        with open("../conf.json") as confFile:
            print(confFile.read())
    else:
        with open("../settings.json",'w') as confFile:
            print('conf file not configured; creating file')
'''
profiles = open("./profiles/profiles.json","r")
searchItems = json.load(profiles)

frameInterval = 1
maxThreadCount = 8

class load:

    def __init__(self):
        self._running = True

    def terminate(self):
        print('terminating')
        self._running = False

    def load(self, url):
        global session
        req = session.get(url)
        results = req.html.find(".srp-results .s-item__wrapper.clearfix")
        print('loading page')
        self.terminate()
        #sys.exit()
    
def loadSearches():
    for itm in searchItems:
        if threading.active_count() < maxThreadCount:
            print(type(searchItems[0]))
            loadItm = load()
            t = threading.Thread(target=loadItm.load, args=(searchItems[0]['searchURL'],))
            t.start()
    '''
    for itm in searchItems:
        print("search item")
        #processThread = threading.Thread(target=processLine, args=(dRecieved,))  # <- note extra ','
        loadItm = load()
        t = threading.Thread(target=loadItm.load, args=(itm['searchURL'],))
        t.start()
    '''

if __name__ == "__main__":
    profiles = open("./profiles/profiles.json","r")
    searchItems = json.load(profiles)
    for itm in searchItems:
        itm['lastUpdt'] = time.time()#sets baseline timestamp for queue prioritization
    
    iterQueue = []
    frmState = {"lastTime":time.time()}
    while True:
        #minimum interval time delay
        time.sleep(1)
        if time.time() - frmState['lastTime'] > frameInterval:
            #refresh pages
            print("refresh searches")
            loadSearches()
            frmState['lastTime'] = time.time()
        
        print(threading.active_count())

        #queue stack
        for i,itm in enumerate(iterQueue):
            #call queue item
            itm()
            #delete queue item
            del iterQueue[i]

    for searchItem in searchItems:
        print(searchItem)
        #create threads for all network requests
        #
        '''
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
        '''