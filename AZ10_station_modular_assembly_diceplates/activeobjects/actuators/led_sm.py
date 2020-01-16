import abc
from threading import Timer


class SimpleLEDState(metaclass=abc.ABCMeta):
    """ Abstract State class for a simple LED SM """
    def __init__(self, isSubstate=False):
        self._isSubstate = isSubstate

    @property
    def isSubstate(self):
        return self._isSubstate

    @abc.abstractmethod
    def initialize(self):
        raise NotImplemented

    @abc.abstractmethod
    def on(self):
        raise NotImplemented

    @abc.abstractmethod
    def off(self):
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

    # enter/exit actions (UML specification)
    def enter_action(self):
        pass

    def exit_action(self):
        pass


class NotInitialized(SimpleLEDState):
    """ Concrete State class for a NotInitialized SM """
    def __init__(self, led_sm, led, super_sm=None, isSubstate=False):
        super(NotInitialized, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._led_sm = led_sm
        self._led = led
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    def enter_action(self):
        self._led.publisher.publish(topic="State", value="NotInitialized", sender=self._led.name)

    def initialize(self):
        self._led.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._led_sm.set_state(self._led_sm.init_state)

    def on(self):
        self._led.logger.debug("%s event in %s state", self.on.__name__, self.name)

    def off(self):
        self._led.logger.debug("%s event in %s state", self.off.__name__, self.name)

    def error(self):
        self._led.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._led_sm.set_state(self._led_sm.error_state)
        self._led.led_off()

    def acknowledge(self):
        self._led.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._led.logger.debug("%s event in %s state", self.timeout.__name__, self.name)


class Initialized(SimpleLEDState):
    """ Concrete State class for a Initialized SM """
    def __init__(self, led_sm, led, super_sm=None, isSubstate=False):
        super(Initialized, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._led_sm = led_sm
        self._led = led
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    def enter_action(self):
        self._led.led_off()
        self._led.publisher.publish(topic="State", value="Initialized", sender=self._led.name)

    def initialize(self):
        self._led.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._led.led_off()
        self._led.publisher.publish(topic="State", value="Initialized", sender=self._led.name)

    def on(self):
        self._led.logger.debug("%s event in %s state", self.on.__name__, self.name)
        self._led_sm.set_state(self._led_sm.ledon_state)

    def off(self):
        self._led.logger.debug("%s event in %s state", self.off.__name__, self.name)
        self._led_sm.set_state(self._led_sm.ledoff_state)

    def error(self):
        self._led.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._led_sm.set_state(self._led_sm.error_state)

    def acknowledge(self):
        self._led.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._led.logger.debug("%s event in %s state", self.timeout.__name__, self.name)


class LedOn(SimpleLEDState):
    """ Concrete State class for a LED On SM """
    def __init__(self, led_sm, led, super_sm=None, isSubstate=False):
        super(LedOn, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._led_sm = led_sm
        self._led = led
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    def enter_action(self):
        self._led.publisher.publish(topic="Value", value=True, sender=self._led.name)
        self._led.led_on()

    def initialize(self):
        self._led.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._led_sm.set_state(self._led_sm.init_state)

    def on(self):
        self._led.logger.debug("%s event in %s state", self.on.__name__, self.name)

    def off(self):
        self._led.logger.debug("%s event in %s state", self.off.__name__, self.name)
        self._led_sm.set_state(self._led_sm.ledoff_state)

    def error(self):
        self._led.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._led_sm.set_state(self._led_sm.error_state)

    def acknowledge(self):
        self._led.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._led.logger.debug("%s event in %s state", self.timeout.__name__, self.name)


class LedOff(SimpleLEDState):
    """ Concrete State class for a LED Off SM """
    def __init__(self, led_sm, led, super_sm=None, isSubstate=False):
        super(LedOff, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._led_sm = led_sm
        self._led = led
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    def enter_action(self):
        self._led.publisher.publish(topic="Value", value=False, sender=self._led.name)
        self._led.led_off()

    def initialize(self):
        self._led.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._led_sm.set_state(self._led_sm.init_state)

    def on(self):
        self._led.logger.debug("%s event in %s state", self.on.__name__, self.name)
        self._led_sm.set_state(self._led_sm.ledon_state)

    def off(self):
        self._led.logger.debug("%s event in %s state", self.off.__name__, self.name)

    def error(self):
        self._led.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._led_sm.set_state(self._led_sm.error_state)

    def acknowledge(self):
        self._led.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._led.logger.debug("%s event in %s state", self.timeout.__name__, self.name)


class Error(SimpleLEDState):
    """ Concrete State class for a Error SM """

    def __init__(self, led_sm, led, super_sm=None, isSubstate=False):
        super(Error, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._led_sm = led_sm
        self._led = led
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    def enter_action(self):
        self._led.publisher.publish(topic="State", value="Error", sender=self._led.name)
        self._led.led_off()

    def initialize(self):
        self._led.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._led_sm.set_state(self._led_sm.init_state)

    def on(self):
        self._led.logger.debug("%s event in %s state", self.on.__name__, self.name)

    def off(self):
        self._led.logger.debug("%s event in %s state", self.off.__name__, self.name)

    def error(self):
        self._led.logger.debug("%s event in %s state", self.error.__name__, self.name)

    def acknowledge(self):
        self._led.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)
        self._led_sm.set_state(self._led_sm.init_state)

    def timeout(self):
        self._led.logger.debug("%s event in %s state", self.timeout.__name__, self.name)


class SimpleLEDStateMachine(object):
    """ Context class for the LED state machine """
    def __init__(self, led):
        self._name = self.__class__.__name__

        self._notinit_state = NotInitialized(self, led) # an instance for tracking current state

        self._init_state = Initialized(self, led)
        self._ledon_state = LedOn(self, led)
        self._ledoff_state = LedOff(self, led)
        self._error_state = Error(self, led)

        self._led = led

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
    def ledon_state(self):
        return self._ledon_state

    @property
    def ledoff_state(self):
        return self._ledoff_state

    @property
    def error_state(self):
        return self._error_state

    def set_state(self, state):
        self._led.logger.debug("%s State is switching to %s State", self._current_state.name, state.name)

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

        self._led.logger.debug("%s has received a message: %s", self.name, kwargs)

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

        except KeyError:
            event = kwargs["event"]

            eventID = event.eventID
            sender = event.sender

            if eventID == self._led.input_events.eventIDs.Initialize:  # this a part of the service generic interface
                self._current_state.initialize()
            elif eventID == self._led.input_events.eventIDs.Ack:
                self._current_state.acknowledge()
            elif eventID == self._led.input_events.eventIDs.LedOn:
                self._current_state.on()
            elif eventID == self._led.input_events.eventIDs.LedOff:
                self._current_state.off()
            elif eventID == self._led.input_events.eventIDs.Error:
                self._current_state.error()
            elif eventID == self._led.input_events.eventIDs.Timeout:
                self._current_state.timeout()
            else:
                self._led.logger.debug("Unknown event : %s", event)

