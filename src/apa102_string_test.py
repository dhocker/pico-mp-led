#
# apa102_string_test.py APA102/DotStar LED string test
# © 2022 by Dave Hocker
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# See the LICENSE file for more details.
#


import sys
from micropython_dotstar import DotStar
from machine import Pin, SPI
from lcd_line_display import LCDLineDisplay
from .configuration import Configuration
import utime


def run_apa102_led_string():
    """
    Use PWM on a non-addressable RGB LED string
    :return:
    """
    led_string = None
    lcd_display = LCDLineDisplay.get_singleton()
    lcd_display.print("Running na-LED string...")

    config = Configuration.get_configuration()
    clk_pin = config[Configuration.CFG_SPI_CLK]
    tx_pin = config[Configuration.CFG_SPI_TX]
    rx_pin = config[Configuration.CFG_SPI_RX]
    hold_time = config[Configuration.CFG_HOLD_TIME]
    test_time = config[Configuration.CFG_TEST_TIME]
    # From 0-100 percent brightness to 0-1.0
    brightness = float(config[Configuration.CFG_BRIGHTNESS]) / 100.0
    pixels = config[Configuration.CFG_PIXELS]
    lcd_display.print(f"clk pin: {clk_pin}")
    lcd_display.print(f"tx pin: {tx_pin}")
    lcd_display.print(f"rx pin: {rx_pin}")
    lcd_display.print(f"pixels: {pixels}")
    lcd_display.print(f"Hold time: {hold_time}")
    lcd_display.print(f"Brightness: {brightness}")

    repeat_count = int(test_time / hold_time)

    try:
        # The miso pin is required, but not used in this case
        spi = SPI(0, sck=Pin(clk_pin), mosi=Pin(tx_pin), miso=Pin(rx_pin))
        led_string = DotStar(spi, pixels)

        led_string.brightness = brightness

        for i in range(repeat_count):
            cx = i % len(config[Configuration.CFG_COLORS])
            rgb = config[Configuration.CFG_COLORS][cx]
            r = int(rgb[0])
            g = int(rgb[1])
            b = int(rgb[2])
            lcd_display.print(str(f"{rgb}"))

            for px in range(pixels):
                led_string[px] = (r, g, b)
            led_string.show()
            utime.sleep(hold_time)
    except KeyboardInterrupt:
        print("ctrl-c pressed")
    except Exception as ex:
        print("Unhandled exception in apa102_string_test.run_apa102_led_string")
        print(str(ex))
        sys.print_exception(ex)
    finally:
        if led_string is not None:
            led_string.deinit()
            lcd_display.print("LED turned off")
