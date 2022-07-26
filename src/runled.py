#
# runled.py - run the Pico's onboard LED
# © 2022 by Dave Hocker
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# See the LICENSE file for more details.
#


from machine import Pin, PWM
import time
import mp_logging as logging


logger = logging.getLogger("led")


def _pwm_value_from_percent(p):
    """
    Convert a percent value to a PWM value
    :param p: An int or float value in the range 0-100
    :return: An integer PWM value in the range 0-65535
    """
    p = float(p)
    if p > 100.0:
        p = 100.0
    elif p < 0.0:
        p = 0.0
    pwm_value = p * 655.35
    return int(pwm_value)


def run_led(led_pin=25):
    """
    Use PWM on an LED
    :param led_pin: The GPIO pin where the LED is connected
    :return:
    """
    logger.info("Running LED using PWM...")
    pwm_led = None
    try:
        pwm_led = PWM(Pin(led_pin, Pin.OUT))
        pwm_led.freq(1000)

        for i in range(5):
            # Brighter
            for b in range(10, 100, 5):
                pwm_value = _pwm_value_from_percent(b)
                # print(b, pwm_value)
                pwm_led.duty_u16(pwm_value)
                time.sleep(0.1)
            # Dimmer
            # For unknown reasons the value 65535 produces the same result as the value 0
            for c in range(100, 0, -5):
                pwm_value = _pwm_value_from_percent(c)
                # print(c, pwm_value)
                pwm_led.duty_u16(pwm_value)
                time.sleep(0.1)
    except KeyboardInterrupt:
        logger.info("ctrl-c pressed")
    except Exception as ex:
        logger.error("Unhandled exception")
        logger.error(str(ex))

    if pwm_led is not None:
        pwm_led.duty_u16(0)
        logger.info("LED turned off")
