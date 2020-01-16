import logging
from activeobjects.actor import Actor, event_decorator
from communication import events
from communication.pubsub import Publisher
from activeobjects.sensors.forceswitch_sm import ForceSwitchStateMachine
from activeobjects.sensors.no_sensor_sm import NOSensorSM
import struct

class ForceSwitch(Actor):
    """ Force sensor class as an active object """
    def __init__(self, name, id, topics, inputobj, outputobj, motor,  force_limit, monitor_interval, auto_init=False,):
        super(ForceSwitch, self).__init__(name=name)
        self._name = name
        self._id = id

        # events:
        self.posedge_event = events.ForceSwitchInputEvent(eventID=events.ForceSwitchInputEvents.PosEdge,
                                                     sender=self.name)
        self.negedge_event = events.ForceSwitchInputEvent(eventID=events.ForceSwitchInputEvents.NegEdge,
                                                     sender=self.name)
        self.init_ok_event = events.ForceSwitchInputEvent(eventID=events.ForceSwitchInputEvents.InitCheckOk,
                                                     sender=self.name)
        self.error_event = events.ForceSwitchInputEvent(eventID=events.ForceSwitchInputEvents.Error,
                                                   sender=self.name)

        self._auto_init = auto_init

        self._max_forcelimit = 400  # ToDo : need the real limits
        self._max_monitor_interval = 0.5
        self._min_monitor_interval = 0.02

        self.force_limit = force_limit
        self.monitor_interval = monitor_interval
        self.allowed_topics = ('State', 'Value', 'AnalogValue', 'StationErrorCode', 'StationErrorDescription',
                               'StationMessageCode', 'StationMessageDescription')
        self.topics = topics
        self.motor = motor

        self.logger = logging.getLogger(name)
        self.publisher = Publisher(self.topics, logger=self.logger,  name=name)           # publisher's instance

        self.inputobj = inputobj  # reference to the revpi driver input object
        self.outputobj = outputobj  # reference to the revpi driver output object

        # self.sensor_sm = ForceSwitchStateMachine(self)
        self.sensor_sm = NOSensorSM(self)

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
    def force_limit(self):
        return self._force_limit

    @force_limit.setter
    def force_limit(self, new_force_limit):
        if (new_force_limit <= 0) or  (new_force_limit >= self._max_forcelimit):
            raise ValueError("Force liimit should be less then max: %s , but greater then zero.", self._max_forcelimit)
        self._force_limit = new_force_limit

    @property
    def monitor_interval(self):
        return self._monitor_interval

    @monitor_interval.setter
    def monitor_interval(self, new_monitor_interval):
        if (new_monitor_interval < self._min_monitor_interval) or (new_monitor_interval >= self._max_monitor_interval):
            raise ValueError("Monitor interval shoul be in the range from %s to %s.", self._min_monitor_interval, self._max_monitor_interval)
        self._monitor_interval = new_monitor_interval
        print(self._monitor_interval)

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
        current_value = self.inputobj.value

        self.publisher.publish(topic="AnalogValue", value=current_value, sender=self.name)
        if current_value >= self.force_limit:
            self._inputpos_cb()
        else:
            self._inputneg_cb()

    def is_greater_then_setpoint(self):
        current_value = self.inputobj.value
        self.publisher.publish(topic="AnalogValue", value=current_value, sender=self.name)
        if current_value >= self.force_limit:
            return True
        else:
            return False

    def _inputpos_cb(self):
        """ Fire an event PosEdge if the actual input's value is true"""
        self.handle_event(event=self.posedge_event)

    def _inputneg_cb(self):
        """ Fire an event NegEdge if the actual input's value is false"""
        self.handle_event(event=self.negedge_event)

    def init_check(self):
        # set output to 5v
        self.outputobj.value = 5000
        # read output
        current_output = self.outputobj.value
        if current_output == 5000:

            self.handle_event(event=self.init_ok_event)
            self.logger.info("Output voltage is %s V. Should be 5.0 V.", current_output / 1000)
        else:
            self.handle_event(event=self.error_event)
            self.logger.info("Output voltage is %s V. Should be 5.0 V.", current_output/1000)

    @event_decorator
    def handle_event(self, *args, **kwargs):
        self.sensor_sm.dispatch(*args, **kwargs)









