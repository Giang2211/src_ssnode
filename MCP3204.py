#!/usr/bin/python
#
#       MCP3204/MCP3208 sample program for Raspberry Pi
#
#       how to setup /dev/spidev?.?
#               $ suod modprobe spi_bcm2708
#
#       how to setup spidev
#               $ sudo apt-get install python-dev python-pip
#               $ sudo pip install spidev
#
import spidev
import sys
import smbus
import io  # used to create file streams
import fcntl  # used to access I2C parameters like addresses
import subprocess
import time  # used for sleep delay and timestamps
import string  # helps parse strings
import json
import datetime
import requests
import logging, threading, functools

# Define some constants from the datasheet
nodeID     = "SACSYCHY778483477873YHSH"
node_type  = "3"

DEBUG = True
url_Post = "http://demo.ilyra.vn/node/sensordata"
config_direct = "/home/pi/config/"
DataLog_direct = "/home/pi/log/log.txt"
Data_offline = "/home/pi/log/offline.json"
host_addr = "http://demo.ilyra.vn"
url_regist ="http://demo.ilyra.vn/api/device/register"
url_Config_File = 'http://demo.ilyra.vn/api/device/loadconfig'
up_threshold = 3000

class MCP3204:
        def __init__(self, spi_channel=0):
                self.spi_channel = spi_channel
                self.conn = spidev.SpiDev(0, spi_channel)
                self.conn.max_speed_hz = 1000000 # 1MHz

        def __del__( self ):
                self.close

        def close(self):
                if self.conn != None:
                        self.conn.close
                        self.conn = None

        def bitstring(self, n):
                s = bin(n)[2:]
                return '0'*(8-len(s)) + s

        def read(self, adc_channel=0):
                # build command
                cmd  = 128 # start bit
                cmd +=  64 # single end / diff
                if adc_channel % 2 == 1:
                        cmd += 8
                if (adc_channel/2) % 2 == 1:
                        cmd += 16
                if (adc_channel/4) % 2 == 1:
                        cmd += 32

                # send & receive data
                reply_bytes = self.conn.xfer2([cmd, 0, 0, 0])

                #
                reply_bitstring = ''.join(self.bitstring(n) for n in reply_bytes)
                # print reply_bitstring

                # see also... http://akizukidenshi.com/download/MCP3204.pdf (page.20)
                reply = reply_bitstring[5:19]
                return int(reply, 2)
def ph():
        spi = MCP3204(0)
	data =[]
	for i in range (0,10):
            data.append(spi.read(0))
	    time.sleep(0.2)
	data = sorted(data)
	a=0
	for i in range (2,9):
	    a=a+data[i]
	a=a/7
	print a
        return str(a)    
def log(message):
    if DEBUG:
	print str(message)
def pushData(type,Message):
    print Message
    headers = {'Content-type': 'application/json'}
    payload = {
               "name":"SS_DATA",
                "nodeId":nodeID,
                "data":str(type)+":"+str(Message),
                "time":str(datetime.datetime.utcnow().isoformat())
               }

    rsp = requests.post(url_Post, json=payload, headers=headers)
    for i in range (1,10):
    	time.sleep(0.2)
    if rsp.status_code == 200:
	log("Succes")
      	return True
    else:
        log("False")
	return False
def writeLog(Message):
    log_file = open(DataLog_direct,"ab")
    log_file.write(Message+str(datetime.datetime.now())+'\n')
    log_file.close()
def check_Internet_connect(hostname):
    ret_code = subprocess.call(['ping', '-c', '5', '-W', '3', hostname],stdout=open(os.devnull, 'w'),stderr=open(os.devnull, 'w'))
    for i in range(1,5):
	time.sleep(0.5)
    if ret_code == 0 :
    	return True
    	pass
    else: 
    	return False

if __name__ == '__main__':
	resp = ph()
	print resp
        #pushData(node_type,resp)
