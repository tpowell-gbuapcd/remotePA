#!/usr/bin/env python3

import board
import busio
import time
import numpy as np

import adafruit_tca9548a
import adafruit_mcp9808
import adafruit_bme680
import adafruit_ccs811
import purple_air_diagnostic as pa

#i2c = busio.I2C(board.SCL, board.SDA)
#i2c = board.I2C()
mux, tca = pa.mux_init()
pa.channel_enable(mux, [0,1,2,3,4,5,6,7])

i=1 

while i > 0:
    
    # CCS811 eCO2 (ppm), TVOC (ppm), temp (C)
    
    #ccs811 = adafruit_ccs811.CCS811(tca[1])
    print('CCS811:\neCO2: {:<10.1f} ppm\nTVOC: {:<10.1f} ppm\nTemp: {:<10.2f} C'.format(ccs9811.eco2, ccs811.tvoc, ccs811.temperature))

    # MCP Temperature (C)
    
    mcp = adafruit_mcp9808.MCP9808(tca[6])
    print('MCP9808:\nTemp: {:>14.2f} C'.format(mcp.temperature))
    print()

    # BME680 gas (ohms, which is proportional to VOC content), temp (C), RH (%), pressure (hPa), altitude  (will vary with location, ignore for now
    # gas sensor does not report accurate results due to codebase error. Will need to keep an eye out for updates.
    bme = adafruit_bme680.Adafruit_BME680_I2C(tca[2])
    print('BME688:\nGas: {:>15} ohms\nHumidity: {:>10.2f} %\nPressure: {:>10.2f} hPa\nTemp: {:>14.2f} C'.format(bme.gas, bme.humidity, bme.pressure, bme.temperature))
    print() 
    time.sleep(1)
