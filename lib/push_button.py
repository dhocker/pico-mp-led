#
# push_button.py - a debounced, latching push button class
# © 2022 by Dave Hocker
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# See the LICENSE file for more details.
#


from machine import Pin
import utime
import _thread
from task_manager import Task, TaskManager, the_task_manager

class PushButton(Task):
    """
    A push button with debouncing. The button acts like a latching button.
    When a button press is detected, it is held until reset. The button press detection
    logic can differentiate a short-click and a hold (long) click.

    The code that monitors the button runs as a task on the task manager thread.
    """
    # State machine states
    STATE_START = 0
    STATE_TIMING_DOWN = 1
    STATE_TIMING_HOLD = 2

    # value() return values
    BUTTON_UP = 0
    BUTTON_SHORT_CLICK = 1
    BUTTON_HOLD_CLICK = 2

    def __init__(self, pin=16, short_click=50, hold_click=1000):
        """
        Create a push button instance
        :param pin: The GPIO pin where the push button is connected. This pin should
        be connected to the push button and the push button should be connected to 3.3V(out)
        which is hardware pin 36 of the Pico.
        :param short_click: Time, in ms, button must be down to register a short click
        :param hold_click: Time, in ms, until a hold click is registered
        """
        self._button = Pin(pin, Pin.IN, Pin.PULL_DOWN)
        self._state = PushButton.STATE_START
        self._down_time = 0
        self._up_time = 0
        self._elapsed_time = 0
        self._button_status = PushButton.BUTTON_UP
        self._short_click = short_click
        self._hold_click = hold_click

        # Button status lock
        self._status_lock = _thread.allocate_lock()

        # Queue the push button to run on the background task thread
        the_task_manager.add_task(self)

    def run(self):
        """
        Poll the button, run the state machine, update the button status.
        This method is run on the background task thread.
        :return:
        """
        self._status_lock.acquire()
        # True means down/pressed
        button_position = self._button.value()
        # print(f"button position: {button_position}")

        # State START
        if self._state == PushButton.STATE_START:
            if button_position:
                self._state = PushButton.STATE_TIMING_DOWN
                self._down_time = utime.ticks_ms()
                self._elapsed_time = 0
                self._button_status = PushButton.BUTTON_UP
                # print("Going to state_timing_down")
            else:
                # Button up, stay at START
                self._down_time = 0
                self._elapsed_time = 0
                # print("Staying at start")

        # State timing button down, short click
        elif self._state == PushButton.STATE_TIMING_DOWN:
            # print("At state_timing_down")
            if button_position:
                # Still down
                self._up_time = utime.ticks_ms()
                if utime.ticks_diff(self._up_time, self._down_time) >= self._short_click:
                    self._state = PushButton.STATE_TIMING_HOLD
                    # print("Going to state_timeing_hold")
                    self._button_status = PushButton.BUTTON_SHORT_CLICK
                    # print("Detected short click")
            else:
                # Button up, test for down or hold
                self._state = PushButton.STATE_START
                self._elapsed_time = utime.ticks_diff(utime.ticks_ms(), self._down_time)
                if self._elapsed_time >= self._short_click:
                    self._button_status = PushButton.BUTTON_SHORT_CLICK
                    # print("Detected short click")

        # State down/pressed, timing hold press
        elif self._state == PushButton.STATE_TIMING_HOLD:
            # print("At state_timing_hold")
            if button_position:
                # Still down
                self._up_time = utime.ticks_ms()
                if utime.ticks_diff(self._up_time, self._down_time) >= self._short_click:
                    self._state = PushButton.STATE_TIMING_HOLD
            else:
                # Button up, test for down or hold
                self._state = PushButton.STATE_START
                self._elapsed_time = utime.ticks_diff(utime.ticks_ms(), self._down_time)
                if self._elapsed_time >= self._hold_click:
                    self._button_status = PushButton.BUTTON_HOLD_CLICK
                    # print("Detected hold click")
                else:
                    self._button_status = PushButton.BUTTON_SHORT_CLICK

        else:
            pass

        self._status_lock.release()

    def terminate(self):
        """
        Terminate the push button monitor task
        :return:
        """
        the_task_manager.remove_task(self)

    def value(self):
        """
        Return the debounced button status. This method is thread-safe
        because it is only read. Its value is only set on the task thread.
        :return: See value() return values above
        """
        return self._button_status

    def reset(self):
        """
        Reset the button status so another click can be detected
        :return: None
        """
        self._status_lock.acquire()
        self._button_status = PushButton.BUTTON_UP
        self._status_lock.release()


def test():
    button = PushButton(pin=16)

    count = 0
    print("Press ctrl-c to terminate button test")
    try:
        while True:
            button.poll()
            button_status = button.value()
            if button_status == PushButton.BUTTON_SHORT_CLICK:
                count += 1
                print(f"Pressed {count} times")
                button.reset()
            elif button_status == PushButton.BUTTON_HOLD_CLICK:
                print(f"HOLD pressed")
                button.reset()
                count = 0
            # else:
            #     print(f"button status: {button_status}")
            utime.sleep(0.3)
    except KeyboardInterrupt:
        pass
    finally:
        del button
        button = None

    print("Button test ended")
