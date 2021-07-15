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


def dict_init(points):
    '''
    Initialize the dictionary containing all of the arrays for storing data from I2C devices
    
    input param: points, the number of data points to be stored for a given test run. User input (will probably be hardcoded into cronjob at some point)
    input type: int

    input param: tests. the number of tests being run
    input type: int
    
    output param: new_dict, dictionary containing arrays for all of the (as of 6/15/2021) data we would like to monitor
        arrays are 3 dimensional [current, power, voltage]
    output type: dictionary
    '''

    new_dict = {}
    
    new_dict["time"] = np.zeros(points)
    new_dict["purpleair"] = np.zeros((3, points))
    new_dict["wifi"] = np.zeros((3, points))
    new_dict["rpi"] = np.zeros((3, points))
    new_dict["comms"] = np.zeros((3, points))
    new_dict["duration"] = np.zeros(points)
    new_dict["total_i"] = np.zeros(points)
    new_dict["total_p"] = np.zeros(points)

    return new_dict


def avg_dict_init(tests):
    '''
    ###
    NOT SURE IF THIS IS NEEDED NOW, BUT MAY COME IN HANDY IN THE FUTURE
    ###
    Initialize dictionary of average values for I2C devices

    input param: tests, the number of tests runs. User input (will probably be hardcoded into cron job at some point)
    input type: int

    output param: new_dict, dictionary of arrays for average values
    output type: dictionary
    '''

    new_dict = {}

    new_dict["avg_voltage"] = np.zeros((4, tests)) # new_dict["avg_voltage"][device, test_run]
    new_dict["averages"] = np.zeros(2) # just power and current

    return new_dict


def file_write(mux, tca, pa_channel, wait_time, n_points, n_tests):
    '''
    Write the data from the IN219s to file for export

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

    while j < n_tests:
            
        start_time = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        file_name = data_dir + "test_" + str(j) + "_" + datetime.now().strftime("%m%d%Y%H%M%S") + ".csv"

        print("Run Start Time: {}".format(start_time))
        print("Test run {} of {}".format(str(j+1), str(n_tests)))

        # begin new test run
        # reinitialize arrays to zero for appending
        # probably write a write_csv file too, to save test runs in text format
        i = 0
         
        with open(file_name, 'w', newline = '') as f:
        
            file_writer = csv.writer(f, delimiter = ',')
        
            while i < n_points:
                
                #file_writer = csv.writer(f, delimiter = ',')
        
                if i == 0:
                    file_writer.writerow(header_vals)

                row = [datetime.now().strftime("%m/%d/%Y %H:%M:%S"), purple_air.current, purple_air.power, purple_air.bus_voltage,
                        wifi.current, wifi.power, wifi.bus_voltage, raspberry_pi.current, raspberry_pi.power, raspberry_pi.bus_voltage,
                        comms.current, comms.power, comms.bus_voltage]

                file_writer.writerow(row)
                time.sleep(wait_time)

                i += 1
            
            j += 1
            
            f.close()


def time_test(pa_channel, wait_time, n_points, n_tests):
    '''
    Test the collection of data from the IN219s. 

    input param: pa_channel, list of channels to enable (default = all)
    input param: wait_time, capture data points every wait_time seconds
    input param: n_points, number of data points to capture
    input param: n_test, number of separate tests for data capture
    input param: data_dict, dictionary containing all of the arrays needed to store data from I2C devices
    
    output param: data_dict, dictionary with all the data from the run
    output param: avg_dict, dictionary with the averages of the data from the run 
    '''

    pa_mux, tca_board = mux_init()
    channel_enable(pa_mux, pa_channel)
    channel_status(pa_mux)
    j = 0

    total_current = 0
    total_power = 0

    # the channels numbers are subject to change, not sure if I can detect what device is at each channel
    # these may just need to stay hardcoded and the hardware will need to remain the same from unit to unit
    purple_air = adafruit_ina219.INA219(tca_board[0])
    raspberry_pi = adafruit_ina219.INA219(tca_board[7])
    wifi = adafruit_ina219.INA219(tca_board[4])
    comms  = adafruit_ina219.INA219(tca_board[3])

    avg_dict = avg_dict_init(n_tests)
     
    print("Args: ", wait_time, n_points, n_tests)
    print("Data Capture Start Time: {}".format(datetime.now().strftime("%m/%d/%Y %H:%M:%S")))
    # begin n number of test runs
    
    while j < n_tests:
        
        start_time = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        file_start_time = datetime.now().strftime("%m%d%Y%H%M%S")

        print("Run Start Time: {}".format(start_time))
        print("Test run {} of {}".format(str(j+1), str(n_tests)))

        # begin new test run
        # reinitialize arrays to zero for appending
        # probably write a write_csv file too, to save test runs in text format
        i = 0
        total_current = 0
        total_power = 0

        data_dict = dict_init(n_points)

        while i < n_points:
            
            data_dict["time"][i] = datetime.now().strftime("%m/%d/%Y %H:%M%S")

            data_dict["purpleair"][0][i] = purple_air.current
            data_dict["purpleair"][1][i] = purple_air.power
            data_dict["purpleair"][2][i] = purple_air.bus_voltage

            data_dict["wifi"][0][i] = wifi.current
            data_dict["wifi"][1][i] = wifi.power
            data_dict["wifi"][2][i] = wifi.bus_voltage

            data_dict["rpi"][0][i] = raspberry_pi.current
            data_dict["rpi"][1][i] = raspberry_pi.power
            data_dict["rpi"][2][i] = raspberry_pi.bus_voltage

            data_dict["comms"][0][i] = comms.current
            data_dict["comms"][1][i] = comms.power
            data_dict["comms"][2][i] = comms.bus_voltage 
            
            data_dict["duration"][i] = i 
            
            data_dict["total_i"][i] = purple_air.current + wifi.current + raspberry_pi.current + comms.current
            data_dict["total_p"][i] = purple_air.power + wifi.power + raspberry_pi.power + comms.power
            
            total_current += purple_air.current + wifi.current + raspberry_pi.current + comms.current
            total_power += purple_air.power + wifi.power + raspberry_pi.power + comms.power

            time.sleep(wait_time)

            i += 1

        #print("Data")
        #for key, value in data_dict.items():
        #    print(key, value)
        
        avg_dict["averages"][0] = total_current/n_points
        avg_dict["averages"][1] = total_power/n_points
        
        avg_dict["avg_voltage"][0][j] = np.average(data_dict["purpleair"][2])
        avg_dict["avg_voltage"][1][j] = np.average(data_dict["wifi"][2])
        avg_dict["avg_voltage"][2][j] = np.average(data_dict["rpi"][2])
        avg_dict["avg_voltage"][3][j] = np.average(data_dict["comms"][2])

        print("Averages: ", avg_dict)

        j += 1
        
        #csv writing function goes here

        # want specific name for each PA system for file management
        #file_name = "test_raw_" + file_start_time
        #with open(file_name, 'w', newline='') as f:
        #    if j
        #    f_writer = csv.writer(f, delimiter= ",")

        print("Run End Time: {}".format(datetime.now().strftime("%m/%d/%Y %H:%M:%S")))
    
    return data_dict, avg_dict


def make_plots(data_plot, avg_plot, test_time, run_number):
    
    props = dict(boxstyle = 'round', facecolor='wheat', alpha=0.4)
    fig, ax = plt.subplots(2,  sharex=True, figsize=(10, 10))

    ax[0].plot(data_plot["duration"], data_plot["purpleair"][0], label = "PurpleAir")
    ax[0].plot(data_plot["duration"], data_plot["wifi"][0], label = "WiFi")
    ax[0].plot(data_plot["duration"], data_plot["rpi"][0], label = "Pi")
    ax[0].plot(data_plot["duration"], data_plot["comms"][0], label = "Comms")
    ax[0].plot(data_plot["duration"], data_plot["total_i"], label = "Total")
    ax[0].set_xlabel("Seconds")
    ax[0].set_ylabel("mA")
    ax[0].legend(loc="upper left")
    ax[0].grid(True)
    ax[0].set_title(str(test_time+1) + " Second Test Run, Current")
    ax[0].text(0.70, 0.95, "Average Current: {:.2f}  mA".format(avg_plot["averages"][0]), transform=ax[0].transAxes, bbox=props)

    ax[1].plot(data_plot["duration"], data_plot["purpleair"][1], label = "PurpleAir")
    ax[1].plot(data_plot["duration"], data_plot["wifi"][1], label = "WiFi")
    ax[1].plot(data_plot["duration"], data_plot["rpi"][1], label = "Pi")
    ax[1].plot(data_plot["duration"], data_plot["comms"][1], label = "Comms")
    ax[1].plot(data_plot["duration"], data_plot["total_p"], label = "Total")
    ax[1].set_ylabel("W")
    ax[1].legend(loc="upper left")
    ax[1].grid(True)
    ax[1].set_title(str(test_time+1) + " Second Test Run, Power")
    ax[1].text(0.70, 0.95, "Average power: {:.2f} W".format(avg_plot["averages"][1]), transform=ax[1].transAxes, bbox=props)

    plt.savefig("{}_{}_second_test.png".format(run_number, test_time))
    plt.clf()



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
    
    #data_dict, avg_dict = time_test(args.channels, args.wait_time, args.n_points, args.n_tests)
    #make_plots(data_dict, avg_dict)
    


