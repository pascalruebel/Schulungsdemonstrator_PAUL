import threading
import time


class TimeoutTimerClass(threading.Timer):
    """ Simple timeout timer class """

    def __init__(self, time=None, callback=None):
        threading.Thread.__init__(self)
        self.event = threading.Event()
        self.time = time

        if callback is None:
            self._callback = self.default_callback

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, new_time):
        if new_time < 0:
            raise ValueError("Time can not be less then zero")
        if new_time is None:
            self._time = 1000
        self._time = new_time

    def default_callback(self):
        print("The timer has elapsed")


    # TODO : under construction, may be not needed