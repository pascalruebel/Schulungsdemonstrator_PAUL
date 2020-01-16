# from utils.logger import Logger
from activeobjects.actor import Actor, event_decorator
from communication.events import GenericServiceEvent
from communication.pubsub import Publisher
from activeobjects.services.storage.storage_service_sm import StorageDicePlateStateMachine
from communication import events

from threading import Timer

import logging

class StorageDicePlateService(Actor):
    """ InitService class as an active object """
    def __init__(self, name, storageracklist, enable_timeout=False, timeout_interval=600, topics=None):
        super(StorageDicePlateService, self).__init__(name=name)
        self._name = self.__class__.__name__
        self.enable_timeout = enable_timeout
        self.timeout_interval = timeout_interval
		
        self.allowed_topics = ('eventID', 'StationErrorCode', 'StationErrorDescription', 'StationMessageCode', 'StationMessageDescription', 'StorageMaterialState')

        self.callable_services = dict()  # dict of services that can be called from this service
        self.service_users = dict()  # dict of service users

        if topics is None:
            self.topics = self.allowed_topics
        else:
            self.topics = topics

        self.logger = logging.getLogger(self._name)

        self.publisher = Publisher(self.topics, logger=self.logger,  name=self._name)          # publisher instance

        # references to the objects, which the service needs
        self._storageracklist = storageracklist
		
        self.storageDicePlateStateMachine = StorageDicePlateStateMachine(self, enable_timeout=self.enable_timeout, timeout_interval=self.timeout_interval, storageracklist=self._storageracklist)

    @property
    def name(self):
        return self._name

    @property
    def enable_timeout(self):
        return self._enable_timeout

    @enable_timeout.setter
    def enable_timeout(self, new_enable_timeout):
        if isinstance(new_enable_timeout, bool):
            self._enable_timeout = new_enable_timeout

    @property
    def timeout_interval(self):
        return self._timeout_interval

    @timeout_interval.setter
    def timeout_interval(self, new_timeout_interval):
        if new_timeout_interval >= 0.0:
            self._timeout_interval = new_timeout_interval		
		
    @property
    def storageracklist(self):
        return self._storageracklist

    def register_subscribers(self, topic, who, callback=None):
        if topic not in self.allowed_topics:
            raise ValueError("Unknown topic")
        self.publisher.register(topic, who, callback)

    def register_services(self, service_index, service_interface):
        """ Register services to be called from this service """
        self.callable_services[service_index] = service_interface

    def setup_service(self, service_index, service_interface):
        """ Setup of this service as callable from another service """
        self.service_users[service_index] = service_interface

    @event_decorator
    def handle_event(self, *args, **kwargs):
        self.storageDicePlateStateMachine.dispatch(*args, **kwargs)




