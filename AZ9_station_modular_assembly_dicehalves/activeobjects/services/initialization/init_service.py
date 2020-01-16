from activeobjects.actor import Actor, event_decorator
from communication.pubsub import Publisher
from activeobjects.services.initialization.init_service_sm import InitServiceStateMachine
import logging


class InitService(Actor):
    """ InitService class as an active object """
    def __init__(self, name, dev_list, enable_timeout=False, timeout_interval=600, topics=None):
        super(InitService, self).__init__(name=name)
        self._name = name
        self.enable_timeout = enable_timeout
        self.timeout_interval = timeout_interval

        self.callable_services = dict()  # dict of services that can be called from this service
        self.service_users = dict()  # dict of service users

        self._dev_list = dev_list  # list of devices for initialization

        self.allowed_topics = ('eventID', 'StationErrorCode', 'StationErrorDescription',
                               'StationMessageCode', 'StationMessageDescription', 'InitServiceState')

        if topics is None:
            self.topics = self.allowed_topics
        else:
            self.topics = topics

        self.logger = logging.getLogger(self._name)

        self.publisher = Publisher(self.topics, logger=self.logger,  name=self._name)          # publisher instance

        self.initServiceStateMachine = InitServiceStateMachine(self, self.enable_timeout, self.timeout_interval, devices_list=self.dev_list)

    @property
    def name(self):
        return self._name

    @property
    def dev_list(self):
        return self._dev_list

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
        self.initServiceStateMachine.dispatch(*args, **kwargs)



