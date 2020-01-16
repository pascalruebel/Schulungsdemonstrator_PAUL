import abc
from threading import Timer
from communication import events


class RGB_LEDState(metaclass=abc.ABCMeta):
    """ Abstract State class for a RGB LED SM """
    def __init__(self, isSubstate=False):
        self._isSubstate = isSubstate

    @property
    def isSubstate(self):
        return self._isSubstate

    @abc.abstractmethod
    def initialize(self):
        raise NotImplemented

    @abc.abstractmethod
    def red(self):
        raise NotImplemented

    @abc.abstractmethod
    def green(self):
        raise NotImplemented

    @abc.abstractmethod
    def yellow(self):
        raise NotImplemented

    @abc.abstractmethod
    def purple(self):
        raise NotImplemented

    @abc.abstractmethod
    def custom(self, red, green, blue):
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


class NotInitialized(RGB_LEDState):
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
        self._led.led_off()
        self._led_sm.set_state(self._led_sm.init_state)

    def initialize(self):
        self._led.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._led_sm.set_state(self._led_sm.init_state)

    def red(self):
        self._led.logger.debug("%s event in %s state", self.red.__name__, self.name)

    def green(self):
        self._led.logger.debug("%s event in %s state", self.green.__name__, self.name)

    def yellow(self):
        self._led.logger.debug("%s event in %s state", self.yellow.__name__, self.name)

    def purple(self):
        self._led.logger.debug("%s event in %s state", self.purple.__name__, self.name)

    def custom(self, red, green, blue):
        self._led.logger.debug("%s event in %s state", self.purple.__name__, self.name)

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


class Initialized(RGB_LEDState):
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

    def red(self):
        self._led.logger.debug("%s event in %s state", self.red.__name__, self.name)
        self._led_sm.set_state(self._led_sm.redon_state)

    def green(self):
        self._led.logger.debug("%s event in %s state", self.green.__name__, self.name)
        self._led_sm.set_state(self._led_sm.greenon_state)

    def yellow(self):
        self._led.logger.debug("%s event in %s state", self.yellow.__name__, self.name)
        self._led_sm.set_state(self._led_sm.yellowon_state)

    def purple(self):
        self._led.logger.debug("%s event in %s state", self.purple.__name__, self.name)
        self._led_sm.set_state(self._led_sm.purpleon_state)

    def custom(self, red, green, blue):
        self._led.logger.debug("%s event in %s state", self.purple.__name__, self.name)
        self._led.custom_on(red, green, blue)
        self._led_sm.set_state(self._led_sm.customon_state)

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


class RedOn(RGB_LEDState):
    """ Concrete State class for a LED Red SM """
    def __init__(self, led_sm, led, super_sm=None, isSubstate=False):
        super(RedOn, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._led_sm = led_sm
        self._led = led
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    def enter_action(self):
        self._led.publisher.publish(topic="Value", value='red', sender=self._led.name)
        self._led.red_on()

    def initialize(self):
        self._led.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._led_sm.set_state(self._led_sm.init_state)

    def red(self):
        self._led.logger.debug("%s event in %s state", self.red.__name__, self.name)

    def green(self):
        self._led.logger.debug("%s event in %s state", self.green.__name__, self.name)
        self._led_sm.set_state(self._led_sm.greenon_state)

    def yellow(self):
        self._led.logger.debug("%s event in %s state", self.yellow.__name__, self.name)
        self._led_sm.set_state(self._led_sm.yellowon_state)

    def purple(self):
        self._led.logger.debug("%s event in %s state", self.purple.__name__, self.name)
        self._led_sm.set_state(self._led_sm.purpleon_state)

    def custom(self, red, green, blue):
        self._led.logger.debug("%s event in %s state", self.purple.__name__, self.name)
        self._led.custom_on(red, green, blue)
        self._led_sm.set_state(self._led_sm.customon_state)

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


class GreenOn(RGB_LEDState):
    """ Concrete State class for a LED GreenOn SM """

    def __init__(self, led_sm, led, super_sm=None, isSubstate=False):
        super(GreenOn, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._led_sm = led_sm
        self._led = led
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    def enter_action(self):
        self._led.publisher.publish(topic="Value", value='green', sender=self._led.name)
        self._led.green_on()

    def initialize(self):
        self._led.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._led_sm.set_state(self._led_sm.init_state)

    def red(self):
        self._led.logger.debug("%s event in %s state", self.red.__name__, self.name)
        self._led_sm.set_state(self._led_sm.redon_state)

    def green(self):
        self._led.logger.debug("%s event in %s state", self.green.__name__, self.name)

    def yellow(self):
        self._led.logger.debug("%s event in %s state", self.yellow.__name__, self.name)
        self._led_sm.set_state(self._led_sm.yellowon_state)

    def purple(self):
        self._led.logger.debug("%s event in %s state", self.purple.__name__, self.name)
        self._led_sm.set_state(self._led_sm.purpleon_state)

    def custom(self, red, green, blue):
        self._led.logger.debug("%s event in %s state", self.purple.__name__, self.name)
        self._led.custom_on(red, green, blue)
        self._led_sm.set_state(self._led_sm.customon_state)

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


class YellowOn(RGB_LEDState):
    """ Concrete State class for a LED YellowOn SM """

    def __init__(self, led_sm, led, super_sm=None, isSubstate=False):
        super(YellowOn, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._led_sm = led_sm
        self._led = led
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    def enter_action(self):
        self._led.publisher.publish(topic="Value", value='yellow', sender=self._led.name)
        self._led.yellow_on()

    def initialize(self):
        self._led.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._led_sm.set_state(self._led_sm.init_state)

    def red(self):
        self._led.logger.debug("%s event in %s state", self.red.__name__, self.name)
        self._led_sm.set_state(self._led_sm.redon_state)

    def green(self):
        self._led.logger.debug("%s event in %s state", self.green.__name__, self.name)
        self._led_sm.set_state(self._led_sm.greenon_state)

    def yellow(self):
        self._led.logger.debug("%s event in %s state", self.yellow.__name__, self.name)

    def purple(self):
        self._led.logger.debug("%s event in %s state", self.purple.__name__, self.name)
        self._led_sm.set_state(self._led_sm.purpleon_state)

    def custom(self, red, green, blue):
        self._led.logger.debug("%s event in %s state", self.purple.__name__, self.name)
        self._led.custom_on(red, green, blue)
        self._led_sm.set_state(self._led_sm.customon_state)

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


class PurpleOn(RGB_LEDState):
    """ Concrete State class for a LED PurpleOn SM """

    def __init__(self, led_sm, led, super_sm=None, isSubstate=False):
        super(PurpleOn, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._led_sm = led_sm
        self._led = led
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    def enter_action(self):
        self._led.publisher.publish(topic="Value", value='purple', sender=self._led.name)
        self._led.purple_on()

    def initialize(self):
        self._led.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._led_sm.set_state(self._led_sm.init_state)

    def red(self):
        self._led.logger.debug("%s event in %s state", self.red.__name__, self.name)
        self._led_sm.set_state(self._led_sm.redon_state)

    def green(self):
        self._led.logger.debug("%s event in %s state", self.green.__name__, self.name)
        self._led_sm.set_state(self._led_sm.greenon_state)

    def yellow(self):
        self._led.logger.debug("%s event in %s state", self.yellow.__name__, self.name)
        self._led_sm.set_state(self._led_sm.yellowon_state)

    def purple(self):
        self._led.logger.debug("%s event in %s state", self.purple.__name__, self.name)

    def custom(self, red, green, blue):
        self._led.logger.debug("%s event in %s state", self.purple.__name__, self.name)
        self._led.custom_on(red, green, blue)
        self._led_sm.set_state(self._led_sm.customon_state)

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


class CustomOn(RGB_LEDState):
    """ Concrete State class for a LED CustomOn SM """

    def __init__(self, led_sm, led, super_sm=None, isSubstate=False):
        super(CustomOn, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._led_sm = led_sm
        self._led = led
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    def enter_action(self):
        self._led.publisher.publish(topic="Value", value='custom', sender=self._led.name)

    def initialize(self):
        self._led.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._led_sm.set_state(self._led_sm.init_state)

    def red(self):
        self._led.logger.debug("%s event in %s state", self.red.__name__, self.name)
        self._led_sm.set_state(self._led_sm.redon_state)

    def green(self):
        self._led.logger.debug("%s event in %s state", self.green.__name__, self.name)
        self._led_sm.set_state(self._led_sm.greenon_state)

    def yellow(self):
        self._led.logger.debug("%s event in %s state", self.yellow.__name__, self.name)
        self._led_sm.set_state(self._led_sm.yellowon_state)

    def purple(self):
        self._led.logger.debug("%s event in %s state", self.purple.__name__, self.name)
        self._led_sm.set_state(self._led_sm.purpleon_state)

    def custom(self, red, green, blue):
        self._led.logger.debug("%s event in %s state", self.purple.__name__, self.name)
        self._led.custom_on(red, green, blue)

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


class LedOff(RGB_LEDState):
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
        self._led.publisher.publish(topic="Value", value='off', sender=self._led.name)
        self._led.led_off()

    def initialize(self):
        self._led.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._led_sm.set_state(self._led_sm.init_state)

    def red(self):
        self._led.logger.debug("%s event in %s state", self.red.__name__, self.name)
        self._led_sm.set_state(self._led_sm.redon_state)

    def green(self):
        self._led.logger.debug("%s event in %s state", self.green.__name__, self.name)
        self._led_sm.set_state(self._led_sm.greenon_state)

    def yellow(self):
        self._led.logger.debug("%s event in %s state", self.yellow.__name__, self.name)
        self._led_sm.set_state(self._led_sm.yellowon_state)

    def purple(self):
        self._led.logger.debug("%s event in %s state", self.purple.__name__, self.name)
        self._led_sm.set_state(self._led_sm.purpleon_state)

    def custom(self, red, green, blue):
        self._led.logger.debug("%s event in %s state", self.purple.__name__, self.name)
        self._led.custom_on(red, green, blue)
        self._led_sm.set_state(self._led_sm.customon_state)

    def off(self):
        self._led.logger.debug("%s event in %s state", self.off.__name__, self.name)

    def error(self):
        self._led.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._led_sm.set_state(self._led_sm.error_state)

    def acknowledge(self):
        self._led.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._led.logger.debug("%s event in %s state", self.timeout.__name__, self.name)


class Error(RGB_LEDState):
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
        self._led.publisher.publish(topic="State", value="error", sender=self._led.name)
        self._led.led_off()

    def initialize(self):
        self._led.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._led_sm.set_state(self._led_sm.init_state)

    def red(self):
        self._led.logger.debug("%s event in %s state", self.red.__name__, self.name)

    def green(self):
        self._led.logger.debug("%s event in %s state", self.green.__name__, self.name)

    def yellow(self):
        self._led.logger.debug("%s event in %s state", self.yellow.__name__, self.name)

    def purple(self):
        self._led.logger.debug("%s event in %s state", self.purple.__name__, self.name)

    def custom(self, red, green, blue):
        self._led.logger.debug("%s event in %s state", self.purple.__name__, self.name)

    def off(self):
        self._led.logger.debug("%s event in %s state", self.off.__name__, self.name)

    def error(self):
        self._led.logger.debug("%s event in %s state", self.error.__name__, self.name)

    def acknowledge(self):
        self._led.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)
        self._led_sm.set_state(self._led_sm.init_state)

    def timeout(self):
        self._led.logger.debug("%s event in %s state", self.timeout.__name__, self.name)


class RGB_LEDStateMachine(object):
    """ Context class for the RGB LED state machine """
    def __init__(self, led):
        self._name = self.__class__.__name__

        self._notinit_state = NotInitialized(self, led) # an instance for tracking current state

        self._init_state = Initialized(self, led)
        self._redon_state = RedOn(self, led)
        self._greenon_state = GreenOn(self, led)
        self._yellowon_state = YellowOn(self, led)
        self._purpleon_state = PurpleOn(self, led)
        self._customon_state = CustomOn(self, led)
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
    def redon_state(self):
        return self._redon_state

    @property
    def greenon_state(self):
        return self._greenon_state

    @property
    def yellowon_state(self):
        return self._yellowon_state

    @property
    def purpleon_state(self):
        return self._purpleon_state

    @property
    def customon_state(self):
        return self._customon_state

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
        # self._led.logger.debug("%s has received a message: %s", self.name, kwargs)

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

            if eventID == events.RGBLEDInputEvents.Initialize:  # this a part of the service generic interface
                self._current_state.initialize()
            elif eventID == events.RGBLEDInputEvents.Ack:
                self._current_state.acknowledge()
            elif eventID == events.RGBLEDInputEvents.Red:
                self._current_state.red()
            elif eventID == events.RGBLEDInputEvents.Green:
                self._current_state.green()
            elif eventID == events.RGBLEDInputEvents.Yellow:
                self._current_state.yellow()
            elif eventID == events.RGBLEDInputEvents.Purple:
                self._current_state.purple()
            elif eventID == events.RGBLEDInputEvents.Custom:
                self._current_state.custom(red=event.rgb_colors["red"],
                                           green=event.rgb_colors["green"],
                                           blue=event.rgb_colors["blue"])

            elif eventID == events.RGBLEDInputEvents.Off:
                self._current_state.off()
            elif eventID == events.RGBLEDInputEvents.Error:
                self._current_state.error()
            elif eventID == events.RGBLEDInputEvents.Timeout:
                self._current_state.timeout()
            elif eventID == events.RGBLEDInputEvents.NoEvent:
                self._led.logger.debug("Empty event : %s", event)
            else:
                self._led.logger.debug("Unknown event : %s", event)

