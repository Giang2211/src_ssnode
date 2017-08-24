#!/usr/bin/env python

import io  # used to create file streams
import fcntl  # used to access I2C parameters like addresses
import time  # used for sleep delay and timestamps
import string  # helps parse strings
import json
import datetime
import requests
import logging, threading, functools

nodeID = "SACSYCHY778483477873YHSH"
node_type = "4"



DEBUG = True
url_Post = "http://demo.ilyra.vn/node/sensordata"
config_direct = "/home/pi/config/"
DataLog_direct = "/home/pi/log/log.txt"
Data_offline = "/home/pi/log/offline.json"
host_addr = "http://demo.ilyra.vn"
url_regist ="http://demo.ilyra.vn/api/device/register"
url_Config_File = 'http://demo.ilyra.vn/api/device/loadconfig'


class atlas_i2c:
    long_timeout = 5  # the timeout needed to query readings and calibrations
    short_timeout = 5  # timeout for regular commands
    default_bus = 1  # the default bus for I2C on the newer Raspberry Pis
                     #certain older boards use bus 0
    default_address = 97  # the default address for the EC sensor

    def __init__(self, address=default_address, bus=default_bus):
        # open two file streams, one for reading and one for writing
        # the specific I2C channel is selected with bus
        # it is usually 1, except for older revisions where its 0
        # wb and rb indicate binary read and write
        self.file_read = io.open("/dev/i2c-" + str(bus), "rb", buffering=0)
        self.file_write = io.open("/dev/i2c-" + str(bus), "wb", buffering=0)

        # initializes I2C to either a user specified or default address
        self.set_i2c_address(address)

    def set_i2c_address(self, addr):
        # set the I2C communications to the slave specified by the address
        # The commands for I2C dev using the ioctl functions are specified in
        # the i2c-dev.h file from i2c-tools
        I2C_SLAVE = 0x703
        fcntl.ioctl(self.file_read, I2C_SLAVE, addr)
        fcntl.ioctl(self.file_write, I2C_SLAVE, addr)

    def write(self, string):
        # appends the null character and sends the string over I2C
        string += "\00"
        self.file_write.write(string)

    def read(self, num_of_bytes=31):
        # reads a specified number of bytes from I2C
        #then parses and displays the result
        res = self.file_read.read(num_of_bytes)  # read from the board
        response = filter(lambda x: x != '\x00', res)
        # remove the null characters to get the response
        if(ord(response[0]) == 1):  # if the response isnt an error
            char_list = map(lambda x: chr(ord(x) & ~0x80), list(response[1:]))
            # change MSB to 0 for all received characters except
            #the first and get a list of characters
            # NOTE: having to change the MSB to 0 is a glitch
            #in the raspberry pi, and you shouldn't have to do this!
            return "Command succeeded " + ''.join(char_list)
            # convert the char list to a string and returns it
        else:
            return "Error " + str(ord(response[0]))

    def query(self, string):
        # write a command to the board, wait the correct timeout
        #and read the response
        self.write(string)

        # the read and calibration commands require a longer timeout
        if((string.upper().startswith("R")) or
           (string.upper().startswith("CAL"))):
            time.sleep(self.long_timeout)
        elif((string.upper().startswith("SLEEP"))):
            return "sleep mode"
        else:
            time.sleep(self.short_timeout)

        return self.read()

    def close(self):
        self.file_read.close()
        self.file_write.close()

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



def main():
    device = atlas_i2c()  # creates the I2C port object, specify the address
                       # or bus if necessary
    print ">> Atlas Scientific sample code"
    print ">> Any commands entered are passed to the board via I2C except:"
    print (">> Address,xx changes the I2C address the Raspberry Pi "
    "communicates with.")
    print (">> Poll,xx.x command continuously polls the board every "
    "xx.x seconds")
    print (" where xx.x is longer than the %0.2f second "
    "timeout." % atlas_i2c.long_timeout)
    print " Pressing ctrl-c will stop the polling"

    # main loop
    while True:
        myinput = raw_input("Enter command: ")

        # address command lets you change which address
        # the Raspberry Pi will poll
        if(myinput.upper().startswith("ADDRESS")):
            addr = int(string.split(myinput, ',')[1])
            device.set_i2c_address(addr)
            print ("I2C address set to " + str(addr))

        # contiuous polling command automatically polls the board
        elif(myinput.upper().startswith("POLL")):
            delaytime = float(string.split(myinput, ',')[1])

            # check for polling time being too short,
            # change it to the minimum timeout if too short
            if(delaytime < atlas_i2c.long_timeout):
                print ("Polling time is shorter than timeout, setting "
                "polling time to %0.2f" % atlas_i2c.long_timeout)
                delaytime = atlas_i2c.long_timeout

            # get the information of the board you're polling
            info = string.split(device.query("I"), ",")[1]
            print ("Polling %s sensor every %0.2f seconds, press ctrl-c "
            "to stop polling" % (info, delaytime))

            try:
                while True:
                    print device.query("R")
                    time.sleep(delaytime - atlas_i2c.long_timeout)
            except KeyboardInterrupt:  # catches the ctrl-c command,
                                       # which breaks the loop above
                print "Continuous polling stopped"

        # if not a special keyword, pass commands straight to board
        else:
            try:
                print device.query(myinput)
            except IOError:
                print "Query failed"


if __name__ == '__main__':
    #main()
    device = atlas_i2c()
    device.query("R")
    time.sleep(0.5)
    data = device.query("R")
    data=data.split("Command succeeded ")[1]
    pushData(node_type,data)

    
