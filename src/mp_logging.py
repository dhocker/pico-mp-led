#
# mp_logging.py - MicroPython version of logging module
# © 2022 by Dave Hocker
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# See the LICENSE file for more details.
#


from lcd_line_display import LCDLineDisplay


class Logger:
    def __init__(self):
        self._lcd_display = LCDLineDisplay.get_singleton()

    def info(self, log_data):
        self._lcd_display.print(f"I:{log_data}")
        print("info:", log_data)

    def warning(self, log_data):
        self._lcd_display.print(f"W:{log_data}")
        print("warning:", log_data)

    def error(self, log_data):
        self._lcd_display.print(f"E:{log_data}")
        print("error:", log_data)

    def debug(self, log_data):
        self._lcd_display.print(f"D:{log_data}")
        print("debug:", log_data)

    def critical(self, log_data):
        self._lcd_display.print(f"C:{log_data}")
        print("critical:", log_data)


thelogger = Logger()


def getLogger(name):
    return thelogger
