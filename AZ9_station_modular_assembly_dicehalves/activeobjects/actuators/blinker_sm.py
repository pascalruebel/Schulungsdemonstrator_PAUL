import abc
from utils.monitoring_timer import MonitoringTimer
from communication import events
from utils import error_codes, message_codes

class BlinkerState(metaclass=abc.ABCMeta):
    """ Abstract State class for a Blinker SM """

    def __init__(self, isSubstate=False):
        self._isSubstate = isSubstate

    @property
    def isSubstate(self):
        return self._isSubstate

    @abc.abstractmethod
    def start(self):
        raise NotImplemented

    @abc.abstractmethod
    def stop(self):
        raise NotImplemented

    @abc.abstractmethod
    def error(self):
        raise NotImplemented

    @abc.abstractmethod
    def acknowledge(self):
        raise NotImplemented

    def enter_action(self):
        pass

    def exit_action(self):
        pass


class NotInitialized(BlinkerState):
    """ Concrete State class for a NotInitialized SM """
    def __init__(self, blinker_sm, blinker, super_sm=None, isSubstate=False):
        super(NotInitialized, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._blinker_sm = blinker_sm
        self._blinker = blinker
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    def enter_action(self):
        #self._blinker.publisher.publish(topic="State", value="NotInitialized", sender=self._blinker.name)
        self._blinker_sm.set_state(self._blinker_sm.init_state)

    def initialize(self):
        self._blinker.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._blinker_sm.set_state(self._blinker_sm.init_state)

    def start(self):
        self._blinker.logger.debug("%s event in %s state", self.start.__name__, self.name)

    def stop(self):
        self._blinker.logger.debug("%s event in %s state", self.stop.__name__, self.name)

    def error(self):
        self._blinker.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._blinker_sm.set_state(self._blinker_sm.error_state)
        self._blinker.shutter_open()

    def acknowledge(self):
        self._blinker.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._blinker.logger.debug("%s event in %s state", self.timeout.__name__, self.name)


class Initialized(BlinkerState):
    """ Concrete State class for a Initialized SM """
    def __init__(self, blinker_sm, blinker, super_sm=None, isSubstate=False):
        super(Initialized, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._blinker_sm = blinker_sm
        self._blinker = blinker
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    def enter_action(self):
        #self._blinker.publisher.publish(topic="State", value="Initialized", sender=self._blinker.name)
        self._blinker.shutter_open()
        self._blinker_sm.reset_blinks_counter()
        self._blinker.publisher.publish(topic="Value", value=False, sender=self._blinker.name)

    def initialize(self):
        self._blinker.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._blinker.shutter_open()
        self._blinker_sm.reset_blinks_counter()
        self._blinker_sm.set_state(self._blinker_sm.init_state)

    def start(self):
        # self._blinker.logger.debug("%s event in %s state", self.start.__name__, self.name)
        if not self._blinker_sm.blinks_counter_overflow():
            self._blinker_sm.set_state(self._blinker_sm.shutterclose_state)

    def stop(self):
        self._blinker.logger.debug("%s event in %s state", self.stop.__name__, self.name)

    def error(self):
        self._blinker.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._blinker_sm.set_state(self._blinker_sm.error_state)
        self._blinker.shutter_open()

    def acknowledge(self):
        self._blinker.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._blinker.logger.debug("%s event in %s state", self.timeout.__name__, self.name)


class ShutterOpen(BlinkerState):
    """ Concrete State class for a ShutterOpen SM """
    def __init__(self, blinker_sm, blinker, super_sm=None, isSubstate=False):
        super(ShutterOpen, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._blinker_sm = blinker_sm
        self._blinker = blinker
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    def enter_action(self):
       # self._blinker.publisher.publish(topic="State", value="ShutterOpen", sender=self._blinker.name)
        self._blinker_sm.shutteropen_timer.interval = self._blinker_sm.shutterclose_time
        self._blinker_sm.shutteropen_timer.start()

        self._blinker.shutter_open()

        self._blinker_sm.increase_blinks_counter()

        self._blinker.publisher.publish(topic="Value", value=True, sender=self._blinker.name)

    def initialize(self):
        self._blinker.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._blinker_sm.shutteropen_timer.cancel()
        self._blinker_sm.set_state(self._blinker_sm.init_state)

    def start(self):
        self._blinker.logger.debug("%s event in %s state", self.start.__name__, self.name)

        self._blinker_sm.shutteropen_timer.interval = self._blinker_sm.shutterclose_time
        self._blinker_sm.shutteropen_timer.start()

        self._blinker.shutter_open()

    def stop(self):
        self._blinker.logger.debug("%s event in %s state", self.stop.__name__, self.name)
        self._blinker_sm.shutteropen_timer.cancel()
        self._blinker_sm.set_state(self._blinker_sm.init_state)

    def error(self):
        self._blinker.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._blinker_sm.shutteropen_timer.cancel()
        self._blinker_sm.set_state(self._blinker_sm.error_state)

    def acknowledge(self):
        self._blinker.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        #self._blinker.logger.debug("%s event in %s state", self.timeout.__name__, self.name)
        if self._blinker_sm.blinks_counter_overflow():
            self._blinker.shutter_open()
            self._blinker_sm.set_state(self._blinker_sm.init_state)
        else:
            self._blinker_sm.set_state(self._blinker_sm.shutterclose_state)


class ShutterClose(BlinkerState):
    """ Concrete State class for a ShutterClose SM """
    def __init__(self, blinker_sm, blinker, super_sm=None, isSubstate=False):
        super(ShutterClose, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._blinker_sm = blinker_sm
        self._blinker = blinker
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    def enter_action(self):
        #self._blinker.publisher.publish(topic="State", value="ShutterClose", sender=self._blinker.name)

        self._blinker_sm.shutterclose_timer.interval = self._blinker_sm.shutterclose_time
        self._blinker_sm.shutterclose_timer.start()
        self._blinker.shutter_close()

        self._blinker.publisher.publish(topic="Value", value=True, sender=self._blinker.name)

    def initialize(self):
        self._blinker.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._blinker_sm.shutterclose_timer.cancel()
        self._blinker_sm.set_state(self._blinker_sm.init_state)

    def start(self):
        self._blinker.logger.debug("%s event in %s state", self.start.__name__, self.name)

        self._blinker_sm.shutterclose_timer.interval = self._blinker_sm.shutterclose_time
        self._blinker_sm.shutterclose_timer.start()
        self._blinker.shutter_close()

    def stop(self):
        self._blinker.logger.debug("%s event in %s state", self.stop.__name__, self.name)
        self._blinker_sm.shutterclose_timer.cancel()
        self._blinker_sm.set_state(self._blinker_sm.init_state)

    def error(self):
        self._blinker.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._blinker_sm.shutterclose_timer.cancel()
        self._blinker_sm.set_state(self._blinker_sm.error_state)

    def acknowledge(self):
        self._blinker.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        #self._blinker.logger.debug("%s event in %s state", self.timeout.__name__, self.name)
        self._blinker_sm.set_state(self._blinker_sm.shutteropen_state)


class Error(BlinkerState):
    """ Concrete State class for a Error SM """
    def __init__(self, blinker_sm, blinker, super_sm=None, isSubstate=False):
        super(Error, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._blinker_sm = blinker_sm
        self._blinker = blinker
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    def enter_action(self):
        #self._blinker.publisher.publish(topic="State", value="Error", sender=self._blinker.name)
        self._blinker.publisher.publish(topic="Value", value=False, sender=self._blinker.name)
        self._blinker.shutter_open()

    def initialize(self):
        self._blinker.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._blinker_sm.set_state(self._blinker_sm.init_state)

    def start(self):
        self._blinker.logger.debug("%s event in %s state", self.start.__name__, self.name)

    def stop(self):
        self._blinker.logger.debug("%s event in %s state", self.stop.__name__, self.name)

    def error(self):
        self._blinker.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._blinker_sm.set_state(self._blinker_sm.error_state)

    def acknowledge(self):
        self._blinker.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)
        self._blinker_sm.set_state(self._blinker_sm.init_state)

    def timeout(self):
        self._blinker.logger.debug("%s event in %s state", self.timeout.__name__, self.name)


class BlinkerStateMachine(object):
    """ Context class for the Blinker state machine """
    def __init__(self, blinker):
        self._name = self.__class__.__name__

        self._blinker = blinker
        self._blinksCounter = self._blinker.blinks_number

        self.timeout_event = events.BlinkerEvent(eventID=events.BlinkerEvents.Timeout, sender=self._blinker.name)

        self.shutteropen_time = self._blinker.ontime
        self.shutterclose_time = self._blinker.offtime

        self.shutteropen_timer = MonitoringTimer(name="ShutterOpenTimer",
                                                        interval=self._blinker.ontime,
                                                        callback_fnc=self.timeout_handler)

        self.shutterclose_timer = MonitoringTimer(name="ShutterCloseTimer",
                                                        interval=self._blinker.offtime,
                                                        callback_fnc=self.timeout_handler)

        self._notinit_state = NotInitialized(self, self._blinker)

        self._init_state = Initialized(self, self._blinker)
        self._shutteropen_state = ShutterOpen(self, self._blinker)
        self._shutterclose_state = ShutterClose(self, self._blinker)
        self._error_state = Error(self, self._blinker)


        self._current_state = self._notinit_state
        self.set_state(self._current_state)

    @property
    def name(self):
        return self._name

    @property
    def shutteropen_time(self):
        return self._shutteropen_time

    @shutteropen_time.setter
    def shutteropen_time(self, new_shutteropen_time):
        if new_shutteropen_time > 0:
            self._shutteropen_time = new_shutteropen_time
        else:
            self._shutteropen_time = 0

    @property
    def shutterclose_time(self):
        return self._shutterclose_time

    @shutterclose_time.setter
    def shutterclose_time(self, new_shutterclose_time):
        if new_shutterclose_time > 0:
            self._shutterclose_time = new_shutterclose_time
        else:
            self._shutterclose_time = 0

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
    def shutteropen_state(self):
        return self._shutteropen_state

    @property
    def shutterclose_state(self):
        return self._shutterclose_state

    @property
    def error_state(self):
        return self._error_state

    def set_state(self, state):
        # self._blinker.logger.debug("%s State is switching to %s State", self._current_state.name, state.name)

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
        self._blinker.publisher.publish(topic="StationErrorCode",
                                              value=hex(error_code),
                                              sender=self._blinker.name)
        self._blinker.publisher.publish(topic="StationErrorDescription",
                                              value=error_codes.code_to_text[error_code],
                                              sender=self._blinker.name)

    def publish_message(self, message_code):
        self._blinker.publisher.publish(topic="StationMessageCode",
                                                value=hex(message_code),
                                                sender=self._blinker.name)
        self._blinker.publisher.publish(topic="StationMessageDescription",
                                                value=message_codes.code_to_text[message_code],
                                                sender=self._blinker.name)

    def timeout_handler(self):
        self._blinker.handle_event(event=self.timeout_event)

    def increase_blinks_counter(self):
        self._blinksCounter = self._blinksCounter + 1

    def reset_blinks_counter(self):
        self._blinksCounter = 0

    def blinks_counter_overflow(self):
        if (self._blinksCounter  >= self._blinker.blinks_number) and (self._blinker.blinks_number != 0):
            return True
        else:
            return False

    def dispatch(self, *args, **kwargs):

        # self._blinker.logger.debug("%s has received a message: %s", self.name, kwargs)

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

            if eventID == events.BlinkerEvents.Initialize:
                self._current_state.initialize()
            elif eventID == events.BlinkerEvents.Ack:
                self._current_state.acknowledge()
            elif eventID == events.BlinkerEvents.Start:
                if event.blinker_parameters is not None:
                    self.shutteropen_time = event.blinker_parameters["ontime"]
                    self.shutterclose_time = event.blinker_parameters["offtime"]
                    self._blinker.blinks_number  = event.blinker_parameters["blinks"]
                self._current_state.start()
            elif eventID == events.BlinkerEvents.Stop:
                self._blinker.shutter_open()
                self._current_state.stop()
            elif eventID == events.BlinkerEvents.Error:
                self._current_state.error()
            elif eventID == events.BlinkerEvents.Timeout:
                self._current_state.timeout()
            elif eventID == events.BlinkerEvents.NoEvent:
                self._blinker.logger.debug("Empty event : %s", event)
            else:
                self._blinker.logger.debug("Unknown event : %s", event)