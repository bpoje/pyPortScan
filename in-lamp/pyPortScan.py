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

#Command line argument parsing
parser = argparse.ArgumentParser()
parser.add_argument("hostFilename", help="File with json of hosts and ports to scan.", type=str)
parser.add_argument("idSet", help="An integer indicating a set.", type=int)
args = parser.parse_args()
idSet = args.idSet

#Load MySQL settings from json file
with open('db.json') as configMySQL_file:
    configMySQL = json.load(configMySQL_file)

#Load hosts and ports to scan from json file
with open(args.hostFilename) as remoteServers_file:
    remoteServers = json.load(remoteServers_file)

# Clear the screen
subprocess.call('clear', shell=True)

try:
	cnx = mysql.connector.connect(**configMySQL)

	cursor = cnx.cursor()

	#add_progInstance = ("INSERT INTO progInstance() VALUES ()")

	# Insert new instance
	#cursor.execute(add_progInstance)
	#progInstance_no = cursor.lastrowid

	#print (progInstance_no)

	#Any previous timestamps in set idSet?
	query_timestamp = ("SELECT id FROM timestamp WHERE idSet = %s ORDER BY atDate DESC LIMIT 1")
	data_timestamp = (idSet,)

	cursor.execute(query_timestamp, data_timestamp)
	row = cursor.fetchone()
	print ("row")
	print (row)

	#If part of existing set, get id of last timestamp from set
	previousTimestamp_no = None
	if (row != None):
		previousTimestamp_no = row[0]
		print ("previous:", previousTimestamp_no)

	add_timestamp = ("INSERT INTO timestamp "
					"(idSet, atDate) "
					"VALUES (%s, %s)")

	#data_timestamp = (progInstance_no, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
	data_timestamp = (idSet, datetime.now().strftime("%Y-%m-%d %H:%M:%S"),)

	# Insert new timestamp
	cursor.execute(add_timestamp, data_timestamp)
	timestamp_no = cursor.lastrowid

	print (timestamp_no)

	#If part of existing set, update previous timestamp
	if (previousTimestamp_no != None):
		#Update previous timestamp
		update_timestamp = ("UPDATE timestamp "
							"SET idNext = %s "
							"WHERE id = %s AND idSet = %s")

		data_timestamp = (timestamp_no, previousTimestamp_no, idSet)

		cursor.execute(update_timestamp, data_timestamp)

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
		ports = remoteServer[2]
		print ports
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
