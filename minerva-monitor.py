# coding:UTF-8
import re, time, sys, threading
import urllib
from datetime import datetime
import time
from bs4 import BeautifulSoup
import mechanize
import os

###################################################
### Settings

username = "youremail@mail.mcgill.ca"		#McGill Username
password = ""	#Password
term = "201809"	#term (201801 for Winter 2018, 201909 for Fall 2018)
sel_subj = "MATH"	#Course Prefix
sel_crse = "263"	#Course Number
sel_crn = "3362"	#Course CRN
wait_time = "300"		#Time interval to check the seat availability (in seconds)

###################################################
###################################################

br = mechanize.Browser()
br.set_handle_equiv(True)
br.set_handle_redirect(True)
br.set_handle_referer(True)
br.set_handle_robots(False)
br.addheaders = [('User-agent', 'Mozila/5.0(X11; U; Linux i686; en-us; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

def notify(title, subtitle, message):
    t = '-title {!r}'.format(title)
    s = '-subtitle {!r}'.format(subtitle)
    m = '-message {!r}'.format(message)
    os.system('terminal-notifier {}'.format(' '.join([m, t, s,'-sound default'])))

def countdown(t):
    while t > 0:
        sys.stdout.write('\rDuration : {}s'.format(t))
        t -= 1
        sys.stdout.flush()
        time.sleep(1)

def check_vacancy():
	# Access the login page, input the credentials and login. 
	br.open("https://horizon.mcgill.ca/pban1/twbkwbis.P_WWWLogin")
	br.select_form(name="loginform1")
	br['sid'] = username
	br['PIN'] = password
	br.submit()
	print('\nChecking the availability for'+sel_subj+sel_crse)
	print('Logged in to Minerva.')
	
	# Access "Search Class Schedule and Add Course Sections" and choose term.  
	br.open("https://horizon.mcgill.ca/pban1/bwskfcls.p_sel_crse_search")
	br.select_form(nr = 1)
	br['p_term'] = [term]
	br.submit()
	print("Choosing the term " + term)
	
	# Submit the course subject
	br.select_form(nr = 1)
	subject_list = br.find_control(name="sel_subj", nr=1)
	subject_list.value = [sel_subj]
	res = br.submit()
	print ("Course subject selected. ")
	
	# If the course number exists, move on to the section list. 
	html = br.response().read()
	bs = BeautifulSoup(html, 'lxml')
	i = 2;
	for t in bs.findAll('td', {'class':'dddefault'}):
	    if t.text.strip() == sel_crse: 
	    	print ("found the course number")
	    	br.select_form(nr = i)
	    	res = br.submit()
	    	break
	    i+=0.5
	else:
	    print("course number not found, exit. ")
	    sys.exit()
	
	#
	# Put the list of sections into list
	#
	html = br.response().read()
	bs = BeautifulSoup(html, 'lxml')
	table = bs.findAll("table",{"class":"datadisplaytable"})[0]
	rows = table.findAll("tr")
	
	i = -1
	arr = []
	for row in rows:
		for cell in row.findAll(['td', 'th']):
			if i > 18: 
				break;
			temp = cell.get_text()
			if temp == sel_crn: 
				i = 0
			if i != -1: 
				arr.append(temp)
				i += 1;
		if i > 18: 
			break;
	print ("-"*20)
	print ("Course: " + str(arr[1]) + str(arr[2]) + ", Section " + str(arr[3]) + ", CRN: " + str(arr[0]) )
	print ("Seat available: " + str(arr[11]))
	print ("Waitlist available:" + str(arr[14]))
	print ("-"*20)
	
	if str(arr[11]) == "0" and str(arr[14]) == "0":
		print ("Unavailable - program is going to attempt again in " + wait_time + "seconds. ")
	elif str(arr[11]) == "0" and str(arr[14]) != "0":
		print ("Waitlist is available!\n")
		notify(title    = 'minerva', subtitle = 'minerva_monitor', message  = "Waitlist is available for " + sel_subj+sel_crse+"!!!")
		sys.exit()
	else: 
		print ("Seats available!\n")
		notify(title    = 'minerva', subtitle = 'minerva_monitor', message  = "Seats are available for " + sel_subj+sel_crse+"!!!")
		sys.exit()
	
###############

while True:
	check_vacancy()
	countdown(float(wait_time))