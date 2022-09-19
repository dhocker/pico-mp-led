from logger_device import LoggerDevice
import utime
from rpico_board import is_host_connected


class ConsoleLogger(LoggerDevice):
    HOST_CONNECTED = is_host_connected()

    def __init__(self):
        super().__init__()

    def print(self, level, logdata):
        if ConsoleLogger.HOST_CONNECTED:
            t = utime.localtime()
            print(f"{t[3]}:{t[4]:02d}:{t[5]:02d} {level}:{logdata}")
