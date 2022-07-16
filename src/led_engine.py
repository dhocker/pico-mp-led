#
# led_engine - LED show script engine
# © 2022 by Dave Hocker
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# See the LICENSE file for more details.
#


from . import script_vm
from . import script_compiler
from . import script_cpu_led
import src.mp_logging as logging
from push_button import PushButton
from src.configuration import Configuration
import sys

logger = logging.getLogger("led")


class TerminateEvent:
    """
    Substitute for the Python threading event. This is not specific thread-safe
    code here because the terminate flag is only set by the parent and read by the _thread.
    """
    def __init__(self):
        self._terminate_flag = False
        self._terminated = False
        # Push button for terminating LED app
        config = Configuration.get_configuration()
        self._terminate_button = PushButton(pin=config[Configuration.CFG_TERMINATE_BUTTON_PIN])

    def is_set(self):
        self._terminate_button.poll()
        # We're looking for a hold click (long click)
        button_state = self._terminate_button.value()
        if button_state == PushButton.BUTTON_HOLD_CLICK:
            self.set_terminate_flag()
            logger.info("The terminate button has been pressed")
        return self._terminate_flag

    def set_terminate_flag(self):
        self._terminate_flag = True

    def set_terminated(self):
       self._terminated = True

    def is_terminated(self):
        return self._terminated


# This class should be used as a singleton
class LEDEngine:
    def __init__(self):
        self.engine_thread = None
        self._vm = None
        self._compiler = None
        self._last_error = None
        self._dev = None
        self._terminate_signal = TerminateEvent()

    @property
    def last_error(self):
        """
        Returns the last logged error message
        :return:
        """
        return self._last_error

    def compile(self, script_file):
        # Create a VM instance
        self._vm = script_vm.ScriptVM(script_file)

        # Compile the script (pass 1) of the current (main) thread
        self._compiler = script_compiler.ScriptCompiler(self._vm)
        rc = self._compiler.compile(script_file)
        if not rc:
            self._last_error = self._compiler.last_error
            return rc

        logger.info(f"Successfully compiled script {script_file}")
        return rc

    def execute(self, driver):
        """
        Execute the compiled script on a separate thread
        :return: True if the script started. Otherwise, False.
        """
        #
        self._dev = driver
        try:
            # self.engine_thread = led_engine_thread.LEDEngineThread(1, "LEDEngineThread", self._vm)
            # self.engine_thread.start()

            # We need a LED driver and a terminate signal.
            # Use configuration to determine which driver to use. Wire to DotStar initially.

            cpu = script_cpu_led.ScriptCPULED(self._dev, self._vm, self._terminate_signal)
            # TODO Consider running the script on a MicroPython _thread.
            # This will be required to support a "break in" button.
            cpu.run()
        except KeyboardInterrupt:
            self._terminate_signal.set_terminate_flag()
            # TODO Wait for _thread to exit
            self._dev.clear()
            logger.info("ctrl-c terminated script execution")
            return False
        except Exception as e:
            logger.error("Unhandled exception starting LED engine")
            logger.error(e)
            sys.print_exception(e)
            return False
        return True
