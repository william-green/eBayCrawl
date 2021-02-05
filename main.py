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
        found = False
        fileExists = os.path.isfile(fileName)
        if not found:
            with open(fileName,'a') as file:
                fields = ['url','endTime','notif']
                writer = csv.DictWriter(file,fieldnames=fields)
                writer.writeheader()

        '''
        fileName = 'data/'+self.searchPrefs['dataName']
		found = False
		fileExists = os.path.isfile(fileName)
		if fileExists:
			#print('file exists')
			with open(fileName,'r') as file:
				reader = csv.DictReader(file)
				for row in reader:
					if data['url'] == row['url']:
						#print('duplicate detected')
						found = True
        if not found:
			#the new data is not a duplicate or the file does not exist
			with open(fileName,'a') as file:
				#if not os.path.isfile(fileName)
				fields = ['url','endTime','notif']
				writer = csv.DictWriter(file,fieldnames=fields)
				if not fileExists:
					writer.writeheader()
				data['notif'] = False
				writer.writerow(data)
        '''
    
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
        
        print(str(threading.active_count()) + " active threads")

        #queue stack
        for i,itm in enumerate(iterQueue):
            #call queue item
            itm()
            #delete queue item
            del iterQueue[i]