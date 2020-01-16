from activeobjects.actor import Actor, event_decorator
from communication.pubsub import Publisher
from activeobjects.services.to_position.to_pos_sm import ToPosStateMachine
from communication import events

import logging

class ToPosService(Actor):
    """ ToPosService class as an active object """
    def __init__(self, name,  sensorPos, led, blinker, topics=None):
        super(ToPosService, self).__init__(name=name)
        self._name = name

        self.callable_services = dict()  # dict of services that can be called from this service
        self.service_users = dict()  # dict of service users

        self.allowed_topics = ('eventID', 'StationErrorCode', 'StationErrorDescription',
                               'StationMessageCode', 'StationMessageDescription',
                               'ToPosition1ServiceState', 'ToPosition2ServiceState', 'ToPosition3ServiceState')
        if topics is None:
            self.topics = self.allowed_topics
        else:
            self.topics = topics

        self.logger = logging.getLogger(self._name)
        self.publisher = Publisher(self.topics, logger=self.logger,  name=self._name)          # publisher instance

        # references to the objects, which the service needs
        self._sensorPos= sensorPos
        self._led = led
        self._blinker = blinker

        self.toPosStateMachine = ToPosStateMachine(self)

    @property
    def name(self):
        return self._name

    @property
    def sensorPos(self):
        return self._sensorPos

    @property
    def led(self):
        return self._led

    @property
    def blinker(self):
        return self._blinker

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
        self.toPosStateMachine.dispatch(*args, **kwargs)

