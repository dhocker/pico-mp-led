#
# boot.py - this file is run first after reset/reboot.
# © 2022 by Dave Hocker
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# See the LICENSE file for more details.
#


from ds1307 import DS1307
from machine import RTC, I2C, Pin


# Look for an RTC module. If found, set the system time.
i2c_rtc = None
try:
    # Be careful of id and/or pin collisions
    i2c_rtc = I2C(id=1, scl=Pin(7), sda=Pin(6), freq=100000)
    rtc = DS1307(i2c_rtc)
    dt = rtc.datetime()
    print(dt)
except Exception as ex:
    print("Failed to find RTC")
    print(ex)
finally:
    if i2c_rtc is not None:
        del i2c_rtc

print("####")
print("boot.py was run")
print("####")


# TODO Put the RTC setup code here
# When you are running attached to a PC, rshell will set the clock with date and time.
# When running standalone, there is nothing to set the clock. You must use an RTC
# module like the DS1307 to maintain/set date and time.
# TODO Timezone?
