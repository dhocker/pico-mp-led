
from logger_device import LoggerDevice
from lcd_line_display import LCDLineDisplay


class LCDLogger(LoggerDevice):
    def __init__(self):
        super().__init__()
        self._lcd_logger = LCDLineDisplay.get_singleton()

    def print(self, level, logdata):
        self._lcd_logger.print(f"{level.upper()[0]}: {logdata}")
