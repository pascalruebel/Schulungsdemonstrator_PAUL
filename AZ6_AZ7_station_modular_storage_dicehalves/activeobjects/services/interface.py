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
        self._service_event = events.GenericServiceEvent(eventID=events.GenericServiceEvents.Error,
                                                 sender=self._service.name,
                                                 service_index=self._service_index)

    @property
    def service_name(self):
        return self._service_name

    @property
    def serviceuser_name(self):
        return self._serviceuser_name

    def execute(self):
        # execute_event = events.GenericServiceEvent(eventID=events.GenericServiceEvents.Execute, sender=self._service_user.name, service_index=self._service_index)
        # self._service.handle_event(event=execute_event)
        self._service_event.eventID = events.GenericServiceEvents.Execute
        self._service_event.sender = self._service_user.name
        self._service_event.service_index = self._service_index

        self._service.handle_event(event=self._service_event)

    def cancel(self):
        # cancel_event = events.GenericServiceEvent(eventID=events.GenericServiceEvents.Cancel, sender=self._service_user.name, service_index=self._service_index)
        # self._service.handle_event(event=cancel_event)
        self._service_event.eventID = events.GenericServiceEvents.Cancel
        self._service_event.sender = self._service_user.name
        self._service_event.service_index = self._service_index

        self._service.handle_event(event=self._service_event)

    def done(self):
        # done_event = events.GenericServiceEvent(eventID=events.GenericServiceEvents.Done,
        #                                         sender=self._service.name,
        #                                         service_index=self._service_index)
        self._service_event.eventID = events.GenericServiceEvents.Done
        self._service_event.sender = self._service.name
        self._service_event.service_index = self._service_index

        self._service_user.handle_event(event=self._service_event)

    def error(self, init_required=False):

        # self.error_event = events.GenericServiceEvent(eventID=events.GenericServiceEvents.Error,
        #                                          sender=self._service.name,
        #                                          service_index=self._service_index,
        #                                          parameters_list=[init_required])
        #
        # self.error_event.parameters_list = [True]
        # print("in interface", self.error_event)
        # self._service_user.handle_event(event=self.error_event)

        self._service_event.eventID = events.GenericServiceEvents.Error
        self._service_event.sender = self._service.name
        self._service_event.service_index = self._service_index
        self._service_event.parameters_list = [init_required]

        self._service_user.handle_event(event=self._service_event)

