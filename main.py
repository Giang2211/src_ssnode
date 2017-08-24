# -*- coding: utf-8 -*-
#!/usr/bin/env python
import json
import requests
import os.path
import io
import os
import datetime
import time
import os
import subprocess
from wifi import Cell, Scheme 
from socketIO_client import SocketIO, LoggingNamespace
import logging, threading, functools
from apscheduler.schedulers.background import BackgroundScheduler
import logging
logging.basicConfig()


nodeID = "SACSYCHY778483477873YHSH"
node_type = "1"

imei= 'pncuong'

DEBUG = True

config_direct = "/home/pi/config/"
DataLog_direct = "/home/pi/log/log.txt"
Data_offline = "/home/pi/log/offline.json"
host_addr = "http://demo.ilyra.vn"
url_regist ="http://demo.ilyra.vn/api/device/register"
url_Config_File = 'http://demo.ilyra.vn/api/device/loadconfig'
url_Post = "http://demo.ilyra.vn/api/sensordata"

query = {
    "__sails_io_sdk_version": "0.13.8",
    "__sails_io_sdk_platform": "browser",
    "__sails_io_sdk_language": "javascript"
}
headers = {'Authorization': 'aWx5cmE6NzAzZmMxNDUwMDk2MTg1ZDZmYzAwMzQ5YzhlOGQ2ZjU='}
emit_data = {"url": "/actuator/34/communicate"}

Conf_File = "config.json"
isConnected = False 
Active_Flag = False
regist_flag = False
Pause_Flag  = False
#/* ------ Config ------------------- */
#****Type Node ****
#	1 : Sensor
#	2 : Actuator
#	3 : Feedback
#   1-nhiet do   		: I2C : AM2315
#   2- Do Am    		: I2C : AM2315 
#	3-pH				: Analog : MCP3204 : IN0
#	4-DO				: I2C : id= 100
#	5-EC				: I2C : id=  97
#       6-Level
#
#	7-Light Density
#       8-DS18B20
#	9-WindSpeed
#	10-GPIO
#		GPIO 22 : HIGH | LOW
#		GPIO 23 : HIGH | LOW
#		GPIO 24 : HIGH | LOW
#		GPIO 25 : HIGH | LOW
#		GPIO 26 : HIGH | LOW
#		GPIO 27 : HIGH | LOW
#
#
AM2315_Temp_Flag = False
AM2315_Temp_Clock = 0
AM2315_Hum_Flag = False
AM2315_Hum_Clock = 0
MCP3204_level_Flag = False
MCP3204_level_Clock = 0
MCP3204_Flag = False
MCP3204_Clock = 0
DS18B20_Flag = False
DS18B20_Clock = 0
DO_Flag = False
DO_Clock = 0
EC_Flag = False
EC_Clock = 0
Light_Flag = False
Light_Clock = 0
Wind_Flag = False
Wind_Clock = 0
  
## ------------------------ Function ----------------------------
def on_connect():
    # check exist file
    if check_offlineData_exist():
	resp = upload_offline_log()
	if resp:
	    ## eraselog
	    os.remove(Data_offline)
    
def on_disconnect():
    ## try create new connect
    socketIO = SocketIO('http://demo.ilyra.vn', 1337,params=query)
    socketIO.on('connect', on_connect)
    socketIO.on('disconnect', on_disconnect)
    socketIO.on('reconnect', on_reconnect)
    socketIO.emit("get",emit_data)
    socketIO.on('command', on_aaa_response)
    # Wait for some seconds
def on_reconnect():
    socketIO.emit("get",emit_data)
def log(message):
    if DEBUG:
	print str(message)
def timeout():
    print " -----  Rewaiting --------"
    socketIO.wait(30)
def AM2315_Temp():
    print "-------- AM2315_Temp -----------"
    log(datetime.datetime.now())
    procs = subprocess.Popen('sudo python /home/pi/am2315_Tem.py',shell=True)#,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,)
    #out,stderrs = procs.communicate('through stdin to stdout\n')
    #procs.wait()
    #log(out)    
def AM2315_Hum():
    print "-------- AM2315_Hum -----------"
    log(datetime.datetime.now())
    procs = subprocess.Popen('sudo python /home/pi/am2315_Hum.py',shell=True)#,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,)
    #stdout,stderrs = procs.communicate('through stdin to stdout\n')
    #procs.wait()
    #log(stdout) 
def MCP3204():
    print "-------- PH -----------"
    log(datetime.datetime.now())
    procs = subprocess.Popen('sudo python /home/pi/mcp3204.py',shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,)
    stdout,stderrs = procs.communicate('through stdin to stdout\n')
    procs.wait()
    log(stdout)   
def DO():
    print "-------- DO -----------"
    log(datetime.datetime.now())
    procs = subprocess.Popen('sudo python /home/pi/do.py',shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,)
    stdout,stderrs = procs.communicate('through stdin to stdout\n')
    procs.wait()
    log(stdout)
def EC():
    print "-------- EC -----------"
    log(datetime.datetime.now())
    procs = subprocess.Popen('python /home/pi/ec.py',shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,)
    stdout,stderrs = procs.communicate('through stdin to stdout\n')
    procs.wait()
    log(stdout)
def Level():
    print "-------- Level -----------"
    log(datetime.datetime.now())
    procs = subprocess.Popen('sudo python /home/pi/level.py',shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,)
    stdout,stderrs = procs.communicate('through stdin to stdout\n')
    procs.wait()
    log(stdout)
def DS18B20():
    print "-------- DS18B20 -----------"
    log(datetime.datetime.now())
    procs = subprocess.Popen('sudo python /home/pi/dsb18b20.py',shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,)
    stdout,stderrs = procs.communicate('through stdin to stdout\n')
    procs.wait()
    log(stdout)
def Light_Density():
    print "-------- Light_Density -----------"
    log(datetime.datetime.now())
    procs = subprocess.Popen('sudo python /home/pi/bh1750.py',shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,)
    stdout,stderrs = procs.communicate('through stdin to stdout\n')
    procs.wait()
    log(stdout)
def Wind_Speed():
    print "-------- Wind_Speed -----------"
    #procs = subprocess.Popen('sudo python /home/pi/test/ec.py',shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,)
    #stdout,stderrs = procs.communicate('through stdin to stdout\n')
    #procs.wait()
    #log(stdout)    
def check_config_exist():
    file = config_direct+Conf_File
    if os.path.isfile(file):
        return True
	pass
    else:
        return False
def check_offlineData_exist():
    file = Data_offline
    if os.path.isfile(file):
        return True
	pass
    else:
        return False
def upload_offline_log():
    with io.open(Data_offline) as ourfile:
        dataLoad = json.load(ourfile)
    try:
        resp = requests.post(url_Config_File,data=dataLoad)
        if resp.status_code == 200:
	    return True
	else:
	    return Falses
    except Exception as e:
	raise
	return False
def check_Internet_connect(hostname):
    ret_code = subprocess.call(['ping', '-c', '5', '-W', '3', hostname],stdout=open(os.devnull, 'w'),stderr=open(os.devnull, 'w'))
    for i in range(1,5):
	time.sleep(0.5)
    if ret_code == 0 :
    	return True
    	pass
    else: 
    	return False
def down_Config():
    headers = {'Authorization': 'aWx5cmE6NzAzZmMxNDUwMDk2MTg1ZDZmYzAwMzQ5YzhlOGQ2ZjU='}
    data = {
	'imei': imei
       }
    
    if check_config_exist():
        os.remove(config_direct+Conf_File)
    try:
	resp = requests.post(url_Config_File,data=data,headers=headers)
	#log(resp.json())
	with io.open( config_direct+Conf_File,'w+', encoding='utf8') as ourfile:
	    #json.dump(resp.json(),ourfile)
	    #ourfile.write(str_)
            ourfile.write(unicode(json.dumps(resp.json(), ensure_ascii=False)))
	    ourfile.close()
	    return True
	    pass
    except Exception as e:
	raise
	return False
def read_config_file():
    with io.open( config_direct+ Conf_File) as ourfile:
        dataLoad = json.load(ourfile)
        ourfile.close()
	return dataLoad

def write_offline(a):
    try:
        with open(Data_offline,'w+') as data:
	    data_loaded = json.load(data_file)
    except Exception as e:
	log("Error")
    log = data_loaded[log]
    log =+ str(a)+"|"
    data_loaded[log] = log
    with open(Data_offline,'w') as data:
	data.write(json.dumps(data_loaded))
def check_Wifi_connected():
    wifi = Cell.all('wlan0')[0]
    if wifi.ssid != "":
	return True
    else:
	return False
def config_wifi(ssid,passw):
    try:
        procs = subprocess.Popen('sudo /home/pi/raspi-wifi/config.sh '+ssid+' '+passw,shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,)
	res,errs = procs.communicate('through stdin to stdout\n')
	log(res)
    except Exception as e:
	raise e
    else:
         os.system('sudo reboot')
def controller(*args):
    # check command
    if args[command] == "reconfig":
	resp = down_Config()
	if resp:
	    os.system('sudo reboot')
def regist_device():
    
    data = {
        "imei":imei,
        "type":node_type,
        "port": 6,
	"dataport":"1:4;2:1;3:2;4:5;5:6;6:3"
       }
    #try:
    resp = requests.post(url_regist,data=data,headers=headers)
    for x in xrange(1,5):
	time.sleep(0.3)
        #log("regist fucntion")
    #print(resp.json()["status"])
    return resp.json()["status"]
    #except Exception as e:
    #	return 400
    #	print("error")
def parse_command():
    resp = requests.get("link check command")
    for x in xrange(1,5):
	time.sleep(0.5)
    data = resp.json()
	
def _init_():
    global Active_Flag
    global isConnected
    global regist_flag
    global Pause_Flag 
    global AM2315_Temp_Flag
    global AM2315_Hum_Flag
    global MCP3204_Flag
    global MCP3204_level_Flag
    global DS18B20_Flag
    global DO_Flag
    global EC_Flag
    global Light_Flag
    global Wind_Flag
    global AM2315_Temp_Clock 
    global AM2315_Hum_Clock
    global MCP3204_Clock
    global MCP3204_level_Clock
    global DS18B20_Clock
    global DO_Clock
    global EC_Clock
    global Light_Clock
    global Wind_Clock
    
    log("---- Init () ____")
    log(Active_Flag)
    readed = False
    if check_config_exist():
	log("----- regist_flag == True -----")
        regist_flag = True     

    if regist_flag == False:
	log("----- regist_flag == False -----")
        regist_resp = regist_device()
        print regist_resp
        if regist_resp == 300:
            log("right")
            regist_flag = True    
    if Active_Flag == False and regist_flag == True :
        log("---- state 1 ____")
        if check_config_exist():
	    log(" --- read config ---- ")
	    try:
	        config = read_config_file()
		readed = True
	    except IOError:
	        log(" Read file error")
	else:
            log("down load config")
	    out = down_Config()
	    if out:
	    	log(" success download confg")
	    	config = read_config_file()
		readed = True
	    else:
	    	log("error download")
	if check_Wifi_connected() == False:
            if ('wifi' in config):
		ssid = config["data"]["ssid"]
		passw = config["data"]["password"]
		try:
		    config_wifi(ssid,passw)
		except Exception as e:
		    raise e
	    else:
		log(" Missing Wifi config")
	else:
	    isConnected = True
	    log(" Already connect wlan")
	        # Parse Config Device
        if readed:
	    log("----- readed  -----")
	    if ('1' in config["config"]):
		for key, value in config["config"]["1"].items():
		    if key == "status":
			if value == 1:
	                    AM2315_Temp_Flag = True
                    if key == "interval":
	                AM2315_Temp_Clock = value
	    else:
	        log(" AM2315 Tem not config")
	    if ('2' in config["config"]):
		for key, value in config["config"]["2"].items():
		    if key == "status":
			if value == 1:
	                    AM2315_Hum_Flag = True
                    if key == "interval":
	                AM2315_Hum_Clock = value
	    else:
	        log(" AM2315 Hum not config")
	    if ('3' in config["config"]):
		for key, value in config["config"]["3"].items():
		    if key == "status":
			if value == 1:
	                    MCP3204_Flag = True
                    if key == "interval":
	                MCP3204_Clock = value        
	    else:
	        log(" MCP3204 not config")
	    if ('4' in config["config"]):
		for key, value in config["config"]["4"].items():
		    if key == "status":
			if value == 1:
	                    DO_Flag = True
			    log("----- DO Start  -----")
                    if key == "interval":
	                DO_Clock = value
	    else:
	        log(" DO not config")
	    if ('5' in config["config"]):
		for key, value in config["config"]["5"].items():
		    if key == "status":
			if value == 1:
	                    EC_Flag = True
			    log("----- EC Start  -----")
                    if key == "interval":
	                EC_Clock = value	        
	    else:
	        log(" EC not config")
            if ('6' in config["config"]):
		for key, value in config["config"]["6"].items():
		    if key == "status":
			if value == 1:
	                    MCP3204_level_Flag = True
			    log("----- EC MCP3204_levelStart  -----")
                    if key == "interval":
	                MCP3204_level_Clock = value
	    else:
	        log(" Wind Speed not config")

	    if ('7' in config["config"]):
		for key, value in config["config"]["7"].items():
		    if key == "status":
			if value == 1:
	                    Light_Flag = True
			    log("----- Light Start  -----")
                    if key == "interval":
	                Light_Clock = value
	    else:
	        log(" Light Density not config")
	    if ('8' in config["config"]):
		for key, value in config["config"]["8"].items():
		    if key == "status":
			if value == 1:
	                    DS18B20_Flag = True
                    if key == "interval":
	                DS18B20_Clock = value
	    else:
	        log(" DS18B20 not config")
	    Active_Flag = True
	    log("----- Active_Flag:%s ---" %Active_Flag)

#    else:
#        log(" System Actived")

    
def on_aaa_response(*args):
    print('on_aaa_response', args)
    print datetime.datetime.now()   
def writeLog(Message):
    log_file = open(DataLog_direct,"ab")
    log_file.write(Message+str(datetime.datetime.now())+'\n')
    log_file.close()
def pushData(type,Message):
    headers = {'Authorization': 'aWx5cmE6NzAzZmMxNDUwMDk2MTg1ZDZmYzAwMzQ5YzhlOGQ2ZjU='}
    payload = {
               "name":"SS_DATA",
                "nodeId":nodeID,
                "data":str(type)+":"+str(Message),
                "time":str(datetime.datetime.utcnow().isoformat())
               }
    print json.dumps(payload)
    rsp = requests.post(url_Post, data=payload, headers=headers)
    for i in range (1,10):
    	time.sleep(0.2)
    #if rsp.status_code == 200 & rsp.reason =="OK" :
	#log("Succes")
      	#return True
    #else:
     #   log("False")
	#return False
def main():
    log("----- main ()-----")
    global Active_Flag
    scheduler = BackgroundScheduler()
    try:
        _init_()
    except (RuntimeError, TypeError, NameError):
        log(" Error Init ")
        #_Log_ =" Error _init_() --- "    
        writeLog(_Log_)
    #Active_Flag = False
    log("------------------------")
    log(AM2315_Temp_Flag)
    log(AM2315_Hum_Flag)
    if Active_Flag :
        #socketIO = SocketIO(
    #'http://demo.ilyra.vn', 80,
    #params=query)
        #socketIO.on('connect', on_connect)
	#socketIO.on('disconnect', on_disconnect)
	#socketIO.on('reconnect', on_reconnect)
	#socketIO.emit("get",emit_data)
	#socketIO.on('command', on_aaa_response)
	#socketIO.wait(5)
	#scheduler.add_job(timeout, 'interval', seconds=30)
	log("----- Main Begin -----")
    	if AM2315_Temp_Flag:
	    log("----- AM2315_Temp on -----")
    	    AM2315_Temp_run = scheduler.add_job(AM2315_Temp,'interval',seconds=AM2315_Temp_Clock)
    	if AM2315_Hum_Flag:
	    log("----- AM2315_Hum on -----")
    	    AM2315_Hum_run = scheduler.add_job(AM2315_Hum,'interval',seconds=AM2315_Hum_Clock)
    	
    	if MCP3204_Flag:
	    log("----- MCP3204 on -----")
    	    MCP3204_run = scheduler.add_job(MCP3204,'interval',seconds=MCP3204_Clock)
    	   
    	if DO_Flag:
	    log("----- DO on -----")
    	    do_run = scheduler.add_job(DO,'interval',seconds=DO_Clock)

    	if EC_Flag:
	    log("----- EC on -----")
    	    ec_run = scheduler.add_job(EC,'interval',seconds=EC_Clock)

        if MCP3204_level_Flag:
	    log("----- level on -----")
    	    MCP3204_level_run = scheduler.add_job(Level,'interval',seconds=MCP3204_level_Clock)

    	if Light_Flag:
	    log("----- Light on -----")
    	    Light_run = scheduler.add_job(Light_Density,'interval',seconds=Light_Clock)

        if DS18B20_Flag:
	    log("----- DS18B20 on -----")
    	    DS18B20_run = scheduler.add_job(DS18B20,'interval',seconds=DS18B20_Clock)

    	if Wind_Flag:
	    log("----- Wind on -----")
    	    Wind_run = scheduler.add_job(Wind_Speed,'interval',seconds=Wind_Clock)

        scheduler.start()

    	#while Active_Flag:
    	#    if Pause_Flag:
    	#        try:
        # This is here to simulat()e application activity (which keeps the main thread alive).
        #            while True:
        #                time.sleep(0.1)
        #        except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        #scheduler.shutdown()
        #os.system('sudo reboot')
        try:
        # This is here to simulat()e application activity (which keeps the main thread alive).
            while True:
                time.sleep(0.1)
        except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
            scheduler.shutdown()
            #os.system('sudo reboot')

    	

if __name__ == '__main__':
    #while True:
    main()
    #EC()
    #while True:
        #time.sleep(1)
    #writeLog("haha")
    #check_config_exist()
    #log(check_Internet_connect('demo.ilyra.vn'))
    #config_wifi('Hayabusa','kctestonly')
    #log(read_config_file())
    #down_Config()
    #pushData("1","123")
    #regist_device()    
