#
# na_rgb_led_string.py - a non-addressable RGB LED string
# © 2022 by Dave Hocker
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# See the LICENSE file for more details.
#


from machine import Pin, PWM


class NaRGBLEDString():
    def __init__(self, red_pin=15, green_pin=14, blue_pin=13, pwm_freq=1000):
        """
        Initialize string instance
        :param red_pin: GPIO pin
        :param green_pin: GPIO pin
        :param blue_pin: GPIO pin
        :param pwm_freq: pulse frequency
        :param pwm_duty: duty as a percent 0-100
        """
        self.red_gpio_pin = red_pin
        self.green_gpio_pin = green_pin
        self.blue_gpio_pin = blue_pin

        self.pwm_freq = pwm_freq

        self.pwm_red_led = None
        self.pwm_green_led = None
        self.pwm_blue_led = None

    def open(self):
        """
        Initialize the string for operation
        :return:
        """
        self.pwm_red_led = PWM(Pin(self.red_gpio_pin, Pin.OUT))
        self.pwm_red_led.freq(self.pwm_freq)

        self.pwm_green_led = PWM(Pin(self.green_gpio_pin, Pin.OUT))
        self.pwm_green_led.freq(self.pwm_freq)

        self.pwm_blue_led = PWM(Pin(self.blue_gpio_pin, Pin.OUT))
        self.pwm_blue_led.freq(self.pwm_freq)

    def close(self):
        """
        Shutdown the LED string
        :return:
        """
        # For unknown reasons, this does not always work. It's supposed
        # disable PWM output. Sometimes it does, and sometimes it doesn't.
        # self.pwm_red_led.deinit()
        # self.pwm_green_led.deinit()
        # self.pwm_blue_led.deinit()

        if self.pwm_red_led is not None:
            # Instead, just set the color to zero
            self.set_color(0, 0, 0)

            self.pwm_red_led = None
            self.pwm_green_led = None
            self.pwm_blue_led = None

    def set_color(self, red, green, blue):
        """
        Set the string color with an RGB value. In reality, this sets
        the duty cycle of the PWM thus controlling the brightness of each LED.
        :param red: 0-255
        :param green: 0-255
        :param blue: 0-255
        :return: None
        """
        pwm_red_value = NaRGBLEDString._pwm_value_from_rgb(red)
        pwm_green_value = NaRGBLEDString._pwm_value_from_rgb(green)
        pwm_blue_value = NaRGBLEDString._pwm_value_from_rgb(blue)
        self.pwm_red_led.duty_u16(pwm_red_value)
        self.pwm_green_led.duty_u16(pwm_green_value)
        self.pwm_blue_led.duty_u16(pwm_blue_value)

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
