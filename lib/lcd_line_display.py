#
# lcd_line_display.py - PCF8574 based LCD panel display
# © 2022 by Dave Hocker
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# See the LICENSE file for more details.
#
# This is NOT thread safe
#


from pico_i2c_lcd import I2cLcd
from machine import I2C
from machine import Pin
import time


class LCDLineDisplay:
    # Default I2C address for the LCD panel
    DISPLAY_ADDR = 0x27

    _singleton = None

    def __init__(self, id=0, rows=4, cols=20, i2c_addr=DISPLAY_ADDR, scl_pin=9, sda_pin=8):
        """
        Create a display instance
        :param id: I2C device identifier.
        :param rows: Number of rows on display (usually 2 or 4)
        :param cols: Number of columns per row (usually 16 or 20)
        :param i2c_addr: I2C bus address, usually 0x2F or 0x3F
        :param scl_pin: Pico GPIO pin to be used for the I2C clk signal
        :param sda_pin: Pico GPIO pin to be used for the I2C data signal
        """
        self._id = id
        self._rows = rows
        self._cols = cols
        self._scl = Pin(scl_pin)
        self._sda = Pin(sda_pin)

        self._i2c = None
        self._lcd = None

        self._current_row = None
        self._display_rows = None

    def open(self):
        """
        Open/initialize the LCD.
        :return: None
        """
        self._i2c = I2C(self._id, scl=Pin(9), sda=Pin(8), freq=400000)
        self._lcd = I2cLcd(self._i2c, LCDLineDisplay.DISPLAY_ADDR, self._rows, self._cols)
        self.clear()

    def close(self, clear=False):
        """
        Close/de-initialize the LCD
        :param clear:
        :return: None
        """
        if clear:
            self._lcd.clear()
            self._lcd.backlight_off()

    def clear(self):
        """
        Clear the entire LCD.
        :return: None
        """
        self._current_row = 0
        self._display_rows = []
        self._lcd.clear()

    def print(self, row_str):
        """
        Terminal style print. Prints the next line on a scrolling display.
        :param row_str:
        :return: None
        """
        if len(self._display_rows) == self._rows:
            self._display_rows.pop(0)
        self._display_rows.append(row_str)
        self._render()

    def _render(self):
        """
        Rewrites the entire LCD with the contents of the row list,
        :return:
        """
        self._lcd.clear()
        for i in range(len(self._display_rows)):
            self._lcd.put_str(0, i, self._display_rows[i])

    @staticmethod
    def get_singleton(rows=4, cols=20, i2c_addr=DISPLAY_ADDR, scl_pin=9, sda_pin=8):
        """
        Creates a singleton instance of the LCD class.
        Designed for single thread use only.
        WARNING: NOT thread safe
        :param rows: Number of LCD rows (usually 2 or 4)
        :param cols: Number of LCD columns/characters (typically 16 or 20)
        :param i2c_addr: I2C bus address, usually 0x2F or 0x3F
        :param scl_pin: I2C clock GPIO pin
        :param sda_pin: I2C data GPIO pin
        :return: Returns the singleton instance
        """
        if LCDLineDisplay._singleton is None:
            LCDLineDisplay._singleton = LCDLineDisplay(rows=rows,
                                                       cols=cols,
                                                       i2c_addr=i2c_addr,
                                                       scl_pin=scl_pin,
                                                       sda_pin=sda_pin)
            LCDLineDisplay._singleton.open()
        return LCDLineDisplay._singleton
