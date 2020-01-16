import abc
import logging
from activeobjects.actor import Actor, event_decorator
from communication import events
from communication.pubsub import Publisher
from activeobjects.actuators.rgb_led_sm import RGB_LEDStateMachine


class RGB_LED(Actor):
    """ RGB LED class as an active object """

    def __init__(self, name, id, revpi_red, revpi_green, revpi_blue, topics=None):
        super(RGB_LED, self).__init__(name=name)

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
        self.input_events = events.RGBLEDInputEvent(events.RGBLEDInputEvents.NoEvent, self._name)

        self.revpi_red= revpi_red
        self.revpi_green= revpi_green
        self.revpi_blue = revpi_blue

        self._rgbledStateMachine = RGB_LEDStateMachine(self)

    def register_subscribers(self, topic, who, callback=None):
        if topic not in self.allowed_topics:
            raise ValueError("Unknown topic")
        self.publisher.register(topic, who, callback)

    def red_on(self):
        self.revpi_red.value = 100
        self.revpi_green.value = 0
        self.revpi_blue.value = 0

    def green_on(self):
        self.revpi_red.value = 0
        self.revpi_green.value = 100
        self.revpi_blue.value = 0

    def yellow_on(self):
        self.revpi_red.value = 100
        self.revpi_green.value = 80
        self.revpi_blue.value = 0

    def purple_on(self):
        self.revpi_red.value = 100
        self.revpi_green.value = 0
        self.revpi_blue.value = 100
		
    def blue_on(self):
        self.revpi_red.value = 0
        self.revpi_green.value = 0
        self.revpi_blue.value = 100

    def led_off(self):
        self.revpi_red.value = 0
        self.revpi_green.value = 0
        self.revpi_blue.value = 0

    @event_decorator
    def handle_event(self, *args, **kwargs):
        self._rgbledStateMachine.dispatch(*args, **kwargs)

