from activeobjects.actor import Actor, event_decorator
from communication.events import GenericServiceEvent
from communication.pubsub import Publisher
from communication import events
from activeobjects.actuators.blinker_sm import BlinkerStateMachine

import logging

class Blinker(Actor):
    """ Blinker class as an active object """
    def __init__(self, name, shutter, ontime=1.0, offtime=1.0, blinks_number=0, topics=None):
        super(Blinker, self).__init__(name=name)
        self._name = name
        self.ontime = ontime
        self.offtime = offtime
        self.blinks_number = blinks_number

        self.allowed_topics = ('State', 'Value', 'StationErrorCode', 'StationErrorDescription',
                               'StationMessageCode', 'StationMessageDescription')
        if topics is None:
            self.topics = self.allowed_topics
        else:
            self.topics = topics

        self.logger = logging.getLogger(self._name)

        self.publisher = Publisher(self.topics, logger=self.logger,  name=self._name)          # publisher instance

        # references to the objects, which the service needs
        self._shutter = shutter

        self.blinkerStateMachine = BlinkerStateMachine(self)

    @property
    def name(self):
        return self._name

    @property
    def ontime(self):
        return self._ontime

    @ontime.setter
    def ontime(self, new_ontime):
        # perform check
        self._ontime = new_ontime

    @property
    def offtime(self):
        return self._offtime

    @offtime.setter
    def offtime(self, new_offtime):
        # perform check
        self._offtime = new_offtime

    @property
    def blinks_number(self):
        return self._blinks_number

    @blinks_number.setter
    def blinks_number(self, new_blinks_number):
        # perform check
        self._blinks_number = new_blinks_number

    @property
    def shutter(self):
        return self._shutter

    def register_subscribers(self, topic, who, callback=None):
        if topic not in self.allowed_topics:
            raise ValueError("Unknown topic")
        self.publisher.register(topic, who, callback)

    def shutter_open(self):
        self.shutter.shutter_open()

    def shutter_close(self):
        self.shutter.shutter_close()

    @event_decorator
    def handle_event(self, *args, **kwargs):
        self.blinkerStateMachine.dispatch(*args, **kwargs)