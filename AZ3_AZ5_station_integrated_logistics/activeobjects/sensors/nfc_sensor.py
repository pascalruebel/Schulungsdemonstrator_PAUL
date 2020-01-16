import logging
from activeobjects.actor import Actor, event_decorator

from communication.pubsub import Publisher
from activeobjects.sensors.nfc_sensor_sm import NFCSensorSM

from communication import events


class NFCSensor(Actor):
    """ NFC sensor class as an active object """
    def __init__(self, name, id, topics, hw_input, card_monitor, reader_monitor, auto_init=False, normally_open=True):
        super(NFCSensor, self).__init__(name=name)
        self._name = name
        self._hw_input = hw_input
        self._id = id
        self._auto_init = auto_init

        # events:
        self.nfc_posedge = events.ComplexSensorEvent(eventID=events.ComplexSensorEvents.PosEdge,
                                                     sender=self.name)
        self.nfc_negedge = events.ComplexSensorEvent(eventID=events.ComplexSensorEvents.NegEdge,
                                                     sender=self.name)
        self.nfc_nok = events.ComplexSensorEvent(eventID=events.ComplexSensorEvents.StatusNOK,
                                                 sender=self.name)
        self.nfc_ok = events.ComplexSensorEvent(eventID=events.ComplexSensorEvents.StatusOK,
                                                sender=self.name)


        self.allowed_topics = ('State', 'Value', 'StationErrorCode', 'StationErrorDescription',
                               'StationMessageCode', 'StationMessageDescription')
        self.topics = topics

        self.logger = logging.getLogger(name)
        self.publisher = Publisher(self.topics, logger=self.logger, name=name)  # publisher's instance

        self.card_monitor = card_monitor
        self.reader_monitor = reader_monitor

        if normally_open:
            self.sensor_sm = NFCSensorSM(self)  # Sensor's state machine instance for NO sensor
        else:
            # ToDo: NC functionality needs to be realiazed
            self.sensor_sm = NFCSensorSM(self)  # Sensor's state machine instance for NO sensor



    @property
    def normally_open(self):
        return self._normally_open

    @normally_open.setter
    def normally_open(self, new_normally_open):
        self._normally_open = new_normally_open

    @property
    def auto_init(self):
        return self._auto_init

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
    def revpi_input_name(self):
        return self._hw_input

    @property
    def id(self):
        return self._id

    def register_subscribers(self, topic, who, callback=None):
        if topic not in self.allowed_topics:
            raise ValueError("Unknown topic")
        self.publisher.register(topic, who, callback)

    def update_input(self):
        self.card_monitor.check_pos(pos_number=self._hw_input, cb_true=self._inputpos_cb, cb_false=self._inputneg_cb)

    def _inputpos_cb(self):
        """ Fire an event PosEdge if the actual input's value is true"""
        self.handle_event(event=self.nfc_posedge)

    def _inputneg_cb(self):
        """ Fire an event NegEdge if the actual input's value is false"""
        self.handle_event(event=self.nfc_negedge)

    def check_sensor(self):
        self.reader_monitor.check_reader(reader_number=self._hw_input, cb_true=self._sensor_ok, cb_false=self._sensor_nok)
        print("check sensor {0}",format(self.name) )

    def _sensor_ok(self):
        self.handle_event(event=self.nfc_ok)

    def _sensor_nok(self):
        self.handle_event(event=self.nfc_nok)

    @event_decorator
    def handle_event(self, *args, **kwargs):
        self.sensor_sm.dispatch(*args, **kwargs)






