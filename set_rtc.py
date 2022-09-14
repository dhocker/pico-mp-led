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


def console_input(prompt, default):
    """
    Console input with a default value
    :param prompt: Input prompt
    :param default: Returned value if use types enter with no value
    :return: Input or default value as a string
    """
    ci = input(f"{prompt} [{default}]: ")
    if ci == "":
        ci = default
    return ci


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
                now_rtc = rtc.datetime()
                print(now_rtc)
                # Set the defaults for manual input
                year = now_rtc[0]
                month = now_rtc[1]
                day = now_rtc[2]
                dow = now_rtc[3]
                hour = now_rtc[4]
                minute = now_rtc[5]
                second = now_rtc[6]
                usecond = now_rtc[7]
            except Exception as ex:
                print("An exception occurred while attempting to get the current time from the DS1307")
                print("The likely cause of this error is no DS1307.")
                print(ex)
                del rtc
                del i2c_rtc
                raise ex

        if action.lower() == 'm':
            year = int(console_input("Year (YYYY)", year))
            month = int(console_input("month (Jan --> 1 , Dec --> 12)", month))
            day = int(console_input("day", day))
            dow = int(console_input("day of week (1 --> Mon , 2 --> Tue ... 0 --> Sun)", dow))
            hour = int(console_input("hour (24 Hour format)", hour))
            minute = int(console_input("minute", minute))
            second = int(console_input("second", second))

            # Form the 8-tuple for the specified date/time
            now = (year, month, day, dow, hour, minute, second, 0)
            print("The time to be set is: ", now)
            input("Press enter to set RTC")

            # Set the RTC
            print("Setting the RTC")
            rtc.datetime(now)

            print("The new value of the RTC is:")
            print(rtc.datetime())

            done = True
        elif action.lower() == "s":
            # NOTE: All times are local time. We do not use UTC time.
            # localtime() returns the following 8-tuple:
            # (year, month, mday, hour, minute, second, weekday 0=Monday, yearday)
            lt = utime.localtime()
            # The 8-tuple for the specified date/time:
            # year,month,day,dayofweek 0=Sunday,hour,minute,second,microsecond
            # Note the conversion of day-of-week.
            dow_cnv = [1, 2, 3, 4, 5, 6, 0]
            now = (lt[0], lt[1], lt[2], dow_cnv[lt[6]], lt[3], lt[4], lt[5], 0)

            print("Setting the RTC from Pico time")
            rtc.datetime(now)

            print("The new value of the RTC is:")
            print(rtc.datetime())

            done = True
        elif action.lower() == "c":
            # Configure I2C
            print("-------------------------------------------------")
            print("Configure the I2C port where the RTC is connected")
            print("-------------------------------------------------")
            print("Possible I2C configurations")
            valid_configurations = [
                (0, 0, 1),
                (0, 4, 5),
                (0, 8, 9),
                (0, 12, 13),
                (0, 16, 17),
                (0, 20, 21),
                (1, 2, 3),
                (1, 6, 7),
                (1, 10, 11),
                (1, 14, 15),
                (1, 18, 19),
                (1, 26, 27)
            ]
            selection = 0
            print("Select\tSDA/SCL\tId")
            for s in valid_configurations:
                print(f"{selection} - \t{s[1]}/{s[2]}\t{s[0]}")
                selection += 1
            try:
                selection = int(input("Selection (0-11): "))
                if selection < 0 or selection > 11:
                    print("Invalid selection value")
                else:
                    # (id, SDA, SCL)
                    default_id = valid_configurations[selection][0]
                    default_sda = valid_configurations[selection][1]
                    default_scl = valid_configurations[selection][2]
                    print("")
                    print(f"I2C Id: {default_id}")
                    print(f"I2C SDA: {default_sda}")
                    print(f"I2C SCL: {default_scl}")
            except Exception:
                print("")
                print("Invalid selection value")
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
