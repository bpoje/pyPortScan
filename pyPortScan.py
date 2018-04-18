#!/usr/bin/env python
import socket
import subprocess
import sys
from datetime import datetime
import sqlite3

# Clear the screen
subprocess.call('clear', shell=True)

# Ask for input
#remoteServer    = raw_input("Enter a remote host to scan: ")
#remoteServer	= "192.168.254.2"

remoteServers = (
	("192.168.254.2",  "ZSSS1b"),
	("192.168.254.3",  "ZSSSme"),
	("192.168.254.4",  "ZSSS3c"),
	("192.168.254.5",  "ZSSS2a"),
	("192.168.254.7",  "ZSSS3a"),
	("192.168.254.8",  "ZSSS3b"),
	("192.168.254.9",  "ZSSS4a"),
	("192.168.254.10", "ZSSS4b"),
	("192.168.254.11", "ZSSS5a"),
	("192.168.254.12", "ZSSS5b"),
	("192.168.254.13", "ZSSS6a"),
	("192.168.254.14", "ZSSS3d"),
	("192.168.254.21", "ZSSS1d"),
)

ports = (
	# (80,)
	(80,443)
)

try:
	# Creates or opens a file called sqlitedb.db with a SQLite3 DB
	db = sqlite3.connect('sqlitedb.db')
	# Get a cursor object
	cursor = db.cursor()
	# Check if table log does not exist and create it
	cursor.execute('''CREATE TABLE IF NOT EXISTS
		log(
		id INTEGER PRIMARY KEY,
		remoteServerIP TEXT NOT NULL,
		remoteServerLabel TEXT,
		remoteServerPort INTEGER NOT NULL,
		isOpen BOOLEAN NOT NULL CHECK (isOpen IN (0,1)),
		atDate DATETIME NOT NULL)''')
	# Commit the change
	db.commit()
	
# Catch the exception
except Exception as e:
	# Roll back any change if something goes wrong
	db.rollback()
	raise e

#atDate = datetime.now().strftime("%B %d, %Y %I:%M%p")
atDate = datetime.now().strftime("%Y.%m.%d %H:%M:%S")

for remoteServer in remoteServers:
	remoteServerIP  = socket.gethostbyname(remoteServer[0])

	# Print a nice banner with information on which host we are about to scan
	print "-" * 60
	print "Please wait, scanning remote host", remoteServerIP, remoteServer[1]
	print "-" * 60

	# Check what time the scan started
	t1 = datetime.now()
	
	try:
		# Using the range function to specify ports (here it will scans all ports between 1 and 1024)
		#for port in range(1,1025):
		#for port in (80,443,8080):
		for port in ports:
			open = False
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.settimeout(10)
			result = sock.connect_ex((remoteServerIP, port))
			#You just need to use the socket settimeout() method before attempting the connect(), please note that after connecting you must settimeout(None) to set the socket into blocking mode, such is required for the makefile . 
			sock.settimeout(None)
			if result == 0:
				print "Port {}:			Open".format(port)
				open = True
			else:
				print "Port {}:			Closed".format(port)
			sock.close()
			
			# Insert data into table log
			cursor.execute('''INSERT INTO log (remoteServerIP, remoteServerLabel, remoteServerPort, isOpen, atDate)
			VALUES (?,?,?,?,?)''', (remoteServer[0], remoteServer[1], port, open, atDate))
			# Commit the change
			db.commit()

	except KeyboardInterrupt:
		print "You pressed Ctrl+C"
		db.close()
		sys.exit()

	except socket.gaierror:
		print 'Hostname could not be resolved. Exiting'
		db.close()
		sys.exit()

	except socket.error:
		print "Couldn't connect to server"
		db.close()
		sys.exit()
	
	# Catch the exception
	except Exception as e:
		# Roll back any change if something goes wrong
		db.rollback()
		raise e

	# Checking the time again
	t2 = datetime.now()

	# Calculates the difference of time, to see how long it took to run the script
	total =  t2 - t1

	# Printing the information to screen
	print 'Scanning Completed in: ', total

# Close the db connection
db.close()