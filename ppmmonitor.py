#!/usr/bin/python
# -*- coding: UTF-8 -*-

import serial, time, struct
import datetime
import time
import os
import json
import paho.mqtt.client as mqtt 


from influxdb import InfluxDBClient
DBNAME = 'house'
host ="127.0.0.1"
port="8088"

from datetime import datetime


mqttc = mqtt.Client()
ser = serial.Serial()
ser.port = "/dev/ttyUSB1" # Set this to your serial port
ser.baudrate = 9600

mqttc.username_pw_set("username","password")
mqttc.connect("192.168.0.7", 1883, 60)
mqttc.subscribe("#", 0)
#mqttc.loop_forever()


ser.open()
ser.flushInput()

byte, lastbyte = "\x00", "\x00"
i=0
pmm_10=0
pmm_25=0
while True:
    lastbyte = byte
    byte = ser.read(size=1)
    
    # We got a valid packet header
    if lastbyte == "\xAA" and byte == "\xC0":
	now = datetime.today()
	points = []
        sentence = ser.read(size=8) # Read 8 more bytes
        readings = struct.unpack('<hhxxcc',sentence) # Decode the packet - big endian, 2 shorts for pm2.5 and pm10, 2 reserved bytes, checksum, message tail
        pm_25 = readings[0]/10.0
        pm_10 = readings[1]/10.0
        # ignoring the checksum and message tail
        pmm_25=pmm_25+pm_25
        pmm_10=pmm_10+pm_10
        i=i+1
        if i==60:
            pm2=pmm_25/60
            pm10=pmm_10/60
            #print "PM 2.5:",pm_25,"μg/m^3  PM 10:",pm_10,"μg/m^3"
            i=0
            pmm_10=0
            pmm_25=0
	    mqttc.publish("home/aria/pm2.5",pm_25)
            mqttc.publish("home/aria/pm10",pm_10)


	    try: 
              valore1 = float(pm2)
              valore2 = float(pm10)
              points = [
               {
               		"measurement": "PM",
               		"time": now ,
               		"fields": {
                        	   "PM_2.5": valore1, "PM_10": valore2
               			  }
               }
              ]
            except:
        	print("errore")    
     	    try:
        	client = InfluxDBClient(host='127.0.0.1',port=8086,username='username',password='password')
        	client.switch_database(DBNAME)
        	client.write_points(points)
        	client.close()
        	#print("fatto")
     	    except:
        	print("errore")

