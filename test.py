import qwiic
import time
import board
import busio
import digitalio
import displayio
import adafruit_tca9548a
import adafruit_ina219
import adafruit_ssd1306
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from datetime import datetime

'''
Test script for testing I2C INA219 boards and QWIIC MUX board
Build library for future scripts using INA219 and MUX board
'''

print("Begin I2C testing")
print()

#instantiate object to talk to MUX board
test = qwiic.QwiicTCA9548A()


def channel_status(board_name):
    '''
    Return the status of the channels on the MUX board (enabled or disabled)

    input param: board_name, object used to call the MUX board
    input type: object
    '''

    print("Channels:")
    board_name.list_channels()
    time.sleep(1)


def channel_enable(board_name, channels):
    '''
    Enable the channels on the MUX board. Default mode is off, so this will need to be called whenever the device is rebooted or after
    power off. 
    
    input param: board_name, object used to call the MUX board
    input type: object

    input param: channels, channels  to be turned on 0-7 as labled on the QWIIC MUX board 
    input type: list of int
    '''

    board_name.enable_channels(channels)
    time.sleep(1)


print("Enabling channels 0, 2, 4, and 7")

test.enable_channels([0, 3, 4, 7])

time.sleep(1)

print("Channels:")
print()

test.list_channels()

print("Test adafruit package")
print()

#i2c = board.I2C()
i2c =  busio.I2C(board.SCL, board.SDA)

tca = adafruit_tca9548a.TCA9548A(i2c) 

# the channels numbers are subject to change. 
# current empty channels will be filled with LCDs later
purple_air = adafruit_ina219.INA219(tca[0])
raspberry_pi = adafruit_ina219.INA219(tca[7])
WiFi = adafruit_ina219.INA219(tca[4])
comms  = adafruit_ina219.INA219(tca[3])

#print(datetime.now().strftime("%m/%d/%Y %H:%M:%S"))

test_time = 599
test_numbers = 10
j = 0

while j <= test_numbers:

    pa_current = np.zeros(0)
    pa_power = np.zeros(0)
    wifi_current = np.zeros(0)
    wifi_power = np.zeros(0)
    rpi_current = np.zeros(0)
    rpi_power = np.zeros(0)
    comms_current = np.zeros(0)
    comms_power = np.zeros(0)
    total_current = np.zeros(0)
    total_power = np.zeros(0)
    duration = np.zeros(0)

    i = 0

    while i <= test_time:

        pa_current = np.append(pa_current, purple_air.current)
        pa_power = np.append(pa_power, purple_air.power)
        wifi_current = np.append(wifi_current, WiFi.current)
        wifi_power = np.append(wifi_power, WiFi.power)
        rpi_current = np.append(rpi_current, raspberry_pi.current)
        rpi_power = np.append(rpi_power, raspberry_pi.power)
        comms_current = np.append(comms_current, comms.current)
        comms_power = np.append(comms_power, comms.power)
        total_current = np.append(total_current, (purple_air.current+WiFi.current+raspberry_pi.current+comms.current))
        total_power = np.append(total_power, (purple_air.power+WiFi.power+raspberry_pi.power+comms.power))
        duration = np.append(duration, i)
        
        time.sleep(1)
        i += 1


    avg_current = np.average(total_current)
    avg_power = np.average(total_power)

    props = dict(boxstyle = 'round', facecolor='wheat', alpha=0.4)
    fig, ax = plt.subplots(2,  sharex=True, figsize=(10, 10))

    ax[0].plot(duration, pa_current, label = "PurpleAir")
    ax[0].plot(duration, wifi_current, label = "WiFi")
    ax[0].plot(duration, rpi_current, label = "Pi")
    ax[0].plot(duration, comms_current, label = "Comms")
    ax[0].plot(duration, total_current, label = "Total")
    ax[0].set_xlabel("Seconds")
    ax[0].set_ylabel("mA")
    ax[0].legend(loc="upper left")
    ax[0].grid(True)
    ax[0].set_title(str(test_time+1) + " Second Test Run, Current")
    ax[0].text(0.70, 0.95, "Average Current: {:.2f}  mA".format(avg_current), transform=ax[0].transAxes, bbox=props)

    ax[1].plot(duration, pa_power, label = "PurpleAir")
    ax[1].plot(duration, wifi_power, label = "WiFi")
    ax[1].plot(duration, rpi_power, label = "Pi")
    ax[1].plot(duration, comms_power, label = "Comms")
    ax[1].plot(duration, total_power, label = "Total")
    ax[1].set_ylabel("W")
    ax[1].legend(loc="upper left")
    ax[1].grid(True)
    ax[1].set_title(str(test_time+1) + " Second Test Run, Power")
    ax[1].text(0.70, 0.95, "Average power: {:.2f} W".format(avg_power), transform=ax[1].transAxes, bbox=props)

    plt.savefig(str(test_time+1)+"_"+str(j)+"_second_test.png")

    j+=1
