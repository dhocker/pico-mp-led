#
# theapp.py - runs the AthomeLED code that was ported
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
from machine import SPI, Pin
from lcd_line_display import LCDLineDisplay
from src.configuration import Configuration
from src.led_engine import LEDEngine
from src.script_cpu_led import ScriptCPULED
from src.dotstar_driver import MPDotStar


def run():
    # The app starts here

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

    clk_pin = config[Configuration.CFG_SPI_CLK]
    tx_pin = config[Configuration.CFG_SPI_TX]
    rx_pin = config[Configuration.CFG_SPI_RX]
    pixels = config[Configuration.CFG_PIXELS]
    color_order = config[Configuration.CFG_ORDER]
    script_file = config[Configuration.CFG_SCRIPT_FILE]

    try:
        # Run the AHLED code from here
        print("Running the AHLED code")
        lcd_display.print("Running the AHLED code")

        # Compile the script
        engine = LEDEngine()
        rc = engine.compile(script_file)
        if not rc:
            # Compile failed
            lcd_display.print(f"{script_file} compile failed")
            print(f"{script_file} compile failed")
            return
        lcd_display.print(f"{script_file} compiled")
        print(f"{script_file} compiled")

        # Execute
        spi = SPI(0, sck=Pin(clk_pin), mosi=Pin(tx_pin), miso=Pin(rx_pin))
        driver = MPDotStar()
        driver.open(spi, pixels, order=color_order)
        engine.execute(driver)

        print("theapp succeeded")
        lcd_display.print("theapp succeeded")
    except Exception as ex:
        print("theapp unhandled exception")
        lcd_display.print("theapp unhandled exception")
        print(str(ex))
        lcd_display.print(str(ex))
        sys.print_exception(ex)
    finally:
        lcd_display.close(clear=config[Configuration.CFG_CLEAR_AT_CLOSE])
