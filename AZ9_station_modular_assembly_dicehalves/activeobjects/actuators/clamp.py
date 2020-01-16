import logging
from activeobjects.actor import Actor, event_decorator
from communication.pubsub import Publisher
from activeobjects.actuators.clamp_sm import SimpleClampStateMachine


class SimpleClamp(Actor):
    """ Simple Clamp class as an active object """

    def __init__(self, name, id, revpi_output, pwm=False, topics=None):
        super(SimpleClamp, self).__init__(name=name)

        self._name = name
        self._id = id
        self._value = False
        self._opcuastate = "notInitialized"
        self._pwm = pwm

        self.allowed_topics = ('State', 'Value', 'StationErrorCode', 'StationErrorDescription',
                               'StationMessageCode', 'StationMessageDescription')
        if topics is None:
            self.topics = self.allowed_topics
        else:
            self.topics = topics

        self.logger = logging.getLogger(self._name)

        self.publisher = Publisher(self.topics, logger=self.logger,  name=name)       # publisher instance

        self.revpi_output= revpi_output

        self._ledStateMachine = SimpleClampStateMachine(self)

    def register_subscribers(self, topic, who, callback=None):
        if topic not in self.allowed_topics:
            raise ValueError("Unknown topic")
        self.publisher.register(topic, who, callback)

    def clamp_close(self):
        if self._pwm:
            self.revpi_output.value = 100
        else:
            self.revpi_output.value = True

    def clamp_open(self):
        if self._pwm:
            self.revpi_output.value = 0
        else:
            self.revpi_output.value = False

    @event_decorator
    def handle_event(self, *args, **kwargs):
        self._ledStateMachine.dispatch(*args, **kwargs)