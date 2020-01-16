import abc
from communication import events
from utils import error_codes, message_codes
from utils.monitoring_timer import MonitoringTimer


class InitializationState(metaclass=abc.ABCMeta):
    """ Abstract State class for a Init Service SM """

    def __init__(self, isSubstate=False):
        self._isSubstate = isSubstate

    @property
    def isSubstate(self):
        return self._isSubstate

    @abc.abstractmethod
    def initialize(self):
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
    def device_is_initialized(self):
        raise NotImplemented

    def enter_action(self):
        pass

    def exit_action(self):
        pass


class NotInitialized(InitializationState):
    """ Concrete State class for representing NotInitialized State"""

    def __init__(self, initservice_sm, initservice, super_sm=None, isSubstate=False):
        super(NotInitialized, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._initservice_sm = initservice_sm
        self._initservice = initservice
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._initservice.logger.debug("Entering the %s state", self.name)
        self._initservice.publisher.publish(topic="InitServiceState", value="NotInitialized", sender=self._initservice.name)

    def initialize(self):
        self._initservice.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._initservice_sm.set_state(self._initservice_sm.initialization_state)

    def error(self):
        self._initservice.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._initservice_sm.set_state(self._initservice_sm.error_state)

    def acknowledge(self):
        self._initservice.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._initservice.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def device_is_initialized(self):
        self._initservice.logger.debug("%s event in %s state", self.device_is_initialized.__name__, self.name)


class Initialization(InitializationState):
    """ Concrete State class for representing Init State"""
    def __init__(self, initservice_sm, initservice, super_sm=None, isSubstate=False):
        super(Initialization, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._initservice_sm = initservice_sm
        self._initservice = initservice
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._initservice.publisher.publish(topic="InitServiceState", value="Initialization", sender=self._initservice.name)
        self._initservice.logger.debug("Entering the %s state", self.name)

        if self._initservice_sm.service_timeout_timer is not None:
            self._initservice_sm.service_timeout_timer.start()

        # initialize a first device from the list
        self._initservice_sm.current_dev_index = 0
        self._initservice_sm.devices_list[self._initservice_sm.current_dev_index].handle_event(event=self._initservice_sm.init_event)

        self._initservice.logger.info("Device %s of %s, %s is initializing", self._initservice_sm.current_dev_index,
                                      self._initservice_sm.devices_list_length,
                                      self._initservice_sm.devices_list[
                                          self._initservice_sm.current_dev_index].name)

    def initialize(self):
        self._initservice.logger.debug("%s event in %s state", self.initialize.__name__, self.name)

        # initialize a first device from the list
        self._initservice_sm.current_dev_index = 0
        self._initservice_sm.devices_list[self._initservice_sm.current_dev_index].handle_event(event=self._initservice_sm.init_event)

    def error(self):
        self._initservice.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._initservice_sm.set_state(self._initservice_sm.error_state)

    def acknowledge(self):
        self._initservice.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._initservice.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

        self._initservice_sm.publish_error(error_codes.StationErrorCodes.InitServiceTimeout)

        self._initservice_sm.set_state(self._initservice_sm.error_state)

    def device_is_initialized(self):
        self._initservice.logger.debug("%s event in %s state", self.device_is_initialized.__name__, self.name)

        number_of_devices = self._initservice_sm.devices_list_length

        self._initservice.logger.info("Device %s of %s, %s was initialized", self._initservice_sm.current_dev_index,
                                                                                number_of_devices,
                                        self._initservice_sm.devices_list[self._initservice_sm.current_dev_index].name)

        self._initservice_sm.current_dev_index = self._initservice_sm.current_dev_index + 1

        if self._initservice_sm.current_dev_index >= number_of_devices:
            self._initservice_sm.set_state(self._initservice_sm.initdone_state)
        else:
            # initialize the next device from the list
            self._initservice_sm.devices_list[self._initservice_sm.current_dev_index].handle_event(event=self._initservice_sm.init_event)
            self._initservice.logger.info("Device %s of %s, %s is initializing", self._initservice_sm.current_dev_index,
                                          number_of_devices,
                                          self._initservice_sm.devices_list[
                                              self._initservice_sm.current_dev_index].name)


class InitializationDone(InitializationState):
    """ Concrete State class for representing  Initialization done state"""
    def __init__(self, initservice_sm, initservice, super_sm=None, isSubstate=False):
        super(InitializationDone, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._initservice_sm = initservice_sm
        self._initservice = initservice
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._initservice.logger.debug("Entering the %s state", self.name)
        self._initservice.publisher.publish(topic="InitServiceState", value="Initialization:Done",
                                            sender=self._initservice.name)
        self._initservice.service_users[self._initservice_sm._current_service_user].done()

        if self._initservice_sm.service_timeout_timer is not None:
            self._initservice_sm.service_timeout_timer.cancel()

    def initialize(self):
        self._initservice.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._initservice_sm.set_state(self._initservice_sm.initialization_state)

    def error(self):
        self._initservice.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._initservice_sm.set_state(self._initservice_sm.error_state)

    def acknowledge(self):
        self._initservice.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._initservice.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def device_is_initialized(self):
        self._initservice.logger.debug("%s event in %s state", self.device_is_initialized.__name__, self.name)


class Error(InitializationState):
    """ Concrete State class for representing Error State"""
    def __init__(self, initservice_sm, initservice, super_sm=None, isSubstate=False):
        super(Error, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._initservice_sm = initservice_sm
        self._initservice = initservice
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._initservice.logger.debug("Entering the %s state", self.name)
        self._initservice.publisher.publish(topic="InitServiceState", value="Error", sender=self._initservice.name)

        if self._initservice_sm.service_timeout_timer is not None:
            self._initservice_sm.service_timeout_timer.cancel()

        if self._initservice_sm.init_required:
            self._initservice_sm.init_required = False
            self._initservice.service_users[self._initservice_sm._current_service_user].error(init_required=True)
        else:
            self._initservice.service_users[self._initservice_sm._current_service_user].error(init_required=False)

    def initialize(self):
        self._initservice.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._initservice_sm.set_state(self._initservice_sm.initialization_state)

    def error(self):
        self._initservice.logger.debug("%s event in %s state", self.error.__name__, self.name)

    def acknowledge(self):
        self._initservice.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)
        self._initservice_sm.set_state(self._initservice_sm.initdone_state)

    def timeout(self):
        self._initservice.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def device_is_initialized(self):
        self._initservice.logger.debug("%s event in %s state", self.device_is_initialized.__name__, self.name)


class InitServiceStateMachine(object):
    """ Context class for the Init Service state machine """
    def __init__(self, initservice, enable_timeout, timeout_interval, devices_list):
        self._name = self.__class__.__name__

        self._initservice = initservice  # ref to the service object

        self._enable_timeout = enable_timeout
        self._timeout_interval = timeout_interval

        self.init_required = False

        # timeout monitoring timer
        if self._enable_timeout:
            self.service_timeout_timer = MonitoringTimer(name="InitServiceTimeoutTimer",
                                                         interval=self._timeout_interval,
                                                         callback_fnc=self.timeout_handler,
                                                         logger=self._initservice.logger)
        else:
            self.service_timeout_timer = None

        # events :
        self.timeout_event = events.GenericServiceEvent(eventID=events.GenericServiceEvents.Timeout,
                                                   sender=self._initservice.name)
        self.init_event = events.BaseInputEvent(eventID=events.BaseInputEvents.Initialize, sender=self._initservice.name)


        self.devices_list = devices_list
        self.devices_list_length = len(self.devices_list)
        self.current_dev_index = 0

        self._notinitialized_state = NotInitialized(self, self._initservice)  # rack's states instances
        self._initialization_state = Initialization(self, self._initservice)
        self._initdone_state = InitializationDone(self, self._initservice)
        self._error_state = Error(self, self._initservice)

        self._current_state = self._notinitialized_state
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
    def notinitialized_state(self):
        return self._notinitialized_state

    @property
    def initialization_state(self):
        return self._initialization_state

    @property
    def initdone_state(self):
        return self._initdone_state

    @property
    def error_state(self):
        return self._error_state

    def set_state(self, state):
        self._initservice.logger.debug("Switching from state %s to state %s", self.current_state.name, state.name)

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
        self._initservice.publisher.publish(topic="StationErrorCode",
                                                value=hex(error_code),
                                                sender=self._initservice.name)
        self._initservice.publisher.publish(topic="StationErrorDescription",
                                                value=error_codes.code_to_text[error_code],
                                                sender=self._initservice.name)

    def publish_message(self, message_code):
        self._initservice.publisher.publish(topic="StationMessageCode",
                                                value=hex(message_code),
                                                sender=self._initservice.name)
        self._initservice.publisher.publish(topic="StationMessageDescription",
                                                value=message_codes.code_to_text[message_code],
                                                sender=self._initservice.name)

    def timeout_handler(self):
        self.init_required = True
        self.dispatch(event=self.timeout_event)

    def dispatch(self, *args, **kwargs):

        self._initservice.logger.debug("%s has received a message: %s", self.name, kwargs)

        try:
            # topics coming from the publishers
            topic = kwargs["topic"]
            value = kwargs["value"]
            sender = kwargs["sender"]

            if topic == "Value":
                pass

            elif topic == "State":

                if value == "Error":
                    self._current_state.error()
                elif value == "Initialized":
                    self._current_state.device_is_initialized()

            elif topic == "Ack":

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
                self._current_state.initialize()
                self._current_service_user = service_index
            elif eventID == events.GenericServiceEvents.Cancel:
                self._initservice.logger.debug("Cancel service was not implemented for the %s service", self._initservice.name)
            elif eventID == events.GenericServiceEvents.Done:  # for callable services
                pass

            elif eventID == events.GenericServiceEvents.Timeout:  # timeout event comes from the service itself ???
                self._current_state.timeout()

