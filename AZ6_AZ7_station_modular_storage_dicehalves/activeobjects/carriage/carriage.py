from utils.logger import Logger
from activeobjects.actor import Actor, event_decorator
from communication import events
from communication.pubsub import Publisher
from activeobjects.carriage.carriage_sm import CarriageStateMachine
import logging

class Carriage(Actor):
    """ Carriage class as an active object """

    def __init__(self, name, sensor_rack, sensor_front, motor, topics=None):
        super(Carriage, self).__init__(name=name)
        self._name = name

        self.allowed_topics = ('CarriageState','State', 'StationErrorCode', 'StationErrorDescription',
                               'StationMessageCode', 'StationMessageDescription')
        if topics is None:
            self.topics = self.allowed_topics
        else:
            self.topics = topics

        # references to the objects, of which the carriage consists
        self.rackSensor = sensor_rack
        self.frontSensor = sensor_front
        self.motor = motor

        self.logger = logging.getLogger(self._name)
        self.publisher = Publisher(self.topics, logger=self.logger,  name=name)          # publisher instance
        self.carriage_events = events.CarriageEvent(events.CarriageEvents.NoEvent, self._name)

        self._carriageStateMachine = CarriageStateMachine(self)

    def register_subscribers(self, topic, who, callback=None):
        if topic not in self.allowed_topics:
            raise ValueError("Unknown topic")
        self.publisher.register(topic, who, callback)

    @event_decorator
    def handle_event(self, *args, **kwargs):
        self._carriageStateMachine.dispatch(*args, **kwargs)


