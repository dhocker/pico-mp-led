
from logger_device import LoggerDevice
from lcd_line_display import LCDLineDisplay
import utime


class LCDLogger(LoggerDevice):
    def __init__(self):
        super().__init__()
        self._lcd_logger = LCDLineDisplay.get_singleton()

    def print(self, level, logdata):
        t = utime.localtime()
        self._lcd_logger.print(f"{t[3]}:{t[4]:02d} {level.upper()[0]}:{logdata}")
