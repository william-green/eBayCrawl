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
import csv

profiles = open("./profiles/profiles.json","r")
searchItems = json.load(profiles)

lockedFiles = []

frameInterval = 60
maxThreadCount = 8

class load:

    def __init__(self):
        self._running = True

    def terminate(self):
        print('terminating network thread')
        self._running = False

    def load(self, searchItem):
        global session
        req = session.get(searchItem['searchURL'])
        if(searchItem['searchType'] == 'auction'):
            print('auction page')
            searchAuction.parseResults(req, searchItem)
        if(searchItem['searchType'] == 'fixed'):
            print('fixed page')
        print('loading page')
        self.terminate()
    
def loadSearches():
    for itm in searchItems:
        #sort the search queue such that the oldest update is prioritized
        sorted(searchItems, key = lambda item: item['lastUpdt'])
        if threading.active_count() < maxThreadCount:
            loadItm = load()
            t = threading.Thread(target=loadItm.load, args=(itm,))
            t.start()
            itm['lastUpdt'] = time.time()

if __name__ == "__main__":
    profiles = open("./profiles/profiles.json","r")
    searchItems = json.load(profiles)
    for itm in searchItems:
        #sets baseline timestamp for queue prioritization
        itm['lastUpdt'] = time.time()
        fileName = 'data/'+itm['dataName']
        fileExists = os.path.isfile(fileName)
        if not fileExists:
            with open(fileName,'a') as file:
                fields = ['url','endTime','notif']
                writer = csv.DictWriter(file,fieldnames=fields)
                writer.writeheader()
    
    iterQueue = []
    frmState = {"lastTime":time.time() - frameInterval}
    while True:
        #minimum interval time delay
        time.sleep(1)
        if time.time() - frmState['lastTime'] > frameInterval:
            #refresh pages
            print("refresh searches")
            loadSearches()
            frmState['lastTime'] = time.time()
        
        print(str(threading.active_count()) + " active threads")

        #queue stack
        for i,itm in enumerate(iterQueue):
            #call queue item
            itm()
            #delete queue item
            del iterQueue[i]