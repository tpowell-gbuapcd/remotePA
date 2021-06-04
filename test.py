import qwiic
import time
import board
import busio
import adafruit_tca9548a
import adafruit_ina219

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
i2c = board.I2C()

tca = adafruit_tca9548a.TCA9548A(i2c)

# the channels numbers are subject to change. 
# current empty channels will be filled with LCDs later
purple_air = adafruit_ina219.INA219(tca[0])
raspberry_pi = adafruit_ina219.INA219(tca[3])
WiFi = adafruit_ina219.INA219(tca[4])
comms  = adafruit_ina219.INA219(tca[7])

#print(datetime.now().strftime("%m/%d/%Y %H:%M:%S"))

i = 0
while i < 1:
    print("PurpleAir Voltage:      {:.2f}V, PurpleAir Current:      {:.2f}mA".format(purple_air.bus_voltage, purple_air.current))
    print()
    print("Raspberry Pi Voltage:   {:.2f}V, Raspberry Pi Current:   {:.2f}mA".format(raspberry_pi.bus_voltage, raspberry_pi.current))
    print()
    print("WiFi Voltage:           {:.2f}V, WiFi Current:           {:.2f}mA".format(WiFi.bus_voltage, WiFi.current))
    print()
    print("Communications Voltage: {:.2f}V, Communications Current: {:.2f}mA".format(comms.bus_voltage, comms.current))
    print()

    total_current = purple_air.current + raspberry_pi.current + WiFi.current + comms.current
    print("Total Current Draw:     {:.2f}mA".format(total_current))
    print()
    
    time.sleep(1)
    i += 1
