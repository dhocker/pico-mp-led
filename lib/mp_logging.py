#
# mp_logging.py - MicroPython version of logging module
# © 2022 by Dave Hocker
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# See the LICENSE file for more details.
#


class Logger:
    # Prioritized logging levels
    LEVEL_DEBUG = 10
    LEVEL_INFO = 20
    LEVEL_WARNING = 30
    LEVEL_ERROR = 40
    LEVEL_CRITICAL = 50

    def __init__(self, log_level="info"):
        # The default log level is INFO
        self._log_level = Logger.LEVEL_INFO
        self.set_log_level(log_level)

        # Loggers
        self._loggers = []

    def debug(self, log_data):
        if self._log_level <= Logger.LEVEL_DEBUG:
            self._log("debug", log_data)

    def info(self, log_data):
        if self._log_level <= Logger.LEVEL_INFO:
            self._log("info", log_data)

    def warning(self, log_data):
        if self._log_level <= Logger.LEVEL_WARNING:
            self._log("warning", log_data)

    def error(self, log_data):
        if self._log_level <= Logger.LEVEL_ERROR:
            self._log("error", log_data)

    def critical(self, log_data):
        if self._log_level <= Logger.LEVEL_CRITICAL:
            self._log("critical", log_data)

    def _log(self, level, logdata):
        if len(self._loggers):
            for x in self._loggers:
                x.print(level, logdata)

    def set_log_level(self, log_level):
        log_level = log_level.lower()
        if log_level == "debug":
            self._log_level = Logger.LEVEL_DEBUG
        elif log_level == "info":
            self._log_level = Logger.LEVEL_INFO
        elif log_level == "warning":
            self._log_level = Logger.LEVEL_WARNING
        elif log_level == "error":
            self._log_level = Logger.LEVEL_ERROR
        elif log_level == "critical":
            self._log_level = Logger.LEVEL_CRITICAL
        else:
            # Default to INFO
            self._log_level = Logger.LEVEL_INFO

    def add_logger(self, new_logger):
        self._loggers.append(new_logger)


thelogger = Logger()


def getLogger(name):
    return thelogger
