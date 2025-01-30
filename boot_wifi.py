#
# boot_wifi.py - this file is run first after reset/reboot.
# © 2023 by Dave Hocker
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# See the LICENSE file for more details.
#
# Copy this file to the Pico and rename it to boot.py
#


from pico_wifi import PicoWiFi
import utime


wifi = PicoWiFi()

# Look for the app configuration file
ssid = None
password = None
timeout = 10
tz = -6

try:
    print("Trying led.conf for network configuration")
    from src.configuration import Configuration
    app_cfg = Configuration()
    config = app_cfg.get_configuration()
    ssid = config[Configuration.CFG_WIFI_SSID]
    password = config[Configuration.CFG_WIFI_PASSWORD]
    timeout = config[Configuration.CFG_NTP_TIMEOUT]
    tz = config[Configuration.CFG_TIME_ZONE]
    del app_cfg
except Exception as ex:
    print(str(ex))
    password = None
    raise ex

# Log into the WiFi network
try:
    status = wifi.connect_wifi(ssid, password, timeout=timeout)
except RuntimeError as ex:
    print(f"WiFi connect failed after waiting {timeout} sec")
    raise ex
finally:
    password = None

print(f"Connected to {ssid} with status {status} and wait {timeout} sec")

# Time zone CDT = -5 and CST = -6
wifi.set_rtc_from_ntp('time.nist.gov', tz=tz)
print("Pico-w RTC clock set")
# Report the current time
print(f"utime.localtime reports: {utime.localtime()}")

# The wifi package seems to consume a lot of CPU
wifi.disconnect_wifi()

print("####")
print("boot.py was run")
print("####")
