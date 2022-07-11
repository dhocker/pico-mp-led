#
# theapp.py
# Replace this code with the start of your application.
# © 2022 by Dave Hocker
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# See the LICENSE file for more details.
#


import sys
from .apa102_string_test import run_apa102_led_string
from .na_rgb_led_string_test import run_na_rgb_led_string
from .runled import run_led
from lcd_line_display import LCDLineDisplay
from src.configuration import Configuration


def run():
    # Your app starts here

    # Create a singleton, read-only instance of the configuration file
    singleton = Configuration()
    Configuration.dump_configuration()

    # The list of tests to be run
    config = Configuration.get_configuration()
    run_tests = config[Configuration.CFG_RUN_TESTS]

    # The LCD is a singleton
    lcd_address = int(config[Configuration.CFG_LCD_ADDRESS], 16)
    lcd_rows = config[Configuration.CFG_LCD_ROWS]
    lcd_cols = config[Configuration.CFG_LCD_COLS]
    lcd_scl_pin = config[Configuration.CFG_LCD_SCL_PIN]
    lcd_sda_pin = config[Configuration.CFG_LCD_SDA_PIN]
    lcd_display = LCDLineDisplay.get_singleton(rows=lcd_rows,
                                               cols=lcd_cols,
                                               i2c_addr=lcd_address,
                                               scl_pin=lcd_scl_pin,
                                               sda_pin=lcd_sda_pin)

    print("theapp is running...")
    print("Press ctrl-c to terminate")
    lcd_display.print("theapp is running...")

    try:
        # run_led(led_pin=15)
        # Run the onboard LED
        # run_led()
        # run_lcd_test()
        # Test non-addressable LED string
        # run_na_led()
        # run_apa102_led_string()

        for test in run_tests:
            print(f"Running test: {test}")
            if test == "non-addressable":
                run_na_rgb_led_string()
            elif test == "apa102" or test == "dotstar":
                run_apa102_led_string()
            elif test == "onboard-led":
                run_led()
            else:
                print(f"{test} is not a recognized test")

        print("theapp succeeded")
        lcd_display.print("theapp succeeded")
    except Exception as ex:
        print("theapp unhandled exception")
        lcd_display.print("theapp unhandled exception")
        print(str(ex))
        lcd_display.print(str(ex))
        sys.print_exception(ex)
    finally:
        lcd_display.close(clear=True)
