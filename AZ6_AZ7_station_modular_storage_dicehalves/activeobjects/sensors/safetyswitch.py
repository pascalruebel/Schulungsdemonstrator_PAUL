import logging
from activeobjects.actor import Actor, event_decorator
from communication import events
from communication.pubsub import Publisher
from activeobjects.sensors.no_sensor_sm import NOSensorSM
from activeobjects.sensors.nc_sensor_sm import NCSensorSM


class SafetySwitch(Actor):
    """ Safety switch class as an active object """
    def __init__(self, name, id, topics, inputobj, auto_init=False, normally_open=True):
        super(SafetySwitch, self).__init__(name=name)
        self._name = name
        self._id = id

        self.allowed_topics = ('State', 'Value', 'StationErrorCode', 'StationErrorDescription',
                               'StationMessageCode', 'StationMessageDescription')
        self.topics = topics

        self._normally_open = normally_open
        self._auto_init = auto_init

        self.logger = logging.getLogger(name)
        self.publisher = Publisher(self.topics, logger=self.logger,  name=name)           # publisher's instance

        self.input_events = events.SimpleSensorInputEvent(events.SimpleSensorInputEvents.NoEvent, self._name)

        self.inputobj = inputobj  # reference to the revpi driver input object

        if normally_open:
            self.sensor_sm = NOSensorSM(self)               # Sensor's state machine instance for NO sensor
        else:
            self.sensor_sm = NCSensorSM(self)               # NC sensor (see state diagram in Documentation


    @property
    def normally_open(self):
        return self._normally_open

    @property
    def auto_init(self):
        return self._auto_init

    @normally_open.setter
    def normally_open(self, new_normally_open):
        self._normally_open = new_normally_open

    @property
    def topics(self):
        return self._topics

    @topics.setter
    def topics(self, new_topics):
        for topic in new_topics:
            if topic not in self.allowed_topics:
                raise ValueError("Unknown topic: {0}".format(topic))
        self._topics = new_topics

    @property
    def name(self):
        return self._name

    @property
    def id(self):
        return self._id

    def register_subscribers(self, topic, who, callback=None):
        if topic not in self.allowed_topics:
            raise ValueError("Unknown topic")
        self.publisher.register(topic, who, callback)

    def update_input(self):
        current_value = self.inputobj.get_value()
        if current_value:
            self._inputpos_cb()
        else:
            self._inputneg_cb()

    def _inputpos_cb(self):
        """ Fire an event PosEdge if the actual input's value is true"""
        posedge_event = events.SimpleSensorInputEvent(eventID=events.SimpleSensorInputEvents.PosEdge, sender=self.name)
        self.handle_event(event=posedge_event)

    def _inputneg_cb(self):
        """ Fire an event NegEdge if the actual input's value is false"""
        negedge_event = events.SimpleSensorInputEvent(eventID=events.SimpleSensorInputEvents.NegEdge, sender=self.name)
        self.handle_event(event=negedge_event)

    @event_decorator
    def handle_event(self, *args, **kwargs):
        self.sensor_sm.dispatch(*args, **kwargs)