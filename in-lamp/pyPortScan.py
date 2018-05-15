#!/usr/bin/env python

# https://dev.mysql.com/doc/connector-python/en/connector-python-example-connecting.html

import socket
import subprocess
import sys
from datetime import datetime
import sqlite3
import mysql.connector
import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument("idSet", help="An integer indicating a set.", type=int)
args = parser.parse_args()
idSet = args.idSet

#configMySQL = {
#	'user' : 'scan',
#	'password' : '-Pass12345',
#	'host' : '127.0.0.1',
#	'database' : 'portScan',
#}

#Load MySQL settings from db.json file
with open('db.json') as configMySQL_file:
    configMySQL = json.load(configMySQL_file)
print(configMySQL)
#print(configMySQL['user'])




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
	cnx = mysql.connector.connect(**configMySQL)

	cursor = cnx.cursor()

	#add_progInstance = ("INSERT INTO progInstance() VALUES ()")

	# Insert new instance
	#cursor.execute(add_progInstance)
	#progInstance_no = cursor.lastrowid

	#print (progInstance_no)

	add_timestamp = ("INSERT INTO timestamp "
					"(idSet, atDate) "
					"VALUES (%s, %s)")

	#data_timestamp = (progInstance_no, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
	data_timestamp = (idSet, datetime.now().strftime("%Y-%m-%d %H:%M:%S"),)

	# Insert new timestamp
	cursor.execute(add_timestamp, data_timestamp)
	timestamp_no = cursor.lastrowid

	print (timestamp_no)

	add_node = ("INSERT INTO node "
				"(ip4, label) "
				"VALUES (%s,%s)")

	for remoteServer in remoteServers:
		#SELECT EXISTS(SELECT * FROM table1 WHERE ...)
		#query_node = ("SELECT EXISTS(SELECT ip4 FROM node WHERE ip4 = %s)")
		query_node = ("SELECT idNode, ip4 FROM node WHERE ip4 = %s LIMIT 1")
		data_node = (remoteServer[0],)

		cursor.execute(query_node, data_node)

		row = cursor.fetchone()
		node_no = cursor.lastrowid

		if (row == None):
			print "New node"
			data_node = (remoteServer[0], remoteServer[1])

			#Insert new node
			cursor.execute(add_node, data_node)
			node_no = cursor.lastrowid
			print (node_no)
		else:
			print "Node exists"
			#Get existing node id
			node_no = row[0]
			print (node_no)

		remoteServerIP  = socket.gethostbyname(remoteServer[0])

		# Print a nice banner with information on which host we are about to scan
		print "-" * 60
		print "Please wait, scanning remote host", remoteServerIP, remoteServer[1]
		print "-" * 60

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

			add_log = ("INSERT INTO log "
						"(idNode, idTimestamp, port, isOpen) "
						"VALUES (%s, %s, %s, %s)")

			data_log = (node_no, timestamp_no, str(port), open)

			# Insert data into table log
			cursor.execute(add_log, data_log)


	# Make sure data is committed to the database
	cnx.commit()

	cursor.close()
	cnx.close()

except KeyboardInterrupt:
	print "You pressed Ctrl+C"

	#Commit data on CTRL+C
	cnx.commit()

	print "Data commited"

	cnx.close()
	sys.exit()

except socket.gaierror:
	print 'Hostname could not be resolved. Exiting'
	cnx.rollback()
	cnx.close()
	sys.exit()

except socket.error:
	print "Couldn't connect to server"
	cnx.rollback()
	cnx.close()
	sys.exit()

except Exception as e:
	cnx.rollback()
	cnx.close()
	raise e
