from logger_device import LoggerDevice


class ConsoleLogger(LoggerDevice):
    def __init__(self):
        super().__init__()

    def print(self, level, logdata):
        print(f"{level}: {logdata}")
