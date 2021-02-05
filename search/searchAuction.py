from requests_html import HTMLSession
session = HTMLSession()
from urllib import parse
from urllib.parse import urlparse
import re
import json
import time
import os.path
import csv
import webbrowser

def calculateTime(timeString, searchItem):
	timeCodes = {'s':1,'m':60,'h':60*60,'d':60*60*24}
	timeRem = 0
	for seg in timeString:
		for code in timeCodes:
			if seg.find(code) != -1:
				#timecode math; pull int from string
				addTime = int(re.findall("\d+",seg)[0])*timeCodes[code]
				timeRem += addTime
	#return auction time remaining
	return timeRem - searchItem['notifTime']

def parseResult(result, searchItem):
	#get time remaining in seconds
	timing = calculateTime(result.find('.s-item__time-left')[0].text.split(" "), searchItem)
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
		#send notif of error and listing link
	#check price constraints
	if price < searchItem['maxPrice'] and price > searchItem['minPrice']:
		#check item specifics
		spcMtch = True
		if(len(searchItem['specifics']) > 0):
			global session
			req = session.get(listingURL)
			itemSpecifics = req.html.find('#viTabs_0_is')[0]
			for term in searchItem['specifics']:
				if(itemSpecifics.text.lower().find(term.lower()) == -1):
					spcMtch = False
		#if(spcMtch):
		#all applicable item specific constraints have been met
		#all price constraints have been met
		#append to monitoring queue

	#pull remaining time text string
	if(len(result.find('.s-item__time-left')) > 0):
		timing = calculateTime(result.find('.s-item__time-left')[0].text.split(' '), searchItem)
		#pull listing link
		listingURL = result.find('.s-item__link')[0].attrs['href'].split('?')[0]
		#calculate total item cost...
		#find the shipping cost if applicable...
		try:
			shipping = float(re.findall("\d+\.\d+",result.find('.s-item__shipping')[0].text.replace(',',''))[0])
		except:
			#free shipping
			shipping = 0
		#find item price and add shipping...
		try:
			price = float(re.findall("\d+\.\d+",result.find('.s-item__price')[0].text.replace(',',''))[0])+shipping
		except:
			print('could not find price for '+listingURL)
	

def parseResults(req,searchItem):
	#pull all individual listings from search results...
	results = req.html.find(".srp-results .s-item__wrapper.clearfix")
	for result in results:
		#parse a single search result...
		parseResult(result, searchItem)
		'''
		#get time remaining in seconds
		timing = self.calculateTime(result.find('.s-item__time-left')[0].text.split(" "))
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
		if price < self.searchPrefs['maxPrice'] and price > self.searchPrefs['minPrice']:
			#within price constraints
			timing = 0 if timing < 0 else timing
			self.appendQueue({"url":listingURL,"endTime":time.time()+timing})
		'''

class search:
	def __init__(self,searchPrefs):
		self.searchPrefs = searchPrefs
		self.status = {
			'page':searchPrefs['searchURL']
		}
		while True:
			self.loadResults(searchPrefs['searchURL'])
			time.sleep(60)
	def loadResults(self,url):
		global session
		'''
		urlParams = dict(parse.parse_qsl(parse.urlsplit(url).query))
		if "_pgn" not in urlParams:
			urlParams['_pgn'] = 1
			self.status['pageURL'] = page.split('?')[0]+'?'+parse.urlencode(urlParams)
		else:
			urlParams['_pgn'] = str(int(urlParams['_pgn']) + 1)
			self.status['pageURL'] = page.split('?')[0]+'?'+parse.urlencode(urlParams)
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
			return timeRem
	def appendQueue(self,data):
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
	def parseResult(self,result):
		#get time remaining in seconds
		timing = self.calculateTime(result.find('.s-item__time-left')[0].text.split(" "))
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
		if price < self.searchPrefs['maxPrice'] and price > self.searchPrefs['minPrice']:
			#within price constraints
			timing = 0 if timing < 0 else timing
			self.appendQueue({"url":listingURL,"endTime":time.time()+timing})

