#
# NTP functions adapted from the following:
#
#   https://github.com/LutzEmbeddedTec/Pico_w_RTC
#
# This code does not appear to be copyrighted nor subject to any license.
# If that is the case, then it is now covered as follows:
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# See the LICENSE file for more details.
#


import network
import time
import usocket as socket
import ustruct as struct
from machine import RTC
import rp2


class PicoWiFi:
    """
    A singleton class representing the Pico's WiFi system
    """
    def __init__(self, country="US"):
        if not hasattr(self, "_wlan"):
            self._wlan = network.WLAN(network.STA_IF)
            self._ssid = None
            rp2.country(country)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(PicoWiFi, cls).__new__(cls)
        return cls.instance

    @property
    def wlan(self):
        return self._wlan

    @property
    def ssid(self):
        return self._ssid

    def connect_wifi(self, ssid, password, timeout=10):
        """
        Connect the WiFi adapter to a network. The process of connecting
        to a WiFi network seems to be both sequence and timing dependent.
        This code was arrived at by substantial trial-and-error.
        :param ssid:
        :param password:
        :param timeout: How long to wait for connection to complete (in sec)
        :param country: WiFi country code (e.g. US or GB)
        :return: Ending status. For success 3.
        """
        if self._wlan.isconnected():
            self._wlan.disconnect()
        time.sleep(1.0)

        """
        Status codes from RPi documentation
        https://datasheets.raspberrypi.com/picow/connecting-to-the-internet-with-pico-w.pdf
        // Return value of cyw43_wifi_link_status
        #define CYW43_LINK_DOWN (0)
        #define CYW43_LINK_JOIN (1)
        #define CYW43_LINK_NOIP (2)
        #define CYW43_LINK_UP (3)
        #define CYW43_LINK_FAIL (-1)
        #define CYW43_LINK_NONET (-2)
        #define CYW43_LINK_BADAUTH (-3)
        """

        max_wait = timeout
        self._wlan.active(True)
        self._wlan.connect(ssid=ssid, key=password)
        self._wlan.active()
        time.sleep(1.0)

        while max_wait > 0:
            time.sleep(1.0)

            self._wlan.active()
            if self._wlan.isconnected() or self._wlan.status() >= 3:
                # Success
                break

            max_wait -= 1
            print(f"waiting for connection...{max_wait}")

        if self._wlan.status() != 3:
            raise RuntimeError(f"Network connection failed with status {self._wlan.status()}")

        self._ssid = ssid
        return self._wlan.status()

    def disconnect_wifi(self):
        if self._wlan is not None:
            self._wlan.disconnect()
            self._wlan.active(False)

    def get_ntp_time(self, ntp_host, tz=-6):
        """
        Use NTP to determine the current time. Note that NTP time is
        based on 1900-01-01 while Unix time is based on 1970-01-01.
        The difference between the two is the Unix epoch.
        :param ntp_host: NTP server to be used
        :param tz:
        :return:
        """
        NTP_DELTA = 2208988800  # AKA the Unix epoch, 1970-1900 in sec
        ntp_query = bytearray(48)
        ntp_query[0] = 0x1B
        addr = socket.getaddrinfo(ntp_host, 123)[0][-1]
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.settimeout(5)  # Originally this was 1 sec but that was too short
            res = s.sendto(ntp_query, addr)
            msg = s.recv(48)
        except Exception as ex:
            print(str(ex))
            raise ex
        finally:
            s.close()
        ntp_time = struct.unpack("!I", msg[40:44])[0]
        return time.gmtime(ntp_time - NTP_DELTA + (tz * 3600))

    #
    #  Set the pico´s RTC using NTP
    def set_rtc_from_ntp(self, ntp_host, tz=-6):
        """
        Set the Pico's RTC using the time obtained from an NTP server
        :param ntp_host:
        :param tz: Time zone (e.g. CST = -6)
        :return:
        """
        tm = self.get_ntp_time(ntp_host, tz=tz)
        rtc = RTC()
        rtc.datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))


def run():
    """
    Test code
    :return:
    """
    # Find a place to hide this (probably the configuration file)

    ssid = "TPLad8074"
    pw = ""
    timeout = 10
    wifi = PicoWiFi()
    try:
        status = wifi.connect_wifi(ssid, pw, timeout=timeout)
    except TimeoutError as ex:
        print(f"WiFi connect timed out after {timeout} sec")
        return
    print(f"Connected to {ssid} with status {status} and wait {timeout} sec")

    # Time zone is CDT or -5
    wifi.set_rtc_from_ntp('time.nist.gov', tz=-5)
    print("Pico RTC clock set")


if __name__ == "picow_network":
    # run()
    pass
