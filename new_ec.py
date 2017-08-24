#!/usr/bin/env python
import os
import glob
import subprocess
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
import RPi.GPIO as GPIO

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
GPIO.setmode(GPIO.BCM)
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28-0416012529ff')[0]
device_file = device_folder + '/w1_slave'

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
def resistor():
    spi = MCP3204(0)
    return spi.read(0)
def temperature():
    data=read_temp()
    return data
def calib_K():
    CalibrationEC=1.6857 #EC value of Calibration solution is s/cm
    R1= 1200
    Ra=55 #//Resistance of powering Pins
    Rd=100000 #// Bottom half of adc oltage divider
    ECPower = 25 # gpio control power for EC sensor
    GPIO.setup(ECPower, GPIO.OUT)
    TemperatureCoef = 0.019
    TemperatureFinish=0
    TemperatureStart=0
    EC=0
    ppm =0
    raw= 0
    Vin= 3.3
    Vout = 0
    Vdrop= 0
    Rc= 0
    K=0
    buffe=0
    TemperatureStart = temperature()
    for x in xrange(1,10):
        GPIO.output(ECPower,GPIO.HIGH)
        raw = resistor()
        time.sleep(0.1)
        raw = resistor()
        GPIO.output(ECPower,GPIO.LOW)
        buffe=buffe+raw
        time.sleep(0.5)
        pass
    raw = raw/10
    print "-----------"
    print raw
    TemperatureFinish = temperature()
    EC =CalibrationEC/(1+(TemperatureCoef*(TemperatureFinish-25.0))) 
    Vout= raw/4095.0
    Rc=(((3.2*Vout)/(((Vin-(3.2*Vout))/(R1+Ra))-(Vout/Rd)))-Ra)
    K = (Rc*EC)/1000.0
    print("TemperatureFinish: ")
    print(TemperatureFinish)
    print("Calibration Fluid EC: ")
    print(CalibrationEC)
    print(" S  ")# //add units here
    print("Cell Constant K")
    print(K);
    if TemperatureStart==TemperatureFinish :
        print("  Results are Trustworthy")
        print("  Safe To Use Above Cell Constant in Main EC code")
        pass
    else:
        print("  Error -Wait For Temperature To settle")
def EC():
    #//*********** Converting to ppm [Learn to use EC it is much better**************//
    #// Hana      [USA]        PPMconverion:  0.5
    #// Eutech    [EU]          PPMconversion:  0.64
    #//Tranchen  [Australia]  PPMconversion:  0.7
    #// Why didnt anyone standardise this?
    PPMconversion=0.7
    R1= 1200
    Ra=55 #//Resistance of powering Pins
    Rd=100000 #// Bottom half of adc oltage divider
    ECPower = 25 # gpio control power for EC sensor
    GPIO.setup(ECPower, GPIO.OUT)
    TemperatureCoef = 0.019
    Temperature=0
    EC=0
    ppm =0
    ppm_EC = 0
    raw= 0
    Vin= 3.
    Vout = 0
    Vdrop= 0
    Rc= 0
    K=0
    buffe=0
    
 
    TemperatureStart = temperature()
    GPIO.output(ECPower,HIGH)
    raw = resistor()
    time.sleep(0.1)
    raw = resistor()
    GPIO.output(ECPower,LOW)
    time.sleep(0.5)
    Temperature=sensors.temperature()
    Vout= raw/4095.0
    Rc=(((3.2*Vout)/(((Vin-(3.2*Vout))/(R1+Ra))-(Vout/Rd)))-Ra)

    EC = (1000.0*K)/Rc

    #//*************Compensating For Temperaure********************//
    EC25  =  EC/ (1+ TemperatureCoef*(Temperature-25.0))
    ppm=(EC25)*(PPMconversion*1000)
 

    print("Rc: ")
    print(Rc)
    print(" EC: ")
    print(EC25)
    print(" Simens  ")
    print(ppm)
    print(" ppm  ")
    print(Temperature)
    print(" *C ")
if __name__ == '__main__':
    calib_K()
	
	

