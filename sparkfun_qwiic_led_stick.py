# based on Sparkfun's python library
#-----------------------------------------------------------------------------
# qwiic_led_stick.py
#
# Python library for the SparkFun Qwiic LED Stick - APA102C.
#   https://www.sparkfun.com/products/18354
#
#------------------------------------------------------------------------
#
# Written by Priyanka Makin @ SparkFun Electronics, June 2021
# 
# This python library supports the SparkFun Electroncis qwiic 
# qwiic sensor/board ecosystem
#
# More information on qwiic is at https:// www.sparkfun.com/qwiic
#
# Do you like this library? Help support SparkFun. Buy a board!
#==================================================================================
# Copyright (c) 2020 SparkFun Electronics
#
# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the "Software"), to deal 
# in the Software without restriction, including without limitation the rights 
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all 
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
# SOFTWARE.
#==================================================================================

"""
qwiic_led_stick
===============
Python module for the SparkFun Qwiic LED Stick - APA102C.

This package is a port of the existing [SparkFun Qwiic LED Stick Arduino Library](https://github.com/sparkfun/SparkFun_Qwiic_LED_Stick_Arduino_Library).

This package can be used in conjunction with the overall [SparkFun Qwiic Python Package](https://github.com/sparkfun/Qwiic_Py).

New to qwiic? Take a look at the entire [SparkFun Qwiic Ecoststem](https://www.sparkfun.com/qwiic).
"""
# ---------------------------------------------------------------------------------

import math
import time
from micropython import const
from adafruit_bus_device.i2c_device import I2CDevice
from adafruit_pixelbuf import PixelBuf

RETRIES = 4
_DEFAULT_ADDRESS = const(0x23)

# Qwiic LED Stick commands
COMMAND_CHANGE_ADDRESS = 0xC7
COMMAND_CHANGE_LED_LENGTH = 0x70
COMMAND_WRITE_SINGLE_LED_COLOR = 0x71
COMMAND_WRITE_ALL_LED_COLOR = 0x72
COMMAND_WRITE_RED_ARRAY = 0x73
COMMAND_WRITE_GREEN_ARRAY = 0x74
COMMAND_WRITE_BLUE_ARRAY = 0x75
COMMAND_WRITE_SINGLE_LED_BRIGHTNESS = 0x76
COMMAND_WRITE_ALL_LED_BRIGHTNESS = 0x77
COMMAND_WRITE_ALL_LED_OFF = 0x78


class QwiicLEDStick(PixelBuf):
    """
    QwiicLEDStick

    :param i2c: An existing i2c driver object.
    :param address: The I2C address to use for the device.
    :return: The GPIO device object.
    :rtype: Object
    """

    def __init__(self, i2c, address=_DEFAULT_ADDRESS, num_pixels=10, brightness=1.0, auto_write=True):
        # Did the user specify an I2C address?
        self.i2c = i2c
        self.device = I2CDevice(i2c, address)
        self.num_pixels = num_pixels
        self.retries = 0
        super().__init__(
            num_pixels, byteorder="RGB", brightness=brightness, auto_write=auto_write
        )

    def _transmit(self, buffer: bytearray) -> None:
        """Update the pixels"""
        for pos in range(self.num_pixels):
            self.set_led(pos, buffer[3 * pos:3 * (pos + 1)])

    def _write(self, data):
        """Write data with retries"""
        with self.device as bus:
            for i in range(RETRIES):
                try:
                    bus.write(data)
                    break
                except OSError:
                    time.sleep(0.001)
                    self.retries += 1

    @staticmethod
    def color_bytes(color):
        """Convert multiple color formats into 3 bytes"""
        if isinstance(color, (tuple, list, bytes, bytearray)) and len(color) == 3:
            return bytes(color)
        elif isinstance(color, int):
            return color.to_bytes(3, "big")
        raise ValueError("color must be an int or (r,g,b) tuple")

    def set_led(self, number, color):
        """
        Change the color of a specific LED.

        :param number: the number of LED. Indexing starts at 1.
        :param color: the color is a (r,g,b) tuple or 0xRRGGBB int.
        """
        if number not in range(self.num_pixels):
            raise ValueError(f"pixel position must be one of 0-{self.num_pixels - 1}")

        color = self.color_bytes(color)
        data = bytes([COMMAND_WRITE_SINGLE_LED_COLOR, number]) + color
        self._write(data)
        # return self._i2c.writeBlock(self.address, self.COMMAND_WRITE_SINGLE_LED_COLOR, data)

    def optimized_fill(self, color):
        """
        Set the color of all LEDs in the string. Each will be shining the same color.

        :param color: the color is a (r,g,b) tuple or 0xRRGGBB int.
        """
        color = bytes([int(cc * self.brightness) for cc in self.color_bytes(color)])
        data = bytes([COMMAND_WRITE_ALL_LED_COLOR]) + color
        self._write(data)
        # return self._i2c.writeBlock(self.address, self.COMMAND_WRITE_ALL_LED_COLOR, data_list)

    def set_led_brightness(self, number, brightness):
        """
            Change the brightness of a specific LED while keeping their current color.
            To turn LEDs off but remember their previous color, set brightness to 0.

            :param number: number of LED to change brightness. LEDs indexed starting at 1.
            :param brightness: value of LED brightness between 0 and 31.
            :return: true if the command was sent successfully, false otherwise.
            :rtype: bool
        """
        if number not in range(self.num_pixels):
            raise ValueError(f"pixel position must be one of 0-{self.num_pixels - 1}")
        if brightness < 0 or brightness > 31:
            raise ValueError("brightness is a number between 0 and 31")

        data = bytes([COMMAND_WRITE_SINGLE_LED_BRIGHTNESS, number, brightness])
        self._write(data)
        # return self._i2c.writeBlock(self.address, self.COMMAND_WRITE_SINGLE_LED_BRIGHTNESS, data)

    def set_brightness(self, brightness):
        """
            Change the brightness of all LEDs while keeping their current color.
            To turn all LEDs off but remember their previous color, set brightness to 0

            :param brightness: value of LED brightness between 0 and 31.
            :return: true if the command was sent successfully, false otherwise.
            :rtype: bool
        """
        if number not in range(self.num_pixels):
            raise ValueError("pixel position must be one of 0-8")
        if brightness < 0 or brightness > 31:
            raise ValueError("brightness is a number between 0 and 31")

        data = bytes([COMMAND_WRITE_ALL_LED_BRIGHTNESS, brightness])
        self._write(data)
        # return self._i2c.writeByte(self.address, self.COMMAND_WRITE_ALL_LED_BRIGHTNESS, brightness)

    def off(self):
        """ 
            Turn all LEDs off by setting color to 0

            :return: true if the command was sent successfully, false otherwise.
            :rtype: bool
        """
        data = bytes([COMMAND_WRITE_ALL_LED_OFF, 0])
        self._write(data)
        # return self._i2c.writeByte(self.address, self.COMMAND_WRITE_ALL_LED_OFF, 0)

    def change_address(self, new_address):
        """
            Change the I2C address from one address to another.

            :param new_address: the new address to be set to. Must be valid.
            :return: Nothing
            :rtype: Void
        """
        # First, check if the specified address is valid
        if new_address < 0x08 or new_address > 0x77:
            return False

        data = bytes([COMMAND_CHANGE_ADDRESS, new_address])
        self._write(data)
        self.device = I2CDevice(self.i2c, new_address)
        # self._i2c.writeByte(self.address, self.COMMAND_CHANGE_ADDRESS, new_address)
