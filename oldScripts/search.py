from requests_html import HTMLSession
session = HTMLSession()
import threading
import re
import webbrowser
import analyze
from notifs import notif
from urllib import parse

class search:
    def __init__(self,search):
        self.currentPage = 0
        self.parsing = False
        self.searchPrefs = search
        self.queue = []
        self.updateFeed(search['searchURL'])
    def calculateTime(self,timeSegs):
        timeCodes = {
            's':1,
            'm':60,
            'h':60*60,
            'd':60*60*24
        }
        timeRem = 0
        for seg in timeSegs:
            for code in timeCodes:
                if seg.find(code) != -1:
                    #timecode match; pull int from string
                    addTime = int(re.findall("\d+",seg)[0])*timeCodes[code]
                    timeRem += addTime
        if self.searchPrefs['notifTime'] != 0:
            #schedule checkup on listing once notif time approaches
            return timeRem - self.searchPrefs['notifTime']
    def analyzeListing(self,listingURL):
        print('')
        req = session.get(listingURL)
        try:
            sellerConditionDesc = req.html.find('#itmSellerDesc') or req.html.find('.viSNotesCnt')[0]
            posWordSearchResult = [analyze.searchText(x,sellerConditionDesc) for x in self.searchPrefs['posWords']]
            negWordSearchResult = [analyze.searchText(x,sellerConditionDesc) for x in self.searchPrefs['negWords']]
            #print(posWordSearchResult)
            #print(negWordSearchResult)
        except:
            #webbrowser.open(listingURL,new=2)
            print('seller description not found')
            pass
        try:
            sellerDescURL = req.html.find('#desc_ifr')[0].attrs['src']
            sellerDesc = session.get(sellerDescURL)
            sellerDescText = sellerDesc.html.text
            posWordSearchResult = [analyze.searchText(x,sellerDescText) for x in self.searchPrefs['posWords']]
            negWordSearchResult = [analyze.searchText(x,sellerDescText) for x in self.searchPrefs['negWords']]
            #print(posWordSearchResult)
            #print(negWordSearchResult)

        except:
            print('item description not found')
            #webbrowser.open(listingURL,new=2)
            pass

        try:
            itemPrice = float(re.findall("\d+\.\d+",req.html.find("#prcIsum_bidPrice, #prcIsum, #mm-saleDscPrc, #convbidPrice")[0].text)[0])
            try:
                shippingPrice = float(re.findall("\d+\.\d+",req.html.find("#fshippingCost, #fshippingCost")[0].text)[0])
            except:
                shippingPrice = 0

            try:
                if (itemPrice + shippingPrice) < self.searchPrefs['maxPrice'] and (itemPrice + shippingPrice) > self.searchPrefs['minPrice']:
                    print('within price restrictions')
                    self.queue.remove(listingURL)
                    if len(self.queue) < 25 and self.parsing == False:
                        searchURLParams = dict(parse.parse_qsl(parse.urlsplit(self.currentPage).query))
                        if '_&pgn' in searchURLParams:
                            searchURLParams['_&pgn'] += 1
                        else:
                            searchURLParams['_&pgn'] = 1
                        #SplitResult(scheme='https', netloc='www.ebay.com', path='/sch/i.html', query='_from=R40&_nkw=ds&_sacat=0&_sop=1', fragment='')
                        pageCmp = parse.urlsplit(self.currentPage)
                        print('next page')
                        self.updateFeed(URL=pageCmp['scheme']+"://"+pageCmp['netloc']+pageCmp['path']+urllib.urlencode(searchURLParams)+pageCmp['fragment'])
                        #print(parse.urlsplit(self.currentPage))
                    '''
                    if self.queue.index(listingURL):
                        print('url in queue')
                    if listingURL in self.queue:
                        print('url in queue')
                        self.queue.remove(listingURL)
                        if len(self.queue) < 25:
                            self.updateFeed()
                    '''
                    notif.send(listingURL)
            except Exception as e:
                print(e)
        except:
            print("error getting price")
            webbrowser.open(listingURL,new=2)
            pass
        print("===========")
        
    def updateFeed(self,URL,**kwargs):
        self.currentPage = URL
        self.parsing = True
        req = session.get(URL)
        results = req.html.find("#mainContent .srp-river-results .srp-results .s-item__wrapper")
        for result in results:
            timing = self.calculateTime(result.find('.s-item__time-left')[0].text.split(" "))
            listingURL = result.find('.s-item__link')[0].attrs['href']
            price = False
            shipping = 0
            try:
                shipping = float(re.findall("\d+\.\d+",result.find('.s-item__shipping')[0].text)[0])
            except:
                shipping = 0
            try:
                price = float(re.findall("\d+\.\d+",result.find('.s-item__price')[0].text)[0])+shipping
            except:
                print('')
            self.queue.append(listingURL)
            if price < self.searchPrefs['maxPrice'] and price > self.searchPrefs['minPrice']:
                if timing <= 0:
                    self.analyzeListing(listingURL)
                else:
                    #print(str(timing))
                    analyzeTimer = threading.Timer(timing,self.analyzeListing,args=(listingURL,))
                    analyzeTimer.start()
                #print("found")
            else:
                print('')
        self.parsing = False


