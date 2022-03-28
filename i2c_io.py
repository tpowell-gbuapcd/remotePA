#!/usr/bin/env python3

import argparse, sys, os
import purple_air_diagnostic as pa
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument('-w', '--wait_time', type=int, help='The amount of seconds to wait between reads. Must be at least 2 seconds long. Default is 2 seconds. ex.) 2', default=2)
parser.add_argument('-n', '--n_points', type=int, help='The number of points to average over. Total time span between writes to csv is n_points*wait_time. Default is 300 ex.) 300 (300*2 = 10 minute averaging)', default=300)
parser.add_argument('-l', '--log', type=bool, help='Would you like to print the output to screen? True is print to screen, False is direct output to log.txt file in data directory Default is False.', default=False)
args = parser.parse_args()

if args.log is False:
    sys.stdout = open(os.getcwd() + '/data/' + 'file.txt', 'w')
    print("Logging to File: {}".format(datetime.now()), flush=True)

try:
    print('Initializing I2C devices: {}'.format(datetime.now()), flush=True)
    mux, tca, i2c = pa.mux_init()
except Exception as e:
    print('ERROR INITIALIZING I2C DEVICES', flush=True)
    print('ERROR: {}'.format(e), flush=True)

wait_time = args.wait_time
n_points = args.n_points

j = 0 
while j == 0:

    try:
        print('Enabling channels: {}'.format(datetime.now()), flush=True)
        pa.channel_enable(mux, [0,1,2,3,4,5,6,7])
        print('Channels Enabled: {}'.format(datetime.now()), flush=True)
    except Exception as e:
        print('ERROR ENABLING CHANNELS', flush=True)
        print('ERROR: {}'.format(e), flush=True)

    try:
        device_list = pa.device_list(i2c)
        print('Device List Made: {}'.format(datetime.now()), flush=True)
    except Exception as e:
        print('ERROR CREATING DEVICE LIST', flush=True)
        print('ERROR: {}'.format(e), flush=True)

    try:
        device_data = pa.make_device_dict(device_list)
        print('Dictionary Initialized: {}'.format(datetime.now()), flush=True)
    except Exception as e:
        print('ERROR INITIALIZING DICTIONARY', flush=True)
        print('ERROR: {}'.format(e), flush=True)

    try:
        data_dict = pa.capture_data(device_data, tca, wait_time, n_points)
        print('Dictionary Filled: {}'.format(datetime.now()), flush=True)
    except Exception as e:
        print('ERROR CAPTURING DATA', flush=True)
        print('ERROR: {}'.format(e), flush=True)

    try:
        avg_dict = pa.get_averages(data_dict)
        print("Dictionary Averagad: {}".format(datetime.now()), flush=True)
    except Exception as e:
        print('ERROR AVERAGING DATA', flush=True)
        print('ERROR: {}'.format(e), flush=True)
    
    if args.log == 'YES':
        try:
            pa.print_avg_data(avg_dict)
            print("Averaged Data Printed: {}".format(datetime.now()), flush=True)
        except Exception as e:
            print('ERROR PRINTING AVERAGED DATA', flush=True)
            print('ERROR: {}'.format(e), flush=True)
    
    try:
        pa.csv_write(avg_dict)
        print('CSV Written: {}'.format(datetime.now()), flush=True)
    except Exception as e:
        print('ERROR WRITING CSV', flush=True)
        print('ERROR: {}'.format(e), flush=True)
