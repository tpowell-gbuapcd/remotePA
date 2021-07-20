#import qwiic
import time
import board
import busio
import adafruit_tca9548a
import adafruit_ina219
import adafruit_ssd1306
import argparse
import csv
import os

#import matplotlib.pyplot as plt
import numpy as np

#from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from qwiic import QwiicTCA9548A

'''
LIBRARY FOR REMOTE PA DATA CAPTURE AND EXPORT
'''

def mux_init():
    '''
    Initialize the mux board constructor 

    output param: mux, used to enable and disable channels on the  mux board. 
    output type: object
    
    output param: tca, used for contacting any I2C device on mux (ex. tca[0] contacts I2C on channel 0)
    output type: object
    '''
    
    i2c = busio.I2C(board.SCL, board.SDA)

    mux = QwiicTCA9548A() # this is used for enabling/disabling mux channels
    tca = adafruit_tca9548a.TCA9548A(i2c) # this is for contacting I2C devices on mux

    return mux, tca


def channel_status(board_name):
    '''
    Return the status of the channels on the MUX board (enabled or disabled)

    input param: board_name, object used to call the MUX board
    input type: object
    '''

    print("Channels:")
    board_name.list_channels()


def channel_enable(board_name, channels):
    '''
    Enable the channels on the MUX board. Default mode is off, so this will need to be called whenever the device is rebooted or after
    power off. 
    
    input param: board_name, object used to call the MUX board
    input type: object

    input param: channels, channels  to be turned on 0-7 as labled on the QWIIC MUX board 
    input type: list of int
    '''

    print("Enabling Channels {}".format(channels))
    board_name.enable_channels(channels)
    time.sleep(1)


def file_write(mux, tca, pa_channel, wait_time, n_points, n_tests):
    '''
    Write the data from the IN219s to file for export. DOES NOT USE ANY DICTIONARIES INITIALIZED ABOVE.

    input param: pa_channel, list of channels to enable (default = all)
    input param: wait_time, capture data points every wait_time seconds
    input param: n_points, number of data points to capture
    input param: n_test, number of separate tests for data capture
    input param: data_dict, dictionary containing all of the arrays needed to store data from I2C devices
    '''

    j = 0

    #pa_mux, tca_board = mux_init()
    #channel_enable(pa_mux, pa_channel)
    #channel_status(pa_mux)
    
    data_dir = os.getcwd() + "/data/"

    purple_air = adafruit_ina219.INA219(tca[0])
    raspberry_pi = adafruit_ina219.INA219(tca[7])
    wifi = adafruit_ina219.INA219(tca[4])
    comms  = adafruit_ina219.INA219(tca[3])
    
    print("Args: ", wait_time, n_points, n_tests)
    print("Testing File Writer")
    print("Data Capture Start Time: {}".format(datetime.now().strftime("%m/%d/%Y %H:%M:%S")))
    # begin n number of test runs
    
    # file_name = "test_" +  datetime.now()strftime("%m%d%Y%H%M%S") + ".csv"
    header_vals = ['Time', 'PA Current', 'PA Power', 'PA Voltage', 'WIFI Current', 'WIFI Power', 'WIFI Voltage',
                    'RPi Current', 'RPi Power', 'RPi Voltage', 'Comms Current', 'Comms Power', 'Comms Voltage']

    #while j < n_tests:
    # we don't care about the number of tests anymore, this runs continuously and breaks tests into 1 hour chunks.
    while j < n_tests:       
        
        start_time = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        file_name = data_dir + "remotePA_" + datetime.now().strftime("%m%d%Y%H%M%S") + ".csv"

        print("Run Start Time: {}".format(start_time))
        print("Test run {} of {}".format(str(j+1), str(n_tests)))
        
        r = 0
        i = 0
         
        with open(file_name, 'w', newline = '') as f:
        
            file_writer = csv.writer(f, delimiter = ',')
        
            # n_points will be hardcoded in the crontab at 3600 (one hour)

            while i <= n_points:
                
                #file_writer = csv.writer(f, delimiter = ',')
        
                if i == 0:
                    file_writer.writerow(header_vals)
                else:
                    row = [datetime.now().replace(microsecond=0), purple_air.current, purple_air.power, purple_air.bus_voltage,
                        wifi.current, wifi.power, wifi.bus_voltage, raspberry_pi.current, raspberry_pi.power, raspberry_pi.bus_voltage,
                        comms.current, comms.power, comms.bus_voltage]
                    file_writer.writerow(row)
                    time.sleep(wait_time)
                    r += 1
                i += 1
            
            j += 1
            
            f.close()
            print("Time: {} File Closing: {} N Rows: {}".format(datetime.now().strftime("%m/%d/%Y %H:%M:%S"), file_name, r))


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument("-w", "--wait_time", type=int, help = "capture data points every wait_time seconds, i.e time resolution of data")
    parser.add_argument("-p", "--n_points", type=int, help = "Number of data points to capture. Ex.) n_points = 60, --wait_time = 1 is a data point every second for one minute")
    parser.add_argument("-t", "--n_tests", type=int,  help = "Number of tests to run, break up n_points into n_test chunks. Ex.) --n_tests = 3. --n_points = 60, --wait_time = 1 will give 3 separate tests of data points every second for 60 seconds")
    parser.add_argument("-c", "--channels", type=list, help="List of channels to enable on mux board, default=all, Ex.) [0, 3] enables channels 0 and 3", default=[0, 1, 2, 3, 4, 5, 6, 7])

    args = parser.parse_args()

    try:
        args.wait_time > 0
    except: 
        print("Invalid wait_time, must be greater than 0")

    try:
        args.n_points > 0
    except:
        print("Invalid n_points, must be greater than 0")

    try:
        args.n_tests > 0
    except:
        print("Invalid n_tests, must be greater than 0")
   
    print("MUX init Time: {}".format(datetime.now().strftime("%m/%d/%Y %H:%M:%S")))
    pa_mux, tca_board = mux_init()
    print("Channel Enable Start Time: {}".format(datetime.now().strftime("%m/%d/%Y %H:%M:%S")))
    channel_enable(pa_mux, args.channels)
    print("Channel Status Start Time: {}".format(datetime.now().strftime("%m/%d/%Y %H:%M:%S")))
    channel_status(pa_mux)
    print("File Writer Start Time: {}".format(datetime.now().strftime("%m/%d/%Y %H:%M:%S")))
    file_write(pa_mux, tca_board, args.channels, args.wait_time, args.n_points, args.n_tests)
    


