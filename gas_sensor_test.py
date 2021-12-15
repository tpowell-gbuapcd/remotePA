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
#i2c = busio.I2C(board.SCL, board.SDA)
#i2c = board.I2C()
mux, tca = pa.mux_init()
pa.channel_enable(mux, [0,1,2,3,4,5,6,7])

i=1 

while i > 0:
    
    # CCS811 eCO2 (ppm), TVOC (ppm), temp (C)
    
    #ccs811 = adafruit_ccs811.CCS811(tca[1])
    #print('CCS811:\neCO2: {:<10.1f} ppm\nTVOC: {:<10.1f} ppm\nTemp: {:<10.2f} C'.format(ccs9811.eco2, ccs811.tvoc, ccs811.temperature))

    # MCP Temperature (C)
    
    mcp = adafruit_mcp9808.MCP9808(tca[6])
    print('MCP9808\nTemp: {:>14.2f} C'.format(mcp.temperature))
    print()

    # BME680 gas (ohms, which is proportional to VOC content), temp (C), RH (%), pressure (hPa), altitude  (will vary with location, ignore for now
    # gas sensor does not report accurate results due to codebase error. Will need to keep an eye out for updates.
    bme = adafruit_bme680.Adafruit_BME680_I2C(tca[5])
    print('BME688\nGas: {:>15} ohms\nHumidity: {:>10.2f} %\nPressure: {:>10.2f} hPa\nTemp: {:>14.2f} C'.format(bme.gas, bme.humidity, bme.pressure, bme.temperature))
    print()
    
    scd = adafruit_scd30.SCD30(tca[5])

    print('SCD CO2 Sensor\nCO2: {:>15} PPM\nHumidity: {:>10.2f} %\nTemp: {:>14.2f} C'.format(scd.CO2, scd.relative_humidity, scd.temperature))
    print()

    pm25 = PM25_I2C(tca[5])
    try:
        pmdata = pm25.read()
    except RuntimeError:
        print('UNABLE TO READ PM2.5 SENSOR, RETRYING')
        continue

    print('PM SENSOR\nPM1.0 [STANDARD]: {:>20}\nPM2.5 [STANDARD] {:>20}\nPM10 [STANDARD] {:>20}'.format(pmdata["PM10 standard"], pmdata["PM25 standard"], pmdata["PM100 standard"]))
    print()

    print('PM1.0 [ENVIRONMENTAL]: {:>20}\nPM2.5 [ENVIRONMENTAL] {:>20}\nPM10 [ENVIRONMENTAL] {:>20}'.format(pmdata["PM10 env"], pmdata["PM25 env"], pmdata["PM100 env"]))    


        
    print('')
    time.sleep(1)
