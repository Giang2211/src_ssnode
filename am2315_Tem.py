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
from tentacle_pi.AM2315 import AM2315
from sht1x.Sht1x import Sht1x as SHT1x

dataPin = 16
clkPin = 18
sht1x = SHT1x(dataPin, clkPin, SHT1x.GPIO_BOARD)


nodeID     = "SACSYCHY778483477873YHSH"
node_type  = "7"

DEBUG = True
url_Post = "http://demo.ilyra.vn/api/sensordata"
config_direct = "/home/pi/config/"
DataLog_direct = "/home/pi/log/log.txt"
Data_offline = "/home/pi/log/offline.json"
host_addr = "http://demo.ilyra.vn"
url_regist ="http://demo.ilyra.vn/api/device/register"
url_Config_File = 'http://demo.ilyra.vn/api/device/loadconfig'


def log(message):
    if DEBUG:
	print str(message)
def pushData(type,Message):
    print Message
    headers = {'Authorization': 'aWx5cmE6NzAzZmMxNDUwMDk2MTg1ZDZmYzAwMzQ5YzhlOGQ2ZjU='}
    payload = {
               "name":"SS_DATA",
                "nodeId":nodeID,
                "data":str(type)+":"+str(Message),
                "time":str(datetime.datetime.utcnow().isoformat())
               }

    rsp = requests.post(url_Post, data=payload, headers=headers)
    for i in range (1,10):
    	time.sleep(0.2)
    print (rsp.status_code,rsp.reason)
    #if rsp.status_code == 200 & rsp.reason == 'OK':
	#log("Succes")
      	#return True
    #else:
        #log("False")
	#return False
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


#am = AM2315(0x5c,"/dev/i2c-1")
#temperature, humidity, crc_check = am.sense()
#if humidity >= 100:
#    temperature, humidity, crc_check = am.sense()
#time.sleep(0.5)
temperature = sht1x.read_temperature_C()
humidity = sht1x.read_humidity()
dewPoint = sht1x.calculate_dew_point(temperature, humidity)

pushData(node_type,temperature)
