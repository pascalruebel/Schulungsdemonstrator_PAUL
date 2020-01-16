
import logging
from activeobjects.actor import Actor, event_decorator
from communication import events
from communication.pubsub import Publisher
from activeobjects.actuators.motor_sm import MotorStateMachine


class Motor(Actor):
    """ Motor class as an active object:

    rotate_cw - revpi output for rotating clockwise
    rotate_ccw - revpi output for rotating counterclockwise
    topics - list of topics for publishing

    """

    def __init__(self, name, id, rotate_cw, rotate_ccw, topics=None):
        super(Motor, self).__init__(name=name)

        self._name = name
        self._id = id

        self.allowed_topics = ('State', 'Value', 'StationErrorCode', 'StationErrorDescription',
                               'StationMessageCode', 'StationMessageDescription')
        if topics is None:
            self.topics = self.allowed_topics
        else:
            self.topics = topics

        self._rotate_cw = rotate_cw
        self._rotate_ccw = rotate_ccw

        self.logger = logging.getLogger(self._name)

        self._motorStateMachine = MotorStateMachine(self)
        self.publisher = Publisher(self.topics, logger=self.logger,  name=name)       # publisher instance
        self.input_events = events.SimpleMotorInputEvent(events.SimpleMotorInputEvents.NoEvent, self._name)


    def register_subscribers(self, topic, who, callback=None):
        if topic not in self.allowed_topics:
            raise ValueError("Unknown topic")
        self.publisher.register(topic, who, callback)

    def motor_cw(self):
        self._rotate_cw.set_value(True)
        self._rotate_ccw.set_value(False)

    def motor_ccw(self):
        self._rotate_ccw.set_value(True)
        self._rotate_cw.set_value(False)

    def motor_stop(self):

        self._rotate_ccw.set_value(False)
        self._rotate_cw.set_value(False)

    @event_decorator
    def handle_event(self, *args, **kwargs):
        self._motorStateMachine.dispatch(*args, **kwargs)


