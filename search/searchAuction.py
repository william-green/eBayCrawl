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
import globalData
from shutil import copyfile
from notifs import notif
import sys

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
	except Exception as e:
		print(str(e))
		notif.send('--------\r\n' + str(e) + ' \r\n .s-item__price \r\n ' + listingURL + '\r\n --------------\r\n')
	#check price constraints
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
			data = {"listingUrl":listingURL,"endTime":time.time()+timing-searchItem['notifTime']} #data dict package
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
						fields = ['url','endTime','notif']
						writer = csv.DictWriter(file,fieldnames = fields)
						data['notif'] = False
						#debugging only...
						data['url'] = data['listingUrl']
						del data['listingUrl']
						writer.writerow(data)
					globalData.lockedFiles.remove(fileName)

def checkListing(url, searchItem):
	global session
	req = session.get(url)
	#seller condition description
	try:
		sellerConditionDesc = req.html.find('#itmSellerDesc') or req.html.find('.viSNotesCnt')[0]
	except Exception as e:
		sellerConditionDesc = ''
		print("error getting seller desc: "+str(e))
	#listing description
	try:
		sellerDescUrl = req.html.find('#desc_ifr')[0].attrs['src']
		sellerDesc = session.get(sellerDescUrl)
		sellerDescText = sellerDesc.html.text
	except Exception as e:
		print('error getting listing description: '+str(e))
	#listing price
	try:
		itemPrice = float(re.findall("\d+\.\d+",req.html.find("#prcIsum_bidPrice, #prcIsum, #mm-saleDscPrc, #convbidPrice")[0].text)[0])
	except Exception as e:
		itemPrice = 0
		print('exception getting item price: '+str(e))
	#listing shipping price
	try:
		shippingPrice = float(re.findall("\d+\.\d+",req.html.find("#fshippingCost")[0].text)[0])
	except Exception as e:
		print('shipping: '+str(e))
		shippingPrice = 0
	#review constraints
	try:
		if (itemPrice + shippingPrice) < searchItem['maxPrice'] and (itemPrice + shippingPrice) > searchItem['minPrice'] and itemPrice != 0:
			print('auction ending; sending notif...')
			#send notification
			notif.send(url)
	except Exception as e:
		print('exception with price analysis: '+str(e))

def parseResults(req,searchItem):
	#pull all individual listings from search results...
	results = req.html.find(".srp-results .s-item__wrapper.clearfix")
	for result in results:
		#parse a single search result...
		parseResult(result, searchItem)

def checkQueue(searchItems):
	for itm in searchItems:
		if 'data/'+itm['dataName'] not in globalData.lockedFiles:
			globalData.lockedFiles.append('data/'+itm['dataName'])
			print('not locked')
			tmpfileName = 'data/.'+itm['dataName']
			fileName = 'data/'+itm['dataName']
			found = False
			fileExists = os.path.isfile(fileName)
			if fileExists:
				copyfile(fileName,tmpfileName)
				with open(tmpfileName,'r') as file:
					reader = csv.DictReader(file)
					with open(fileName,'w') as file:
						fields = ['url','endTime','notif']
						writer = csv.DictWriter(file,fieldnames=fields)
						writer.writeheader()
						for row in reader:
							if ((float(row['endTime']) - time.time())/60) <= 0 and row['notif'] == 'False':
							#listing is ending and has not been processed
								row['notif'] = True
								writer.writerow(row)
								checkListing(row['url'], itm)
							else:
								writer.writerow(row)
				os.remove(tmpfileName)
			globalData.lockedFiles.remove('data/'+itm['dataName'])
		else:
			print('locked')