import logging
from activeobjects.actor import Actor, event_decorator
from communication.pubsub import Publisher
from activeobjects.press.press_sm import PressStateMachine


class Press(Actor):
    """ Press class as an active object """

    def __init__(self, name, motor, uppos_sensor, endswitch_sensor, force_sensor, enable_timeout=False, timeout_interval=600, topics=None):
        super(Press, self).__init__(name=name)

        self._name = name
        self.enable_timeout = enable_timeout
        self.timeout_interval = timeout_interval

        self.allowed_topics = ('PressState', 'State', 'StationErrorCode', 'StationErrorDescription',
                               'StationMessageCode', 'StationMessageDescription')
        if topics is None:
            self.topics = self.allowed_topics
        else:
            self.topics = topics

        self.motor = motor
        self.uppos_sensor = uppos_sensor
        self.endswitch_sensor = endswitch_sensor
        self.force_sensor = force_sensor

        self.logger = logging.getLogger(self._name)

        self.publisher = Publisher(self.topics, logger=self.logger, name=name)  # publisher instance

        self._pressStateMachine = PressStateMachine(self, self.enable_timeout, self.timeout_interval)


    def register_subscribers(self, topic, who, callback=None):
        if topic not in self.allowed_topics:
            raise ValueError("Unknown topic")
        self.publisher.register(topic, who, callback)

    @event_decorator
    def handle_event(self, *args, **kwargs):
        self._pressStateMachine.dispatch(*args, **kwargs)


