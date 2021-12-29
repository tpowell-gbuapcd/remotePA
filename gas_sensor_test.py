#!/usr/bin/env python3

import board
import busio
import time
import numpy as np

import adafruit_tca9548a
import adafruit_mcp9808
import adafruit_bme680
#import adafruit_ccs811
import adafruit_scd30
import purple_air_diagnostic as pa

from adafruit_pm25.i2c import PM25_I2C
from datetime import datetime
#i2c = busio.I2C(board.SCL, board.SDA)
#i2c = board.I2C()
mux, tca = pa.mux_init()
pa.channel_enable(mux, [0,1,2,3,4,5,6,7])
print()

i=1 

while i > 0:
    
    # CCS811 eCO2 (ppm), TVOC (ppm), temp (C)
    
    #ccs811 = adafruit_ccs811.CCS811(tca[1])
    #print('CCS811:\neCO2: {:<10.1f} ppm\nTVOC: {:<10.1f} ppm\nTemp: {:<10.2f} C'.format(ccs9811.eco2, ccs811.tvoc, ccs811.temperature))

    # MCP Temperature (C)

    start_time = datetime.now().strftime("%m/%d/%Y %H:%M:%S")

    print('Start Time: {}'.format(start_time))    
    print()

    mcp = adafruit_mcp9808.MCP9808(tca[6])
    print('MCP9808\nTemp: {:>26.2f} C'.format(mcp.temperature))
    print()

    # BME680 gas (ohms, which is proportional to VOC content), temp (C), RH (%), pressure (hPa), altitude  (will vary with location, ignore for now
    # gas sensor does not report accurate results due to codebase error. Will need to keep an eye out for updates.
    bme = adafruit_bme680.Adafruit_BME680_I2C(tca[5])
    print('BME688\nGas: {:>25} ohms\nHumidity: {:>22.2f} %\nPressure: {:>23.2f} hPa\nTemp: {:>26.2f} C'.format(bme.gas, bme.humidity, bme.pressure, bme.temperature))
    print()
    
    scd = adafruit_scd30.SCD30(tca[5])

    try:
        if scd.data_available == 1:
            print('SCD CO2 Sensor\nCO2: {:>29.2f} PPM\nHumidity: {:>22.2f} %\nTemp: {:>26.2f} C'.format(scd.CO2, scd.relative_humidity, scd.temperature))
    except:
        print("Data Available = ", scd.data_available, " 0 = No Data Available, 1 = Data Available")
    print()
            

    pm25 = PM25_I2C(tca[5])
    try:
        pmdata = pm25.read()
        print('PM SENSOR\nPM1.0 [STANDARD]: {:>10} ug/m3\nPM2.5 [STANDARD]: {:>10} ug/m3\nPM10  [STANDARD]: {:>10} ug/m3'.format(pmdata["pm10 standard"], pmdata["pm25 standard"], pmdata["pm100 standard"]))
        print()
        print('PM1.0 [ENVIRONMENTAL]: {:>5} ug/m3\nPM2.5 [ENVIRONMENTAL]: {:>5} ug/m3\nPM10  [ENVIRONMENTAL]: {:>5} ug/m3'.format(pmdata["pm10 env"], pmdata["pm25 env"], pmdata["pm100 env"]))    
        print()

    except RuntimeError:
        print('UNABLE TO READ PM2.5 SENSOR, RETRYING')
        continue

    #print('PM SENSOR\nPM1.0 [STANDARD]: {:>10} ug/m3\nPM2.5 [STANDARD]: {:>10} ug/m3\nPM10  [STANDARD]: {:>10} ug/m3'.format(pmdata["pm10 standard"], pmdata["pm25 standard"], pmdata["pm100 standard"]))
    #print()

    #print('PM1.0 [ENVIRONMENTAL]: {:>5} ug/m3\nPM2.5 [ENVIRONMENTAL]: {:>5} ug/m3\nPM10  [ENVIRONMENTAL]: {:>5} ug/m3'.format(pmdata["pm10 env"], pmdata["pm25 env"], pmdata["pm100 env"]))    
        
    print()
    time.sleep(10)
