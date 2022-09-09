from logger_device import LoggerDevice
import utime


class ConsoleLogger(LoggerDevice):
    def __init__(self):
        super().__init__()

    def print(self, level, logdata):
        t = utime.localtime()
        print(f"{t[3]}:{t[4]:02d}:{t[5]:02d} {level}:{logdata}")
