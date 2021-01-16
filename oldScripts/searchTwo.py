from requests_html import HTMLSession
session = HTMLSession()
from urllib import parse
from urllib.parse import urlparse
import re
import threading
import time
import webbrowser
from notifs import notif


class search:
	def __init__(self,searchPrefs):
		self.searchPrefs = searchPrefs
		#self.status = {}
		self.queue = []
		#self.page = False
		self.getResultsPage(searchPrefs['searchURL'])
	def getResultsPage(self,page):
		print('loading page')
		urlParams = dict(parse.parse_qsl(parse.urlsplit(page).query))
		if "_pgn" not in urlParams:
			urlParams['_pgn'] = 1
			page = page.split('?')[0]+'?'+parse.urlencode(urlParams)
		else:
			urlParams['_pgn'] = str(int(urlParams['_pgn']) + 1)
			page = page.split('?')[0]+'?'+parse.urlencode(urlParams)
		req = session.get(page)
		#parse result blocks
		results = req.html.find(".srp-results .s-item__wrapper.clearfix")
		for result in results:
			self.parseResult(result)
		self.getResultsPage(page)

	def calculateTime(self,timeString):
		timeCodes = {'s':1,'m':60,'h':60*60,'d':60*60*24}
		timeRem = 0
		for seg in timeString:
			for code in timeCodes:
				if seg.find(code) != -1:
					#timecode math; pull int from string
					addTime = int(re.findall("\d+",seg)[0])*timeCodes[code]
					timeRem += addTime
		if self.searchPrefs['notifTime'] != 0:
			#return time remaining
			return timeRem - self.searchPrefs['notifTime']
		else:
			#return time remaining
			return timerem
	def analyzeListing(self,url):
		print('analyze listing')
		#update queue
		for item in self.queue:
			if item['url'] == url:
				self.queue.remove(item)
		print(str(len(self.queue))+' items in queue')

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
				if (itemPrice + shippingPrice) < self.searchPrefs['maxPrice'] and (itemPrice + shippingPrice) > self.searchPrefs['minPrice']:
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
		timing = self.calculateTime(result.find('.s-item__time-left')[0].text.split(" "))
		listingURL = result.find('.s-item__link')[0].attrs['href']
		try:
			shipping = float(re.findall("\d+\.\d+",result.find('.s-item__shipping')[0].text)[0])
		except:
			shipping = 0
		try:
			price = float(re.findall("\d+\.\d+",result.find('.s-item__price')[0].text)[0])+shipping
		except:
			print('Could not find price.')
		if price < self.searchPrefs['maxPrice'] and price > self.searchPrefs['minPrice']:
			#within price constraints
			self.queue.append({"url":listingURL,"queueTime":time.time(),"timeRem":timing})
		if self.searchPrefs['notifTime'] != 0:
			print('setting timer: '+str(timing)+" || "+result.find('.s-item__time-left')[0].text)
			if timing <= 0:
				#already below notif time
				self.analyzeListing(listingURL)
			else:
				#wait before issuing notification
				analyzeTimer = threading.Timer(timing,self.analyzeListing,args=(listingURL,))
				analyzeTimer.start()
		else:
			print('notif time not set. Write further analysis.')
		try:
			if len(self.queue) > self.searchPrefs['queueMax']:
				print(str(len(self.queue)))
				print('wait for queue for '+str(self.queue[-1]['timeRem']))
				time.sleep(self.queue[-1]['timeRem'])
		except:
			pass