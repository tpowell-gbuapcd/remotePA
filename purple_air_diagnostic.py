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
from datetime import timedelta
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

    return mux, tca, i2c


def channel_status(board_name):
    '''
    Return the status of the channels on the MUX board (enabled or disabled)

    input param: board_name, object used to call the MUX board
    input type: object
    '''

    print("Channels:")
    print()
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
    print()
    board_name.enable_channels(channels)
    time.sleep(1)


def device_list(device):
    '''
    Return a list of the hex addresses for all connected I2C devices. This will include the MUX breakout

    0x12 = PM sensor
    0x18 = MCP9808
    0x40 = INA219, there is only one address here for all 5 INA219s. I could solder the address pads to change the addresses (0x40-0x44),
    but I think this is unnecessary. If one is there, then they will all be there and they will be connected to predesignated MUX ports.
    0x61 = SCD-30
    0x70 = MUX breakout
    0x77 = BME688

    input param: device, the i2c object needed to call the scan() function.
    input type: object

    return: a list of the hex addresses of the connected I2C devices 
    '''

    return [hex(x) for x in device.scan()]


def make_device_dict(list_of_devices):
    '''
    Create a dictionary of devices and their data attributes. Also create the objects needed to call the individual data points on each sensor.
    
    input param: list_of_devices, the list of I2C devices by hex address
    input type: list
    
    output param: dict_of_devices
    output type: dict
    '''
    
    dict_of_devices = {}
    
    if '0x12' in list_of_devices:
        print('PM Sensor connected')
        dict_of_devices['PM'] = {'PM1.0 ENV': [], 'PM2.5 ENV': [], 'PM10.0 ENV': [], 'PM1.0 ST': [], 'PM2.5 ST': [], 'PM10.0 ST': []}

    if '0x18' in list_of_devices:
        print('MCP9808 connected')
        dict_of_devices['MCP'] = {'Temp': []}

    if '0x40' in list_of_devices:
        print('INA219 connected')
        dict_of_devices['Purpleair'] = {'Current': [], 'Power': [], 'Voltage': []}
        dict_of_devices['WIFI'] = {'Current': [], 'Power': [], 'Voltage': []}
        dict_of_devices['RPI'] = {'Current': [], 'Power': [], 'Voltage': []}
        dict_of_devices['Comms'] = {'Current': [], 'Power': [], 'Voltage': []}
        dict_of_devices['Fans'] = {'Current': [], 'Power': [], 'Voltage': []}
    
    if '0x61' in list_of_devices:
        print('SCD-30 connected')
        dict_of_devices['SCD'] = {'CO2': [], 'RH': [], 'Temp': []}

    if '0x70' in list_of_devices:
        print('MUX breakout connected')
    if '0x77' in list_of_devices:
        print('BME688 connected')
        dict_of_devices['BME'] = {'Gas': [], 'RH': [], 'Pressure': [], 'Temp': []}
 
    print()

    return dict_of_devices


def capture_data(device_dict, tca, wait_time, n_points):
    '''
    Capture data over the desired averaging time. Ex.) For the default wait time of 2 seconds and 300 points, this will be an average over 10 minutes.
    
    input param: device_dict, nested dictionary where the keys are the sensor and the data parameter ex.) device_dict['MCP']['Temp']
    input type: dictionary

    input param: tca, object needed to call the individual channels on the MUX breakout board
    input type: object

    input param: wait_time, the amount of time between each data acquisition. Should be 2 seconds minimum to account for clock stretching on PM sensor.
    input type: integer

    input param: n_points, the number of data points to acquire. n_points * wait_time gives the time of each "averaged" time. 
    input type: integer

    output_param: device_dict, the filled nested dictionary. Each list is n_points * wait_time in size.
    output_type: dictionary
    '''

    device_list = list(device_dict.keys())

    #initialize objects needed to call individual data points on each sensor
    if 'PM' in device_list:
        pm = PM25_I2C(tca[5])
    if 'MCP' in device_list:
        mcp = adafruit_mcp9808.MCP9808(tca[6])
    if 'Purpleair' in device_list:
        purple_air = adafruit_ina219.INA219(tca[0])
    if 'WIFI' in device_list:
        wifi = adafruit_ina219.INA219(tca[7])
    if 'RPI' in device_list:
        rpi = adafruit_ina219.INA219(tca[4])
    if 'Comms' in device_list:
        comms = adafruit_ina219.INA219(tca[3])
    if 'Fans' in device_list:
        fans = adafruit_ina219.INA219(tca[2])
    if 'SCD' in device_list:
        scd = adafruit_scd30.SCD30(tca[5])
    if 'BME' in device_list:
        bme = adafruit_bme680.Adafruit_BME680_I2C(tca[5])

    #print("Wait Time = ", wait_time, " s")
    #print("Number of Points To Average Over = ", n_points, " Points")
    
    #print("Testing File Writer")
    #print("Data Capture Start Time: {}".format(datetime.now().strftime("%m/%d/%Y %H:%M:%S")))
    #print()
        
    i = 1
    start_time = datetime.now().strftime('%m:%d:%Y %H:%M:%S')
    device_dict['Time'] = start_time
    wait_avg = 0

    while i <= n_points:
        start = datetime.now()
        if 'PM' in device_list:
            try:
                pmdata = pm.read()
                device_dict['PM']['PM1.0 ENV'].append(pmdata["pm10 env"])
                device_dict['PM']['PM2.5 ENV'].append(pmdata["pm25 env"])
                device_dict['PM']['PM10.0 ENV'].append(pmdata["pm100 env"])
                device_dict['PM']['PM1.0 ST'].append(pmdata["pm10 standard"])
                device_dict['PM']['PM2.5 ST'].append(pmdata["pm25 standard"])
                device_dict['PM']['PM10.0 ST'].append(pmdata["pm100 standard"])
            except:
                Exception        
        
        if 'SCD' in device_list:
            try:
                if scd.data_available == 1:
                    device_dict['SCD']['CO2'].append(scd.CO2)
                    device_dict['SCD']['RH'].append(scd.relative_humidity)
                    device_dict['SCD']['Temp'].append(scd.temperature)
            except:
                Exception

        if 'Purpleair' in device_list:
            device_dict['Purpleair']['Current'].append(purple_air.current)
            device_dict['Purpleair']['Power'].append(purple_air.power)
            device_dict['Purpleair']['Voltage'].append(purple_air.bus_voltage)

        if 'WIFI' in device_list:
            device_dict['WIFI']['Current'].append(wifi.current)
            device_dict['WIFI']['Power'].append(wifi.power)
            device_dict['WIFI']['Voltage'].append(wifi.bus_voltage)

        if 'RPI' in device_list:
            device_dict['RPI']['Current'].append(rpi.current)
            device_dict['RPI']['Power'].append(rpi.power)
            device_dict['RPI']['Voltage'].append(rpi.bus_voltage)

        if 'Comms' in device_list:
            device_dict['Comms']['Current'].append(comms.current)
            device_dict['Comms']['Power'].append(comms.power)
            device_dict['Comms']['Voltage'].append(comms.bus_voltage)

        if 'Fans' in device_list:
            device_dict['Fans']['Current'].append(fans.current)
            device_dict['Fans']['Power'].append(fans.power)
            device_dict['Fans']['Voltage'].append(fans.bus_voltage)
        
        if 'MCP' in device_list:
            device_dict['MCP']['Temp'].append(mcp.temperature)

        if 'BME' in device_list:
            device_dict['BME']['Gas'].append(bme.gas)
            device_dict['BME']['RH'].append(bme.humidity)
            device_dict['BME']['Pressure'].append(bme.pressure)
            device_dict['BME']['Temp'].append(bme.temperature)


        # the above portion takes ~.5 seconds to run. To make sure we get close to the desired n_points*wait_time
        # averaging time, we need to subtract how long this portion of code takes to run from the input wait_time.
        #time.sleep(wait_time)
        end = datetime.now()
        diff = end - start
        new_wait = (timedelta(seconds=wait_time) - diff)
        if new_wait.total_seconds() > wait_time:
            new_wait = timedelta(seconds=wait_time) 
        wait_avg += new_wait.total_seconds()
        time.sleep(new_wait.total_seconds())
        i += 1

    end_time = datetime.now().strftime('%m/%d/%Y %H:%M:%S')
    print('Start: {}\nEnd: {}\nWait Average: {}\ni: {}'.format(start_time, end_time, wait_avg/i, i))

    return device_dict


def get_averages(data_dict):
    '''
    Average each list in data_dict. Create a new dictionary that has the same keys as data_dict but each key has only one
    float value rather than a list. This is the dictionary that will be converted to csv and then sent from the raspberry
    pi to the linux box where plotting occurs.

    input param: data_dict, nested dictionary of data values
    input type: dictionary

    output param: avg_dict, nested dictionary of averaged data values from data_dict
    output type: dictionary
    '''

    avg_dict = {}

    for device in data_dict.keys():
        if device is 'Time':
            # the start time of the data acquisition is not averaged since there's only one point and it's a datetime string.
            avg_dict[device] = data_dict[device]
        else:
            #everything else is averaged
            avg_dict[device] = {}
            for param in data_dict[device].keys():
                avg_dict[device][param] =  sum(data_dict[device][param])/len(data_dict[device][param])
        

    return avg_dict


def print_avg_data(avg_data_dict):
    '''
    Print the average data dictionary to screen in an easy to read format.
    
    input param: avg_data_dict, nested dictionary of averaged data values.
    input type: dictionary
    '''

    for device in avg_data_dict.keys():
        if device is 'Time':
            print('Start Time: {}'.format(avg_data_dict[device]))
        else:
            for param in avg_data_dict[device].keys():
                #print(device, param)
                print('Device: {:<10} Data: {:<10} Value: {:<10.2f}'.format(device, param, avg_data_dict[device][param]))
    

def make_header(avg_data_dict):
    '''
    Create the header for the CSV file. Just a list of device keys plus the data parameter keys.

    
    input param: avg_data_dict, nested dictionary of averaged data values
    input type: dictionary

    output param: header, list of header values needed for the csv file
    output type: list
    '''
    
    #Time needs to be the first column of the csv
    header = ['Time']

    for device in avg_data_dict.keys():
        if device is 'Time':
            next
        else:
            for param in avg_data_dict[device].keys():
                header.append(device + ' ' + param)
    
    return header


def csv_write(avg_data_dict):
    '''
    Write the averaged data to a csv file so that it can be rsynced to the linux box

    input param: avg_data_dict, nested dictionary of averaged data values
    input type: dictionary
    '''

    data_dir = os.getcwd() + "/data/"
    file_name = data_dir + str(platform.node()) + datetime.now().strftime("%m%d%Y") + ".csv"
    csv_header = make_header(avg_data_dict)
   
    #Time needs to be the first column in the csv, this will always exist in the dictionary so I will hardcode it in

    with open(file_name, 'a+', newline = '') as f:
        
        file_writer = csv.writer(f, delimiter = ',')

        #write the rows of data if the file size is greater than 0 (AKA it doesn't exist yet). 
        #write the header and the rows of data if it is the first write
        if os.stat(file_name).st_size > 0:
            
            print("Writing Row")
            #time is the first column of the csv, this is always true
            row = [avg_data_dict['Time']]
            for device in avg_data_dict.keys():
                #skip 'Time' in loop
                if device is 'Time':
                    next
                else:
                    for param in avg_data_dict[device].keys():
                        #append data based on device and param key
                        row.append(avg_data_dict[device][param])
            file_writer.writerow(row)
        else:
            file_writer.writerow(csv_header)
            row = [avg_data_dict['Time']]
            
            for device in avg_data_dict.keys():
                #skip 'Time' in loop
                if device is 'Time':
                    next
                else:
                    for param in avg_data_dict[device].keys():
                        #append data based on device and param key
                        row.append(avg_data_dict[device][param])
            file_writer.writerow(row)

        f.close()
            
 
def print_data(tca, wait_time, n_points, n_tests):
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
    
    print("Args: ", wait_time, n_points, n_tests)
    print("Testing File Writer")
    print("Data Capture Start Time: {}".format(datetime.now().strftime("%m/%d/%Y %H:%M:%S")))
    print()
    # begin n number of test runs
    j = 0

    while j != n_tests:
        
        i=0

        while i <= n_points:

            print('Time: {:>34}\nPA Current: {:>15.2f} mA\nPA Power: {:>15.2f} W\nPA Voltage: {:>14.2f} V\nWiFi Current: {:>12.2f} mA\nWiFi Power: {:>13.2f} W\nWiFi Voltage: {:>12.2f} V\nRP Current: {:>15.2f} mA\nRP Power: {:>15.2f} W\nRP Voltage: {:>14.2f} V\nComms Current: {:>11.2f} mA\nComms Power: {:>12.2f} W\nComms Voltage: {:>10.2f} V\nTemp: {:>20.2f} C'.format(datetime.now().strftime("%m:%d:%Y %H:%M:%S"), purple_air.current, purple_air.power, purple_air.bus_voltage, wifi.current, wifi.power, wifi.bus_voltage, raspberry_pi.current, raspberry_pi.power, raspberry_pi.bus_voltage, comms.current, comms.power, comms.bus_voltage, temp.temperature))

            print()
            time.sleep(wait_time)         
            i += 1

        j += 1


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

    data_dir = os.getcwd() + "/data/"

    purple_air = adafruit_ina219.INA219(tca[0])
    raspberry_pi = adafruit_ina219.INA219(tca[7])
    wifi = adafruit_ina219.INA219(tca[4])
    comms  = adafruit_ina219.INA219(tca[3])
    temp = adafruit_mcp9808.MCP9808(tca[6])
    
    print("Args: ", wait_time, n_points, n_tests)
    print("Testing File Writer")
    print("Data Capture Start Time: {}".format(datetime.now().strftime("%m/%d/%Y %H:%M:%S")))
    # begin n number of test runs
    
    # file_name = "test_" +  datetime.now()strftime("%m%d%Y%H%M%S") + ".csv"
    header_vals = ['Time', 'PA Current', 'PA Power', 'PA Voltage', 'WIFI Current', 'WIFI Power', 'WIFI Voltage',
                    'RPi Current', 'RPi Power', 'RPi Voltage', 'Comms Current', 'Comms Power', 'Comms Voltage', 'Temp']

    #while j < n_tests:
    # we don't care about the number of tests anymore, this runs continuously and breaks tests into 1 hour chunks.
    while j != n_tests:       
        
        start_time = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        file_name = data_dir + str(platform.node()) + datetime.now().strftime("%m%d%Y%H%M%S") + ".csv"

        print("Run Start Time: {}".format(start_time))
        print("Test run {} of {}".format(str(j+1), str(n_tests)))
        
        # r = 0 # used for debugging
        i = 0
        
        with open(file_name, 'w', newline = '') as f:
        
            file_writer = csv.writer(f, delimiter = ',')
        
            while i <= n_points:
                
                if i == 0:
                    file_writer.writerow(header_vals)
                else:
                    row = [datetime.now().replace(microsecond=0), purple_air.current, purple_air.power, purple_air.bus_voltage,
                        wifi.current, wifi.power, wifi.bus_voltage, raspberry_pi.current, raspberry_pi.power, raspberry_pi.bus_voltage,
                        comms.current, comms.power, comms.bus_voltage, temp.temperature]
                    print(row)
                    file_writer.writerow(row)
                    time.sleep(wait_time)
                    # r += 1 # used for debugging
                i += 1
            
            j += 1
            
            f.close()
            # print("Time: {} File Closing: {} N Rows: {}".format(datetime.now().strftime("%m/%d/%Y %H:%M:%S"), file_name, r)) # used for debugging

'''
if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument("-w", "--wait_time", type=int, help = "capture data points every wait_time seconds, i.e time resolution of data. Default is 1 second.", default=1)
    parser.add_argument("-p", "--n_points", type=int, help = "Number of data points to capture. Ex.) n_points = 60, --wait_time = 1 is a data point every second for one minute. Default is 600, or 10 minutes with default wait_time of 1 second.", default=600)
    parser.add_argument("-t", "--n_tests", type=int,  help = "Number of tests to run, break up n_points into n_test chunks. Ex.) --n_tests = 3. --n_points = 60, --wait_time = 1 will give 3 separate tests of data points every second for 60 seconds. If no parameter is give, an indefinite number of tests will be run. ", default=-1)
    parser.add_argument("-c", "--channels", type=list, help="List of channels to enable on mux board, default=all, Ex.) [0, 3] enables channels 0 and 3", default=[0, 1, 2, 3, 4, 5, 6, 7])
    parser.add_argument("-test", "--testing", type=str, help="Is this run for testing or for true data collection? Yes or No?", default="No")
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
        file_write(pa_mux, tca_board, args.channels, args.wait_time, args.n_points, args.n_tests)
    else:
        print_data(tca_board, args.wait_time, args.n_points, args.n_tests)        
    
'''


