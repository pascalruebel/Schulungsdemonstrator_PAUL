import abc


class SimpleSensorState(metaclass=abc.ABCMeta):
    """ Abstract State class for a simple sensor """
    def __init__(self, isSubstate=False):
        self._isSubstate = isSubstate

    @property
    def isSubstate(self):
        return self._isSubstate

    @abc.abstractmethod
    def initialize(self):
        raise NotImplemented

    @abc.abstractmethod
    def positive_edge(self):
        raise NotImplemented

    @abc.abstractmethod
    def negative_edge(self):
        raise NotImplemented

    @abc.abstractmethod
    def error(self):
        raise NotImplemented

    @abc.abstractmethod
    def acknowledge(self):
        raise NotImplemented

    @abc.abstractmethod
    def update(self):
        raise NotImplemented

    # enter/exit actions (UML specification)
    def enter_action(self):
        pass

    def exit_action(self):
        pass