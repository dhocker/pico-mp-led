#
# AtHomeLED - LED interface driver for APA102/dotstar strips/strings
# Copyright (C) 2016  Dave Hocker
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# See the LICENSE file for more details.
#

# The dotstar module comes from the Adafruit_DotStar_Pi repo. The original
# repo can be found at https://github.com/adafruit/Adafruit_DotStar_Pi. A fork
# of the original repo is at https://github.com/dhocker/Adafruit_DotStar_Pi
from micropython_dotstar import DotStar, RGB, RBG, GRB, GBR, BRG, BGR
from .driver_base import DriverBase
import src.mp_logging as logging

#
# LED interface driver for APA102 controlled strips and strings
# DotStar strips are a popular example
#


logger = logging.getLogger("led")


class MPDotStar(DriverBase):
    """
    A device driver must implement each of the methods in the DriverBase class.
    The driver class name is arbitrary and generally is not exposed.
    Add the driver to the app by modifying the manager.get_driver()
    method (the driver factory).
    """

    def __init__(self):
        DriverBase.__init__(self)
        self._num_pixels = 30

    @property
    def name(self):
        """
        Human-readable name of driver
        :return:
        """
        return "MPDotstarDriver"

    def open(self, spi, num_pixels, order='bgr'):
        """
        Open the device
        :param spi: SPI instance connecting the DotStar string
        :param num_pixels: Total number of pixels on the strip/string.
        :param order: The order of colors as expected by the strip/string. The default
        is bgr which is rgb backwards.
        :return: True/False
        """
        # Need to translate color order into mp_dotstar color order
        self._strip = DotStar(spi, num_pixels, pixel_order=MPDotStar._pixel_order(order))
        # print self._strip
        self._num_pixels = num_pixels
        return self._begin()

    def _begin(self):
        # The begin() method does not return a useful value
        # self._strip.begin()
        return True

    def show(self):
        """
        Send all pixels to string.
        :return:
        """
        return self._strip.show() == 0

    @property
    def numPixels(self):
        """
        Returns the number of pixels in the string
        :return:
        """
        return self._num_pixels

    def setBrightness(self, brightness):
        """
        Set brightness for entire string
        :param brightness: 0 <= brightness <= 255
        :return:
        """
        # Scale brightness to 0-1.0
        b = float(brightness) / 255.0
        self._strip.brightness = b
        logger.debug(f"Brightness: {b}")
        return True

    def setPixelColor(self, index, color_value):
        """
        Set a single pixel's color
        :param index: 0 <= n < num_pixels
        :param color_value: 0xrrggbb
        :return:
        """
        # self._strip.setPixelColor(index, color_value)
        # Need to convert 0xrrggbb to (r,g,b)
        r = (color_value >> 16) & 0xFF
        g = (color_value >> 8) & 0xFF
        b = color_value & 0xFF
        # This is here in case deep debugging is required. It is really slow.
        # logger.debug(f"index: {index} rgb: {r} {g} {b}")
        self._strip[index] = (r, g, b)
        return True

    def clear(self):
        """
        Clear (turn off) all pixels in the string
        :return:
        """
        for i in range(self._numpixels):
            self.setPixelColor(i, 0)
        self.show()
        return True

    def close(self):
        """
        Close and release the current device.
        :return: None
        """
        self._strip.deinit()
        del self._strip
        self._strip = None
        return True

    def color(self, r, g, b, gamma=False):
        """
        Create a composite RGB color value
        :param r: 0-255
        :param g: 0-255
        :param b: 0-255
        :param gamma: If True, gamma correction is applied.
        :return:
        """
        # Note that this IS NOT the same order as the DotStar
        if gamma:
            return (MPDotStar._gamma8[r] << 16) | (MPDotStar._gamma8[g] << 8) | MPDotStar._gamma8[b]
        return (r << 16) | (g << 8) | b

    @staticmethod
    def _pixel_order(order_str):
        """
        Translate an order string into a tuple used by the MP DotStar code.
        :param order_str: RGB, RBG, GRB, GBR, BRG, BGR (case insensitive)
        :return: Corresponding tuple (see micropython_dotstar)
        """
        order_str = order_str.lower()
        if order_str == "bgr":
            return BGR
        elif order_str == "brg":
            return BRG
        elif order_str == "gbr":
            return GBR
        elif order_str == "grb":
            return GRB
        elif order_str == "rbg":
            return RBG
        # Default or rgb
        return RGB
