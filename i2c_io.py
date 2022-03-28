#!/usr/bin/env python3

import argparse, sys, os
import purple_air_diagnostic as pa
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument('-w', '--wait_time', type=int, help='The amount of seconds to wait between reads. Must be at least 2 seconds long. Default is 2 seconds. ex.) 2', default=2)
parser.add_argument('-n', '--n_points', type=int, help='The number of points to average over. Total time span between writes to csv is n_points*wait_time. Default is 300 ex.) 300 (300*2 = 10 minute averaging)', default=300)
parser.add_argument('-l', '--log', type=str, help='Would you like to print the output to screen? YES or NO. Otherwise direct output to .txt file in log directory. Default is NO.', default='NO')
args = parser.parse_args()

if args.log == 'NO':
    sys.stdout = open(os.getcwd() + '/data/' + 'file.txt', 'w')

try:
    print('Initializing I2C devices: {}'.format(datetime.now()))
    mux, tca, i2c = pa.mux_init()
except Exception as e:
    print('ERROR INITIALIZING I2C DEVICES')
    print('ERROR: {}'.format(e))

wait_time = args.wait_time
n_points = args.n_points

j = 0 
while j == 0:

    try:
        print('Enabling channels: {}'.format(datetime.now()))
        pa.channel_enable(mux, [0,1,2,3,4,5,6,7])
        print('Channels Enabled: {}'.format(datetime.now()))
    except Exception as e:
        print('ERROR ENABLING CHANNELS')
        print('ERROR: {}'.format(e))

    try:
        device_list = pa.device_list(i2c)
        print('Device List Made: {}'.format(datetime.now()))
    except Exception as e:
        print('ERROR CREATING DEVICE LIST')
        print('ERROR: {}'.format(e))

    try:
        device_data = pa.make_device_dict(device_list)
        print('Dictionary Initialized: {}'.format(datetime.now()))
    except Exception as e:
        print('ERROR INITIALIZING DICTIONARY')
        print('ERROR: {}'.format(e))

    try:
        data_dict = pa.capture_data(device_data, tca, wait_time, n_points)
        print('Dictionary Filled: {}'.format(datetime.now()))
    except Exception as e:
        print('ERROR CAPTURING DATA')
        print('ERROR: {}'.format(e))

    try:
        avg_dict = pa.get_averages(data_dict)
        print("Dictionary Averagad: {}".format(datetime.now()))
    except Exception as e:
        print('ERROR AVERAGING DATA')
        print('ERROR: {}'.format(e))
    
    if args.log == 'YES':
        try:
            pa.print_avg_data(avg_dict)
            print("Averaged Data Printed: {}".format(datetime.now()))
        except Exception as e:
            print('ERROR PRINTING AVERAGED DATA')
            print('ERROR: {}'.format(e))
    
    try:
        pa.csv_write(avg_dict)
        print('CSV Written: {}'.format(datetime.now()))
    except Exception as e:
        print('ERROR WRITING CSV')
        print('ERROR: {}'.format(e))
