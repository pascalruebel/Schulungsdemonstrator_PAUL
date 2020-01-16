import logging
from activeobjects.actor import Actor, event_decorator
from communication import events
from communication.pubsub import Publisher
from activeobjects.actuators.led_sm import SimpleLEDStateMachine


class SimpleLED(Actor):
    """ Simple LED class as an active object """

    def __init__(self, name, id, revpi_output, topics=None):
        super(SimpleLED, self).__init__(name=name)

        self._name = name
        self._id = id
        self._value = False
        self._opcuastate = "notInitialized"

        self.allowed_topics = ('State', 'Value')
        if topics is None:
            self.topics = self.allowed_topics
        else:
            self.topics = topics

        self.logger = logging.getLogger(self._name)

        self.publisher = Publisher(self.topics, logger=self.logger,  name=name)       # publisher instance
        self.input_events = events.SimpleLEDInputEvent(events.SimpleLEDInputEvents.NoEvent, self._name)

        self.revpi_output= revpi_output

        self._ledStateMachine = SimpleLEDStateMachine(self)

    def register_subscribers(self, topic, who, callback=None):
        if topic not in self.allowed_topics:
            raise ValueError("Unknown topic")
        self.publisher.register(topic, who, callback)

    def led_on(self):
        self.revpi_output.set_value(True)

    def led_off(self):
        self.revpi_output.set_value(False)

    @event_decorator
    def handle_event(self, *args, **kwargs):
        self._ledStateMachine.dispatch(*args, **kwargs)