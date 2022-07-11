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


print("####")
print("boot.py was run")
print("####")


# TODO Put the RTC setup code here
# When you are running attached to a PC, rshell will set the clock with date and time.
# When running standalone, there is nothing to set the clock. You must use an RTC
# module like the DS1307 to maintain/set date and time.
# TODO Timezone?
