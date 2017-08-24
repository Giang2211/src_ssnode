#!/usr/bin/env python
from w1thermsensor import W1ThermSensor
import io  # used to create file streams
import fcntl  # used to access I2C parameters like addresses
import time  # used for sleep delay and timestamps
import string  # helps parse strings
import json
import datetime
import requests
import logging, threading, functools
import os
import glob
import subprocess
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

# Define some constants from the datasheet
nodeID     = "SACSYCHY778483477873YHSH"
node_type  = "8"

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28-0416012529ff')[0]
device_file = device_folder + '/w1_slave'


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
def read_temp_raw():
    catdata = subprocess.Popen(['cat',device_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out,err = catdata.communicate()
    out_decode = out.decode('utf-8')
    lines = out_decode.split('\n')
    return lines
 
def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c

data=read_temp()
#sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, "00000588806a")
#tempe = sensor.get_temperature()
pushData(node_type,data)

