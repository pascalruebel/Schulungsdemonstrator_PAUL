import abc
from communication import events

""" These classes are used to realize a modified command pattern"""


class Interface(metaclass=abc.ABCMeta):
    """ Abstract class for an Interface """
    @abc.abstractmethod
    def execute(self):
        raise NotImplemented

    @abc.abstractmethod
    def cancel(self):
        raise NotImplemented

    @abc.abstractmethod
    def done(self):
        raise NotImplemented

    @abc.abstractmethod
    def error(self):
        raise NotImplemented


class ServiceInterface(Interface):
    """ Binding service with the service user """
    def __init__(self, service_user, service, service_index):
        self._service_user = service_user
        self._service = service
        self._service_index = service_index
        self._service_name = self._service.name
        self._serviceuser_name = self._service_user.name

        self._execute_event = events.GenericServiceEvent(eventID=events.GenericServiceEvents.Execute,
                                                 sender=self._service_user.name,
                                                 service_index=self._service_index)
        self._cancel_event = events.GenericServiceEvent(eventID=events.GenericServiceEvents.Cancel,
                                                         sender=self._service_user.name,
                                                         service_index=self._service_index)
        self._done_event = events.GenericServiceEvent(eventID=events.GenericServiceEvents.Done,
                                                         sender=self._service.name,
                                                         service_index=self._service_index)
        self._error_event = events.GenericServiceEvent(eventID=events.GenericServiceEvents.Error,
                                                         sender=self._service.name,
                                                         service_index=self._service_index)

    @property
    def service_name(self):
        return self._service_name

    @property
    def serviceuser_name(self):
        return self._serviceuser_name

    def execute(self):
        self._service.handle_event(event=self._execute_event)

    def cancel(self):
        self._service.handle_event(event=self._cancel_event)

    def done(self):
        self._service_user.handle_event(event=self._done_event)

    def error(self, init_required=False):
        self._error_event.parameters_list = [init_required]
        self._service_user.handle_event(event=self._error_event)
