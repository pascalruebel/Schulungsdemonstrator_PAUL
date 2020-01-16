from activeobjects.sensors.abstract_sensor import ComplexSensorState
from utils import error_codes, message_codes
from communication import events

class NotInitialized(ComplexSensorState):
    """ Concrete State class for representing NotInitialized State"""

    def __init__(self, sensor_sm, sensor, super_sm=None, isSubstate=False):
        super(NotInitialized, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._sensor_sm = sensor_sm
        self._sensor = sensor
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    def enter_action(self):
        self._sensor.publisher.publish(topic="State", value="NotInitialized", sender=self._sensor.name)
        if self._sensor.auto_init:
            self._sensor_sm.set_state(self._sensor_sm.check_conn_state)

    def initialize(self):
        self._sensor.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._sensor_sm.set_state(self._sensor_sm.check_conn_state)

    def positive_edge(self):
        self._sensor.logger.debug("%s event in %s state", self.positive_edge.__name__, self.name)

    def negative_edge(self):
        self._sensor.logger.debug("%s event in %s state", self.negative_edge.__name__, self.name)

    def conn_ok(self):
        self._sensor.logger.debug("%s event in %s state", self.conn_ok.__name__, self.name)

    def conn_nok(self):
        self._sensor.logger.debug("%s event in %s state", self.conn_nok.__name__, self.name)

    def error(self):
        self._sensor.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._sensor_sm.init_required = True
        self._sensor_sm.set_state(self._sensor_sm.error_state)

    def acknowledge(self):
        self._sensor.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def update(self):
        self._sensor.logger.debug("%s event in %s state", self.update.__name__, self.name)

    def check_conn(self):
        self._sensor.logger.debug("%s event in %s state", self.check_conn.__name__, self.name)
        self._sensor_sm.set_state(self._sensor_sm.check_conn_state)


class Initialized(ComplexSensorState):
    """ Concrete State class for representing Initialized State"""

    def __init__(self, sensor_sm, sensor, super_sm=None, isSubstate=False):
        super(Initialized, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._sensor_sm = sensor_sm
        self._sensor = sensor
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    def enter_action(self):
        self._sensor.publisher.publish(topic="State", value="Initialized", sender=self._sensor.name)
        self._sensor_sm.init_required = False
        self._sensor.update_input()

    def initialize(self):
        self._sensor.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._sensor.update_input()
        self._sensor_sm.set_state(self._sensor_sm.init_state)

    def positive_edge(self):
        self._sensor.logger.debug("%s event in %s state", self.positive_edge.__name__, self.name)
        self._sensor_sm.set_state(self._sensor_sm.sensoron_state)
        self._sensor.publisher.publish(topic="Value", value=True, sender=self._sensor.name)

    def negative_edge(self):
        self._sensor.logger.debug("%s event in %s state", self.negative_edge.__name__, self.name)
        self._sensor_sm.set_state(self._sensor_sm.sensoroff_state)
        self._sensor.publisher.publish(topic="Value", value=False, sender=self._sensor.name)

    def conn_ok(self):
        self._sensor.logger.debug("%s event in %s state", self.conn_ok.__name__, self.name)

    def conn_nok(self):
        self._sensor.logger.debug("%s event in %s state", self.conn_nok.__name__, self.name)
        self._sensor_sm.set_state(self._sensor_sm.nok_state)

    def error(self):
        self._sensor.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._sensor_sm.set_state(self._sensor_sm.error_state)

    def acknowledge(self):
        self._sensor.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def update(self):
        self._sensor.logger.debug("%s event in %s state", self.update.__name__, self.name)
        self._sensor_sm.set_state(self._sensor_sm.update_state)

    def check_conn(self):
        self._sensor.logger.debug("%s event in %s state", self.check_conn.__name__, self.name)
        self._sensor_sm.set_state(self._sensor_sm.check_conn_state)


class SensorOn(ComplexSensorState):
    """ Concrete State class for representing ON State"""

    def __init__(self, sensor_sm, sensor, super_sm=None, isSubstate=False):
        super(SensorOn, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._sensor_sm = sensor_sm
        self._sensor = sensor
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    def initialize(self):
        self._sensor.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._sensor_sm.set_state(self._sensor_sm.init_state)

    def positive_edge(self):
        self._sensor.logger.debug("%s event in %s state", self.positive_edge.__name__, self.name)

    def negative_edge(self):
        self._sensor.logger.debug("%s event in %s state", self.negative_edge.__name__, self.name)
        self._sensor_sm.set_state(self._sensor_sm.sensoroff_state)
        self._sensor.publisher.publish(topic="Value", value=False, sender=self._sensor.name)

    def conn_ok(self):
        self._sensor.logger.debug("%s event in %s state", self.conn_ok.__name__, self.name)

    def conn_nok(self):
        self._sensor.logger.debug("%s event in %s state", self.conn_nok.__name__, self.name)
        self._sensor_sm.set_state(self._sensor_sm.nok_state)

    def error(self):
        self._sensor.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._sensor_sm.set_state(self._sensor_sm.error_state)

    def acknowledge(self):
        self._sensor.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def update(self):
        self._sensor.logger.debug("%s event in %s state", self.update.__name__, self.name)
        self._sensor_sm.set_state(self._sensor_sm.update_state)

    def check_conn(self):
        self._sensor.logger.debug("%s event in %s state", self.check_conn.__name__, self.name)
        self._sensor_sm.set_state(self._sensor_sm.check_conn_state)


class SensorOff(ComplexSensorState):
    """ Concrete State class for representing OFF State"""

    def __init__(self, sensor_sm, sensor, super_sm=None, isSubstate=False):
        super(SensorOff, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._sensor_sm = sensor_sm
        self._sensor = sensor
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    def initialize(self):
        self._sensor.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._sensor_sm.set_state(self._sensor_sm.init_state)

    def positive_edge(self):
        self._sensor.logger.debug("%s event in %s state", self.positive_edge.__name__, self.name)
        self._sensor_sm.set_state(self._sensor_sm.sensoron_state)
        self._sensor.publisher.publish(topic="Value", value=True, sender=self._sensor.name)

    def negative_edge(self):
        self._sensor.logger.debug("%s event in %s state", self.negative_edge.__name__, self.name)

    def conn_ok(self):
        self._sensor.logger.debug("%s event in %s state", self.conn_ok.__name__, self.name)

    def conn_nok(self):
        self._sensor.logger.debug("%s event in %s state", self.conn_nok.__name__, self.name)
        self._sensor_sm.set_state(self._sensor_sm.nok_state)

    def error(self):
        self._sensor.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._sensor_sm.set_state(self._sensor_sm.error_state)

    def acknowledge(self):
        self._sensor.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def update(self):
        self._sensor.logger.debug("%s event in %s state", self.update.__name__, self.name)
        self._sensor_sm.set_state(self._sensor_sm.update_state)

    def check_conn(self):
        self._sensor.logger.debug("%s event in %s state", self.check_conn.__name__, self.name)
        self._sensor_sm.set_state(self._sensor_sm.check_conn_state)


class Error(ComplexSensorState):
    """ Concrete State class for representing ERROR State"""

    def __init__(self, sensor_sm, sensor, super_sm=None, isSubstate=False):
        super(Error, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._sensor_sm = sensor_sm
        self._sensor = sensor
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    def enter_action(self):
        self._sensor.publisher.publish(topic="State", value="Error", sender=self._sensor.name)

    def initialize(self):
        self._sensor.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        # self._sensor_sm.set_state(self._sensor_sm.init_state)

    def positive_edge(self):
        self._sensor.logger.debug("%s event in %s state", self.positive_edge.__name__, self.name)

    def negative_edge(self):
        self._sensor.logger.debug("%s event in %s state", self.negative_edge.__name__, self.name)

    def conn_ok(self):
        self._sensor.logger.debug("%s event in %s state", self.conn_ok.__name__, self.name)

    def conn_nok(self):
        self._sensor.logger.debug("%s event in %s state", self.conn_nok.__name__, self.name)
        self._sensor_sm.set_state(self._sensor_sm.nok_state)

    def error(self):
        self._sensor.logger.debug("%s event in %s state", self.error.__name__, self.name)

    def acknowledge(self):
        self._sensor.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

        if self._sensor_sm.init_required:
            self._sensor_sm.init_required = False
            self._sensor_sm.set_state(self._sensor_sm.notinit_state)
        else:
            self._sensor_sm.set_state(self._sensor_sm.init_state)

    def update(self):
        self._sensor.logger.debug("%s event in %s state", self.update.__name__, self.name)

    def check_conn(self):
        self._sensor.logger.debug("%s event in %s state", self.check_conn.__name__, self.name)


class ConnNOK(ComplexSensorState):
    """ Concrete State class for representing ConnNOK State"""

    def __init__(self, sensor_sm, sensor, super_sm=None, isSubstate=False):
        super(ConnNOK, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._sensor_sm = sensor_sm
        self._sensor = sensor
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    def enter_action(self):
        self._sensor.publisher.publish(topic="State", value="StatusNOK", sender=self._sensor.name)
        # self._sensor_sm.init_required = True
        self._sensor_sm.publish_error(error_codes.SensorErrorCodes.ErrorRFIDReader)

    def initialize(self):
        self._sensor.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        # self._sensor_sm.set_state(self._sensor_sm.init_state)

    def positive_edge(self):
        self._sensor.logger.debug("%s event in %s state", self.positive_edge.__name__, self.name)

    def negative_edge(self):
        self._sensor.logger.debug("%s event in %s state", self.negative_edge.__name__, self.name)

    def conn_ok(self):
        self._sensor.logger.debug("%s event in %s state", self.conn_ok.__name__, self.name)
        self._sensor_sm.init_required = True
        self._sensor_sm.set_state(self._sensor_sm.error_state)

    def conn_nok(self):
        self._sensor.logger.debug("%s event in %s state", self.conn_nok.__name__, self.name)

    def error(self):
        self._sensor.logger.debug("%s event in %s state", self.error.__name__, self.name)

    def acknowledge(self):
        self._sensor.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def update(self):
        self._sensor.logger.debug("%s event in %s state", self.update.__name__, self.name)

    def check_conn(self):
        self._sensor.logger.debug("%s event in %s state", self.check_conn.__name__, self.name)

class Update(ComplexSensorState):
    """ Concrete State class for representing Update State"""

    def __init__(self, sensor_sm, sensor, super_sm=None, isSubstate=False):
        super(Update, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._sensor_sm = sensor_sm
        self._sensor = sensor
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    def enter_action(self):
        self._sensor.update_input()

    def initialize(self):
        self._sensor.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._sensor_sm.set_state(self._sensor_sm.init_state)

    def positive_edge(self):
        self._sensor.logger.debug("%s event in %s state", self.positive_edge.__name__, self.name)
        self._sensor_sm.set_state(self._sensor_sm.sensoron_state)
        self._sensor.publisher.publish(topic="Value", value=True, sender=self._sensor.name)

    def negative_edge(self):
        self._sensor.logger.debug("%s event in %s state", self.negative_edge.__name__, self.name)
        self._sensor_sm.set_state(self._sensor_sm.sensoroff_state)
        self._sensor.publisher.publish(topic="Value", value=False, sender=self._sensor.name)

    def conn_ok(self):
        self._sensor.logger.debug("%s event in %s state", self.conn_ok.__name__, self.name)

    def conn_nok(self):
        self._sensor.logger.debug("%s event in %s state", self.conn_nok.__name__, self.name)
        self._sensor_sm.set_state(self._sensor_sm.nok_state)

    def error(self):
        self._sensor.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._sensor_sm.set_state(self._sensor_sm.error_state)

    def acknowledge(self):
        self._sensor.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def update(self):
        self._sensor.logger.debug("%s event in %s state", self.update.__name__, self.name)
        self._sensor.update_input()
        self._sensor_sm.set_state(self._sensor_sm.update_state)

    def check_conn(self):
        self._sensor.logger.debug("%s event in %s state", self.check_conn.__name__, self.name)


class CheckConnection(ComplexSensorState):
    """ Concrete State class for representing CheckConnection State"""

    def __init__(self, sensor_sm, sensor, super_sm=None, isSubstate=False):
        super(CheckConnection, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._sensor_sm = sensor_sm
        self._sensor = sensor
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    def enter_action(self):
        self._sensor.check_sensor()

    def initialize(self):
        self._sensor.logger.debug("%s event in %s state", self.initialize.__name__, self.name)

    def positive_edge(self):
        self._sensor.logger.debug("%s event in %s state", self.positive_edge.__name__, self.name)

    def negative_edge(self):
        self._sensor.logger.debug("%s event in %s state", self.negative_edge.__name__, self.name)

    def conn_ok(self):
        self._sensor.logger.debug("%s event in %s state", self.conn_ok.__name__, self.name)
        self._sensor_sm.set_state(self._sensor_sm.init_state)

    def conn_nok(self):
        self._sensor.logger.debug("%s event in %s state", self.conn_nok.__name__, self.name)
        self._sensor_sm.set_state(self._sensor_sm.nok_state)

    def error(self):
        self._sensor.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._sensor_sm.init_required = True
        self._sensor_sm.set_state(self._sensor_sm.error_state)

    def acknowledge(self):
        self._sensor.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def update(self):
        self._sensor.logger.debug("%s event in %s state", self.update.__name__, self.name)

    def check_conn(self):
        self._sensor.logger.debug("%s event in %s state", self.check_conn.__name__, self.name)


class NFCSensorSM(object):
    """ Context class for the NO (normally open) simple sensor state machine """

    def __init__(self, sensor):
        self._name = self.__class__.__name__

        self._sensor = sensor

        self._notinit_state = NotInitialized(self, self._sensor)
        self._init_state = Initialized(self, self._sensor)
        self._sensoron_state = SensorOn(self, self._sensor)
        self._sensoroff_state = SensorOff(self, self._sensor)
        self._error_state = Error(self, self._sensor)
        self._update_state = Update(self, self._sensor)
        self._nok_state = ConnNOK(self, self._sensor)
        self._check_conn_state = CheckConnection(self, self._sensor)

        self._current_state = self._notinit_state
        self.set_state(self._current_state)

        self.init_required = False  # to show that  init is needed


    @property
    def name(self):
        return self._name

    @property
    def current_state(self):
        return self._current_state

    @property
    def init_state(self):
        return self._init_state

    @property
    def notinit_state(self):
        return self._notinit_state

    @property
    def sensoron_state(self):
        return self._sensoron_state

    @property
    def sensoroff_state(self):
        return self._sensoroff_state

    @property
    def error_state(self):
        return self._error_state

    @property
    def update_state(self):
        return self._update_state

    @property
    def check_conn_state(self):
        return self._check_conn_state

    @property
    def nok_state(self):
        return self._nok_state

    def set_state(self, state):
        self._sensor.logger.debug("Switching from state %s to state %s", self.current_state.name, state.name)

        if not self.current_state.isSubstate and state.isSubstate:
            # only enter action of the substate should be called
            self._current_state = state
            self._current_state.enter_action()
        elif self.current_state.isSubstate and not state.isSubstate:
            # first exit-action in current sub-state, then exit-action in super-state,
            # then set new state, at last enter-action in new state
            self._current_state.exit_action()
            self._current_state.super_sm.exit_action()
            self._current_state = state
            self._current_state.enter_action()
        else:
            # normal case: exit action, new state, enter action
            self._current_state.exit_action()
            self._current_state = state
            self._current_state.enter_action()

    def publish_error(self, error_code):
        self._sensor.publisher.publish(topic="StationErrorCode",
                                              value=hex(error_code),
                                              sender=self._sensor.name)
        self._sensor.publisher.publish(topic="StationErrorDescription",
                                              value=self._sensor.name + error_codes.code_to_text[error_code][0] + error_codes.code_to_text[error_code][1],
                                              sender=self._sensor.name)

    def publish_message(self, message_code):
        self._sensor.publisher.publish(topic="StationMessageCode",
                                                value=hex(message_code),
                                                sender=self._sensor.name)
        self._sensor.publisher.publish(topic="StationMessageDescription",
                                                value=message_codes.code_to_text[message_code],
                                                sender=self._sensor.name)

    def dispatch(self, *args, **kwargs):
        self._sensor.logger.debug("%s has received a message: %s", self.name, kwargs)

        try:  # topics coming from the publishers
            topic = kwargs["topic"]
            value = kwargs["value"]
            sender = kwargs["sender"]

            if sender == "Station":

                if topic == "Ack":
                    if value:
                        self._current_state.acknowledge()
                    else:
                        pass

        except KeyError:
            event = kwargs["event"]
            eventID = event.eventID
            sender = event.sender

            if eventID == events.ComplexSensorEvents.Initialize:  # this a part of the service generic interface
                self._current_state.initialize()
            elif eventID == events.ComplexSensorEvents.Ack:
                self._current_state.acknowledge()
            elif eventID == events.ComplexSensorEvents.NegEdge:
                self._current_state.negative_edge()
            elif eventID == events.ComplexSensorEvents.PosEdge:
                self._current_state.positive_edge()
            elif eventID == events.ComplexSensorEvents.NegEdge:
                self._current_state.negative_edge()
            elif eventID == events.ComplexSensorEvents.Update:
                self._current_state.update()
            elif eventID == events.ComplexSensorEvents.CheckConn:
                self._current_state.check_conn()
            elif eventID == events.ComplexSensorEvents.StatusOK:
                self._current_state.conn_ok()
            elif eventID == events.ComplexSensorEvents.StatusNOK:
                self._current_state.conn_nok()
            elif eventID == events.ComplexSensorEvents.Error:
                self._current_state.error()
            elif eventID == events.ComplexSensorEvents.NoEvent:
                self._sensor.logger.debug("Empty event : %s", event)
            else:
                self._sensor.logger.debug("Unknown event : %s", event)

