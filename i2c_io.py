#!/usr/bin/env python3

import board
import busio
import time
import numpy as np

import adafruit_tca9548a
import adafruit_mcp9808
import adafruit_bme680
import purple_air_diagnostic as pa

#i2c = busio.I2C(board.SCL, board.SDA)
#i2c = board.I2C()
mux, tca, i2c = pa.mux_init()
#pa.channel_enable(mux, [0,1,2,3,4,5,6,7])

#device_list = pa.device_list(i2c)
#device_data = pa.make_device_dict(device_list, tca)

#for key, val in device_data.items():
#    print(key, val)

#print(list(device_data.keys()))
#print(objs)

wait_time = 2
n_points = 30

j = 0 
while j == 0:
    pa.channel_enable(mux, [0,1,2,3,4,5,6,7])
    device_list = pa.device_list(i2c)
    device_data = pa.make_device_dict(device_list)
    data_dict = pa.capture_data(device_data, tca, wait_time, n_points)
    avg_dict = pa.get_averages(data_dict)
    pa.print_avg_data(avg_dict)
    pa.csv_write(avg_dict)
