#
# ws281x_driuer.py - standardized driver for WS281X/Neopixels
# © 2022  Dave Hocker
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# See the LICENSE file for more details.
#

from .driver_base import DriverBase
from neopixel import NeoPixel
import machine

class WS281XDriver(DriverBase):
    def __init__(self):
        super().__init__()
        self._brightness = 1.0
        self._order = "RGB"

    @property
    def name(self):
        return "WS281X/Neopixel"


    @property
    def Device(self):
        """
        Returns the wrapped device (a NeoPixel instance)
        """
        return self._strip

    def open(self, num_pixels, datapin=0, order="RGB"):
        """
        Open/create the wrapped driver
        :param num_pixels: Number of pixels in string
        :param datapin: The GPIO pin number that will drive the LED string
        :param order: The order of colors sent to a pixel
        :return:
        """
        self._numpixels = num_pixels
        self._order = order

        # 3 bytes/pixel at 800 Khz
        self._strip = NeoPixel(machine.Pin(datapin), num_pixels, bpp=3, timing=1)
        return self._begin()

    def _begin(self):
        return True

    def show(self):
        """
        Send all pixels to the string
        :return:
        """
        self._strip.write()
        return True

    @property
    def numPixels(self):
        """
        Returns the number of pixels in the string
        :return:
        """
        return self._numpixels

    def setBrightness(self, brightness):
        """
        Set the relative brightness for the entire string
        :param brightness: 0-255
        :return:
        """
        self._brightness = brightness
        return True

    def setPixelColor(self, index, color_value):
        """
        Set an individual pixel's color
        :param index: 0 <= index < num_pixels
        :param color_value: 0xrrggbb
        :return: None
        """
        # Apply brightness factor here
        # print(f"{color_value}={hex(color_value)}")
        r = (color_value >> 16) & 0xFF
        g = (color_value >> 8) & 0xFF
        b = color_value & 0xFF
        r = int((r * self._brightness) / 255)
        g = int((g * self._brightness) / 255)
        b = int((b * self._brightness) / 255)
        self._strip[index] = (r, g, b)
        return True

    def clear(self):
        """
        Clear all pixels
        :return:
        """
        for i in range(self._numpixels):
            self._strip[i] = (0, 0, 0)
        self._strip.write()
        return True


    def close(self):
        """
        Close and release the current device.
        :return: None
        """
        del self._strip
        self._strip = None
        return True
