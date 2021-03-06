
from activeobjects.actor import Actor, event_decorator
from communication.pubsub import Publisher
from activeobjects.services.to_frontpos.to_frontpos_sm import ToFrontPosServiceStateMachine

import logging


class ToFrontPosService(Actor):
    """ ToFrontPosService class as an active object """
    def __init__(self, name, press, clamp, frontpos_sensor, presspos_sensor, blinker,  enable_timeout=False, timeout_interval=600, topics=None):
        super(ToFrontPosService, self).__init__(name=name)
        self._name = name
        self.enable_timeout = enable_timeout
        self.timeout_interval = timeout_interval

        self.serviceState = "Ready"

        self.callable_services = dict()  # dict of services that can be called from this service
        self.service_users = dict()  # dict of service users

        self.allowed_topics = ('eventID', 'StationErrorCode', 'StationErrorDescription',
                               'StationMessageCode', 'StationMessageDescription', 'ToFrontPosServiceState')
        if topics is None:
            self.topics = self.allowed_topics
        else:
            self.topics = topics

        self.logger = logging.getLogger(self._name)

        self.publisher = Publisher(self.topics, logger=self.logger,  name=self._name)          # publisher instance

        self._press= press
        self._clamp = clamp
        self._frontpos_sensor = frontpos_sensor
        self._presspos_sensor = presspos_sensor
        self.blinker = blinker

        self.pressServiceStateMachine = ToFrontPosServiceStateMachine(self, self.enable_timeout, self.timeout_interval)

    @property
    def name(self):
        return self._name

    @property
    def clamp(self):
        return self._clamp

    @property
    def press(self):
        return self._press

    @property
    def frontpos_sensor(self):
        return self._frontpos_sensor

    @property
    def presspos_sensor(self):
        return self._presspos_sensor

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
        self.pressServiceStateMachine.dispatch(*args, **kwargs)



