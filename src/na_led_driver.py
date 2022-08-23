#
# na_led_driver.py - LED interface driver for non-addressable LED strings
# © 2022 Dave Hocker
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
import mp_logging as logging
from machine import Pin, PWM

#
# LED interface driver for non-addressable LED strings (4 wire type)
#


logger = logging.getLogger("led")


class MPNALEDString(DriverBase):
    """
    A device driver must implement each of the methods in the DriverBase class.
    The driver class name is arbitrary and generally is not exposed.
    """

    def __init__(self):
        super().__init__()
        # Treat the string like it had only one pixel
        self._num_pixels = 1
        # Default GPIO pins overridden during open
        self._red_gpio_pin = 15
        self._green_gpio_pin = 14
        self._blue_gpio_pin = 13
        self._pwm_freq = 0

        # PWM instances for each color
        self._pwm_red_led = None
        self._pwm_green_led = None
        self._pwm_blue_led = None

        # The one and only pixel
        self._na_pixels = [(0, 0, 0)]
        self._brightness = 0

    @property
    def name(self):
        """
        Human-readable name of driver
        :return:
        """
        return "MPNALEDString"

    def open(self, red_pin=15, green_pin=14, blue_pin=13, pwm_freq=1000):
        """
        Open driver for a given set of GPIO pins
        :param red_pin: GPIO pin
        :param green_pin: GPIO pin
        :param blue_pin: GPIO pin
        :param pwm_freq: pulse frequency
        """
        self._red_gpio_pin = red_pin
        self._green_gpio_pin = green_pin
        self._blue_gpio_pin = blue_pin

        self._pwm_freq = pwm_freq

        self._pwm_red_led = PWM(Pin(self._red_gpio_pin, Pin.OUT))
        self._pwm_red_led.freq(self._pwm_freq)

        self._pwm_green_led = PWM(Pin(self._green_gpio_pin, Pin.OUT))
        self._pwm_green_led.freq(self._pwm_freq)

        self._pwm_blue_led = PWM(Pin(self._blue_gpio_pin, Pin.OUT))
        self._pwm_blue_led.freq(self._pwm_freq)

        return self._begin()

    def _begin(self):
        return True

    def show(self):
        """
        Set the red, green and blue lines based on the one and only pixel
        :return:
        """
        # Scale colors according to brightness
        red = self._na_pixels[0][0] * self._brightness
        green = self._na_pixels[0][1] * self._brightness
        blue = self._na_pixels[0][2] * self._brightness

        pwm_red_value = MPNALEDString._pwm_value_from_rgb(red)
        pwm_green_value = MPNALEDString._pwm_value_from_rgb(green)
        pwm_blue_value = MPNALEDString._pwm_value_from_rgb(blue)

        self._pwm_red_led.duty_u16(pwm_red_value)
        self._pwm_green_led.duty_u16(pwm_green_value)
        self._pwm_blue_led.duty_u16(pwm_blue_value)

        return True

    @property
    def numPixels(self):
        """
        Returns the number of pixels in the string (always 1)
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
        self._brightness = float(brightness) / 255.0
        logger.debug(f"Brightness: {self._brightness}")
        return True

    def setPixelColor(self, index, color_value):
        """
        Set the single pixel's color
        :param index: ignored, should be 0
        :param color_value: 0xrrggbb
        :return:
        """
        # Need to convert 0xrrggbb to (r,g,b)
        r = (color_value >> 16) & 0xFF
        g = (color_value >> 8) & 0xFF
        b = color_value & 0xFF
        # This is here in case deep debugging is required. It is really slow.
        # logger.debug(f"index: {index} rgb: {r} {g} {b}")
        # Set the single pixel's color
        self._na_pixels[0] = (r, g, b)
        return True

    def clear(self):
        """
        Clear (turn off) all pixels in the string
        :return:
        """
        # Yes, there's only one effective pixel
        for i in range(self._numpixels):
            self.setPixelColor(i, 0)
        self.show()
        return True

    def close(self):
        """
        Close and release the current device.
        :return: None
        """
        # For unknown reasons, this does not always work. It's supposed
        # disable PWM output. Sometimes it does, and sometimes it doesn't.
        # self.pwm_red_led.deinit()
        # self.pwm_green_led.deinit()
        # self.pwm_blue_led.deinit()

        if self._pwm_red_led is not None:
            # Instead, just set the color to zero
            self.setPixelColor(0, 0x000000)
            self.show()

            self._pwm_red_led = None
            self._pwm_green_led = None
            self._pwm_blue_led = None

        return True

    @staticmethod
    def _pwm_value_from_rgb(rgb):
        """
        Convert an RGB value to a PWM value. Effectively, this is
        the duty cycle
        :param rgb: a value in the range 0-255. This becomes the duty cycle.
        :return: PWM duty cycle value 0-65535
        """
        p = float(rgb)
        if p > 255.0:
            p = 255.0
        elif p < 0.0:
            p = 0.0
        pwm_value = (p / 255.0) * 65535.0
        return int(pwm_value)

    def color(self, r, g, b, gamma=False):
        """
        Returns an RGB color in the format 0xRRGGBB
        :param r: Red value 0-255
        :param g: Green value 0-255
        :param b: Blue value 0-255
        :param gamma:
        :return: 24-bit color value 0xRRGGBB
        """
        if gamma:
            return (DriverBase._gamma8[r] << 16) | (DriverBase._gamma8[g] << 8) | DriverBase._gamma8[b]
        return (r << 16) | (g << 8) | b
