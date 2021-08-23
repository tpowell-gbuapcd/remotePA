#!/usr/bin/env python3

#import qwiic
import time
import board
import busio
import adafruit_tca9548a
import adafruit_ina219
import adafruit_ssd1306
import adafruit_mcp9808
import argparse
import csv
import os
import platform
import numpy as np

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


def print_data(tca, wait_time, n_tests, avg):
    '''
    Print the data in human readable format to screen. Used for testing
    input param: pa_channel, list of channels to enable (default = all)
    input param: wait_time, capture data points every wait_time seconds
    input param: n_points, number of data points to capture
    input param: n_test, number of separate tests for data capture
    input param: data_dict, dictionary containing all of the arrays needed to store data from I2C devices
    '''

    purple_air = adafruit_ina219.INA219(tca[0])
    raspberry_pi = adafruit_ina219.INA219(tca[7])
    wifi = adafruit_ina219.INA219(tca[4])
    comms  = adafruit_ina219.INA219(tca[3])
    temp = adafruit_mcp9808.MCP9808(tca[6])
    
    print('Args:\n Wait Time: {}\nTest: {}'.format(wait_time, n_tests))
    print("Testing File Writer")
    print("Data Capture Start Time: {}".format(datetime.now().strftime("%m/%d/%Y %H:%M:%S")))
    print()
    # begin n number of test runs
    j = 0

    while j != n_tests:
        
        i=0
        start_time = datetime.now().strftime('%m:%d:%Y %H:%M:%S')
        purple_air_current = 0
        purple_air_power = 0
        purple_air_voltage = 0

        wifi_current = 0
        wifi_power = 0
        wifi_voltage = 0

        raspberry_pi_current = 0
        raspberry_pi_power = 0
        raspberry_pi_voltage = 0

        comms_current = 0
        comms_power = 0
        comms_voltage = 0

        temp_temp = 0

        while i <= avg:

            #print('{:<25}{:<15}{:<15}{:<15}{:<15}{:<15}{:<15}{:<15}{:<15}{:<15}{:<15}{:<15}{:<15}{:<15}'.format('Time', 'PA Current', 'PA Power', 'PA Voltage', 
            #        'WIFI Current', 'WIFI Power', 'WIFI Voltage', 'RPi Current', 'RPi Power', 'RPi Voltage', 'Comms Current', 'Comms Power', 'Comms Voltage', 'Temp'))
            purple_air_current += purple_air.current
            purple_air_power += purple_air.power
            purple_air_voltage += purple_air.bus_voltage
            wifi_current += wifi.current
            wifi_power += wifi.power
            wifi_voltage += wifi.bus_voltage
            raspberry_pi_current += raspberry_pi.current
            raspberry_pi_power += raspberry_pi.power
            raspberry_pi_voltage += raspberry_pi.bus_voltage
            comms_current += comms.current
            comms_power += comms.power
            comms_voltage += comms.bus_voltage
            temp_temp += temp.temperature

            time.sleep(wait_time)
            
            i += 1
        
        avg_purple_air_current = purple_air_current/avg
        avg_purple_air_power = purple_air_power/avg
        avg_purple_air_voltage = purple_air_voltage/avg

        avg_wifi_current = wifi_current/avg
        avg_wifi_power = wifi_power/avg
        avg_wifi_voltage = wifi_voltage/avg

        avg_raspberry_pi_current = raspberry_pi_current/avg
        avg_raspberry_pi_power = raspberry_pi_power/avg
        avg_raspberry_pi_voltage = raspberry_pi_voltage/avg

        avg_comms_current = comms_current/avg
        avg_comms_power = comms_power/avg
        avg_comms_voltage = comms_voltage/avg

        avg_temp_temp = temp_temp/avg
        end_time = datetime.now().strftime('%m/%d/%Y %H:%M:%S')
        print('Average Time: {} seconds'.format(avg))
        print('Start: {}\nEmd: {}'.format(start_time, end_time))
        print('Time: {:>34}\nPA Current: {:>15.2f} mA\nPA Power: {:>15.2f} W\nPA Voltage: {:>14.2f} V\nWiFi Current: {:>12.2f} mA\nWiFi Power: {:>13.2f} W\nWiFi Voltage: {:>12.2f} V\nRP Current: {:>15.2f} mA\nRP Power: {:>15.2f} W\nRP Voltage: {:>14.2f} V\nComms Current: {:>11.2f} mA\nComms Power: {:>12.2f} W\nComms Voltage: {:>10.2f} V\nTemp: {:>20.2f} C'.format(start_time, avg_purple_air_current, avg_purple_air_power, avg_purple_air_voltage, avg_wifi_current, avg_wifi_power, avg_wifi_voltage, avg_raspberry_pi_current, avg_raspberry_pi_power, avg_raspberry_pi_voltage, avg_comms_current, avg_comms_power, avg_comms_voltage, avg_temp_temp))

        print()
              
        j += 1


def file_write(tca, wait_time, n_points, n_tests, avg):
    '''
    Write the data from the IN219s to file for export. DOES NOT USE ANY DICTIONARIES INITIALIZED ABOVE.

    input param: pa_channel, list of channels to enable (default = all)
    input param: wait_time, capture data points every wait_time seconds
    input param: n_points, number of data points to capture
    input param: n_test, number of separate tests for data capture
    input param: data_dict, dictionary containing all of the arrays needed to store data from I2C devices
    '''

    j = 0
    
    data_dir = os.getcwd() + "/data/"

    purple_air = adafruit_ina219.INA219(tca[0])
    raspberry_pi = adafruit_ina219.INA219(tca[7])
    wifi = adafruit_ina219.INA219(tca[4])
    comms  = adafruit_ina219.INA219(tca[3])
    temp = adafruit_mcp9808.MCP9808(tca[6])
    
    # file_name = "test_" +  datetime.now()strftime("%m%d%Y%H%M%S") + ".csv"
    header_vals = ['Time', 'PA Current', 'PA Power', 'PA Voltage', 'WIFI Current', 'WIFI Power', 'WIFI Voltage',
                    'RPi Current', 'RPi Power', 'RPi Voltage', 'Comms Current', 'Comms Power', 'Comms Voltage', 'Temp']

    #while j < n_tests:
    # we don't care about the number of tests anymore, this runs continuously and breaks tests into 1 hour chunks.
    while j != n_tests:       
        
        start_time = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        file_name = str(platform.node()) + datetime.now().strftime("%m%d%Y") + ".csv"
        
        if file_name not in os.listdir(data_dir):
            with open(data_dir + file_name, 'w', newline='') as f:
                file_writer = csv.writer(f, delimiter=',')
                file_writer.writerow(header_vals)
            f.close()


        print("Run Start Time: {}".format(start_time))
        print("Test run {} of {}".format(str(j+1), str(n_tests)))
        
        # r = 0 # used for debugging
        i = 0
         
        with open(data_dir+file_name, 'a', newline = '') as f:
        
            file_writer = csv.writer(f, delimiter = ',')
                
            i=0
            start_time = datetime.now().strftime('%m:%d:%Y %H:%M:%S')
            purple_air_current = 0
            purple_air_power = 0
            purple_air_voltage = 0

            wifi_current = 0
            wifi_power = 0
            wifi_voltage = 0

            raspberry_pi_current = 0
            raspberry_pi_power = 0
            raspberry_pi_voltage = 0

            comms_current = 0
            comms_power = 0
            comms_voltage = 0

            temp_temp = 0

            while i <= avg:

                #print('{:<25}{:<15}{:<15}{:<15}{:<15}{:<15}{:<15}{:<15}{:<15}{:<15}{:<15}{:<15}{:<15}{:<15}'.format('Time', 'PA Current', 'PA Power', 'PA Voltage', 
                #        'WIFI Current', 'WIFI Power', 'WIFI Voltage', 'RPi Current', 'RPi Power', 'RPi Voltage', 'Comms Current', 'Comms Power', 'Comms Voltage', 'Temp'))
                purple_air_current += purple_air.current
                purple_air_power += purple_air.power
                purple_air_voltage += purple_air.bus_voltage
                wifi_current += wifi.current
                wifi_power += wifi.power
                wifi_voltage += wifi.bus_voltage
                raspberry_pi_current += raspberry_pi.current
                raspberry_pi_power += raspberry_pi.power
                raspberry_pi_voltage += raspberry_pi.bus_voltage
                comms_current += comms.current
                comms_power += comms.power
                comms_voltage += comms.bus_voltage
                temp_temp += temp.temperature

                time.sleep(wait_time)
                
                i += 1
        
            avg_purple_air_current = purple_air_current/avg
            avg_purple_air_power = purple_air_power/avg
            avg_purple_air_voltage = purple_air_voltage/avg

            avg_wifi_current = wifi_current/avg
            avg_wifi_power = wifi_power/avg
            avg_wifi_voltage = wifi_voltage/avg

            avg_raspberry_pi_current = raspberry_pi_current/avg
            avg_raspberry_pi_power = raspberry_pi_power/avg
            avg_raspberry_pi_voltage = raspberry_pi_voltage/avg

            avg_comms_current = comms_current/avg
            avg_comms_power = comms_power/avg
            avg_comms_voltage = comms_voltage/avg

            avg_temp_temp = temp_temp/avg
            end_time = datetime.now().strftime('%m/%d/%Y %H:%M:%S')

               
            row = [start_time, avg_purple_air_current, avg_purple_air_power, avg_purple_air_voltage,
                avg_wifi_current, avg_wifi_power, avg_wifi_voltage,
                avg_raspberry_pi_current, avg_raspberry_pi_power, avg_raspberry_pi_voltage,
                avg_comms_current, avg_comms_power, avg_comms_voltage, avg_temp_temp]
            
            print(file_name)
            print(row, start_time, end_time)
            file_writer.writerow(row)
            
            j += 1
            
            f.close()
            # print("Time: {} File Closing: {} N Rows: {}".format(datetime.now().strftime("%m/%d/%Y %H:%M:%S"), file_name, r)) # used for debugging


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument("-w", "--wait_time", type=int, help = "capture data points every wait_time seconds, i.e time resolution of data. Default is 1 second.", default=1)
    parser.add_argument("-p", "--n_points", type=int, help = "Number of data points to capture. Ex.) n_points = 60, --wait_time = 1 is a data point every second for one minute. Default is 600, or 10 minutes with default wait_time of 1 second.", default=600)
    parser.add_argument("-t", "--n_tests", type=int,  help = "Number of tests to run, break up n_points into n_test chunks. Ex.) --n_tests = 3. --n_points = 60, --wait_time = 1 will give 3 separate tests of data points every second for 60 seconds. If no parameter is give, an indefinite number of tests will be run. ", default=-1)
    parser.add_argument("-c", "--channels", type=list, help="List of channels to enable on mux board, default=all, Ex.) [0, 3] enables channels 0 and 3", default=[0, 1, 2, 3, 4, 5, 6, 7])
    parser.add_argument("-test", "--testing", type=str, help="Is this run for testing or for true data collection? Yes or No?", default="No")
    parser.add_argument("-a", "--average", type=int, help="The number of points to average over", default=1)
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
    if args.testing == "No":
        file_write(tca_board, args.wait_time, args.n_points, args.n_tests, args.average)
    else:
        print_data(tca_board, args.wait_time, args.n_tests, args.average)        
    



