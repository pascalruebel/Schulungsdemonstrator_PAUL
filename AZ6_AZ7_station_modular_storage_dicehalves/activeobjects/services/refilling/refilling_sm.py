import abc
from communication import events
from threading import Timer
from utils import error_codes, message_codes
from utils.monitoring_timer import MonitoringTimer

class RackRefillingState(metaclass=abc.ABCMeta):
    """ Abstract State class for a RackRefillingState Service SM """

    def __init__(self, isSubstate=False):
        self._isSubstate = isSubstate

    @property
    def isSubstate(self):
        return self._isSubstate

    @abc.abstractmethod
    def start_service(self):
        raise NotImplemented

    @abc.abstractmethod
    def rack_is_full(self):
        raise NotImplemented

    @abc.abstractmethod
    def carriage_is_atrack(self):
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


class WaitForJob(RackRefillingState):
    """ Concrete State class for representing WaitForJob State. """

    def __init__(self, rackrefilling_service_sm, rackrefilling_service, super_sm=None, isSubstate=False):
        super(WaitForJob, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._rackrefilling_service_sm = rackrefilling_service_sm
        self._rackrefilling_service = rackrefilling_service
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._rackrefilling_service.logger.debug("Entering the %s state", self.name)
        self._rackrefilling_service.serviceState = "Ready"
        self._rackrefilling_service.publisher.publish(topic="RefillingServiceState", value="WaitForJob",
                                                sender=self._rackrefilling_service.name)

    def start_service(self):
        self._rackrefilling_service.logger.debug("%s event in %s state", self.start_service.__name__, self.name)

        if self._rackrefilling_service_sm.service_timeout_timer is not None:
            self._rackrefilling_service_sm.service_timeout_timer.start()

        self._rackrefilling_service_sm.set_state(self._rackrefilling_service_sm.rackrefilling_state)

    def carriage_is_atrack(self):
        self._rackrefilling_service.logger.debug("%s event in %s state", self.carriage_is_atrack.__name__, self.name)

    def rack_is_full(self):
        self._rackrefilling_service.logger.debug("%s event in %s state", self.rack_is_full.__name__, self.name)

    def error(self):
        self._rackrefilling_service.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._rackrefilling_service_sm.set_state(self._rackrefilling_service_sm.error_state)

    def acknowledge(self):
        self._rackrefilling_service.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def resetjob(self):
        self._rackrefilling_service.logger.debug("%s event in %s state", self.resetjob.__name__, self.name)

    def timeout(self):
        self._rackrefilling_service.logger.debug("%s event in %s state", self.timeout.__name__, self.name)


class RackRefilling(RackRefillingState):
    """ Concrete State class for representing WaitForJob State. """

    def __init__(self, rackrefilling_service_sm, rackrefilling_service, super_sm=None, isSubstate=False):
        super(RackRefilling, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._rackrefilling_service_sm = rackrefilling_service_sm
        self._rackrefilling_service = rackrefilling_service
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._rackrefilling_service.logger.debug("Entering the %s state", self.name)
        self._rackrefilling_service.serviceState = "Busy"
        self._rackrefilling_service.publisher.publish(topic="RefillingServiceState", value="RackRefilling",
                                                      sender=self._rackrefilling_service.name)

        self._rackrefilling_service.rack.handle_event(event=self._rackrefilling_service_sm.rack_update_event)

    def start_service(self):
        self._rackrefilling_service.logger.debug("%s event in %s state", self.start_service.__name__, self.name)

    def carriage_is_atrack(self):
        self._rackrefilling_service.logger.debug("%s event in %s state", self.carriage_is_atrack.__name__, self.name)
        self._rackrefilling_service_sm.set_state(self._rackrefilling_service_sm.error_state)

    def rack_is_full(self):
        self._rackrefilling_service.logger.debug("%s event in %s state", self.rack_is_full.__name__, self.name)

        if self._rackrefilling_service_sm.service_timeout_timer is not None:
            self._rackrefilling_service_sm.service_timeout_timer.cancel()

        self._rackrefilling_service.service_users[self._rackrefilling_service_sm._current_service_user].done()

        self._rackrefilling_service_sm.set_state(self._rackrefilling_service_sm.waitforjob_state)

    def error(self):
        self._rackrefilling_service.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._rackrefilling_service_sm.set_state(self._rackrefilling_service_sm.error_state)

    def acknowledge(self):
        self._rackrefilling_service.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def resetjob(self):
        self._rackrefilling_service.logger.debug("%s event in %s state", self.resetjob.__name__, self.name)

        if self._rackrefilling_service_sm.service_timeout_timer is not None:
            self._rackrefilling_service_sm.service_timeout_timer.cancel()

        self._rackrefilling_service.service_users[self._rackrefilling_service_sm._current_service_user].done()

        self._rackrefilling_service_sm.set_state(self._rackrefilling_service_sm.waitforjob_state)

    def timeout(self):
        self._rackrefilling_service.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

        self._rackrefilling_service_sm.publish_error(error_codes.StationErrorCodes.RefillingServiceTimeout)
        self._rackrefilling_service_sm.set_state(self._rackrefilling_service_sm.error_state)


class Error(RackRefillingState):
    """ Concrete State class for representing Error State. """

    def __init__(self, rackrefilling_service_sm, rackrefilling_service, super_sm=None, isSubstate=False):
        super(Error, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._rackrefilling_service_sm = rackrefilling_service_sm
        self._rackrefilling_service = rackrefilling_service
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._rackrefilling_service.logger.debug("Entering the %s state", self.name)
        self._rackrefilling_service.serviceState = "Error"
        self._rackrefilling_service.publisher.publish(topic="RefillingServiceState", value="Error",
                                                      sender=self._rackrefilling_service.name)

        if self._rackrefilling_service_sm.service_timeout_timer is not None:
            self._rackrefilling_service_sm.service_timeout_timer.cancel()

        try:
            self._rackrefilling_service.service_users[self._rackrefilling_service_sm._current_service_user].error()
        except KeyError:
            self._rackrefilling_service.logger.debug("%s service was not called yet",  self.name)

    def start_service(self):
        self._rackrefilling_service.logger.debug("%s event in %s state", self.start_service.__name__, self.name)

    def carriage_is_atrack(self):
        self._rackrefilling_service.logger.debug("%s event in %s state", self.carriage_is_atrack.__name__, self.name)

    def rack_is_full(self):
        self._rackrefilling_service.logger.debug("%s event in %s state", self.rack_is_full.__name__, self.name)

    def error(self):
        self._rackrefilling_service.logger.debug("%s event in %s state", self.error.__name__, self.name)

    def acknowledge(self):
        self._rackrefilling_service.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)
        self._rackrefilling_service_sm.set_state(self._rackrefilling_service_sm.waitforjob_state)

    def resetjob(self):
        self._rackrefilling_service.logger.debug("%s event in %s state", self.resetjob.__name__, self.name)
        self._rackrefilling_service_sm.set_state(self._rackrefilling_service_sm.waitforjob_state)

    def timeout(self):
        self._rackrefilling_service.logger.debug("%s event in %s state", self.timeout.__name__, self.name)


class RackRefillingStateMachine(object):
    """ Context class for the RackRefilling state machine """
    def __init__(self, rackrefilling_service, enable_timeout, timeout_interval):
        self._name = self.__class__.__name__

        self._rackrefilling_service = rackrefilling_service

        self._enable_timeout = enable_timeout
        self._timeout_interval = timeout_interval

        # timeout monitoring timer
        if self._enable_timeout:
            self.service_timeout_timer = MonitoringTimer(name="ProvideDicehalfServiceTimeoutTimer",
                                                         interval=self._timeout_interval,
                                                         callback_fnc=self.timeout_handler,
                                                         logger=self._rackrefilling_service.logger)
        else:
            self.service_timeout_timer = None

        # events :
        self.rack_update_event = events.RackEvent(eventID=events.RackEvents.Update, sender=self._rackrefilling_service.name)
        self.timeout_event = events.GenericServiceEvent(eventID=events.GenericServiceEvents.Timeout,
                                                        sender=self._rackrefilling_service.name)

        self._waitforjob_state = WaitForJob(self, self._rackrefilling_service)
        self._rackrefilling_state = RackRefilling(self, self._rackrefilling_service)
        self._error_state = Error(self, self._rackrefilling_service)

        self._current_state = self._waitforjob_state
        self.set_state(self._current_state)

        self._current_service_user = 0

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
    def rackrefilling_state(self):
        return self._rackrefilling_state

    @property
    def error_state(self):
        return self._error_state

    def set_state(self, state):
        self._rackrefilling_service.logger.debug("Switching from state %s to state %s", self.current_state.name, state.name)

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
        self.dispatch(event=self.timeout_event)

    def publish_error(self, error_code):
        self._rackrefilling_service.publisher.publish(topic="StationErrorCode",
                                                value=hex(error_code),
                                                sender=self._rackrefilling_service.name)
        self._rackrefilling_service.publisher.publish(topic="StationErrorDescription",
                                                value=error_codes.code_to_text[error_code],
                                                sender=self._rackrefilling_service.name)

    def publish_message(self, message_code):
        self._rackrefilling_service.publisher.publish(topic="StationMessageCode",
                                                value=hex(message_code),
                                                sender=self._rackrefilling_service.name)
        self._rackrefilling_service.publisher.publish(topic="StationMessageDescription",
                                                value=message_codes.code_to_text[message_code],
                                                sender=self._rackrefilling_service.name)

    def dispatch(self, *args, **kwargs):

        self._rackrefilling_service.logger.debug("%s has received a message: %s", self.name, kwargs)

        try:            #  events comming from the publishers
            topic = kwargs["topic"]
            value = kwargs["value"]
            sender = kwargs["sender"]

            if sender == "StorageRack":

                if topic == "Value":
                    pass

                elif topic == "State":

                    if value == "Error":
                        self._current_state.error()
                    elif value == "NotInitialized":
                        # self._current_state.error()
                        pass
                    elif value == "RackEmpty":
                        pass
                    elif value == "RackFilling":
                        pass
                    elif value == "RackFull":
                        self._current_state.rack_is_full()

            elif sender == "Carriage":

                if topic == "Value":
                    pass

                elif topic == "State":

                    if value == "Error":
                        self._current_state.error()
                    elif value == "NotInitialized":
                        pass
                        # self._current_state.error()
                    elif value == "OutOfPosition":
                        pass
                    elif value == "AtFrontPosition":
                        pass
                    elif value == "AtRackPosition":
                        self._current_state.carriage_is_atrack()

                elif topic == "State":

                    if value == "Error":
                        self._current_state.error()
                    elif value == "NotInitialized":
                        pass
                        # self._current_state.error()
                    elif value == "Initialized":
                        pass

            elif sender == "Station":

                if topic == "Ack":
                    if value:
                        self._current_state.acknowledge()
                    else:
                        pass
                elif topic == "StationState" and value == "Error":
                    self._current_state.error()

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


