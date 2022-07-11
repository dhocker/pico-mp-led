#
# mp_datetime.py - extra datetime functions for MicroPython
# Replace this code with the start of your application.
# © 2022 by Dave Hocker
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# See the LICENSE file for more details.
#


import datetime
import time
import re


def str_parse_time(time_str):
    """
    Parse a time string of format HH:MM:SS
    :param time_str: HH:MM:SS
    :return: A date time object for the current date and parsed time
    """
    rx = "(\d*):(\d*):(\d*)"
    m = re.match(rx, time_str)
    # Local time for year, month and day
    lt = time.localtime()
    # Local time plus parsed hour:minutes:seconds
    dt = datetime.datetime(lt[0], lt[1], lt[2], int(m.group(1)), int(m.group(2)), int(m.group(3)))
    return dt
