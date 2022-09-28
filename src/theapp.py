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


from src.configuration import Configuration
# Create a singleton, read-only instance of the configuration file
singleton = Configuration()


print("Loading modules...")
import sys
from machine import SPI, Pin
from lcd_line_display import LCDLineDisplay
from src.led_engine import LEDEngine
from src.dotstar_driver import MPDotStar
from src.na_led_driver import MPNALEDString
from src.ws281x_driver import WS281XDriver
from src.runled import run_led
from set_rtc import set_rtc
from src.na_rgb_led_string_test import run_na_rgb_led_string
import mp_logging as logging
import datetime
from mp_datetime import str_parse_date, date_now
from console_logger import ConsoleLogger
from lcd_logger import LCDLogger
from rpico_board import is_host_connected
print("Modules loaded")


logger = logging.getLogger("led")


def create_lcd_line_display():
    """
    Create a singleton instance of an LCD line display
    :return: Returns the singleton
    """
    # The LCD is a singleton
    config = Configuration.get_configuration()
    lcd_address = int(config[Configuration.CFG_LCD_ADDRESS], 16)
    lcd_rows = config[Configuration.CFG_LCD_ROWS]
    lcd_cols = config[Configuration.CFG_LCD_COLS]
    lcd_i2c_id = config[Configuration.CFG_I2C_ID]
    lcd_scl_pin = config[Configuration.CFG_LCD_SCL_PIN]
    lcd_sda_pin = config[Configuration.CFG_LCD_SDA_PIN]
    lcd_display = LCDLineDisplay.get_singleton(id=lcd_i2c_id,
                                               rows=lcd_rows,
                                               cols=lcd_cols,
                                               i2c_addr=lcd_address,
                                               scl_pin=lcd_scl_pin,
                                               sda_pin=lcd_sda_pin)
    return lcd_display


def compile_script(script_file):
    """
    Compiles a script file and returns a script engine
    :param script_file: The file to be compiled
    :return: An engine instance or None
    """
    # Compile the script
    engine = LEDEngine()
    rc = engine.compile(script_file)
    if not rc:
        # Compile failed
        logger.error(f"{script_file} compile failed")
        return None
    logger.info(f"{script_file} compiled")

    return engine


def script_to_run():
    """
    Determine what script is to be run
    :return: Script file to be run
    """
    script_file = None
    config = Configuration.get_configuration()

    # Look for a calendar schedule first
    if Configuration.CFG_SCRIPT_CALENDAR in config.keys():
        logger.debug("Using configuration calendar for script file")
        # The calendar is a list of date ranges with a script to be run
        calendar = config[Configuration.CFG_SCRIPT_CALENDAR]
        now = date_now()
        logger.debug(f"now: {now}")
        for date_span in calendar:
            start = str_parse_date(date_span["start"])
            end = str_parse_date(date_span["end"])
            logger.debug(f"start: {start} end: {end}")
            if start <= now <= end:
                script_file = date_span["script_file"]
                logger.info(f"Date {now} using script file {script_file}")
                break
    else:
        script_file = config[Configuration.CFG_SCRIPT_FILE]
    return script_file

def run_apa_dotstar():
    """
    Run a script on an APA102 or DotStar LED string
    :return:
    """
    config = Configuration.get_configuration()
    clk_pin = config[Configuration.CFG_SPI_CLK]
    tx_pin = config[Configuration.CFG_SPI_TX]
    rx_pin = config[Configuration.CFG_SPI_RX]
    pixels = config[Configuration.CFG_PIXELS]
    color_order = config[Configuration.CFG_ORDER]
    script_file = script_to_run()

    # Run the AHLED code from here
    logger.info("Running the AHLED code")

    # Compile the script
    engine = compile_script(script_file)
    if engine is None:
        # Compile failed
        return

    # Execute
    spi = SPI(0, sck=Pin(clk_pin), mosi=Pin(tx_pin), miso=Pin(rx_pin))
    driver = MPDotStar()
    driver.open(spi, pixels, order=color_order)
    engine.execute(driver)


def run_ws281x():
    """
    Run a script on a WS281X/Neopixel LED string
    :return:
    """
    config = Configuration.get_configuration()
    datapin = config[Configuration.CFG_DATAPIN]
    pixels = config[Configuration.CFG_PIXELS]
    color_order = config[Configuration.CFG_ORDER].upper()
    script_file = script_to_run()

    logger.info(f"datapin: {datapin}")
    logger.info((f"color_order: {color_order}"))
    logger.info(f"script_file: {script_file}")

    # Run the AHLED code from here
    logger.info("Running the AHLED code")

    # Compile the script
    engine = compile_script(script_file)
    if engine is None:
        # Compile failed
        return

    # Execute
    driver = WS281XDriver()
    driver.open(pixels, datapin=datapin, order=color_order)
    engine.execute(driver)
    driver.close()


def run_non_addressable_led():
    """
    Create driver for NA LED string and run it
    :return: None
    """
    config = Configuration.get_configuration()
    red_pin = config[Configuration.CFG_RED_PIN]
    green_pin = config[Configuration.CFG_GREEN_PIN]
    blue_pin = config[Configuration.CFG_BLUE_PIN]
    pwm_freq = config[Configuration.CFG_PWM_FREQ]
    brightness = float(config[Configuration.CFG_BRIGHTNESS]) / 100.0
    script_file = script_to_run()
    logger.info(f"RGB pins: {red_pin}, {green_pin}, {blue_pin}")
    logger.info(f"PWM freq: {pwm_freq}")
    logger.info(f"Brightness: {brightness}")

    # Run the AHLED code from here
    logger.info("Running the AHLED code")

    # Compile the script
    engine = compile_script(script_file)
    if engine is None:
        # Compile failed
        return

    # Execute
    driver = MPNALEDString()
    driver.open(red_pin=red_pin, green_pin=green_pin, blue_pin=blue_pin, pwm_freq=pwm_freq)
    driver.setBrightness(brightness)
    engine.execute(driver)


def run():
    # The app starts here
    lcd_display = None

    # Configure the logger
    config = Configuration.get_configuration()
    log_level = config[Configuration.CFG_LOG_LEVEL].lower()
    log_devices = config[Configuration.CFG_LOG_DEVICES]
    logger.set_log_level(log_level)

    # Configuration.dump_configuration()

    # The code to be run
    run_code = config[Configuration.CFG_RUN_CODE].lower()

    # Add loggers
    for dev in log_devices:
        device = dev.lower()
        if device == "lcd":
            lcd_display = create_lcd_line_display()
            logger.add_logger(LCDLogger())
        elif device == "console":
            logger.add_logger(ConsoleLogger())

    # Menu selection
    if run_code == "" or run_code == "menu":
        # If no host is connected, exit to REPL
        if not is_host_connected():
            logger.info("No host connected. Exit to REPL.")
            return
        logger.info("Menu selection")
        while True:
            print("-----------------")
            print("Select app to run")
            print("-----------------")

            id = 0
            menu_items = config["menu"]
            # Show list of menu items 1 to len(menu items)
            for item in menu_items:
                id += 1
                print(f"{id} - {item[0]}")
            print("")

            selection = input("Select: ")
            try:
                selection = int(selection)
            except:
                selection = -1

            if selection < 1 or selection > len(menu_items):
                print("Invalid selection")
                continue
            run_code = menu_items[selection - 1][1]
            print(f"{run_code} selected")
            break


    try:
        if run_code == "apa102" or run_code == "dotstar":
            logger.info("APA102/DotStar is running...")
            logger.info("Press ctrl-c to terminate")
            run_apa_dotstar()
            logger.info("APA102/DotStar ended")
        elif run_code == "ws281x" or run_code == "neopixel":
            logger.info("WS281X/Neopixle is running...")
            logger.info("Press ctrl-c to terminate")
            run_ws281x()
            logger.info("WS281X/Neopixel ended")
        elif run_code == "onboard-led":
            logger.info("Onboard LED is running...")
            logger.info("Press ctrl-c to terminate")
            run_led()
            logger.info("Onboard LED ended")
        elif run_code == "non-addressable":
            logger.info("NA LED is running...")
            logger.info("Press ctrl-c to terminate")
            run_non_addressable_led()
            logger.info("Non-addressable LED string test ended")
        elif run_code == "set_rtc":
            set_rtc()
        elif run_code == "exit":
            pass
        else:
            logger.error(f"{run_code} is not recognized as code to be run")
    except Exception as ex:
        logger.error("theapp unhandled exception")
        logger.error(str(ex))
        sys.print_exception(ex)
    finally:
        if lcd_display is not None:
            lcd_display.close(clear=config[Configuration.CFG_CLEAR_AT_CLOSE])
