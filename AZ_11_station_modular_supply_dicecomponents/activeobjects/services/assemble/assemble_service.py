from activeobjects.actor import Actor, event_decorator
from communication.pubsub import Publisher
from activeobjects.services.assemble.assemble_service_sm import AssembleServiceStateMachine

import logging


class AssembleService(Actor):
    """ AssembleService class as an active object """
    def __init__(self, name, complete_button, abort_button, enable_timeout=False, timeout_interval=600, topics=None):
        super(AssembleService, self).__init__(name=name)
        self._name = name

        self.serviceState = "Ready"

        self.enable_timeout = enable_timeout
        self.timeout_interval = timeout_interval

        self.callable_services = dict()  # dict of services that can be called from this service
        self.service_users = dict()  # dict of service users

        self.allowed_topics = ('eventID', 'StationErrorCode', 'StationErrorDescription',
                               'StationMessageCode', 'StationMessageDescription', 'AssembleServiceState')
        if topics is None:
            self.topics = self.allowed_topics
        else:
            self.topics = topics

        self.logger = logging.getLogger(self._name)

        self.publisher = Publisher(self.topics, logger=self.logger,  name=self._name)          # publisher instance

        self._complete_button = complete_button
        self._abort_button = abort_button

        self.assembleServiceStateMachine = AssembleServiceStateMachine(self, self.enable_timeout, self.timeout_interval)

    @property
    def name(self):
        return self._name

    @property
    def complete_button(self):
        return self._complete_button

    @property
    def abort_button(self):
        return self._abort_button

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
        self.assembleServiceStateMachine.dispatch(*args, **kwargs)