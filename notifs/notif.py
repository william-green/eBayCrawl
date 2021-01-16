import smtplib

def send(message):
	gmail_user = 'ebay.computer.nerd@gmail.com'
	gmail_password = 'fuckFish42069::)'

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