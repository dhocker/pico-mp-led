#
# task_manager.py - MicroPython task (thread) manager
# © 2022 by Dave Hocker
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# See the LICENSE file for more details.
#


import _thread
import utime


class Task:
    """
    Base class for a task
    """
    def __init__(self):
        """
        Instance constructor
        """
        pass

    def run(self):
        """
        Called by the task manager every time slice.
        :return:
        """
        pass

    def terminate(self):
        """
        The task is being terminated
        :return:
        """
        pass


class TaskManager:
    """
    Thread-safe task manager that runs tasks on a separate thread
    """
    def __init__(self, time_slice: int = 100):
        """
        Constructor
        :param time_slice: time between executions of Task.run(), in milliseconds
        """
        self._task_list = []
        self._time_slice = time_slice # miliseconds
        self._task_list_lock = _thread.allocate_lock()

        # Set by main thread, read by task thread
        self._terminate = False
        # Set by task thread, read by main thread
        self._terminated = False

        # The task thread does not start until the first task is queued
        self._thread_id = None

    def _run_tasks(self):
        """
        Run all queued tasks until terminate is signaled
        :return:
        """
        while not self._terminate:
            # Only run tasks when the task list is locked
            self._task_list_lock.acquire()
            # Run tasks
            for t in self._task_list:
                t.run()
            self._task_list_lock.release()
            utime.sleep_ms(self._time_slice)

        # Terminate all tasks
        self._task_list_lock.acquire()
        for t in self._task_list:
            t.terminate()
        self._terminated = True
        self._task_list_lock.release()

    def add_task(self, task: Task):
        """
        Add a task to the task list
        :param task:
        :return:
        """
        self._task_list_lock.acquire()
        self._task_list.append(task)
        if self._thread_id is None:
            # Start the task thread. Note that the Pico can only run one thread.
            self._thread_id = _thread.start_new_thread(self._run_tasks, ())
        self._task_list_lock.release()

    def remove_task(self, task: Task):
        """
        Remove a task from the task list
        :param task:
        :return:
        """
        self._task_list_lock.acquire()
        self._task_list.remove(task)
        self._task_list_lock.release()

    def terminate_tasks(self):
        """
        Terminate all running tasks
        :return:
        """
        self._terminate = True
        # Wait for thread to signal all tasks terminated
        while not self._terminated:
            utime.sleep_ms(self._time_slice)

# Singleton instance of task manager
the_task_manager = TaskManager()