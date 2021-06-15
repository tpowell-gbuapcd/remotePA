import qwiic
import time
import board
import busio
import adafruit_tca9548a
import adafruit_ina219
import adafruit_ssd1306

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

test.enable_channels([0, 1, 2, 3, 4, 5, 6, 7])

time.sleep(1)

print("Channels:")
print()

test.list_channels()

print("Test adafruit package")
print()

i2c = board.I2C()
#i2c =  busio.I2C(board.SCL, board.SDA)

tca = adafruit_tca9548a.TCA9548A(i2c) 

# the channels numbers are subject to change. 
# current empty channels will be filled with LCDs later
purple_air = adafruit_ina219.INA219(tca[0])
raspberry_pi = adafruit_ina219.INA219(tca[7])
WiFi = adafruit_ina219.INA219(tca[4])
comms = adafruit_ina219.INA219(tca[3])


WIDTH = 128
HEIGHT = 32 

purple_air_oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, tca[0])
rpi_oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, tca[7]) 
wifi_oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, tca[4])
comms_oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, tca[3])

# CLEAR THE LCD OF ANY ARTIFACTS
purple_air_oled.fill(0)
purple_air_oled.show()

rpi_oled.fill(0)
rpi_oled.show()

wifi_oled.fill(0)
wifi_oled.show()

comms_oled.fill(0)
comms_oled.show()

i = 0

while i < 20:

    # CURRENT
    # CREATE IMAGE FOR DRAWING
    purple_image = Image.new('1', (WIDTH, HEIGHT))
    rpi_image = Image.new('1', (WIDTH, HEIGHT))
    wifi_image = Image.new('1', (WIDTH, HEIGHT))
    comms_image = Image.new('1', (WIDTH, HEIGHT))

    # CREATE DRAWING OBJECT
    purple_draw = ImageDraw.Draw(purple_image)
    rpi_draw = ImageDraw.Draw(rpi_image)
    wifi_draw = ImageDraw.Draw(wifi_image)
    comms_draw = ImageDraw.Draw(comms_image)

    # SET THE FONT FOR THE LEXT ON OLEDS
    purple_font= ImageFont.load_default()
    rpi_font = ImageFont.load_default()
    wifi_font = ImageFont.load_default()
    comms_font = ImageFont.load_default()

    # SET THE TEXT FOR OLEDS
    purple_text = "PurpleAir\nI = {:.2f}mA\nP = {:.2f}W".format(purple_air.current, purple_air.power)
    rpi_text = "Raspberry Pi\nI = {:.2f}mA\nP = {:.2f}W".format(raspberry_pi.current, raspberry_pi.power)
    wifi_text = "WiFi AP\nI = {:.2f}mA\nP = {:.2f}W".format(WiFi.current, WiFi.power)
    comms_text = "Comms\nI = {:.2f}mA\nP = {:.2f}W".format(comms.current, comms.power)

    (purple_font_width, purple_font_height) = purple_font.getsize(purple_text)
    (rpi_font_width, rpi_font_height) = rpi_font.getsize(rpi_text)
    (wifi_font_width, wifi_font_height) = wifi_font.getsize(wifi_text)
    (comms_font_width, comms_font_height) = comms_font.getsize(comms_text)

    # DRAW THE TEXT AND POSITION IT IN THE UPPER LEFT
    purple_draw.text((0, 0, WIDTH, HEIGHT), purple_text, font=purple_font, fill=255)
    rpi_draw.text((0, 0, WIDTH, HEIGHT), rpi_text, font=rpi_font, fill=255)
    wifi_draw.text((0, 0, WIDTH, HEIGHT), wifi_text, font=wifi_font, fill=255)
    comms_draw.text((0, 0, WIDTH, HEIGHT), comms_text, font=comms_font, fill=255)

    # DISPLAY THE IMAGE ON THE OLED
    purple_air_oled.image(purple_image)
    purple_air_oled.show()

    rpi_oled.image(rpi_image)
    rpi_oled.show()

    wifi_oled.image(wifi_image)
    wifi_oled.show()

    comms_oled.image(comms_image)
    comms_oled.show()

    time.sleep(1)
    
    # POWER DISPLAY
    purple_image = Image.new('1', (WIDTH, HEIGHT))
    rpi_image = Image.new('1', (WIDTH, HEIGHT))
    wifi_image = Image.new('1', (WIDTH, HEIGHT))
    comms_image = Image.new('1', (WIDTH, HEIGHT))

    # CREATE DRAWING OBJECT
    purple_draw = ImageDraw.Draw(purple_image)
    rpi_draw = ImageDraw.Draw(rpi_image)
    wifi_draw = ImageDraw.Draw(wifi_image)
    comms_draw = ImageDraw.Draw(comms_image)

    # SET THE FONT FOR THE LEXT ON OLEDS
    purple_font= ImageFont.load_default()
    rpi_font = ImageFont.load_default()
    wifi_font = ImageFont.load_default()
    comms_font = ImageFont.load_default()

    # SET THE TEXT FOR OLEDS
    purple_text = "PurpleAir\nP = {:.2f}W".format(purple_air.power)
    rpi_text = "Raspberry Pi\nP = {:.2f}W".format(raspberry_pi.power)
    wifi_text = "WiFi AP\nP = {:.2f}W".format(WiFi.power)
    comms_text = "Comms\nP = {:.2f}W".format(comms.power)

    (purple_font_width, purple_font_height) = purple_font.getsize(purple_text)
    (rpi_font_width, rpi_font_height) = rpi_font.getsize(rpi_text)
    (wifi_font_width, wifi_font_height) = wifi_font.getsize(wifi_text)
    (comms_font_width, comms_font_height) = comms_font.getsize(comms_text)

    # DRAW THE TEXT AND POSITION IT IN THE UPPER LEFT
    purple_draw.text((0, 0, WIDTH, HEIGHT), purple_text, font=purple_font, fill=255)
    rpi_draw.text((0, 0, WIDTH, HEIGHT), rpi_text, font=rpi_font, fill=255)
    wifi_draw.text((0, 0, WIDTH, HEIGHT), wifi_text, font=wifi_font, fill=255)
    comms_draw.text((0, 0, WIDTH, HEIGHT), comms_text, font=comms_font, fill=255)

    # DISPLAY THE IMAGE ON THE OLED
    purple_air_oled.image(purple_image)
    rpi_oled.image(rpi_image)
    wifi_oled.image(wifi_image)
    comms_oled.image(comms_image)
    
    rpi_oled.show()
    purple_air_oled.show()
    wifi_oled.show()
    comms_oled.show()
    
    time.sleep(1)
    i += 1

purple_air_oled.fill(0)
purple_air_oled.show()

rpi_oled.fill(0)
rpi_oled.show()

wifi_oled.fill(0)
wifi_oled.show()

comms_oled.fill(0)
comms_oled.show()


#print(datetime.now().strftime("%m/%d/%Y %H:%M:%S"))

'''
import numpy as np

pa_current = np.zeros(0)
wifi_current = np.zeros(0)
rpi_current = np.zeros(0)
comms_current = np.zeros(0)

i = 0
while i < 10:

    pa_current = np.append(pa_current, purple_air.current)
    wifi_current = np.append(wifi_current, WiFi.current)
    rpi_current = np.append(rpi_current, raspberry_pi.current)
    comms_current = np.append(comms_current, comms.current)
   
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
    
    print(pa_current, i)
   
    time.sleep(1)
    i += 1


import matplotlib.pyplot as plt

plt.plot(i, pa_current, label = "PurpleAir")
plt.plot(i, wifi_current, label = "WiFi")
plt.plot(i, rpi_current, label = "Pi")
plt.plot(i, comms_current, label = "Comms")
purple_air_oled = adafruit_ssd1306.SSD1306(WIDTH, HEIGHT, tca[0])
plt.xlabel("Seconds")
plt.ylabel("mA")
plt.savefig("current_test.png")
'''
