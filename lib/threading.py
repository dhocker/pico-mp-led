#
# micropython implementation of threading.Lock
#


import _thread


class Lock:
    def __new__(cls):
        return _thread.allocate_lock()


class Thread:
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None):
        self.target = target
        self.args = args
        self.kwargs = {} if kwargs is None else kwargs

    def start(self):
        _thread.start_new_thread(self.run, ())

    def run(self):
        self.target(*self.args, **self.kwargs)