#!/usr/bin/env python
# -*- coding: utf8 -*-

import math
import RPi.GPIO as GPIO
import MFRC522
import sqlite3
import os
from gps import *
from time import *
import time
import threading
import json
import requests
import sys
import Adafruit_CharLCD as LCD



gpsd = None #seting the global variable
lat=0
long=0
bal=0
balp=0


# Raspberry Pi pin configuration:
lcd_rs        = 27  # Note this might need to be changed to 21 for older revision Pi's.
lcd_en        = 16
lcd_d4        = 26  #PREVIOUS 25
lcd_d5        = 24
lcd_d6        = 23
lcd_d7        = 18
lcd_backlight = 4
lcd_columns = 16
lcd_rows    = 2
lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7,lcd_columns, lcd_rows, lcd_backlight)

# GPS THREAD CLASS
class GpsPoller(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    global gpsd #bring it in scope
    gpsd = gps(mode=WATCH_ENABLE) #starting the stream of info
    self.current_value = None
    self.running = True #setting the thread running to true
 
  def run(self):
    global gpsd
    while gpsp.running:
      gpsd.next() #this will continue to loop and grab EACH set of gpsd info to clear the buffer

# validation for cuid
def validation(cuid):
	conn = sqlite3.connect("mydatabase.db")

	c = conn.cursor();
	c.execute("SELECT id FROM USERS")
	rows=c.fetchall()
	flag=False
	for row in rows:
		s="""%s"""%(row)
		if cuid==s:
			flag=True 
	if flag==True:
		c.execute("SELECT counter FROM USERS WHERE id=?",[cuid])
		counter=c.fetchall()
			
		tu=(counter[0])
		cu=tu[0]
		c.execute("SELECT balance FROM USERS WHERE id=?",[cuid])
		bal_get=c.fetchall()
		bal_t=bal_get[0]
		bal=bal_t[0]
		if cu==0 and bal>10:
			print cu
			cu=cu+1
			print lat
			print long
			c.execute("UPDATE USERS SET lat_start=?,long_start=?,counter=? WHERE id=?",[lat,long,cu,cuid])
			conn.commit()
			lcd.clear()
			lcd.message('Have a nice\n Trip!')
			time.sleep(3)
			return
		elif cu==1:
			print cu
			cu=0
			print lat
			print long
			
			c.execute("UPDATE USERS SET lat_end=?,long_end=?,counter=? WHERE id=?",[lat,long,cu,cuid])
			conn.commit()
			time.sleep(3)
			lcd.clear()
			distance(cuid)
			return
		elif bal<10:
			lcd.clear()
			lcd.message('Not enough\nBalance!')
			time.sleep(3)
			return
	else:
		lcd.clear()
		lcd.message ('Invalid Card!')
		print "invalid card"
		time.sleep(3)
		return
	return		
						
# distance api matrix
def distance(cuid):
	conn = sqlite3.connect("mydatabase.db")

	c = conn.cursor();
	c.execute("SELECT lat_start FROM USERS WHERE id=?",[cuid])
	origin_lat_start=c.fetchall()
	
	c.execute("SELECT long_start FROM USERS WHERE id=?",[cuid])
	origin_long_start=c.fetchall()
	
	c.execute("SELECT lat_end FROM USERS WHERE id=?",[cuid])
	des_lat_end=c.fetchall()
	
	c.execute("SELECT long_end FROM USERS WHERE id=?",[cuid])
	des_long_end=c.fetchall()
	

	origin_t=origin_lat_start[0]
	origin_t1=origin_long_start[0]

	des_t=des_lat_end[0]
	des_t1=des_long_end[0]


	origin_lat=str(origin_t[0])
	origin_long=str(origin_t1[0])
	full_origin=origin_lat+", "+origin_long
	print full_origin
	des_lat=str(des_t[0])
	des_long=str(des_t1[0])
	full_des=des_lat+", "+des_long
	print full_des
# RESETTING LAT AND LONG

	c.execute("UPDATE USERS SET lat_start=?,long_start=?,lat_end=?,long_end=? WHERE id=?",[0,0,0,0,cuid])
	conn.commit()
	c.execute("SELECT balance FROM USERS WHERE id=?",[cuid])
	bal_get=c.fetchall()
	bal_t=bal_get[0]
	balp=bal_t[0]
	
 	
	
	api_key = 'AIzaSyCPboq3AlDsQJlfcOULCUqcNTHQ7bFseyQ'

        
	

	# Google Distance Matrix base URL to which all other parameters are attached
	base_url = 'https://maps.googleapis.com/maps/api/distancematrix/json?'

	# Google Distance Matrix domain-specific terms: origins and destinations
	origins = [full_origin]
	destinations = [full_des]
        

	# Prepare the request details for the assembly into a request URL
	payload = {
		'origins' : '|'.join(origins),
		'destinations' : '|'.join(destinations), 
		'mode' : 'driving',
		'api_key' : api_key
	}

	# Assemble the URL and query the web service
	r = requests.get(base_url, params = payload)


	# Check the HTTP status code returned by the server. Only process the response, 
	# if the status code is 200 (OK in HTTP terms).
	if r.status_code != 200:
		print 'HTTP status code {} received, program terminated.'.format(r.status_code)
                

	else:
		try:
			# Try/catch block should capture the problems when loading JSON data, 
			# such as when JSON is broken. It won't, however, help much if JSON format
			# for this service has changed -- in that case, the dictionaries json.loads() produces
			# may not have some of the fields queried later. In a production system, some sort
			# of verification of JSON file structure is required before processing it. In XML
			# this role is performed by XML Schema.
			x = json.loads(r.text)

			# Now you can do as you please with the data structure stored in x.
			# Here, we print it as a Cartesian product.
			for isrc, src in enumerate(x['origin_addresses']):
				for idst, dst in enumerate(x['destination_addresses']):
					row = x['rows'][isrc]
					cell = row['elements'][idst]
					print cell['status']
					if cell['status'] == 'OK':
						dist=((cell['distance']['value']))
						global money
						dist=float(dist)
						print dist
						money=dist*(0.01) 
						balp=balp-money
						
						lcd.message('Distance: '+ str(dist)+'\nFare: '+ str(money))
						time.sleep(5)
						lcd.clear()
						c.execute("UPDATE USERS SET balance=? WHERE id=?",[balp,cuid])
				                conn.commit()
						print '{} to {}: {}, {}.'.format(src, dst, cell['distance']['text'], cell['duration']['text'])
						return
					else:
						print '{} to {}: status = {}'.format(src, dst, cell['status'])

			# Of course, we could have also saved the results in a file,
			with open('gdmpydemo.json', 'w') as f:
				f.write(r.text)

			# TODO Or in a database,
				

			# Or whatever.
			# ???
			# Profit!

		except ValueError:
			print 'Error while parsing JSON response, program terminated.'

	# Prepare for debugging, but only if interactive. Now you can pprint(x), for example.
	if sys.flags.interactive:
    		from pprint import pprint



# RFID READ
def rfidread():
# Create an object of the class MFRC522
	try:
		MIFAREReader = MFRC522.MFRC522()
	
	# Welcome message
		print "Punch RFID"
		print "Press Ctrl-C to stop."
		lcd.clear()
		lcd.message ('Welcome\nPunch Your Card')
		time.sleep(2)
		
		flag=False
	# This loop keeps checking for chips. If one is near it will get the UID and authenticate
		while flag==False:
			
	    
	    # Scan for cards    
			(status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
	
	    # If a card is found
			if status == MIFAREReader.MI_OK:
	        		print "Card detected"
			
	    
	    # Get the UID of the card
			(status,uid) = MIFAREReader.MFRC522_Anticoll()
			cuid="a"
	
	    # If we have the UID, continue
			if status == MIFAREReader.MI_OK:
				print lat
				cuid=(str(uid[0])+str(uid[1])+str(uid[2])+str(uid[3]))
				print "Card read UID: "+cuid
				if(cuid=="a"):
				   print "card not detected"
				validation(cuid)
				return

			time.sleep(2)			
			
	except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
    		print "\nrfid Thread..."
    		gpsp.running = False
    		t1.join()
    		gpsp.join()
    		
			
if __name__ == '__main__':
	gpsp = GpsPoller() # create the thread
  	gpsp.start()
	try:
		while True:
			lat=(gpsd.fix.latitude)
    			long=(gpsd.fix.longitude)
			flagLat = math.isnan(lat)
			flagLong= math.isnan(long)
			print lat
			if (lat==0 and long==0) or (flagLong and flagLong):
				lcd.message('GPS NOT \n FOUND!')
				time.sleep(3)
				lcd.clear()
			else:
				t1=threading.Thread(target=rfidread)
				time.sleep(3)
				t1.start()
				time.sleep(3)
				t1.join()
    		
	# print
 	# print ' GPS reading'
      	# print '----------------------------------------'
      	 	
      	# print 'longitude   ' , gpsd.fix.longitude
      
      	# print
      	# print 'sats        ' , gpsd.satellites
 		time.sleep(1)
  	except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
    		print "\nKilling Thread..."
    		gpsp.running = False
    		t1.join()
    		gpsp.join() # wait for the thread to finish what it's doing
    		lcd.clear()
    	
	

	

	



