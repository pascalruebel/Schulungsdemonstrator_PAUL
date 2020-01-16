import abc
from utils.monitoring_timer import MonitoringTimer
from utils import error_codes, message_codes
from communication import events

class AssembleServiceState(metaclass=abc.ABCMeta):
    """ Abstract State class for a Assemble Service SM """

    def __init__(self, isSubstate=False):
        self._isSubstate = isSubstate

    @property
    def isSubstate(self):
        return self._isSubstate

    @abc.abstractmethod
    def start_service(self):
        raise NotImplemented

    @abc.abstractmethod
    def complete_button_pressed(self):
        raise NotImplemented

    @abc.abstractmethod
    def abort_button_pressed(self):
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


class NotReady(AssembleServiceState):
    """ Concrete State class for representing NotReady State. """

    def __init__(self, assemble_service_sm, assemble_service, super_sm=None, isSubstate=False):
        super(NotReady, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._assemble_service_sm = assemble_service_sm
        self._assemble_service = assemble_service
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._assemble_service.serviceState = "NotReady"
        self._assemble_service.logger.debug("Entering the %s state", self.name)
        self._assemble_service.publisher.publish(topic="eventID", value="NotReady", sender=self._assemble_service.name)
        self._assemble_service.publisher.publish(topic="AssembleServiceState", value="NotReady", sender=self._assemble_service.name)

    def start_service(self):
        self._assemble_service.logger.debug("%s event in %s state", self.start_service.__name__, self.name)

    def complete_button_pressed(self):
        self._assemble_service.logger.debug("%s event in %s state", self.complete_button_pressed.__name__, self.name)

    def abort_button_pressed(self):
        self._assemble_service.logger.debug("%s event in %s state", self.abort_button_pressed.__name__, self.name)

    def error(self):
        self._assemble_service.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._assemble_service_sm.set_state(self._assemble_service_sm.error_state)

    def acknowledge(self):
        self._assemble_service.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def resetjob(self):
        self._assemble_service.logger.debug("%s event in %s state", self.resetjob.__name__, self.name)

    def timeout(self):
        self._assemble_service.logger.debug("%s event in %s state", self.timeout.__name__, self.name)


class WaitForJob(AssembleServiceState):
    """ Concrete State class for representing WaitForJob State. """

    def __init__(self, assemble_service_sm, assemble_service, super_sm=None, isSubstate=False):
        super(WaitForJob, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._assemble_service_sm = assemble_service_sm
        self._assemble_service = assemble_service
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._assemble_service.serviceState = "Ready"
        self._assemble_service.logger.debug("Entering the %s state", self.name)
        self._assemble_service.publisher.publish(topic="eventID", value="Ready", sender=self._assemble_service.name)
        self._assemble_service.publisher.publish(topic="AssembleServiceState", value="Ready",
                                                 sender=self._assemble_service.name)

        if self._assemble_service_sm.service_timeout_timer is not None:
            self._assemble_service_sm.service_timeout_timer.cancel()

    def start_service(self):
        self._assemble_service.logger.debug("%s event in %s state", self.start_service.__name__, self.name)

        if self._assemble_service_sm.service_timeout_timer is not None:
            self._assemble_service_sm.service_timeout_timer.start()

        self._assemble_service_sm.set_state(self._assemble_service_sm.wait_complete_state)

    def complete_button_pressed(self):
        self._assemble_service.logger.debug("%s event in %s state", self.complete_button_pressed.__name__, self.name)

        self._assemble_service_sm.publish_message(message_code=message_codes.StationMessageCodes.NoActiveService)

    def abort_button_pressed(self):
        self._assemble_service.logger.debug("%s event in %s state", self.abort_button_pressed.__name__, self.name)

        self._assemble_service_sm.publish_message(message_code=message_codes.StationMessageCodes.NoActiveService)

    def error(self):
        self._assemble_service.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._assemble_service_sm.set_state(self._assemble_service_sm.error_state)

    def acknowledge(self):
        self._assemble_service.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def resetjob(self):
        self._assemble_service.logger.debug("%s event in %s state", self.resetjob.__name__, self.name)

    def timeout(self):
        self._assemble_service.logger.debug("%s event in %s state", self.timeout.__name__, self.name)


class WaitComplete(AssembleServiceState):
    """ Concrete State class for representing WaitComplete State. """

    def __init__(self, assemble_service_sm, assemble_service, super_sm=None, isSubstate=False):
        super(WaitComplete, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._assemble_service_sm = assemble_service_sm
        self._assemble_service = assemble_service
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._assemble_service.serviceState = "WaitComplete"
        self._assemble_service.logger.debug("Entering the %s state", self.name)
        self._assemble_service.publisher.publish(topic="AssembleServiceState", value="WaitComplete",
                                                 sender=self._assemble_service.name)

        self._assemble_service.abort_button.handle_event(event=self._assemble_service_sm.update_event)

    def start_service(self):
        self._assemble_service.logger.debug("%s event in %s state", self.start_service.__name__, self.name)

    def complete_button_pressed(self):
        self._assemble_service.logger.debug("%s event in %s state", self.complete_button_pressed.__name__, self.name)

        self._assemble_service.service_users[self._assemble_service_sm._current_service_user].done()
        self._assemble_service_sm.set_state(self._assemble_service_sm.waitforjob_state)

    def abort_button_pressed(self):
        self._assemble_service.logger.debug("%s event in %s state", self.abort_button_pressed.__name__, self.name)

        self._assemble_service_sm.publish_error(error_codes.StationErrorCodes.ServiceAbort)
        self._assemble_service_sm.set_state(self._assemble_service_sm.error_state)

    def error(self):
        self._assemble_service.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._assemble_service_sm.set_state(self._assemble_service_sm.error_state)

    def acknowledge(self):
        self._assemble_service.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def resetjob(self):
        self._assemble_service.logger.debug("%s event in %s state", self.resetjob.__name__, self.name)
        self._assemble_service_sm.set_state(self._assemble_service_sm.waitforjob_state)

    def timeout(self):
        self._assemble_service.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

        self._assemble_service_sm.publish_error(error_codes.StationErrorCodes.ServiceTimeoutError)
        self._assemble_service_sm.set_state(self._assemble_service_sm.error_state)


class Error(AssembleServiceState):
    """ Concrete State class for representing Error State. """

    def __init__(self, assemble_service_sm, assemble_service, super_sm=None, isSubstate=False):
        super(Error, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._assemble_service_sm = assemble_service_sm
        self._assemble_service = assemble_service
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._assemble_service.serviceState = "Error"
        self._assemble_service.logger.debug("Entering the %s state", self.name)
        self._assemble_service.publisher.publish(topic="eventID", value="Error", sender=self._assemble_service.name)
        self._assemble_service.publisher.publish(topic="AssembleServiceState", value="Error",
                                                 sender=self._assemble_service.name)

        if self._assemble_service_sm.service_timeout_timer is not None:
            self._assemble_service_sm.service_timeout_timer.cancel()

        try:
            if self._assemble_service_sm.init_required:
                self._assemble_service_sm.init_required = False
                self._assemble_service.service_users[self._assemble_service_sm._current_service_user].error(
                    init_required=True)
            else:
                self._assemble_service.service_users[self._assemble_service_sm._current_service_user].error(
                    init_required=False)
        except KeyError:
            self._assemble_service.logger.debug("%s service was not called yet", self.name)

    def start_service(self):
        self._assemble_service.logger.debug("%s event in %s state", self.start_service.__name__, self.name)

    def complete_button_pressed(self):
        self._assemble_service.logger.debug("%s event in %s state", self.complete_button_pressed.__name__, self.name)

        self._assemble_service_sm.publish_message(message_code=message_codes.StationMessageCodes.ServiceError)

    def abort_button_pressed(self):
        self._assemble_service.logger.debug("%s event in %s state", self.abort_button_pressed.__name__, self.name)

        self._assemble_service_sm.publish_message(message_code=message_codes.StationMessageCodes.ServiceError)

    def error(self):
        self._assemble_service.logger.debug("%s event in %s state", self.error.__name__, self.name)

    def acknowledge(self):
        self._assemble_service.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)
        self._assemble_service_sm.set_state(self._assemble_service_sm.waitforjob_state)

    def resetjob(self):
        self._assemble_service.logger.debug("%s event in %s state", self.resetjob.__name__, self.name)
        # self._assemble_service_sm.set_state(self._assemble_service_sm.waitforjob_state)

    def timeout(self):
        self._assemble_service.logger.debug("%s event in %s state", self.timeout.__name__, self.name)


class AssembleServiceStateMachine(object):
    """ Context class for the AssembleService state machine """
    def __init__(self, assemble_service, enable_timeout, timeout_interval):
        self._name = self.__class__.__name__

        self._assemble_service = assemble_service

        self._enable_timeout = enable_timeout
        self._timeout_interval = timeout_interval

        # timeout monitoring timer
        if self._enable_timeout:
            self.service_timeout_timer = MonitoringTimer(name="PressingServiceTimeoutTimer",
                                                         interval=self._timeout_interval,
                                                         callback_fnc=self.timeout_handler,
                                                         logger=self._assemble_service.logger)
        else:
            self.service_timeout_timer = None

        # event objects
        self.timeout_event = events.GenericServiceEvent(eventID=events.GenericServiceEvents.Timeout,
                                                        sender=self._assemble_service.name)
        self.update_event = events.GenericServiceEvent(eventID=events.GenericServiceEvents.Update,
                                                        sender=self._assemble_service.name)

        # state objects
        self._waitforjob_state = WaitForJob(self, self._assemble_service)
        self._not_ready_state = NotReady(self, self._assemble_service)
        self._wait_complete_state = WaitComplete(self, self._assemble_service)
        self._error_state = Error(self, self._assemble_service)

        self._current_service_user = 0

        self._current_state = self._waitforjob_state

        self.init_required = False

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
    def wait_complete_state(self):
        return self._wait_complete_state

    @property
    def error_state(self):
        return self._error_state

    def set_state(self, state):
        self._assemble_service.logger.debug("Switching from state %s to state %s", self.current_state.name, state.name)

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
        self._assemble_service.publisher.publish(topic="StationErrorCode",
                                             value=hex(error_code),
                                             sender=self._assemble_service.name)
        self._assemble_service.publisher.publish(topic="StationErrorDescription",
                                             value=error_codes.code_to_text[error_code],
                                             sender=self._assemble_service.name)

    def publish_message(self, message_code):
        self._assemble_service.publisher.publish(topic="StationMessageCode",
                                             value=hex(message_code),
                                             sender=self._assemble_service.name)
        self._assemble_service.publisher.publish(topic="StationMessageDescription",
                                             value=message_codes.code_to_text[message_code],
                                             sender=self._assemble_service.name)

    def timeout_handler(self):
        self._assemble_service.handle_event(event=self.timeout_event)

    def dispatch(self, *args, **kwargs):

        self._assemble_service.logger.debug("%s has received a message: %s", self.name, kwargs)

        try:
            # topics coming from the publishers
            topic = kwargs["topic"]
            value = kwargs["value"]
            sender = kwargs["sender"]

            if sender == "ButtonProductionError":

                if topic == "Value":
                    if value:
                        self._current_state.abort_button_pressed()
                    else:
                        # update complete button
                        self._assemble_service.complete_button.handle_event(event=self.update_event)

                elif topic == "State":

                    if value == "Error":
                        self._current_state.error()
                    elif value == "NotInitialized":
                        self._current_state.error()

            elif sender == "ButtonProductionDone":

                if topic == "Value":
                    if value:
                        self._current_state.complete_button_pressed()
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