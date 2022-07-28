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
from src.runled import run_led
from set_rtc import set_rtc
import mp_logging as logging
from console_logger import ConsoleLogger
from lcd_logger import LCDLogger
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
    script_file = config[Configuration.CFG_SCRIPT_FILE]

    # Run the AHLED code from here
    logger.info("Running the AHLED code")

    # Compile the script
    engine = LEDEngine()
    rc = engine.compile(script_file)
    if not rc:
        # Compile failed
        logger.error(f"{script_file} compile failed")
        return
    logger.info(f"{script_file} compiled")

    # Execute
    spi = SPI(0, sck=Pin(clk_pin), mosi=Pin(tx_pin), miso=Pin(rx_pin))
    driver = MPDotStar()
    driver.open(spi, pixels, order=color_order)
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
        logger.info("Menu selection")
        while True:
            print("-----------------")
            print("Select app to run")
            print("-----------------")
            print("1 - APA102/DotStar")
            print("2 - non-addressable LED")
            print("3 - onboard LED")
            print("4 - set_rtc")
            print("5 - exit to REPL")
            print("")
            selection = input("Select: ")
            if selection not in ["1", "2", "3", "4", "5"]:
                print("Invalid selection")
                continue
            apps = ["apa102", "non-addressable", "onboard-led", "set_rtc", "exit"]
            run_code = apps[int(selection) - 1]
            print(f"{run_code} selected")
            break


    try:
        if run_code == "apa102" or run_code == "dotstar":
            logger.info("APA102/DotStar is running...")
            logger.info("Press ctrl-c to terminate")
            run_apa_dotstar()
            logger.info("APA102/DotStar ended")
        elif run_code == "onboard-led":
            logger.info("Onboard LED is running...")
            logger.info("Press ctrl-c to terminate")
            run_led()
            logger.info("Onboard LED ended")
        elif run_code == "non-addressable":
            logger.info("NA LED is running...")
            logger.info("Press ctrl-c to terminate")
            logger.info("NA LED not implemented")
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
