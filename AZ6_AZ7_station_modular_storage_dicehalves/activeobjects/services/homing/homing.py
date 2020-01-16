import logging
from activeobjects.actor import Actor, event_decorator
from communication.pubsub import Publisher
from activeobjects.services.homing.homing_sm import HomingServiceStateMachine

from threading import Timer


class HomingService(Actor):
    """ HomingService class as an active object """
    def __init__(self, name,  rack, carriage, sensorCarriageOccupied, enable_timeout=False, timeout_interval=600, topics=None):
        super(HomingService, self).__init__(name=name)
        self._name = name
        self.enable_timeout = enable_timeout
        self.timeout_interval = timeout_interval

        self.serviceState = "Ready"

        self.callable_services = dict()  # dict of services that can be called from this service
        self.service_users = dict()  # dict of service users

        self.allowed_topics = ('eventID', 'StationErrorCode', 'StationErrorDescription',
                               'StationMessageCode', 'StationMessageDescription', 'HomeServiceState')
        if topics is None:
            self.topics = self.allowed_topics
        else:
            self.topics = topics

        self.logger = logging.getLogger(self._name)

        self.publisher = Publisher(self.topics, logger=self.logger,  name=self._name)          # publisher instance

        # references to the objects, which the service needs
        self._rack = rack
        self._carriage = carriage
        self._sensorCarriageOccupied = sensorCarriageOccupied

        self.homingServiceStateMachine = HomingServiceStateMachine(self, enable_timeout, timeout_interval)

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
    def rack(self):
        return self._rack

    @property
    def carriage(self):
        return self._carriage

    @property
    def sensorCarriageOccupied(self):
        return self._sensorCarriageOccupied

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
        self.homingServiceStateMachine.dispatch(*args, **kwargs)





