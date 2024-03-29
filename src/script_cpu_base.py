#
# AtHomeLED - LED script engine
# Copyright © 2016, 2020  Dave Hocker
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# See the LICENSE file for more details.
#

#
# Script cpu (executes compiled scripts)
#

import time
import datetime
import mp_logging as logging
import random

logger = logging.getLogger("led")

class ScriptCPUBase:
    def __init__(self, leddev, vm, terminate_event):
        """
        Constructor
        :param leddev: A LED device driver instance (e.g. ws2811 or dotstar)
        :param vm: A script VM instance
        :param terminate_event: A threading event to be tested for termination
        :return: None
        """
        self._leddev = leddev
        self._vm = vm
        self._terminate_event = terminate_event
        # This is the equivalent of the next instruction address
        self._stmt_index = 0
        # Do-For-N control
        self._do_for_n_active = -1
        self._do_for_n_count = []
        self._do_for_n_stmt = []
        # Do-For control
        self._do_for_active = -1
        self._do_for_elapsed_time = []
        self._do_for_start_time = []
        self._do_for_stmt = []
        # Do-At control
        self._do_at_active = False
        self._do_at_stmt = -1
        # Do-Until control
        self._do_until_active = False
        self._run_until_time = None
        self._do_until_stmt = -1
        # Do-forever control
        self._do_forever_stmt = -1

        random.seed()

        # Valid statements and their handlers
        self._valid_stmts = {
            "color": None,
            "value": None,
            "import": None,
            "logmessage": self.logmessage_stmt,
            "do-for-n": self.do_for_n_stmt,
            "do-for-n-end": self.do_for_n_end_stmt,
            "do-for": self.do_for_stmt,
            "do-for-end": self.do_for_end_stmt,
            "do-at": self.do_at_stmt,
            "do-at-end": self.do_at_end_stmt,
            "do-until": self.do_until_stmt,
            "do-until-end": self.do_until_end_stmt,
            "do-forever": self.do_forever_stmt,
            "do-forever-end": self.do_forever_end_stmt,
            "select-one": self.select_one_stmt,
            "select-one-end": self.select_one_end_stmt,
            "pause": self.pause_stmt,
            "reset": self.reset_stmt,
        }

    def run(self):
        """
        Run the statements in the VM
        :return:
        """
        logger.info("Virtual CPU running...")
        # The statement index is like an instruction address
        next_index = self._stmt_index

        # Run CPU until termination is signaled by main thread
        while not self._terminate_event.is_set():
            stmt = self._vm.stmts[self._stmt_index]
            # Ignore statements with no handler
            if self._valid_stmts[stmt[0]] is not None:
                # The statement execution sets the next statement index
                next_index = self._execute_stmt(stmt)
                # If the statement threw an exception end the script
                if next_index < 0:
                    logger.error("Virtual CPU stopped due to error")
                    break
            else:
                # Unrecognized statements are treated as no-ops.
                # Since the compile phase fails bad statements, the
                # only reason to be here is for a statement that
                # has not yet been implemented.
                logger.error(f"{stmt[0]} statement is not implemented")
                next_index = self._stmt_index + 1

            # End of program check
            next_index = self.end_of_program_check(next_index)
            if next_index >= len(self._vm.stmts):
                # Time to terminate the script
                break

            # This sets the next statement
            self._stmt_index = next_index

        # End of script error checks iff end of script reached
        if not self._terminate_event.is_set():
            if self._do_for_active >= 0:
                logger.error(f"{self._do_for_active + 1} unterminated do-for statements")

        logger.info("Virtual CPU stopped")
        self._reset()
        self._terminate_event.set_terminated()
        return next_index > 0

    def _execute_stmt(self, stmt):
        """
        Execute a script statement
        @param stmt: A list of the statements tokens.
        @return: Returns the next statement index.
        """
        logger.debug(stmt)
        next_index = self._valid_stmts[stmt[0]](stmt)
        return next_index

    def _reset(self):
        """
        Reset all LED channels to value zero.
        This should turn everything off.
        :return:
        """
        self._leddev.clear()
        logger.info("All LEDs reset")

    @staticmethod
    def _datetime_now():
        """
        MicroPython does not support datetime.now(), so this is the work around.
        :return:
        """
        # TODO How does the time get set when there is no host?
        now = datetime.datetime.now(tz=ScriptCPUBase._tz())
        return now

    @staticmethod
    def _tz():
        """
        Generate a timezone instance for local time. Since everything is maintained
        in local time, the timezone value is 0.
        :return: A timezone instance
        """
        # Hardwired to local time
        return datetime.timezone(datetime.timedelta(hours=0))

    def logmessage_stmt(self, stmt):
        """
        Write a message to the log file
        :param stmt:
        :return:
        """
        tokens = stmt[1].split()
        msg = stmt[1]
        # Do substitution of $vars (anything that starts with $)
        for t in tokens:
            if t[0] == '$':
                sub_value = t
                symbol = t[1:]
                if symbol in self._vm.colors:
                    sub_value = str(self._vm.colors[symbol])
                elif symbol in self._vm.defines:
                    sub_value = str(self._vm.defines[symbol])
                msg = msg.replace(t, sub_value)
        logger.info(msg)
        return self._stmt_index + 1

    def do_for_n_stmt(self, stmt):
        """
        Execute a script block for a given number of iterations.
        :param stmt: stmt[1] is the number of iterations.
        :return:
        """

        self._do_for_n_stmt.append(self._stmt_index)
        self._do_for_n_count.append(stmt[1])
        self._do_for_n_active += 1

        return self._stmt_index + 1

    def do_for_n_end_stmt(self, stmt):
        """
        Foot of Do-For-N loop. Repeat script block until count expires.
        :return:
        """
        if self._do_for_n_active >= 0:
            # A Do-For-N statement is active.
            # When the count expires...
            self._do_for_n_count[self._do_for_n_active] -= 1
            if self._do_for_n_count[self._do_for_n_active] <= 0:
                # Stop running the script block and set the stmt index to the next statement
                logger.debug("Do-For-N loop ended")
                self._do_for_n_active -= 1
                self._do_for_n_stmt.pop()
                self._do_for_n_count.pop()
                next_stmt = self._stmt_index + 1
            else:
                logger.debug(f"Do-For-N {self._do_for_n_count[self._do_for_n_active]}")
                # Loop back to top of script block
                next_stmt = self._do_for_n_stmt[self._do_for_n_active] + 1
        else:
            next_stmt = self._stmt_index + 1

        return next_stmt

    def do_for_stmt(self, stmt):
        """
        Execute a script block for a given duration of time.
        :param stmt: stmt[1] is the duration time struct.
        :return:
        """

        self._do_for_stmt.append(self._stmt_index)

        # Determine the end time
        # Use the start time and a timedelta that allows second accuracy
        now = ScriptCPUBase._datetime_now()
        self._do_for_elapsed_time.append(datetime.timedelta(seconds=(stmt[1].hour * 60 * 60) + (stmt[1].minute * 60) + stmt[1].second))
        self._do_for_start_time.append(now)
        self._do_for_active += 1
        logger.debug(f"Do-For {str(self._do_for_elapsed_time[self._do_for_active])}")

        return self._stmt_index + 1

    def do_for_end_stmt(self, stmt):
        """
        Foot of Do-For loop. Repeat script block until time expires.
        :return:
        """
        if self._do_for_active >= 0:
            # A Do-For statement is active.
            # When the duration expires...
            now = ScriptCPUBase._datetime_now()
            elapsed = now - self._do_for_start_time[self._do_for_active]
            # TODO Include seconds in duration
            if elapsed >= self._do_for_elapsed_time[self._do_for_active]:
                # Stop running the script block and set the stmt index to the next statement
                logger.debug(f"Do-For loop ended at {str(now)}")
                self._do_for_active -= 1
                self._do_for_stmt.pop()
                self._do_for_elapsed_time.pop()
                self._do_for_start_time.pop()
                next_stmt = self._stmt_index + 1
            else:
                # Loop back to top of script block
                next_stmt = self._do_for_stmt[self._do_for_active] + 1
        else:
            next_stmt = self._stmt_index + 1

        return next_stmt

    def do_at_stmt(self, stmt):
        """
        Executes a script block when a given time-of-day arrives.
        :param stmt: stmt[1] is a datetime defining the time of day. The hour and minute is
        all that is used.
        :return:
        """

        # If we are under Do-At control, ignore
        if self._do_at_active:
            return self._stmt_index + 1

        # Determine the start time
        now = ScriptCPUBase._datetime_now()
        run_start_time = datetime.datetime(now.year, now.month, now.day,
                                           stmt[1].hour, stmt[1].minute, stmt[1].second,
                                           tzinfo=ScriptCPUBase._tz())
        # If the start time is earlier than now, adjust to tomorrow
        if run_start_time < now:
            # Start is tomorrow
            run_start_time += datetime.timedelta(days=1)

        # We're now under Do-At control
        self._do_at_active = True
        self._do_at_stmt = self._stmt_index

        logger.info(f"Waiting until {str(run_start_time)}..." )

        # Wait for start time to arrive. Break out on termination signal.
        while not self._terminate_event.is_set():
            time.sleep(1.0)
            now = ScriptCPUBase._datetime_now()
            # The deltatime will be negative until we cross the Do-At time
            dt = now - run_start_time
            if (dt.days == 0) and (dt.seconds >= 0):
                logger.debug(f"Do-At begins at {str(now)}")

                # On to the next sequential statement
                break

        # Execution continues at the next statement after the Do-At
        return self._stmt_index + 1

    def do_at_end_stmt(self, stmt):
        """
        Serves as the foot of the Do-At loop.
        :param stmt:
        :return:
        """
        if not self._do_at_active:
            logger.error("No matching Do-At statement")
            return -1

        # Reset state. Turn off all LED channels.
        self._do_at_active = False
        self._reset()

        # Execution returns to the matching Do-At statement
        return self._do_at_stmt

    def do_until_stmt(self, stmt):
        """
        Executes a script block until a given time-of-day arrives.
        :param stmt: stmt[1] is a datetime defining the time of day. The hour and minute is
        all that is used.
        :return:
        """

        # If we are under Do-Until control, ignore
        if self._do_until_active:
            return self._stmt_index + 1

        # Determine the until time
        now = ScriptCPUBase._datetime_now()
        self._run_until_time = datetime.datetime(now.year, now.month, now.day,
                                                 stmt[1].hour, stmt[1].minute, stmt[1].second,
                                                 tzinfo=ScriptCPUBase._tz())
        # If the start time is earlier than now, adjust to tomorrow
        if self._run_until_time < now:
            # Until time is tomorrow
            self._run_until_time += datetime.timedelta(days=1)

        # We're now under Do-Until control
        self._do_until_active = True
        self._do_until_stmt = self._stmt_index

        logger.debug(f"Running until {str(self._run_until_time)}...")

        # Execution continues at the next statement after the Do-Until
        return self._stmt_index + 1

    def do_until_end_stmt(self, stmt):
        """
        Serves as the foot of the Do-Until loop.
        :param stmt:
        :return:
        """
        if not self._do_until_active:
            logger.error("No matching Do-Until statement")
            return -1

        # Terminate break out
        if self._terminate_event.is_set():
            return self._stmt_index + 1

        # Check for until time to arrive. Break out when it does.
        now = ScriptCPUBase._datetime_now()
        if now >= self._run_until_time:
            logger.debug(f"Do-Until occurs at {str(now)}")
            # On to the next sequential statement
            return self._stmt_index + 1

        # Execution returns to the matching Do-Until statement
        return self._do_until_stmt

    def end_of_program_check(self, next_index):
        """
        End of program occurs when the next statement index is past
        the end of the statement list.
        :param next_index:
        :return: Returns the next statement index to be executed. If RunAt
        is effective, the next index will point to the RunAt statement.
        If RunAt is not in effect, the next index will be the first statement
        past the end of the statement list.
        """
        if next_index >= len(self._vm.stmts):
            logger.info("End of script")

        return next_index

    def do_forever_stmt(self, stmt):
        """
        Executes the following script block until the program is terminated.
        """
        # There is no error checking here because it is all done in the compile phase.
        self._do_forever_stmt = self._stmt_index

        # Execution continues at the next statement after the Do-Forever
        return self._stmt_index + 1

    def do_forever_end_stmt(self, stmt):
        """
        Foot of the the do-forever block
        """
        return self._do_forever_stmt

    def select_one_stmt(self, stmt):
        """
        Randomly execute one statement from a list of statements.
        Token[1] is the index of the select_one_end statement and
        token[1] - _stmt_index is the number of statements in the list.
        @param stmt:
        @return:
        """
        # Randomly select a statement from the list
        number_stmts = stmt[1] - self._stmt_index - 1
        rindex = random.randint(0, number_stmts - 1)
        logger.debug(f"select-one: {rindex}")

        # Execute the selected statement
        selected_stmt = self._vm.stmts[self._stmt_index + 1 + rindex]
        # The next statement return value is ignored as it is only produced
        # by statements that are not supported within a select-one block.
        next_index = self._execute_stmt(selected_stmt)

        # The next statement is the select-one-end statement
        return stmt[1]

    def select_one_end_stmt(self, stmt):
        """
        Foot of a select-one block. Basically a no-op and place holder.
        @param stmt:
        @return:
        """
        return self._stmt_index + 1

    def pause_stmt(self, stmt):
        """
        Pause the script for a given amount of time
        """
        # Determine the time when the pause will end
        now = ScriptCPUBase._datetime_now()
        pause_time = datetime.timedelta(
            seconds=(stmt[1].hour * 60 * 60) + (stmt[1].minute * 60) + stmt[1].second)
        logger.debug(f"Pausing for {str(pause_time)}")

        end_time = ScriptCPUBase._datetime_now() + pause_time
        logger.debug(f"Pause ends at {str(end_time)}")

        # Wait for end of pause time to arrive. Break out on termination signal.
        now = ScriptCPUBase._datetime_now()
        while (not self._terminate_event.is_set()) and (now <= end_time):
            time.sleep(1.0)
            now = ScriptCPUBase._datetime_now()

        return self._stmt_index + 1

    def reset_stmt(self, stmt):
        """
        Reset all LED channels by sending zeroes
        """
        self._reset()
        return self._stmt_index + 1
