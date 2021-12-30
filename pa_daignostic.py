#!/usr/bin/env python3

#import qwiic
import time
import board
import busio
import adafruit_tca9548a
import adafruit_ina219
import adafruit_ssd1306
import adafruit_mcp9808
import adafruit_bme680
import adafruit_scd30
import argparse
import csv
import os
import platform
import numpy as np

from datetime import datetime
from qwiic import QwiicTCA9548A
from adafruit_pm25.i2c import PM25_I2C

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
    '''

    #INA219 devices
    purple_air = adafruit_ina219.INA219(tca[0])
    fans = adafruit_ina219.INA219(tca[2])
    comms  = adafruit_ina219.INA219(tca[3])
    raspberry_pi = adafruit_ina219.INA219(tca[4])
    wifi = adafruit_ina219.INA219(tca[7])
    

    bme = adafruit_bme680.Adafruit_BME680_I2C(tca[5])
    scd = adafruit_scd30.SCD30(tca[5])
    pm25 = PM25_I2C(tca[5])
    mcp = adafruit_mcp9808.MCP9808(tca[6])
    
    print('Args:\n Wait Time: {}\nTest: {}'.format(wait_time, n_tests))
    print("Testing File Writer")
    print("Data Capture Start Time: {}".format(datetime.now().strftime("%m/%d/%Y %H:%M:%S")))
    print()
    # begin n number of test runs
    j = 0

    while j != n_tests:
        
        i=1
        start_time = datetime.now().strftime('%m:%d:%Y %H:%M:%S')
        
        # initialize variables for averaging
        # this is a simple average where I add the values over an averaging time and then divide by the number of samples
        # there is a better way to do this using a dictionary and arrays (?)
        
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
        
        fans_current = 0
        fans_power = 0
        fans_voltage = 0

        mcp_temp = 0

        bme_gas = 0
        bme_hum = 0
        bme_press = 0
        bme_temp = 0
        
        scd_co2 = 0
        scd_hum = 0
        scd_temp = 0
        
        # environmental conditions
        pm1_env = 0
        pm25_env = 0
        pm10_env = 0

        # standart pressure and temp conditions
        pm1_st = 0
        pm25_st = 0
        pm10_st = 0

        # because of the clock stretching on these two devices, it is possible for the data to not be present
        # after the wait_time, so we don't record data when that happens. This means we cannot use the input average
        # parameter for averaging.
        # THIS NEEDS TO BE CORRECTED WITH NUMPY
        scd_avg = 0
        pm_avg = 0
        while i <= avg:

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

            fans_current += fans.current
            fans_power += fans.power
            fans_voltage += fans.bus_voltage

            mcp_temp += mcp.temperature

            bme_gas += bme.gas
            bme_hum += bme.humidity
            bme_press += bme.pressure
            bme_temp += bme.temperature

            try:
                pmdata = pm25.read()
                pm1_env += pmdata["pm10 env"]
                pm25_env += pmdata["pm25 env"]
                pm10_env += pmdata["pm100 env"]

                pm1_st += pmdata["pm10 standard"]
                pm25_st += pmdata["pm25 standard"]
                pm10_st += pmdata["pm100 standard"]
                
                pm_avg += 1
            except:
                Exception

            try:
                if scd.data_available == 1:
                    scd_co2 += scd.CO2
                    scd_hum += scd.relative_humidity
                    scd_temp += scd.temperature
                    scd_avg += 1
            except:
                Exception

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

        avg_fans_current = fans_current/avg
        avg_fans_power = fans_power/avg
        avg_fans_voltage = fans_voltage/avg
        
        avg_mcp_temp = mcp_temp/avg

        avg_bme_gas = bme_gas/avg
        avg_bme_hum = bme_hum/avg
        avg_bme_press = bme_press/avg
        avg_bme_temp = bme_temp/avg

        avg_pm1_env = pm1_env/pm_avg 
        avg_pm25_env = pm25_env/pm_avg
        avg_pm10_env = pm10_env/pm_avg

        avg_pm1_st = pm1_st/pm_avg
        avg_pm25_st = pm25_st/pm_avg
        avg_pm10_st = pm10_env/pm_avg

        avg_scd_co2 = scd_co2/scd_avg
        avg_scd_hum = scd_hum/scd_avg
        avg_scd_temp = scd_temp/scd_avg

        end_time = datetime.now().strftime('%m/%d/%Y %H:%M:%S')
        
        print('Average Time: {} seconds'.format(avg), 'Average PM: {}'.format(pm_avg), 'Average SCD: {}'.format(scd_avg))
        print('Start: {}\nEnd: {}'.format(start_time, end_time))
        # terrible formatting
        print('Time: {:>34}\nPA Current: {:>10.2f} mA      PA Power: {:>8.2f} W      PA Voltage: {:>8.2f} V\nWiFi Current: {:>9.2f} mA     WiFi Power: {:>6.2f} W      WiFi Voltage: {:>6.2f} V\nRP Current: {:>11.2f} mA      RP Power: {:>8.2f} W     RP Voltage: {:>8.2f} V\nComms Current: {:>8.2f} mA     Comms Power: {:>5.2f} W      Comms Voltage: {:>5.2f} V\nFans Current: {:>9.2f} mA     Fans Power: {:>6.2f} W      Fans Voltage: {:>6.2f} V\nMCP Temp: {:>12.2f} C       BME Temp: {:>9.2f} C     SCD Temp: {:>10.2f} C\nBME Humidity: {:>8.2f} %       SCD Humidity: {:>5.2f}\nBME Gas: {:>15.2f} Ohms  SCD CO2: {:>11.2f} PPM\nPM1.0 Env: {:>10.2f} ug/m3    PM2.5 Env: {:>7.2f} ug/m3  PM10.0 Env: {:>8.2f} ug/m3\nPM1.0 ST: {:>11.2f} ug/m3    PM2.5 ST: {:>8.2f} ug/m3  PM10.0 ST: {:>9.2f} ug/m3'.format(start_time, avg_purple_air_current, avg_purple_air_power, avg_purple_air_voltage, avg_wifi_current, avg_wifi_power, avg_wifi_voltage, avg_raspberry_pi_current, avg_raspberry_pi_power, avg_raspberry_pi_voltage, avg_comms_current, avg_comms_power, avg_comms_voltage, avg_fans_current, avg_fans_power, avg_fans_voltage, avg_mcp_temp, avg_bme_temp, avg_scd_temp, avg_bme_hum, avg_scd_hum, avg_bme_gas, avg_scd_co2, avg_pm1_env, avg_pm25_env, avg_pm10_env, avg_pm1_st, avg_pm25_st, avg_pm10_st))

        print()
              
        j += 1


def file_write(tca, wait_time, n_points, n_tests, avg):
    '''
    Write the data from the IN219s to file for export.

    input param: tca, the object needed to call the individual channels the sensors are attached to on the mux board
    input param: wait_time, capture data points every wait_time seconds
    input param: n_points, number of data points to capture
    input param: n_test, number of separate tests for data capture
    input param: avg, the number of points to average over. This is effectively n_points, but it's possible for it to be different depending on what the user wants.
    '''

    j = 0
    
    data_dir = os.getcwd() + "/data/"
    
    #INA219 devices
    purple_air = adafruit_ina219.INA219(tca[0])
    fans = adafruit_ina219.INA219(tca[2])
    comms  = adafruit_ina219.INA219(tca[3])
    raspberry_pi = adafruit_ina219.INA219(tca[4])
    wifi = adafruit_ina219.INA219(tca[7])
    

    bme = adafruit_bme680.Adafruit_BME680_I2C(tca[5])
    scd = adafruit_scd30.SCD30(tca[5])
    pm25 = PM25_I2C(tca[5])
    mcp = adafruit_mcp9808.MCP9808(tca[6])
    
    # file_name = "test_" +  datetime.now()strftime("%m%d%Y%H%M%S") + ".csv"
    header_vals = ['Time', 'PA Current', 'PA Power', 'PA Voltage', 'WIFI Current', 'WIFI Power', 'WIFI Voltage',
                    'RPi Current', 'RPi Power', 'RPi Voltage', 'Comms Current', 'Comms Power', 'Comms Voltage', 
                    'Fans Current', 'Fans Power', 'Fans Voltage', 'Enclosure Temp', 'BME Temp', 'SCD Temp',
                    'BME Humidity', 'CO2 Humidity', 'BME Gas', 'CO2 Gas', 'BME Pressure', 'PM1.0 Env',
                    'PM2.5 Env', 'PM10.0 Env', 'PM1.0 ST', 'PM2.5 ST', 'PM10.0 ST']

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
                
            i=1
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
        
            fans_current = 0
            fans_power = 0
            fans_voltage = 0

            mcp_temp = 0

            bme_gas = 0
            bme_hum = 0
            bme_press = 0
            bme_temp = 0
        
            scd_co2 = 0
            scd_hum = 0
            scd_temp = 0
        
            # environmental conditions
            pm1_env = 0
            pm25_env = 0
            pm10_env = 0

            # standard pressure and temp conditions
            pm1_st = 0
            pm25_st = 0
            pm10_st = 0

            # because of the clock stretching on these two devices, it is possible for the data to not be present
            # after the wait_time, so we don't record data when that happens. This means we cannot use the input average
            # parameter for averaging.
            # THIS NEEDS TO BE CORRECTED WITH NUMPY
            scd_avg = 0
            pm_avg = 0

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

                fans_current += fans.current
                fans_power += fans.power
                fans_voltage += fans.bus_voltage

                mcp_temp += mcp.temperature

                bme_gas += bme.gas
                bme_hum += bme.humidity
                bme_press += bme.pressure
                bme_temp += bme.temperature

                try:
                    pmdata = pm25.read()
                    pm1_env += pmdata["pm10 env"]
                    pm25_env += pmdata["pm25 env"]
                    pm10_env += pmdata["pm100 env"]

                    pm1_st += pmdata["pm10 standard"]
                    pm25_st += pmdata["pm25 standard"]
                    pm10_st += pmdata["pm100 standard"]
                
                    pm_avg += 1
                except:
                    Exception

                try:
                    if scd.data_available == 1:
                        scd_co2 += scd.CO2
                        scd_hum += scd.relative_humidity
                        scd_temp += scd.temperature
                        scd_avg += 1
                except:
                    Exception

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

            avg_fans_current = fans_current/avg
            avg_fans_power = fans_power/avg
            avg_fans_voltage = fans_voltage/avg
        
            avg_mcp_temp = mcp_temp/avg

            avg_bme_gas = bme_gas/avg
            avg_bme_hum = bme_hum/avg
            avg_bme_press = bme_press/avg
            avg_bme_temp = bme_temp/avg

            avg_pm1_env = pm1_env/pm_avg 
            avg_pm25_env = pm25_env/pm_avg
            avg_pm10_env = pm10_env/pm_avg

            avg_pm1_st = pm1_st/pm_avg
            avg_pm25_st = pm25_st/pm_avg
            avg_pm10_st = pm10_env/pm_avg

            avg_scd_co2 = scd_co2/scd_avg
            avg_scd_hum = scd_hum/scd_avg
            avg_scd_temp = scd_temp/scd_avg

            end_time = datetime.now().strftime('%m/%d/%Y %H:%M:%S')

               
            row = [start_time, avg_purple_air_current, avg_purple_air_power, avg_purple_air_voltage,
                    avg_wifi_current, avg_wifi_power, avg_wifi_voltage,
                    avg_raspberry_pi_current, avg_raspberry_pi_power, avg_raspberry_pi_voltage,
                    avg_comms_current, avg_comms_power, avg_comms_voltage, avg_fans_current, 
                    avg_fans_power, avg_fans_voltage, avg_mcp_temp, avg_bme_temp,
                    avg_scd_temp, avg_bme_hum, avg_scd_hum, avg_bme_gas, avg_scd_co2, avg_bme_press,
                    avg_pm1_env, avg_pm25_env, avg_pm10_env, avg_pm1_st, avg_pm25_env, avg_pm10_st]
            
            print(file_name)
            print(row, start_time, end_time)
            print(i, scd_avg, pm_avg)
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
    parser.add_argument("-a", "--average", type=int, help="The number of points to average over, should default to n_points", default=1)
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
    



