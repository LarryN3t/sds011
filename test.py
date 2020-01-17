#!/usr/bin/python
# -*- coding: UTF-8 -*-

import serial, time, struct

ser = serial.Serial()
ser.port = "/dev/ttyUSB1" # Set this to your serial port
ser.baudrate = 9600

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
            print "PM 2.5:",pm_25,"μg/m^3  PM 10:",pm_10,"μg/m^3"
            i=0
            pmm_10=0
            pmm_25=0
