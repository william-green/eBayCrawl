from requests_html import HTMLSession
session = HTMLSession()
#from requests_html import AsyncHTMLSession
#session = AsyncHTMLSession()
from urllib import parse
from urllib.parse import urlparse
import re
import threading
import time
import webbrowser
from notifs import notif


class search:
	def __init__(self,searchPrefs):
		self.status = {
		'searchParams':{
		'minPrice':searchPrefs['minPrice'],
		'maxPrice':searchPrefs['maxPrice'],
		'notifTime':searchPrefs['notifTime'],
		'queueMax':searchPrefs['queueMax']
		},
		'pageURL':searchPrefs['searchURL'],#holds current search page
		'parsing':False, #true if page results are being parsed; false when parsing is complete
		'queue':[],#holds URL and timing for when to check up on listings of interest
		'ctrl':False, #True to pause the control loop
		'queueUpdateTime':0 #last time the queue was updated
		}
		self.timeLoop()
	def loadResults(self):
		print('loading page')
		page = self.status['pageURL']
		self.status['parsing'] = True
		urlParams = dict(parse.parse_qsl(parse.urlsplit(page).query))
		if "_pgn" not in urlParams:
			urlParams['_pgn'] = 1
			self.status['pageURL'] = page.split('?')[0]+'?'+parse.urlencode(urlParams)
		else:
			urlParams['_pgn'] = str(int(urlParams['_pgn']) + 1)
			self.status['pageURL'] = page.split('?')[0]+'?'+parse.urlencode(urlParams)
		#self.status['pageURL'] = page
		req = session.get(self.status['pageURL'])
		#parse result blocks
		results = req.html.find(".srp-results .s-item__wrapper.clearfix")
		for result in results:
			self.parseResult(result)
		if len(self.status['queue']) <= self.status['searchParams']['queueMax']:
			self.status['parsing'] = False
		#self.status['ctrl'] = True
	def calculateTime(self,timeString):
		timeCodes = {'s':1,'m':60,'h':60*60,'d':60*60*24}
		timeRem = 0
		for seg in timeString:
			for code in timeCodes:
				if seg.find(code) != -1:
					#timecode math; pull int from string
					addTime = int(re.findall("\d+",seg)[0])*timeCodes[code]
					timeRem += addTime
		if self.status['searchParams']['notifTime'] != 0:
			#return time remaining
			return timeRem - self.status['searchParams']['notifTime']
		else:
			#return time remaining
			return timerem
	def analyzeListing(self,url):
		for item in self.status['queue']:
			if item['url'] == url:
				currentItem = item
				self.status['queue'].remove(item)

		req = session.get(url)

		try:
			sellerConditionDesc = req.html.find('#itmSellerDesc') or req.html.find('.viSNotesCnt')[0]
		except:
			pass

		try:
			sellerDescUrl = req.html.find('#desc_ifr')[0].attrs['src']
			sellerDesc = session.get(sellerDescUrl)
			sellerDescText = sellerDesc.html.text
		except:
			pass

		try:
			itemPrice = float(re.findall("\d+\.\d+",req.html.find("#prcIsum_bidPrice, #prcIsum, #mm-saleDscPrc, #convbidPrice")[0].text)[0])
			try:
				shippingPrice = float(re.findall("\d+\.\d+",req.html.find("#fshippingCost")[0].text)[0])
			except:
				shippingPrice = 0

			try:
				if (itemPrice + shippingPrice) < self.status['searchParams']['maxPrice'] and (itemPrice + shippingPrice) > self.status['searchParams']['minPrice']:
					notif.send(url.strip())
				else:
					print('outside price')
			except:
				print('exception with price analysis')
				pass
		except:
			print('exception getting item price')
			pass
	def parseResult(self,result):
		#get time remaining in seconds
		timing = self.calculateTime(result.find('.s-item__time-left')[0].text.split(" "))
		#get listing url
		listingURL = result.find('.s-item__link')[0].attrs['href']
		#calculate total item cost
		try:
			shipping = float(re.findall("\d+\.\d+",result.find('.s-item__shipping')[0].text)[0])
		except:
			shipping = 0
		try:
			price = float(re.findall("\d+\.\d+",result.find('.s-item__price')[0].text)[0])+shipping
		except:
			print('Could not find price.')
		#check price constraints
		if price < self.status['searchParams']['maxPrice'] and price > self.status['searchParams']['minPrice']:
			#within price constraints
			timing = 0 if timing < 0 else timing
			self.status['queue'].append({"url":listingURL,"notifTimer":timing*1000.0,"timeAdded":time.time()*1000.0})
		#else:
		#	print('outside price constraints')
	def updateQueue(self):
		#lastTime = time.time()
		#while True:

		#decrease time by time passed for each queue item
		#check if queue time is zero
		#print('queue')
		if len(self.status['queue']) >= 1:
			#webbrowser.open(self.status['queue'][0]['url'])
			print(str(self.status['queue'][0]['notifTimer']/1000)+' seconds remaining on next in queue')
			for item in self.status['queue']:
				if self.status['queueUpdateTime'] == 0:
					item['notifTimer'] -= (time.time()*1000.0 - item['timeAdded'])
				else:
					item['notifTimer'] -= (time.time()*1000.0 - self.status['queueUpdateTime'])
				self.status['queueUpdateTime'] = time.time()*1000.0
				if item['notifTimer'] <= 0:
					self.analyzeListing(item['url'])
					#print('listing timer expired')
		#print('update queue')
			#time.sleep(1)
	def timeLoop(self):
		while True:
			print(str(len(self.status['queue']))+ ' items in queue')
			if not self.status['parsing']:
				self.loadResults()
			else:
				print('parsing')
			self.updateQueue()
			if self.status['ctrl']:
				break
			time.sleep(1)