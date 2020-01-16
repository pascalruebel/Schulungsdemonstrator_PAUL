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

	# Add execute method with params and pass it to the generic service event		
    def execute(self, parameters_list=None, service_process=None):
        execute_event = events.GenericServiceEvent(eventID=events.GenericServiceEvents.Execute, sender=self._service_user.name, service_index=self._service_index, parameters_list=parameters_list, service_process=service_process)
        self._service.handle_event(event=execute_event)


    def cancel(self):
        cancel_event = events.GenericServiceEvent(eventID=events.GenericServiceEvents.Cancel, sender=self._service_user.name, service_index=self._service_index)
        self._service.handle_event(event=cancel_event)


    def done(self):
        done_event = events.GenericServiceEvent(eventID=events.GenericServiceEvents.Done, sender=self._service_user.name, service_index=self._service_index)
        self._service_user.handle_event(event=done_event)


    def error(self, init_required=False):
        error_event = events.GenericServiceEvent(eventID=events.GenericServiceEvents.Error, sender=self._service_user.name, service_index=self._service_index, parameters_list=[init_required])
        self._service_user.handle_event(event=error_event)

