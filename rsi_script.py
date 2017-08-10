import urllib2
import urllib
import smtplib
import sched, time
import argparse
import os
import smtplib
from bs4 import BeautifulSoup
gmail_user = ''
gmail_pwd = ''
firstNFlag = False
currCount = 0
sumOfGains = 0
sumOfLosses = 0
avgGain = 0
avgLoss = 0
timePeriod = 1

def send_email(subject, body):
    FROM = gmail_user
    TO = gmail_user
    SUBJECT = subject
    TEXT = body

    # Prepare actual message
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, TO, SUBJECT, TEXT)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(FROM, TO, message)
        server.quit()
        print 'successfully sent the mail'
    except:
        print "failed to send mail"

def checkValueOfCurrency(sc, currency, tick, prevVal): 
	global firstNFlag
	global currCount
	global sumOfLosses
	global sumOfGains
	global avgGain
	global avgLoss

	hdr = {	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
			'User-Agent' : "Magic Browser"}
	req = urllib2.Request('https://tr.investing.com/currencies/' + currency +  '-try', headers=hdr)
	con = urllib2.urlopen(req)
	html = con.read()
	soup = BeautifulSoup(html, 'html.parser')
	currencySpan = soup.find(id="last_last")
	currencyVal = float(currencySpan.string.replace(",", "."))
	print currencyVal
	currGain = 0
	currLoss = 0
	if currCount != 0:
			change = currencyVal - prevVal
			if change <= 0:
				currLoss = abs(change)
				sumOfLosses += currLoss
			else:
				currGain = change
				sumOfGains += currGain

	if not firstNFlag:
		if currCount == timePeriod:
			firstNFlag = True 
			avgGain = sumOfGains / timePeriod
			avgLoss = sumOfLosses / timePeriod
			rs = avgGain / avgLoss
			rsi = 100 if rs == 0 else 100 - (100 / (1 + rs))
			print rsi
			if rsi >= 80:
				send_email("Sell Alert", currency + "/try has an rsi value of " + str(rsi) + " with the current value of " + str(currencyVal))
			elif rsi <= 20:
				send_email("Buy Alert", currency + "/try has an rsi value of " + str(rsi) + " with the current value of " + str(currencyVal))
	else:
		avgGain = (avgGain * (timePeriod - 1) + currGain) / timePeriod
		avgLoss = (avgLoss * (timePeriod - 1) + currLoss) / timePeriod
		rs = avgGain / avgLoss
		rsi = 100 if rs == 0 else 100 - (100 / (1 + rs))
		print rsi
		if rsi >= 80:
			send_email("Sell Alert", currency + "/try has an rsi value of " + str(rsi) + " with the current value of " + str(currencyVal))
		elif rsi <= 20:
			send_email("Buy Alert", currency + "/try has an rsi value of " + str(rsi) + " with the current value of " + str(currencyVal))
	currCount += 1
	sc.enter(tick, 1, checkValueOfCurrency, (sc,currency,tick, currencyVal))

def main(args):
	global timePeriod
	s = sched.scheduler(time.time, time.sleep)
	timePeriod = args.tp
	s.enter(0, 1, checkValueOfCurrency, (s, args.currency, args.tick, 0))
	s.run()

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("--tp", help="the time period for which rsi will be calculated (unit is --tick seconds)", required=True, type=float)
	parser.add_argument("--currency", help="the currency that you want to check the value of", required=True)
	parser.add_argument("--tick", help="the time period between each fetch (seconds)", required=True, type=int)
	args = parser.parse_args()
	main(args)