#
# set_rtc.py - set the DS1307 RTC
# Original code from the article:
# https://www.iotstarters.com/diy-digital-clock-with-rtc-ds1307-and-raspberry-pi-pico/
#
# Changes © 2022 by Dave Hocker
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# See the LICENSE file for more details.
#
#
# The DS1307 RTC can be set from manual input or the current Pico time.
# Tools like rshell set the Pico clock from the host PC's time. The easiest
# way to get the DS1307 set to the current time is to run this script under rshell
# or a similar tool.
#


from machine import I2C, Pin
from ds1307 import DS1307
import utime


def set_rtc():
    i2c_rtc = None
    rtc = None
    default_id = 1
    default_scl = 7
    default_sda = 6

    done = False
    while not done:
        print("")
        print("------------------")
        print("DS1307 RTC Utility")
        print("------------------")
        print("c - configure RTC I2C")
        print("m - set the RTC from manual input")
        print("s - set the RTC from the current Pico machine time")
        print("t - show current RTC date/time")
        print("q - quit without setting clock")
        print("")
        action = input("Select: ")

        if action.lower() in ["m", "s", "t"] and rtc is None:
            # Must be configured for the actual DS1307 RTC wiring
            i2c_rtc = I2C(default_id, scl=Pin(default_scl), sda=Pin(default_sda), freq=100000)

            result = I2C.scan(i2c_rtc)
            xresult = [hex(x) for x in result]
            print(xresult)

            rtc = DS1307(i2c_rtc)
            print("The current RTC date/time")
            # The return value is an 8-tuple: (year, month, day, weekday 0=Sunday, hour, minute, second, microsecond)
            # This is close to the 7-tuple returned by datetime.datetime.now() which does not include weekday.
            try:
                print(rtc.datetime())
            except Exception as ex:
                print("An exception occurred while attempting to get the current time from the DS1307")
                print(ex)
                del rtc
                del i2c_rtc
                raise ex

        if action.lower() == 'm':
            year = int(input("Year (YYYY): "))
            month = int(input("month (Jan --> 1 , Dec --> 12): "))
            date = int(input("day : "))
            day = int(input("day of week (1 --> monday , 2 --> Tuesday ... 0 --> Sunday): "))
            hour = int(input("hour (24 Hour format): "))
            minute = int(input("minute : "))
            second = int(input("second : "))

            # Form the 8-tuple for the specified date/time
            now = (year,month,date,day,hour,minute,second,0)
            print("The time to be set is: ", now)
            input("Press enter to set RTC")

            # Set the RTC
            print("Setting the RTC")
            rtc.datetime(now)

            print("The new value of the RTC is:")
            print(rtc.datetime())

            done = True
        elif action.lower() == "s":
            # localtime() returns the following 8-tuple:
            # (year, month, mday, hour, minute, second, weekday 0=Monday, yearday)
            lt = utime.localtime()
            # The 8-tuple for the specified date/time:
            # year,month,day,dayofweek 0=Sunday,hour,minute,second,microsecond
            # Note the conversion of day-of-week.
            dow_cnv = [1, 2, 3, 4, 5, 6, 0]
            now = (lt[0], lt[1], lt[2], dow_cnv[lt[6]], lt[3], lt[4], lt[5], 0)

            print("Seeting the RTC from Pico time")
            rtc.datetime(now)

            print("The new value of the RTC is:")
            print(rtc.datetime())

            done = True
        elif action.lower() == "c":
            # Configure I2C
            print("Configure the I2C port")
            done = False
        elif action.lower() == "t":
            print("The current RTC date/time")
            print(rtc.datetime())
            done = False
        else:
            print("RTC was not set")
            done = True

    if rtc is not None:
        del rtc
    if i2c_rtc is not None:
        del i2c_rtc


if __name__ == '__main__':
    set_rtc()
