from requests_html import HTMLSession
session = HTMLSession()
import time
import json
from notifs import notif
import webbrowser
import re
import os
import csv
from shutil import copyfile

class queueManager:
	def __init__(self,searchPrefs):
		self.searchPrefs = searchPrefs
		print('manage')
		time.sleep(5)
		self.ctrlStop = False
		self.updateQueue()
	def analyzeListing(self,url):
		global session
		#print('analyzing listing before loaded')
		req = False
		while not req:
			try:
				req = session.get(url)
			except:
				del session
				session = HTMLSession()
				time.sleep(1)
				pass
		#webbrowser.open(url)
		print('analyze listing after page load')
		#notif.send(url)
		#seller condition description
		try:
			sellerConditionDesc = req.html.find('#itmSellerDesc') or req.html.find('.viSNotesCnt')[0]
			print('======================seller desc found')
		except Exception as e:
			sellerConditionDesc = ''
			print("error getting seller desc: "+str(e))
			pass
		print('sellerConditionDesc: ')
		print(sellerConditionDesc)
		#listing description
		try:
			sellerDescUrl = req.html.find('#desc_ifr')[0].attrs['src']
			try:
				sellerDesc = session.get(sellerDescUrl)
			except:
				del session
				session = HTMLSession()
				sellerDesc = session.get(sellerDescUrl)
			sellerDescText = sellerDesc.html.text
			print('======================listing description found')
		except Exception as e:
			print('error getting listing description: '+str(e))
			pass
		#listing price
		try:
			itemPrice = float(re.findall("\d+\.\d+",req.html.find("#prcIsum_bidPrice, #prcIsum, #mm-saleDscPrc, #convbidPrice")[0].text)[0])
			print('======================item price found')
		except Exception as e:
			itemPrice = 0
			print('exception getting item price: '+str(e))
			pass
		#listing shipping price
		try:
			shippingPrice = float(re.findall("\d+\.\d+",req.html.find("#fshippingCost")[0].text)[0])
			print('======================shipping price found')
		except Exception as e:
			print('shipping: '+str(e))
			shippingPrice = 0
			pass
		#review constraints
		print(str(itemPrice + shippingPrice))
		try:
			if (itemPrice + shippingPrice) < self.searchPrefs['maxPrice'] and (itemPrice + shippingPrice) > self.searchPrefs['minPrice'] and itemPrice != 0:
				print('====================sending notif')
				print("====================auction: "+url)
				print(str(itemPrice+shippingPrice))
				notif.send(url)
			else:
				print('====================outside price')
		except Exception as e:
			print('exception with price analysis: '+str(e))
			pass
		print('testing ====================================')
	def updateQueue(self):
		while not self.ctrlStop:
			tmpfileName = 'data/.'+self.searchPrefs['dataName']
			fileName = 'data/'+self.searchPrefs['dataName']
			found = False
			fileExists = os.path.isfile(fileName)
			if fileExists:
				#copyfile(src, dst)
				copyfile(fileName,tmpfileName)
				with open(tmpfileName,'r') as file:
					reader = csv.DictReader(file)
					with open(fileName,'w') as file:
						fields = ['url','endTime','notif']
						writer = csv.DictWriter(file,fieldnames=fields)
						writer.writeheader()
						for row in reader:
							if ((float(row['endTime']) - time.time())/60) <= 0 and row['notif'] == 'False':
							#lising is ending and has not been processed
								row['notif'] = True
								print(row)
								writer.writerow(row)
								self.analyzeListing(row['url'])
							else:
								writer.writerow(row)
			os.remove(tmpfileName)
			time.sleep(5)