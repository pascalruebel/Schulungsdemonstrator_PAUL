from threading import Timer

class MonitoringTimer(object):

    def __init__(self, name, interval, callback_fnc, repeatable=False, logger=None, *args, **kwargs):
        self._name = name
        self.interval = interval
        self.callback_fnc = callback_fnc
        self.repeatable = repeatable
        self.args = args
        self.kwargs = kwargs
        self._logger = logger

        self._timer = None

    @property
    def name(self):
        return self._name

    @property
    def interval(self):
        return self._interval

    @interval.setter
    def interval(self, new_interval):
        if new_interval >= 0:
            self._interval = new_interval
        else:
            self._interval = 0
            if self._logger is not None:
                self._logger.debug("%s : The interval should be positive, was set to zero.", self.name)

    @property
    def repeatable(self):
        return self._repeatable

    @repeatable.setter
    def repeatable(self, set_repeatable):
        if isinstance(set_repeatable, (bool,)):
            self._repeatable = set_repeatable

    def set_callback(self, callback_fnc=None, *args, **kwargs):
        if callback_fnc is not None:
            self.callback_fnc = callback_fnc
        self.args = args
        self.kwargs = kwargs

    def timer_alive(self):
        if self._timer is not None:
            return True
        else:
            return False

    def _callback(self):
        if self._logger is not None:
            self._logger.debug("%s: Timeout. A callback function %s was called.", self.name, self.callback_fnc.__name__)

        self.callback_fnc(*self.args, **self.kwargs)

        if self.repeatable:
            self.start()

    def cancel(self):
        if self._timer is not None:
            self._timer.cancel()
        if self._logger is not None:
            self._logger.debug("%s was stopped.", self.name)

    def start(self):
        if self._timer is not None:
            self._timer.cancel()
        self._timer = Timer(self.interval, self._callback)
        self._timer.start()
        if self._logger is not None:
            self._logger.debug("%s was started.", self.name)