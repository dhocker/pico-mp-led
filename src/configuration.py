#
# led.conf - non-addressable LED configuration
# © 2022 by Dave Hocker
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# See the LICENSE file for more details.
#
# Currently, it looks like this:
#
# {
#     "colors": [
#         [r, g, b],
#         [r, g, b]
#     ]
# }
#
# The JSON parser is quite finicky about strings being quoted as shown above.
#
# This class behaves like a singleton class. There is only one instance of the configuration.
# There is no need to create an instance of this class, as everything about it is static.
#


import json


class Configuration():
    # Essentially a singleton instance of the configuration
    _active_config = None

    # Keys
    # Non-addressable LED
    CFG_RED_PIN = "red_pin"
    CFG_GREEN_PIN = "green_pin"
    CFG_BLUE_PIN = "blue_pin"
    CFG_PWM_FREQ = "pwm_freq"
    CFG_SPI_CLK = "spi_clk"
    # APA102/DotStar
    CFG_SPI_TX = "spi_tx"
    CFG_SPI_RX = "spi_rx"
    CFG_PIXELS = "pixels"
    CFG_ORDER = "order"
    # LCD panel
    CFG_LCD_ADDRESS = "lcd_address"
    CFG_LCD_ROWS = "lcd_rows"
    CFG_LCD_COLS = "lcd_cols"
    CFG_I2C_ID = "lcd_i2c_id"
    CFG_LCD_SCL_PIN = "lcd_scl_pin"
    CFG_LCD_SDA_PIN = "lcd_sda_pin"
    CFG_CLEAR_AT_CLOSE = "clear_at_close"
    # All
    CFG_COLORS = "colors"
    CFG_BRIGHTNESS = "brightness"
    CFG_HOLD_TIME = "hold_time"
    CFG_TEST_TIME = "test_time"
    CFG_RUN_TESTS = "run_tests"
    CFG_SCRIPT_FILE = "script_file"
    CFG_TERMINATE_BUTTON_PIN = "terminate_button_pin"
    CFG_LOG_LEVEL = "log_level"
    CFG_LOG_DEVICES = "log_devices"

    def __init__(self):
        Configuration.load_configuration()

    # Load the configuration file
    @classmethod
    def load_configuration(cls):
        # Try to open the conf file. If there isn't one, we give up.
        cfg_path = None
        try:
            cfg_path = Configuration.get_configuration_file()
            print("Opening configuration file {0}".format(cfg_path))
            cfg = open(cfg_path, 'r')
        except Exception as ex:
            print("Unable to open {0}".format(cfg_path))
            print(str(ex))
            return

        # Read the entire contents of the conf file
        cfg_json = cfg.read()
        cfg.close()
        # print cfg_json

        # Try to parse the conf file into a Python structure
        try:
            cls._active_config = json.loads(cfg_json)
        except Exception as ex:
            print("Unable to parse configuration file as JSON")
            print(str(ex))
            return

        # print str(Configuration.ActiveConfig)
        return

    @classmethod
    def dump_configuration(cls):
        """
        Print the configuration
        :return: None
        """
        print("Active configuration file")
        print(json.dumps(cls._active_config))

    @classmethod
    def get_configuration(cls):
        """
        Return the current configuration
        :return: The configuration as a dict
        """
        return cls._active_config

    @classmethod
    def get_configuration_file(cls):
        """
        Returns the full path to the configuration file
        """
        file_name = "led.conf"
        return file_name
