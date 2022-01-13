#!/usr/bin/env python3

import argparse
import purple_air_diagnostic as pa
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument('-w', '--wait_time', type=int, help='The amount of seconds to wait between reads. Must be at least 2 seconds long. Default is 2 seconds. ex.) 2', default=2)
parser.add_argument('-n', '--n_points', type=int, help='The number of points to average over. Total time span between writes to csv is n_points*wait_time. Default is 300 ex.) 300 (300*2 = 10 minute averaging)', default=300)
args = parser.parse_args()

mux, tca, i2c = pa.mux_init()

wait_time = args.wait_time
n_points = args.n_points

j = 0 
while j == 0:
    #print("Enabling channels: ", datetime.now())
    pa.channel_enable(mux, [0,1,2,3,4,5,6,7])
    #print("Channels Enabled: ", datetime.now())
    device_list = pa.device_list(i2c)
    #print("Device list made: ", datetime.now())
    device_data = pa.make_device_dict(device_list)
    #print("Dictionary Initialized: ", datetime.now())
    data_dict = pa.capture_data(device_data, tca, wait_time, n_points)
    #print("Dictionary Filled: ", datetime.now())
    avg_dict = pa.get_averages(data_dict)
    print("Dictionary Averagad: ", datetime.now())
    #pa.print_avg_data(avg_dict)
    #print("Averaged Data Printed: ", datetime.now())
    pa.csv_write(avg_dict)
    #print("CSV Written: ", datetime.now())
