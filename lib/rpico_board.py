#
# task_manager.py - MicroPython task (thread) manager
# © 2022 by Dave Hocker
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# See the LICENSE file for more details.
#


import machine


# Pico specific constants
SIE_STATUS = const(0x50110000+0x50)
CONNECTED = const(1<<16)
SUSPENDED = const(1<<4)


def is_host_connected():
    """
    Is the USB host connected?
    :return:
    """
    return (machine.mem32[SIE_STATUS] & (CONNECTED | SUSPENDED)) == CONNECTED
