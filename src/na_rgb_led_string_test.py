#
# na_led_test.py non-addressable RGB LED string test
# © 2022 by Dave Hocker
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# See the LICENSE file for more details.
#


from .na_rgb_led_string import NaRGBLEDString
import mp_logging as logging
from .configuration import Configuration
import time


logger = logging.getLogger("led")


def run_na_rgb_led_string():
    """
    Use PWM on a non-addressable RGB LED string
    :return:
    """
    pwm_led_string = None
    logger.info("Running na-LED string...")

    config = Configuration.get_configuration()
    red_pin = config[Configuration.CFG_RED_PIN]
    green_pin = config[Configuration.CFG_GREEN_PIN]
    blue_pin = config[Configuration.CFG_BLUE_PIN]
    pwm_freq = config[Configuration.CFG_PWM_FREQ]
    hold_time = config[Configuration.CFG_HOLD_TIME]
    test_time = config[Configuration.CFG_TEST_TIME]
    brightness = float(config[Configuration.CFG_BRIGHTNESS]) / 100.0
    logger.info(f"RGB pins: {red_pin}, {green_pin}, {blue_pin}")
    logger.info(f"PWM freq: {pwm_freq}")
    logger.info(f"Hold time: {hold_time}")
    logger.info(f"Brightness: {brightness}")

    repeat_count = int(test_time / hold_time)

    try:
        pwm_led_string = NaRGBLEDString(red_pin=red_pin, green_pin=green_pin, blue_pin=blue_pin, pwm_freq=pwm_freq)
        pwm_led_string.open()

        for i in range(repeat_count):
            cx = i % len(config[Configuration.CFG_COLORS])
            rgb = config[Configuration.CFG_COLORS][cx]
            r = int(rgb[0] * brightness)
            g = int(rgb[1] * brightness)
            b = int(rgb[2] * brightness)
            logger.info(str(f"{rgb}"))
            pwm_led_string.set_color(r, g, b)
            time.sleep(hold_time)
    except KeyboardInterrupt:
        print("ctrl-c pressed")
    except Exception as ex:
        print("Unhandled exception")
        print(str(ex))
    finally:
        if pwm_led_string is not None:
            pwm_led_string.close()
            logger.info("na-LED turned off")
