from requests_html import HTMLSession
session = HTMLSession()
from urllib import parse
from urllib.parse import urlparse
import re
import json
import time
import os.path
import csv
from notifs import notif
import globalData

def parseResult(result, searchItem):
	#get time remaining in seconds
	#timing = self.calculateTime(result.find('.s-item__time-left')[0].text.split(" "))
	#get listing url
	listingURL = result.find('.s-item__link')[0].attrs['href'].split('?')[0]
	print(listingURL)
	#calculate total item cost
	try:
		shipping = float(re.findall("\d+\.\d+",result.find('.s-item__shipping')[0].text.replace(',',''))[0])
	except:
		shipping = 0
	try:
		price = float(re.findall("\d+\.\d+",result.find('.s-item__price')[0].text.replace(',',''))[0])+shipping
	except Exception as e:
		print(str(e))
		notif.send('--------\r\n' + str(e) + ' \r\n .s-item__price \r\n ' + listingURL + '\r\n --------------\r\n')

	if price < searchItem['maxPrice'] and price > searchItem['minPrice']:
		#check item specifics
		spcMtch = True
		if(len(searchItem['specifics']) > 0):
			global session
			req = session.get(listingURL)
			try:
				itemSpecifics = req.html.find("#viTabs_0_is", first=True)
				#print(len(itemSpecifics))
				if itemSpecifics is not None:
					try:
						for term in searchItem['specifics']:
							#notif.send('itemSpecifics type is '+str(type(itemSpecifics)))
							if(itemSpecifics.text.lower().find(term.lower()) == -1):
								spcMtch = False
					except Exception as e:
						print(str(e))
						notif.send('--------\r\n' + str(e) + ' \r\n issue scanning for keywords in item specifics \r\n ' + str(req.html) + '\r\n' + listingURL + '\r\n --------------\r\n')
			except Exception as e:
				print(str(e))
				notif.send('--------\r\n' + str(e) + ' \r\n #viTabs_0_is \r\n ' + str(req.html) + '\r\n' + listingURL + '\r\n --------------\r\n')
		if(spcMtch):
			#all applicable item specific constraints have been met
			#all price constraints have been met
			#append to monitoring queue
			data = {"listingUrl":listingURL,"timeAdded":time.time()} #data dict package
			fileName = 'data/'+searchItem['dataName']
			found = False #flag for whether entry already recorded
			fileExists = os.path.isfile(fileName)
			if fileExists: #queue cache file exists
				with open(fileName,'r') as file:
					reader = csv.DictReader(file)
					for row in reader:
						#keyerror exception bug
						if data['listingUrl'] == row['url']:
							#listing is already in cache queue
							found = True
				if not found: #listing is not in cache queue; append to queue
					globalData.lockedFiles.append(fileName)
					with open(fileName,'a') as file:
						fields = ['url','timeAdded']
						writer = csv.DictWriter(file,fieldnames = fields)
						#data['notif'] = False
						#debugging only...
						data['url'] = data['listingUrl']
						del data['listingUrl']
						writer.writerow(data)
					globalData.lockedFiles.remove(fileName)
					notif.send(listingURL)
	'''
	#check price constraints
	if price < self.searchPrefs['maxPrice'] and price > self.searchPrefs['minPrice'] and listingURL.find('checksum') == -1:
		#within price constraints
		#timing = 0 if timing < 0 else timing
		self.appendRecord({"url":listingURL,"timeAdded":time.time()})
	'''

def parseResults(req, searchItem):
	results = req.html.find(".srp-results .s-item__wrapper.clearfix")
	for result in results:
		parseResult(result, searchItem)

class search:
	def __init__(self,searchPrefs):
		print('searching fixed')
		self.searchPrefs = searchPrefs
		while True:
			self.loadResults(searchPrefs['searchURL'])
			time.sleep(60)
	def loadResults(self,url):
		global session
		print('loading page')
		'''
		connected = False

		while not connected:
		    try:
		        try_connect()
		        connected = True
		    except ...:
		        pass
		'''
		req = False
		while not req:
			try:
				req = session.get(url)
			except:
				del session
				session = HTMLSession()
				time.sleep(1)
				pass
		#parse result blocks
		results = req.html.find(".srp-results .s-item__wrapper.clearfix")
		for result in results:
			self.parseResult(result)
		#update url
		'''
		urlParams = dict(parse.parse_qsl(parse.urlsplit(url).query))
		if "_pgn" not in urlParams:
			urlParams['_pgn'] = 1
			url = url.split('?')[0]+'?'+parse.urlencode(urlParams)
		else:
			urlParams['_pgn'] = str(int(urlParams['_pgn']) + 1)
			url = url.split('?')[0]+'?'+parse.urlencode(urlParams)
		print(url)
		self.loadResults(url)
		'''
	def appendRecord(self,data):
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
				fields = ['url','timeAdded']
				writer = csv.DictWriter(file,fieldnames=fields)
				if not fileExists:
					writer.writeheader()
				writer.writerow(data)
				#print("====================fixed: "+data['url'])
				notif.send(data['url'])
	def parseResult(self,result):
		#get time remaining in seconds
		#timing = self.calculateTime(result.find('.s-item__time-left')[0].text.split(" "))
		#get listing url
		listingURL = result.find('.s-item__link')[0].attrs['href'].split('?')[0]
		#calculate total item cost
		try:
			shipping = float(re.findall("\d+\.\d+",result.find('.s-item__shipping')[0].text.replace(',',''))[0])
		except:
			shipping = 0
		try:
			price = float(re.findall("\d+\.\d+",result.find('.s-item__price')[0].text.replace(',',''))[0])+shipping
		except:
			print('Could not find price.')
		#check price constraints
		if price < self.searchPrefs['maxPrice'] and price > self.searchPrefs['minPrice'] and listingURL.find('checksum') == -1:
			#within price constraints
			#timing = 0 if timing < 0 else timing
			self.appendRecord({"url":listingURL,"timeAdded":time.time()})