import abc
from communication import events
from utils import error_codes, message_codes

class MotorState(metaclass=abc.ABCMeta):
    """ Abstract State class for a Motor SM """
    def __init__(self, isSubstate=False):
        self._isSubstate = isSubstate

    @property
    def isSubstate(self):
        return self._isSubstate

    @abc.abstractmethod
    def initialize(self):
        raise NotImplemented

    @abc.abstractmethod
    def stop(self):
        raise NotImplemented

    @abc.abstractmethod
    def rotate_cw(self):
        """rotate clockwise"""
        raise NotImplemented

    @abc.abstractmethod
    def rotate_ccw(self):
        """rotate counterclockwise"""
        raise NotImplemented

    @abc.abstractmethod
    def error(self):
        raise NotImplemented

    @abc.abstractmethod
    def acknowledge(self):
        raise NotImplemented

    @abc.abstractmethod
    def timeout(self):
        raise NotImplemented

    @abc.abstractmethod
    def estop(self):
        raise NotImplemented

    @abc.abstractmethod
    def estop_ok(self):
        raise NotImplemented

    # enter/exit actions (UML specification)
    def enter_action(self):
        pass

    def exit_action(self):
        pass


class NotInitialized(MotorState):
    """ Concrete State class for a NotInitialized SM """
    def __init__(self, motor_sm, motor, super_sm=None, isSubstate=False):
        super(NotInitialized, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._motor_sm = motor_sm
        self._motor = motor
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    def enter_action(self):
        self._motor.publisher.publish(topic="State", value="NotInitialized", sender=self._motor.name)

    def initialize(self):
        # self._motor.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._motor.motor_stop()
        self._motor_sm.set_state(self._motor_sm.standstill_state)

    def stop(self):
        # self._motor.logger.debug("%s event in %s state", self.stop.__name__, self.name)
        self._motor.motor_stop()

    def rotate_cw(self):
        self._motor.logger.debug("%s event in %s state", self.rotate_cw.__name__, self.name)

    def rotate_ccw(self):
        self._motor.logger.debug("%s event in %s state", self.rotate_ccw.__name__, self.name)

    def error(self):
        # self._motor.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._motor.motor_stop()
        self._motor_sm.set_state(self._motor_sm.error_state)

    def acknowledge(self):
        self._motor.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._motor.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def estop(self):
        # self._motor.logger.debug("%s event in %s state", self.estop.__name__, self.name)
        self._motor.motor_stop()
        self._motor_sm.set_state(self._motor_sm.estop_state)

    def estop_ok(self):
        self._motor.logger.debug("%s event in %s state", self.estop_ok.__name__, self.name)


class Standstill(MotorState):
    """ Concrete State class for a Standstill SM """
    def __init__(self, motor_sm, motor, super_sm=None, isSubstate=False):
        super(Standstill, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._motor_sm = motor_sm
        self._motor = motor
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    def enter_action(self):
        self._motor.publisher.publish(topic="State", value="Initialized", sender=self._motor.name)

    def initialize(self):
        # self._motor.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._motor.publisher.publish(topic="State", value="Initialized", sender=self._motor.name)

    def stop(self):
        # self._motor.logger.debug("%s event in %s state", self.stop.__name__, self.name)
        self._motor.motor_stop()

    def rotate_cw(self):
        # self._motor.logger.debug("%s event in %s state", self.rotate_cw.__name__, self.name)
        self._motor.motor_cw()
        self._motor_sm.set_state(self._motor_sm.rotating_cw_state)

    def rotate_ccw(self):
        # self._motor.logger.debug("%s event in %s state", self.rotate_ccw.__name__, self.name)
        self._motor.motor_ccw()
        self._motor_sm.set_state(self._motor_sm.rotating_ccw_state)

    def error(self):
        # self._motor.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._motor.motor_stop()
        self._motor_sm.set_state(self._motor_sm.error_state)

    def acknowledge(self):
        self._motor.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._motor.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def estop(self):
        # self._motor.logger.debug("%s event in %s state", self.estop.__name__, self.name)
        self._motor.motor_stop()
        self._motor_sm.set_state(self._motor_sm.estop_state)

    def estop_ok(self):
        self._motor.logger.debug("%s event in %s state", self.estop_ok.__name__, self.name)


class RotatingCW(MotorState):
    """ Concrete State class for a RotatingCW SM """
    def __init__(self, motor_sm, motor, super_sm=None, isSubstate=False):
        super(RotatingCW, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._motor_sm = motor_sm
        self._motor = motor
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    def initialize(self):
        # self._motor.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._motor.motor_stop()
        self._motor_sm.set_state(self._motor_sm.standstill_state)

    def stop(self):
        # self._motor.logger.debug("%s event in %s state", self.stop.__name__, self.name)
        self._motor.motor_stop()
        self._motor_sm.set_state(self._motor_sm.standstill_state)

    def rotate_cw(self):
        self._motor.logger.debug("%s event in %s state", self.rotate_cw.__name__, self.name)

    def rotate_ccw(self):
        self._motor.logger.debug("%s event in %s state", self.rotate_ccw.__name__, self.name)

    def error(self):
        # self._motor.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._motor.motor_stop()
        self._motor_sm.set_state(self._motor_sm.error_state)

    def acknowledge(self):
        self._motor.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._motor.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def estop(self):
        # self._motor.logger.debug("%s event in %s state", self.estop.__name__, self.name)
        self._motor.motor_stop()
        self._motor_sm.set_state(self._motor_sm.estop_state)

    def estop_ok(self):
        self._motor.logger.debug("%s event in %s state", self.estop_ok.__name__, self.name)


class RotatingCCW(MotorState):
    """ Concrete State class for a RotatingCCW SM """
    def __init__(self, motor_sm, motor, super_sm=None, isSubstate=False):
        super(RotatingCCW, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._motor_sm = motor_sm
        self._motor = motor
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    def initialize(self):
        # self._motor.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._motor.motor_stop()
        self._motor_sm.set_state(self._motor_sm.standstill_state)

    def stop(self):
        # self._motor.logger.debug("%s event in %s state", self.stop.__name__, self.name)
        self._motor.motor_stop()
        self._motor_sm.set_state(self._motor_sm.standstill_state)

    def rotate_cw(self):
        self._motor.logger.debug("%s event in %s state", self.rotate_cw.__name__, self.name)

    def rotate_ccw(self):
        self._motor.logger.debug("%s event in %s state", self.rotate_ccw.__name__, self.name)

    def error(self):
        # self._motor.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._motor.motor_stop()
        self._motor_sm.set_state(self._motor_sm.error_state)

    def acknowledge(self):
        self._motor.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._motor.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def estop(self):
        # self._motor.logger.debug("%s event in %s state", self.estop.__name__, self.name)
        self._motor.motor_stop()
        self._motor_sm.set_state(self._motor_sm.estop_state)

    def estop_ok(self):
        self._motor.logger.debug("%s event in %s state", self.estop_ok.__name__, self.name)


class Error(MotorState):
    """ Concrete State class for a Error SM """
    def __init__(self, motor_sm, motor, super_sm=None, isSubstate=False):
        super(Error, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._motor_sm = motor_sm
        self._motor = motor
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    def enter_action(self):
        # self._motor.publisher.publish(topic="State", value="Error", sender=self._motor.name)
        self._motor.motor_stop()

    def initialize(self):
        # self._motor.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._motor.motor_stop()
        self._motor_sm.set_state(self._motor_sm.standstill_state)

    def stop(self):
        # self._motor.logger.debug("%s event in %s state", self.stop.__name__, self.name)
        self._motor.motor_stop()

    def rotate_cw(self):
        self._motor.logger.debug("%s event in %s state", self.rotate_cw.__name__, self.name)

    def rotate_ccw(self):
        self._motor.logger.debug("%s event in %s state", self.rotate_ccw.__name__, self.name)

    def error(self):
        self._motor.logger.debug("%s event in %s state", self.error.__name__, self.name)

    def acknowledge(self):
        # self._motor.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)
        self._motor_sm.set_state(self._motor_sm.standstill_state)

    def timeout(self):
        self._motor.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def estop(self):
        # self._motor.logger.debug("%s event in %s state", self.estop.__name__, self.name)
        self._motor.motor_stop()
        self._motor_sm.set_state(self._motor_sm.estop_state)

    def estop_ok(self):
        self._motor.logger.debug("%s event in %s state", self.estop_ok.__name__, self.name)


class Estop(MotorState):
    """ Concrete State class for a Estop SM """

    def __init__(self, motor_sm, motor, super_sm=None, isSubstate=False):
        super(Estop, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._motor_sm = motor_sm
        self._motor = motor
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    def enter_action(self):
        self._motor.motor_stop()
        self._motor.publisher.publish(topic="State", value="Estop", sender=self._motor.name)

    def initialize(self):
        self._motor.logger.debug("%s event in %s state", self.initialize.__name__, self.name)

    def stop(self):
        self._motor.logger.debug("%s event in %s state", self.stop.__name__, self.name)

    def rotate_cw(self):
        self._motor.logger.debug("%s event in %s state", self.rotate_cw.__name__, self.name)

    def rotate_ccw(self):
        self._motor.logger.debug("%s event in %s state", self.rotate_ccw.__name__, self.name)

    def error(self):
        self._motor.logger.debug("%s event in %s state", self.error.__name__, self.name)

    def acknowledge(self):
        self._motor.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._motor.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def estop(self):
        self._motor.logger.debug("%s event in %s state", self.estop.__name__, self.name)

    def estop_ok(self):
        # self._motor.logger.debug("%s event in %s state", self.estop_ok.__name__, self.name)
        self._motor_sm.set_state(self._motor_sm.error_state)


class MotorStateMachine(object):
    """ Context class for the Station's state machine """
    def __init__(self, motor):
        self._name = self.__class__.__name__

        self._motor = motor

        self._current_state = self._notinit_state = NotInitialized(self, self._motor) # an instance for tracking current state

        self._standstill_state = Standstill(self, self._motor)
        self._rotating_cw_state = RotatingCW(self, self._motor)
        self._rotating_ccw_state = RotatingCCW(self, self._motor)
        self._estop_state = Estop(self, self._motor)
        self._error_state = Error(self, self._motor)  # motors's states instances

    @property
    def name(self):
        return self._name

    @property
    def current_state(self):
        return self._current_state

    @property
    def notinit_state(self):
        return self._notinit_state

    @property
    def standstill_state(self):
        return self._standstill_state

    @property
    def rotating_cw_state(self):
        return self._rotating_cw_state

    @property
    def rotating_ccw_state(self):
        return self._rotating_ccw_state

    @property
    def estop_state(self):
        return self._estop_state

    @property
    def error_state(self):
        return self._error_state

    def set_state(self, state):
        self._motor.logger.debug("%s State is switching to %s State", self._current_state.name, state.name)

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
        self._motor.publisher.publish(topic="StationErrorCode",
                                              value=hex(error_code),
                                              sender=self._motor.name)
        self._motor.publisher.publish(topic="StationErrorDescription",
                                              value=error_codes.code_to_text[error_code],
                                              sender=self._motor.name)

    def publish_message(self, message_code):
        self._motor.publisher.publish(topic="StationMessageCode",
                                                value=hex(message_code),
                                                sender=self._motor.name)
        self._motor.publisher.publish(topic="StationMessageDescription",
                                                value=message_codes.code_to_text[message_code],
                                                sender=self._motor.name)

    def dispatch(self, *args, **kwargs):

        self._motor.logger.debug("%s has received a message: %s", self.name, kwargs)

        try:  # topics coming from the publishers
            topic = kwargs["topic"]
            value = kwargs["value"]
            sender = kwargs["sender"]

            if sender == "SafetySwitch":

                if topic == "Value":
                    if value:
                        self._current_state.estop()
                    else:
                        self._current_state.estop_ok()

                elif topic == "State":

                    if value == "Error":
                        self._current_state.error()
                    elif value == "NotInitialized":
                        self._current_state.error()
                    elif value == "Initialized":
                        pass

            elif sender == "Station":

                if topic == "Ack":
                    if value:
                        self._current_state.acknowledge()
                    else:
                        pass

        except KeyError:
            event = kwargs["event"]

            eventID = event.eventID
            sender = event.sender

            if eventID == events.SimpleMotorInputEvents.Initialize:  # this a part of the service generic interface
                self._current_state.initialize()
            elif eventID == events.SimpleMotorInputEvents.Ack:
                self._current_state.acknowledge()
            elif eventID == events.SimpleMotorInputEvents.RotateCW:
                self._current_state.rotate_cw()
            elif eventID == events.SimpleMotorInputEvents.RotateCCW:
                self._current_state.rotate_ccw()
            elif eventID == events.SimpleMotorInputEvents.Stop:
                self._current_state.stop()
            elif eventID == events.SimpleMotorInputEvents.Error:
                self._current_state.error()
            elif eventID == events.SimpleMotorInputEvents.Timeout:
                self._current_state.timeout()
            else:
                self._motor.logger.debug("Unknown event : %s", event)

