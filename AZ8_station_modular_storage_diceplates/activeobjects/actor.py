import queue
import threading
from functools import wraps
import logging


def event_decorator(method):
    """Decorator to enqueue method calls in Actor instances. """
    @wraps(method)
    def enqueue_call(self, *args, **kwargs):
        args = list(args)
        args.insert(0, self)
        self._commands.put((method, args, kwargs))
    return enqueue_call


class Actor(threading.Thread):
    """A simple implementation of the active object design pattern."""

    def __init__(self, name):
        threading.Thread.__init__(self, name=name, daemon=True)
        self._commands = queue.Queue()
        self._must_stop = False

    @event_decorator
    def stop(self):
        self._must_stop = True

    def run(self):
        while not self._must_stop:
            cmd, args, kwargs = self._commands.get()
            cmd(*args, **kwargs)
