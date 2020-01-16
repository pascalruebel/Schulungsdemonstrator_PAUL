import abc
from utils.monitoring_timer import MonitoringTimer
from utils import error_codes, message_codes
from communication import events

class ToFrontPosServiceState(metaclass=abc.ABCMeta):
    """ Abstract State class for a Pressing Service SM """

    def __init__(self, isSubstate=False):
        self._isSubstate = isSubstate

    @property
    def isSubstate(self):
        return self._isSubstate

    @abc.abstractmethod
    def start_service(self):
        raise NotImplemented

    @abc.abstractmethod
    def carriage_in_frontpos(self):
        raise NotImplemented

    @abc.abstractmethod
    def clamp_open(self):
        raise NotImplemented

    @abc.abstractmethod
    def press_not_upperpos(self):
        raise NotImplemented

    @abc.abstractmethod
    def press_uppperpos(self):
        raise NotImplemented

    @abc.abstractmethod
    def error(self):
        raise NotImplemented

    @abc.abstractmethod
    def acknowledge(self):
        raise NotImplemented

    @abc.abstractmethod
    def resetjob(self):
        raise NotImplemented

    @abc.abstractmethod
    def timeout(self):
        raise NotImplemented

    def enter_action(self):
        pass

    def exit_action(self):
        pass


class NotReady(ToFrontPosServiceState):
    """ Concrete State class for representing NotReady State. """

    def __init__(self, tofront_service_sm, tofront_service, super_sm=None, isSubstate=False):
        super(NotReady, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._tofront_service_sm = tofront_service_sm
        self._tofront_service = tofront_service
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._tofront_service.logger.debug("Entering the %s state", self.name)
        self._tofront_service.serviceState = "PressNotUp"
        self._tofront_service.publisher.publish(topic="eventID", value="NotReady", sender=self._tofront_service.name)
        self._tofront_service.publisher.publish(topic="ToFrontPosServiceState", value="NotReady", sender=self._tofront_service.name)

        # blinking
        self._tofront_service.blinker.handle_event(event=self._tofront_service_sm.blinking_start_event)

    def start_service(self):
        self._tofront_service.logger.debug("%s event in %s state", self.start_service.__name__, self.name)

    def carriage_in_frontpos(self):
        self._tofront_service.logger.debug("%s event in %s state", self.carriage_in_frontpos.__name__, self.name)

    def clamp_open(self):
        self._tofront_service.logger.debug("%s event in %s state", self.clamp_open.__name__, self.name)

    def press_not_upperpos(self):
        self._tofront_service.logger.debug("%s event in %s state", self.press_not_upperpos.__name__, self.name)

    def press_uppperpos(self):
        self._tofront_service.logger.debug("%s event in %s state", self.press_uppperpos.__name__, self.name)

        # stop blinking
        self._tofront_service.blinker.handle_event(event=self._tofront_service_sm.blinking_stop_event)

        self._tofront_service_sm.set_state(self._tofront_service_sm.waitforjob_state)

    def error(self):
        self._tofront_service.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._tofront_service_sm.set_state(self._tofront_service_sm.error_state)

    def acknowledge(self):
        self._tofront_service.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def resetjob(self):
        self._tofront_service.logger.debug("%s event in %s state", self.resetjob.__name__, self.name)

    def timeout(self):
        self._tofront_service.logger.debug("%s event in %s state", self.timeout.__name__, self.name)


class WaitForJob(ToFrontPosServiceState):
    """ Concrete State class for representing WaitForJob State. """

    def __init__(self, tofront_service_sm, tofront_service, super_sm=None, isSubstate=False):
        super(WaitForJob, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._tofront_service_sm = tofront_service_sm
        self._tofront_service = tofront_service
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._tofront_service.logger.debug("Entering the %s state", self.name)
        self._tofront_service.serviceState = "Ready"
        self._tofront_service.publisher.publish(topic="eventID", value="Ready", sender=self._tofront_service.name)
        self._tofront_service.publisher.publish(topic="ToFrontPosServiceState", value="Ready",
                                                sender=self._tofront_service.name)

        if self._tofront_service_sm.service_timeout_timer is not None:
            self._tofront_service_sm.service_timeout_timer.cancel()

        # press update:
        self._tofront_service.press.handle_event(event=self._tofront_service_sm.press_update_event)

    def start_service(self):
        self._tofront_service.logger.debug("%s event in %s state", self.start_service.__name__, self.name)

        if self._tofront_service_sm.service_timeout_timer is not None:
            self._tofront_service_sm.service_timeout_timer.start()

        self._tofront_service.clamp.handle_event(event=self._tofront_service_sm.clamp_open_event)
        self._tofront_service_sm.set_state(self._tofront_service_sm.wait_frontpos_state)

    def carriage_in_frontpos(self):
        self._tofront_service.logger.debug("%s event in %s state", self.carriage_in_frontpos.__name__, self.name)

    def clamp_open(self):
        self._tofront_service.logger.debug("%s event in %s state", self.clamp_open.__name__, self.name)

    def press_not_upperpos(self):
        self._tofront_service.logger.debug("%s event in %s state", self.press_not_upperpos.__name__, self.name)
        if self._tofront_service_sm.station_ready:
            self._tofront_service_sm.set_state(self._tofront_service_sm.not_ready_state)

    def press_uppperpos(self):
        self._tofront_service.logger.debug("%s event in %s state", self.press_uppperpos.__name__, self.name)

    def error(self):
        self._tofront_service.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._tofront_service_sm.set_state(self._tofront_service_sm.error_state)

    def acknowledge(self):
        self._tofront_service.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def resetjob(self):
        self._tofront_service.logger.debug("%s event in %s state", self.resetjob.__name__, self.name)

    def timeout(self):
        self._tofront_service.logger.debug("%s event in %s state", self.timeout.__name__, self.name)


class WaitFrontPos(ToFrontPosServiceState):
    """ Concrete State class for representing WaitFrontPos State. """

    def __init__(self, tofront_service_sm, tofront_service, super_sm=None, isSubstate=False):
        super(WaitFrontPos, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._tofront_service_sm = tofront_service_sm
        self._tofront_service = tofront_service
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._tofront_service.logger.debug("Entering the %s state", self.name)
        self._tofront_service.serviceState = "Ready"
        self._tofront_service.publisher.publish(topic="ToFrontPosServiceState", value="WaitFrontPos",
                                                sender=self._tofront_service.name)

        self._tofront_service.press.handle_event(event=self._tofront_service_sm.press_update_event)

    def start_service(self):
        self._tofront_service.logger.debug("%s event in %s state", self.start_service.__name__, self.name)

    def carriage_in_frontpos(self):
        self._tofront_service.logger.debug("%s event in %s state", self.carriage_in_frontpos.__name__, self.name)

        self._tofront_service.service_users[self._tofront_service_sm._current_service_user].done()

        self._tofront_service_sm.set_state(self._tofront_service_sm.waitforjob_state)

    def clamp_open(self):
        self._tofront_service.logger.debug("%s event in %s state", self.clamp_open.__name__, self.name)

    def press_not_upperpos(self):
        self._tofront_service.logger.debug("%s event in %s state", self.press_not_upperpos.__name__, self.name)

    def press_uppperpos(self):
        self._tofront_service.logger.debug("%s event in %s state", self.press_uppperpos.__name__, self.name)

    def error(self):
        self._tofront_service.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._tofront_service_sm.set_state(self._tofront_service_sm.error_state)

    def acknowledge(self):
        self._tofront_service.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def resetjob(self):
        self._tofront_service.logger.debug("%s event in %s state", self.resetjob.__name__, self.name)
        self._tofront_service_sm.set_state(self._tofront_service_sm.waitforjob_state)

    def timeout(self):
        self._tofront_service.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

        self._tofront_service_sm.publish_error(error_codes.StationErrorCodes.ToFrontposServiceTimeout)
        self._tofront_service_sm.set_state(self._tofront_service_sm.error_state)


class Error(ToFrontPosServiceState):
    """ Concrete State class for representing Error State. """

    def __init__(self, tofront_service_sm, tofront_service, super_sm=None, isSubstate=False):
        super(Error, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._tofront_service_sm = tofront_service_sm
        self._tofront_service = tofront_service
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._tofront_service.logger.debug("Entering the %s state", self.name)
        self._tofront_service.serviceState = "Error"
        self._tofront_service.publisher.publish(topic="eventID", value="Error", sender=self._tofront_service.name)
        self._tofront_service.publisher.publish(topic="ToFrontPosServiceState", value="Error",
                                                sender=self._tofront_service.name)

        if self._tofront_service_sm.service_timeout_timer is not None:
            self._tofront_service_sm.service_timeout_timer.cancel()

        try:
            if self._tofront_service_sm.init_required:
                self._tofront_service_sm.init_required = False
                self._tofront_service.service_users[self._tofront_service_sm._current_service_user].error(
                    init_required=True)
            else:
                self._tofront_service.service_users[self._tofront_service_sm._current_service_user].error(
                    init_required=False)
        except KeyError:
            self._tofront_service.logger.debug("%s service was not called yet", self.name)

    def start_service(self):
        self._tofront_service.logger.debug("%s event in %s state", self.start_service.__name__, self.name)

    def carriage_in_frontpos(self):
        self._tofront_service.logger.debug("%s event in %s state", self.carriage_in_frontpos.__name__, self.name)

    def clamp_open(self):
        self._tofront_service.logger.debug("%s event in %s state", self.clamp_open.__name__, self.name)

    def press_not_upperpos(self):
        self._tofront_service.logger.debug("%s event in %s state", self.press_not_upperpos.__name__, self.name)

    def press_uppperpos(self):
        self._tofront_service.logger.debug("%s event in %s state", self.press_uppperpos.__name__, self.name)

    def error(self):
        self._tofront_service.logger.debug("%s event in %s state", self.error.__name__, self.name)

    def acknowledge(self):
        self._tofront_service.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)
        self._tofront_service_sm.set_state(self._tofront_service_sm.waitforjob_state)

    def resetjob(self):
        self._tofront_service.logger.debug("%s event in %s state", self.resetjob.__name__, self.name)
        self._tofront_service_sm.set_state(self._tofront_service_sm.waitforjob_state)

    def timeout(self):
        self._tofront_service.logger.debug("%s event in %s state", self.timeout.__name__, self.name)


class ToFrontPosServiceStateMachine(object):
    """ Context class for the PressService state machine """
    def __init__(self, tofrontpos_service, enable_timeout, timeout_interval):
        self._name = self.__class__.__name__

        self._tofrontpos_service = tofrontpos_service

        self._enable_timeout = enable_timeout
        self._timeout_interval = timeout_interval

        # timeout monitoring timer
        if self._enable_timeout:
            self.service_timeout_timer = MonitoringTimer(name="PressingServiceTimeoutTimer",
                                                         interval=self._timeout_interval,
                                                         callback_fnc=self.timeout_handler,
                                                         logger=self._tofrontpos_service.logger)
        else:
            self.service_timeout_timer = None

        # event objects
        self.press_update_event = events.PressInputEvent(eventID=events.PressInputEvents.Update,
                                                         sender=self._tofrontpos_service.name)
        self.clamp_open_event = events.SimpleClampInputEvent(eventID=events.SimpleClampInputEvents.Open,
                                                             sender=self._tofrontpos_service.name)
        self.timeout_event = events.GenericServiceEvent(eventID=events.GenericServiceEvents.Timeout,
                                                        sender=self._tofrontpos_service.name)
        self.blinking_start_event = events.BlinkerEvent(eventID=events.BlinkerEvents.Start,
                                                        sender=self._tofrontpos_service.name)
        self.blinking_stop_event = events.BlinkerEvent(eventID=events.BlinkerEvents.Stop,
                                                       sender=self._tofrontpos_service.name)

        # state objects
        self._waitforjob_state = WaitForJob(self, self._tofrontpos_service)
        self._not_ready_state = NotReady(self, self._tofrontpos_service)
        self._wait_frontpos_state = WaitFrontPos(self, self._tofrontpos_service)
        self._error_state = Error(self, self._tofrontpos_service)

        self._current_service_user = 0

        self.init_required = False  # to show that an init is needed after the error
        self.station_ready = False # to show that the station is doing job now

        self._current_state = self._waitforjob_state
        self.set_state(self._current_state)

    # properties
    @property
    def current_state(self):
        return self._current_state

    @property
    def name(self):
        return self._name

    @property
    def waitforjob_state(self):
        return self._waitforjob_state

    @property
    def not_ready_state(self):
        return self._not_ready_state

    @property
    def wait_frontpos_state(self):
        return self._wait_frontpos_state

    @property
    def error_state(self):
        return self._error_state

    def set_state(self, state):
        self._tofrontpos_service.logger.debug("Switching from state %s to state %s", self.current_state.name, state.name)

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

    def timeout_handler(self):
        self.init_required = True
        self.dispatch(event=self.timeout_event)

    def publish_error(self, error_code):
        self._tofrontpos_service.publisher.publish(topic="StationErrorCode",
                                             value=hex(error_code),
                                             sender=self._tofrontpos_service.name)
        self._tofrontpos_service.publisher.publish(topic="StationErrorDescription",
                                             value=error_codes.code_to_text[error_code],
                                             sender=self._tofrontpos_service.name)

    def publish_message(self, message_code):
        self._tofrontpos_service.publisher.publish(topic="StationMessageCode",
                                             value=hex(message_code),
                                             sender=self._tofrontpos_service.name)
        self._tofrontpos_service.publisher.publish(topic="StationMessageDescription",
                                             value=message_codes.code_to_text[message_code],
                                             sender=self._tofrontpos_service.name)

    def dispatch(self, *args, **kwargs):

        self._tofrontpos_service.logger.debug("%s has received a message: %s", self.name, kwargs)

        try:
            # topics coming from the publishers
            topic = kwargs["topic"]
            value = kwargs["value"]
            sender = kwargs["sender"]

            if sender == "Press":

                if topic == "Value":
                    pass

                elif topic == "State":

                    if value == "NotInitialized":
                        self._current_state.error()
                    elif value == "InUpperPosition":
                        self._current_state.press_uppperpos()
                    elif (value == "OutOfPosition") or (value == "OnEndSwitch") or (value == "InPressingPosition"):
                        self._current_state.press_not_upperpos()

            elif sender == "SensorDiceCarriageAtHome":

                if topic == "Value":
                    if value:
                        self._current_state.carriage_in_frontpos()
                    else:
                        pass

                elif topic == "State":

                    if value == "Error":
                        self._current_state.error()
                    elif value == "NotInitialized":
                        self._current_state.error()

            elif sender == "Station":

                if topic == "Ack":
                    if value:
                        self._current_state.acknowledge()
                    else:
                        pass
                elif topic == "StationState":
                    if value == "Error":
                        self.station_ready = False
                        self._current_state.error()
                    elif value == "Ready":
                        self.station_ready = True
                    else:
                        self.station_ready = False

        except KeyError:
            event = kwargs["event"]

            eventID = event.eventID
            sender = event.sender
            service_index = event.service_index

            if eventID == events.GenericServiceEvents.Execute:  # this a part of the service generic interface
                self._current_state.start_service()
                self._current_service_user = service_index
            elif eventID == events.GenericServiceEvents.Cancel:
                self._current_state.resetjob()
            elif eventID == events.GenericServiceEvents.Done:  # for callable services
                pass

            elif eventID == events.GenericServiceEvents.Timeout:  # timeout event comes from the service itself ???
                self._current_state.timeout()
