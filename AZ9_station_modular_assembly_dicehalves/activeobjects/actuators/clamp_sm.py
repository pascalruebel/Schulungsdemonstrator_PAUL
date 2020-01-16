import abc
from communication import events
from utils import error_codes, message_codes


class SimpleClampState(metaclass=abc.ABCMeta):
    """ Abstract State class for a simple clamp SM """
    def __init__(self, isSubstate=False):
        self._isSubstate = isSubstate

    @property
    def isSubstate(self):
        return self._isSubstate

    @abc.abstractmethod
    def initialize(self):
        raise NotImplemented

    @abc.abstractmethod
    def close(self):
        raise NotImplemented

    @abc.abstractmethod
    def open(self):
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


class NotInitialized(SimpleClampState):
    """ Concrete State class for a NotInitialized SM """
    def __init__(self, clamp_sm, clamp, super_sm=None, isSubstate=False):
        super(NotInitialized, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._clamp_sm = clamp_sm
        self._clamp = clamp
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    def enter_action(self):
        self._clamp.publisher.publish(topic="State", value="NotInitialized", sender=self._clamp.name)

    def initialize(self):
        self._clamp.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._clamp_sm.set_state(self._clamp_sm.init_state)

    def close(self):
        self._clamp.logger.debug("%s event in %s state", self.close.__name__, self.name)

    def open(self):
        self._clamp.logger.debug("%s event in %s state", self.open.__name__, self.name)

    def error(self):
        self._clamp.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._clamp_sm.set_state(self._clamp_sm.error_state)

    def acknowledge(self):
        self._clamp.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._clamp.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def estop(self):
        self._clamp.logger.debug("%s event in %s state", self.estop.__name__, self.name)
        self._clamp_sm.set_state(self._clamp_sm.estop_state)

    def estop_ok(self):
        self._clamp.logger.debug("%s event in %s state", self.estop_ok.__name__, self.name)


class Initialized(SimpleClampState):
    """ Concrete State class for a Initialized SM """
    def __init__(self, clamp_sm, clamp, super_sm=None, isSubstate=False):
        super(Initialized, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._clamp_sm = clamp_sm
        self._clamp = clamp
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    def enter_action(self):
        # self._clamp.clamp_open()
        self._clamp.publisher.publish(topic="State", value="Initialized", sender=self._clamp.name)

    def initialize(self):
        self._clamp.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._clamp.clamp_open()
        self._clamp.publisher.publish(topic="State", value="Initialized", sender=self._clamp.name)

    def close(self):
        self._clamp.logger.debug("%s event in %s state", self.close.__name__, self.name)
        self._clamp_sm.set_state(self._clamp_sm.clamp_close_state)

    def open(self):
        self._clamp.logger.debug("%s event in %s state", self.open.__name__, self.name)
        self._clamp_sm.set_state(self._clamp_sm.clamp_open_state)

    def error(self):
        self._clamp.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._clamp_sm.set_state(self._clamp_sm.error_state)

    def acknowledge(self):
        self._clamp.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._clamp.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def estop(self):
        self._clamp.logger.debug("%s event in %s state", self.estop.__name__, self.name)
        self._clamp_sm.set_state(self._clamp_sm.estop_state)

    def estop_ok(self):
        self._clamp.logger.debug("%s event in %s state", self.estop_ok.__name__, self.name)


class ClampClose(SimpleClampState):
    """ Concrete State class for a clamp close SM """
    def __init__(self, clamp_sm, clamp, super_sm=None, isSubstate=False):
        super(ClampClose, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._clamp_sm = clamp_sm
        self._clamp = clamp
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    def enter_action(self):
        self._clamp.publisher.publish(topic="Value", value=True, sender=self._clamp.name)
        self._clamp.clamp_close()

    def initialize(self):
        self._clamp.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._clamp_sm.set_state(self._clamp_sm.init_state)

    def close(self):
        self._clamp.logger.debug("%s event in %s state", self.close.__name__, self.name)

    def open(self):
        self._clamp.logger.debug("%s event in %s state", self.open.__name__, self.name)
        self._clamp_sm.set_state(self._clamp_sm.clamp_open_state)

    def error(self):
        self._clamp.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._clamp_sm.set_state(self._clamp_sm.error_state)

    def acknowledge(self):
        self._clamp.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._clamp.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def estop(self):
        self._clamp.logger.debug("%s event in %s state", self.estop.__name__, self.name)
        self._clamp_sm.set_state(self._clamp_sm.estop_state)

    def estop_ok(self):
        self._clamp.logger.debug("%s event in %s state", self.estop_ok.__name__, self.name)


class ClampOpen(SimpleClampState):
    """ Concrete State class for a clamp open SM """
    def __init__(self, clamp_sm, clamp, super_sm=None, isSubstate=False):
        super(ClampOpen, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._clamp_sm = clamp_sm
        self._clamp = clamp
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    def enter_action(self):
        self._clamp.publisher.publish(topic="Value", value=False, sender=self._clamp.name)
        self._clamp.clamp_open()

    def initialize(self):
        self._clamp.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._clamp_sm.set_state(self._clamp_sm.init_state)

    def close(self):
        self._clamp.logger.debug("%s event in %s state", self.close.__name__, self.name)
        self._clamp_sm.set_state(self._clamp_sm.clamp_close_state)

    def open(self):
        self._clamp.logger.debug("%s event in %s state", self.open.__name__, self.name)

    def error(self):
        self._clamp.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._clamp_sm.set_state(self._clamp_sm.error_state)

    def acknowledge(self):
        self._clamp.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._clamp.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def estop(self):
        self._clamp.logger.debug("%s event in %s state", self.estop.__name__, self.name)
        self._clamp_sm.set_state(self._clamp_sm.estop_state)

    def estop_ok(self):
        self._clamp.logger.debug("%s event in %s state", self.estop_ok.__name__, self.name)


class Error(SimpleClampState):
    """ Concrete State class for a Error SM """

    def __init__(self, clamp_sm, clamp, super_sm=None, isSubstate=False):
        super(Error, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._clamp_sm = clamp_sm
        self._clamp = clamp
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    def enter_action(self):
        self._clamp.publisher.publish(topic="State", value="Error", sender=self._clamp.name)
        self._clamp.clamp_open()

    def initialize(self):
        self._clamp.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._clamp_sm.set_state(self._clamp_sm.init_state)

    def close(self):
        self._clamp.logger.debug("%s event in %s state", self.close.__name__, self.name)

    def open(self):
        self._clamp.logger.debug("%s event in %s state", self.open.__name__, self.name)

    def error(self):
        self._clamp.logger.debug("%s event in %s state", self.error.__name__, self.name)

    def acknowledge(self):
        self._clamp.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)
        self._clamp_sm.set_state(self._clamp_sm.clamp_open_state)

    def timeout(self):
        self._clamp.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def estop(self):
        self._clamp.logger.debug("%s event in %s state", self.estop.__name__, self.name)
        self._clamp_sm.set_state(self._clamp_sm.estop_state)

    def estop_ok(self):
        self._clamp.logger.debug("%s event in %s state", self.estop_ok.__name__, self.name)


class Estop(SimpleClampState):
    """ Concrete State class for a Estop SM """

    def __init__(self, clamp_sm, clamp, super_sm=None, isSubstate=False):
        super(Estop, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._clamp_sm = clamp_sm
        self._clamp = clamp
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    def enter_action(self):
        self._clamp.publisher.publish(topic="State", value="Estop", sender=self._clamp.name)
        self._clamp.clamp_open()

    def initialize(self):
        self._clamp.logger.debug("%s event in %s state", self.initialize.__name__, self.name)

    def close(self):
        self._clamp.logger.debug("%s event in %s state", self.close.__name__, self.name)

    def open(self):
        self._clamp.logger.debug("%s event in %s state", self.open.__name__, self.name)

    def error(self):
        self._clamp.logger.debug("%s event in %s state", self.error.__name__, self.name)

    def acknowledge(self):
        self._clamp.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)
        self._clamp_sm.set_state(self._clamp_sm.clamp_open_state)

    def timeout(self):
        self._clamp.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def estop(self):
        self._clamp.logger.debug("%s event in %s state", self.estop.__name__, self.name)

    def estop_ok(self):
        self._clamp.logger.debug("%s event in %s state", self.estop_ok.__name__, self.name)
        self._clamp_sm.set_state(self._clamp_sm.error_state)


class SimpleClampStateMachine(object):
    """ Context class for the Clamp state machine """
    def __init__(self, clamp):
        self._name = self.__class__.__name__

        self._notinit_state = NotInitialized(self, clamp) # an instance for tracking current state

        self._init_state = Initialized(self, clamp)
        self._clamp_close_state = ClampClose(self, clamp)
        self._clamp_open_state = ClampOpen(self, clamp)
        self._error_state = Error(self, clamp)
        self._estop_state = Estop(self, clamp)

        self._clamp = clamp

        self._current_state = self._notinit_state
        self.set_state(self._current_state)

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
    def init_state(self):
        return self._init_state

    @property
    def clamp_close_state(self):
        return self._clamp_close_state

    @property
    def clamp_open_state(self):
        return self._clamp_open_state

    @property
    def error_state(self):
        return self._error_state

    @property
    def estop_state(self):
        return self._estop_state

    def set_state(self, state):
        self._clamp.logger.debug("%s State is switching to %s State", self._current_state.name, state.name)

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
        self._clamp.publisher.publish(topic="StationErrorCode",
                                              value=hex(error_code),
                                              sender=self._clamp.name)
        self._clamp.publisher.publish(topic="StationErrorDescription",
                                              value=error_codes.code_to_text[error_code],
                                              sender=self._clamp.name)

    def publish_message(self, message_code):
        self._clamp.publisher.publish(topic="StationMessageCode",
                                                value=hex(message_code),
                                                sender=self._clamp.name)
        self._clamp.publisher.publish(topic="StationMessageDescription",
                                                value=message_codes.code_to_text[message_code],
                                                sender=self._clamp.name)

    def dispatch(self, *args, **kwargs):

        self._clamp.logger.debug("%s has received a message: %s", self.name, kwargs)

        try:    # topics coming from the publishers
            topic = kwargs["topic"]
            value = kwargs["value"]
            sender = kwargs["sender"]

            if sender == "Station":

                if topic == "Ack":
                    if value:
                        self._current_state.acknowledge()
                    else:
                        pass

            elif sender == "SafetySwitch":

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

        except KeyError:
            event = kwargs["event"]

            eventID = event.eventID
            sender = event.sender

            if eventID == events.SimpleClampInputEvents.Initialize:  # this a part of the service generic interface
                self._current_state.initialize()
            elif eventID == events.SimpleClampInputEvents.Ack:
                self._current_state.acknowledge()
            elif eventID == events.SimpleClampInputEvents.Close:
                self._current_state.close()
            elif eventID == events.SimpleClampInputEvents.Open:
                self._current_state.open()
            elif eventID == events.SimpleClampInputEvents.Error:
                self._current_state.error()
            elif eventID == events.SimpleClampInputEvents.Timeout:
                self._current_state.timeout()
            else:
                self._clamp.logger.debug("Unknown event : %s", event)

