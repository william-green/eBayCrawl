import smtplib
from datetime import datetime
import json

def send(message, log=False):
	with open("../credentials.txt",'r') as credFile:
		credStr = '{'+credFile.read()+'}'
		creds = json.loads(credStr)
		print(creds)
	
	gmail_user = creds['email']
	gmail_password = creds['password']
	sent_from = "eBay Crawler"
	to = creds['recipients']
	subject = ''
	body = str(message)
	email_text = """\
	From: %s
	To: %s
	Subject: %s

	%s
	""" % (sent_from, ", ".join(to), subject, body)

	#try:
	server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
	server.ehlo()
	server.login(gmail_user, gmail_password)
	server.sendmail(sent_from, to, email_text)
	server.close()
	print('Notification sent')
	#except:
	#print('Problem sending notification')

	if log:
		with open("logs/log.txt","a") as logFile:
			logFile.write(datetime.now() + ' : ' + message)

	#gmail_user = 'ebay.computer.nerd@gmail.com'
	#gmail_password = 'fuckFish42069::)'

	'''
	sent_from = 'test'
	to = ['7078902047@vtext.com','7075135679@vtext.com']#'7075135679@vtext.com' 7078902047@vzwpix.com
	subject = ''
	body = str(message)

	email_text = """\
	From: %s
	To: %s
	Subject: %s

	%s
	""" % (sent_from, ", ".join(to), subject, body)

	#try:
	server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
	server.ehlo()
	server.login(gmail_user, gmail_password)
	server.sendmail(sent_from, to, email_text)
	server.close()
	print('Email sent!')
	#except:
	#    print('Something went wrong...')
	'''