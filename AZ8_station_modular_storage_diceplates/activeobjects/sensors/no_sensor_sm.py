from activeobjects.sensors.abstract_sensor import SimpleSensorState
from communication import events


class NotInitialized(SimpleSensorState):
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

    def initialize(self):
        self._sensor.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._sensor_sm.set_state(self._sensor_sm.init_state)

    def positive_edge(self):
        self._sensor.logger.debug("%s event in %s state", self.positive_edge.__name__, self.name)

    def negative_edge(self):
        self._sensor.logger.debug("%s event in %s state", self.negative_edge.__name__, self.name)

    def error(self):
        self._sensor.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._sensor_sm.set_state(self._sensor_sm.error_state)

    def acknowledge(self):
        self._sensor.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def update(self):
        self._sensor.logger.debug("%s event in %s state", self.update.__name__, self.name)


class Initialized(SimpleSensorState):
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

    def error(self):
        self._sensor.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._sensor_sm.set_state(self._sensor_sm.error_state)

    def acknowledge(self):
        self._sensor.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def update(self):
        self._sensor.logger.debug("%s event in %s state", self.update.__name__, self.name)


class SensorOn(SimpleSensorState):
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

    def error(self):
        self._sensor.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._sensor_sm.set_state(self._sensor_sm.error_state)

    def acknowledge(self):
        self._sensor.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def update(self):
        self._sensor.logger.debug("%s event in %s state", self.update.__name__, self.name)
        self._sensor_sm.set_state(self._sensor_sm.update_state)


class SensorOff(SimpleSensorState):
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

    def error(self):
        self._sensor.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._sensor_sm.set_state(self._sensor_sm.error_state)

    def acknowledge(self):
        self._sensor.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def update(self):
        self._sensor.logger.debug("%s event in %s state", self.update.__name__, self.name)
        self._sensor_sm.set_state(self._sensor_sm.update_state)


class Error(SimpleSensorState):
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
        self._sensor_sm.set_state(self._sensor_sm.init_state)

    def positive_edge(self):
        self._sensor.logger.debug("%s event in %s state", self.positive_edge.__name__, self.name)

    def negative_edge(self):
        self._sensor.logger.debug("%s event in %s state", self.negative_edge.__name__, self.name)

    def error(self):
        self._sensor.logger.debug("%s event in %s state", self.error.__name__, self.name)

    def acknowledge(self):
        self._sensor.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)
        self._sensor_sm.set_state(self._sensor_sm.init_state)

    def update(self):
        self._sensor.logger.debug("%s event in %s state", self.update.__name__, self.name)


class Update(SimpleSensorState):
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

    def error(self):
        self._sensor.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._sensor_sm.set_state(self._sensor_sm.error_state)

    def acknowledge(self):
        self._sensor.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def update(self):
        self._sensor.logger.debug("%s event in %s state", self.update.__name__, self.name)


class NOSensorSM(object):
    """ Context class for the NO (normally open) simple sensor state machine """

    def __init__(self, sensor):
        self._name = self.__class__.__name__

        self._notinit_state = NotInitialized(self, sensor)
        self._init_state = Initialized(self, sensor)
        self._sensoron_state = SensorOn(self, sensor)
        self._sensoroff_state = SensorOff(self, sensor)
        self._error_state = Error(self, sensor)
        self._update_state = Update(self, sensor)

        self._current_state = self._notinit_state

        self._sensor = sensor

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

            if eventID == self._sensor.input_events.eventIDs.Initialize:  # this a part of the service generic interface
                self._current_state.initialize()
            elif eventID == self._sensor.input_events.eventIDs.Ack:
                self._current_state.acknowledge()
            elif eventID == self._sensor.input_events.eventIDs.NegEdge:
                self._current_state.negative_edge()
            elif eventID == self._sensor.input_events.eventIDs.PosEdge:
                self._current_state.positive_edge()
            elif eventID == self._sensor.input_events.eventIDs.Update:
                self._current_state.update()
            elif eventID == self._sensor.input_events.eventIDs.Error:
                self._current_state.error()
            else:
                self._sensor.logger.debug("Unknown event : %s", event)