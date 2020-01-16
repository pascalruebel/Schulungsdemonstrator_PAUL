import abc
from communication import events
from utils import error_codes, message_codes
from utils.monitoring_timer import MonitoringTimer

class StorageDicePlateState(metaclass=abc.ABCMeta):
    """ Abstract State class for a ResetDicePlate Service SM """

    def __init__(self, isSubstate=False):
        self._isSubstate = isSubstate

    @property
    def isSubstate(self):
        return self._isSubstate

    @abc.abstractmethod
    def material_refill(self):
        raise NotImplemented

    @abc.abstractmethod
    def material_refill_done(self):
        raise NotImplemented		
		
    @abc.abstractmethod
    def material_reset(self):
        raise NotImplemented

    @abc.abstractmethod
    def material_reset_done(self):
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

    def enter_action(self):
        pass

    def exit_action(self):
        pass


class WaitForJob(StorageDicePlateState):
    """ Concrete State class for representing WaitForJob State. """

    def __init__(self, storagediceplate_sm, storagediceplate, super_sm=None, isSubstate=False):
        super(WaitForJob, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._storagediceplate_sm = storagediceplate_sm
        self._storagediceplate = storagediceplate
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._storagediceplate.logger.debug("Entering the %s state", self.name)
        self._storagediceplate.publisher.publish(topic="eventID", value="Ready", sender=self._storagediceplate.name)
		
    def material_refill(self, parameters_list):
        self._storagediceplate.logger.debug("%s event in %s state", self.material_refill.__name__, self.name)
				
		# First set the current used parameters list to the service object
        self._storagediceplate_sm.set_parameters(parameters_list)
		
        if self._storagediceplate_sm.service_timeout_timer is not None:
            self._storagediceplate_sm.service_timeout_timer.start()		
		
		# Switch into waiting diceplate state if a diceplate material supply has been requested
        self._storagediceplate.logger.debug("%s event in %s state with parameters %s", self.material_refill.__name__, self.name, parameters_list)
        self._storagediceplate_sm.set_state(self._storagediceplate_sm.refill_diceplate_state)
		
    def material_refill_done(self):
        self._storagediceplate.logger.debug("%s event in %s state", self.material_refill_done.__name__, self.name)		
		
    def material_reset(self, parameters_list):
        self._storagediceplate.logger.debug("%s event in %s state", self.material_reset.__name__, self.name)
	    
		# First set the current used parameters list to the service object
        self._storagediceplate_sm.set_parameters(parameters_list)

        if self._storagediceplate_sm.service_timeout_timer is not None:
            self._storagediceplate_sm.service_timeout_timer.start()		
		
		# Switch into waiting diceplate state if a diceplate material supply has been requested
        self._storagediceplate.logger.debug("%s event in %s state with parameters %s", self.material_reset.__name__, self.name, parameters_list)
        self._storagediceplate_sm.set_state(self._storagediceplate_sm.reset_diceplate_state)

    def material_reset_done(self):
        self._storagediceplate.logger.debug("%s event in %s state", self.material_reset_done.__name__, self.name)

    def error(self):
        self._storagediceplate.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._storagediceplate_sm.set_state(self._storagediceplate_sm.error_state)

    def acknowledge(self):
        self._storagediceplate.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._storagediceplate.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

		
class ResetDicePlate(StorageDicePlateState):
    """ Concrete State class for representing ResetDicePlate State. """

    def __init__(self, storagediceplate_sm, storagediceplate, super_sm=None, isSubstate=False):
        super(ResetDicePlate, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._storagediceplate_sm = storagediceplate_sm
        self._storagediceplate = storagediceplate
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._storagediceplate.logger.debug("Entering the %s state", self.name)
		
		# Get the actual parameters setting
        self._parameters_list = self._storagediceplate_sm.parameters_list()
		
	    # Use parameter 1 (diceplate symbol) at list position 0 and reduce the value by one, to address the corresponding storagerack.
        self._storagerackposition = int(self._parameters_list[0]) - 1
        self._storagediceplate.logger.debug("Reset diceplate values from storagerack %s", self._storagerackposition + 1)
        
		# Send the event to the responsible storage rack with the parameter list
        resetmaterial_event = events.StorageStationInputEvent(eventID=events.StorageStationInputEvents.ResetMaterial, sender=self.name, parameters_list=self._parameters_list)
        self._storagediceplate_sm._storageracklist[self._storagerackposition].handle_event(event=resetmaterial_event)

    def material_refill(self):
        self._storagediceplate.logger.debug("%s event in %s state", self.material_refill.__name__, self.name)		
		
    def material_refill_done(self):
        self._storagediceplate.logger.debug("%s event in %s state", self.material_refill_done.__name__, self.name)
		
    def material_reset(self, parameters_list):
        self._storagediceplate.logger.debug("%s event in %s state", self.material_reset.__name__, self.name)

    def material_reset_done(self):
        self._storagediceplate.logger.debug("%s event in %s state", self.material_reset_done.__name__, self.name)		

        if self._storagediceplate_sm.service_timeout_timer is not None:
            self._storagediceplate_sm.service_timeout_timer.cancel()	
		
        self._storagediceplate.service_users[self._storagediceplate_sm._current_service_user].done()
        self._storagediceplate_sm.set_state(self._storagediceplate_sm.waitforjob_state)
		
    def error(self):
        self._storagediceplate.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._storagediceplate_sm.set_state(self._storagediceplate_sm.error_state)

    def acknowledge(self):
        self._storagediceplate.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._storagediceplate.logger.debug("%s event in %s state", self.timeout.__name__, self.name)
		
        self._storagediceplate_sm.publish_error(error_codes.StationErrorCodes.StorageDiceplateServiceTimeout)
        self._storagediceplate_sm.set_state(self._storagediceplate_sm.error_state)

class RefillDicePlate(StorageDicePlateState):
    """ Concrete State class for representing RefillDicePlate State. """

    def __init__(self, storagediceplate_sm, storagediceplate, super_sm=None, isSubstate=False):
        super(RefillDicePlate, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._storagediceplate_sm = storagediceplate_sm
        self._storagediceplate = storagediceplate
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._storagediceplate.logger.debug("Entering the %s state", self.name)
		
		# Get the actual parameters setting
        self._parameters_list = self._storagediceplate_sm.parameters_list()
		
	    # Use parameter 1 (diceplate symbol) at list position 0 and reduce the value by one, to address the corresponding storagerack.
        self._storagerackposition = int(self._parameters_list[0]) - 1
        self._storagediceplate.logger.debug("Reset diceplate values from storagerack %s", self._storagerackposition + 1)		
        
		# Send the event to the responsible storage rack with the parameter list
        refillmaterial_event = events.StorageStationInputEvent(eventID=events.StorageStationInputEvents.RefillMaterial, sender=self.name, parameters_list=self._parameters_list)
        self._storagediceplate_sm._storageracklist[self._storagerackposition].handle_event(event=refillmaterial_event)

    def material_refill(self):
        self._storagediceplate.logger.debug("%s event in %s state", self.material_refill.__name__, self.name)		
		
    def material_refill_done(self):
        self._storagediceplate.logger.debug("%s event in %s state", self.material_refill_done.__name__, self.name)

        if self._storagediceplate_sm.service_timeout_timer is not None:
            self._storagediceplate_sm.service_timeout_timer.cancel()			
		
        self._storagediceplate.service_users[self._storagediceplate_sm._current_service_user].done()
        self._storagediceplate_sm.set_state(self._storagediceplate_sm.waitforjob_state)
		
    def material_reset(self, parameters_list):
        self._storagediceplate.logger.debug("%s event in %s state", self.material_reset.__name__, self.name)

    def material_reset_done(self):
        self._storagediceplate.logger.debug("%s event in %s state", self.material_reset_done.__name__, self.name)		
		
    def error(self):
        self._storagediceplate.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._storagediceplate_sm.set_state(self._storagediceplate_sm.error_state)

    def acknowledge(self):
        self._storagediceplate.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._storagediceplate.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

        self._storagediceplate_sm.publish_error(error_codes.StationErrorCodes.StorageDiceplateServiceTimeout)
        self._storagediceplate_sm.set_state(self._storagediceplate_sm.error_state)		
		
class Error(StorageDicePlateState):
    """ Concrete State class for representing Error State. """

    def __init__(self, storagediceplate_sm, storagediceplate, super_sm=None, isSubstate=False):
        super(Error, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._storagediceplate_sm = storagediceplate_sm
        self._storagediceplate = storagediceplate
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._storagediceplate.logger.debug("Entering the %s state", self.name)
        self._storagediceplate.publisher.publish(topic="eventID", value="Error", sender=self._storagediceplate.name)

        if self._storagediceplate_sm.service_timeout_timer is not None:
            self._storagediceplate_sm.service_timeout_timer.cancel()		

        try:
            if self._storagediceplate_sm.init_required:
                self._storagediceplate_sm.init_required = False
                self._storagediceplate.service_users[self._storagediceplate_sm._current_service_user].error(init_required=True)
            else:
                self._storagediceplate.service_users[self._storagediceplate_sm._current_service_user].error(init_required=False)
        except KeyError:
            self._storagediceplate.logger.debug("%s service was not called yet",  self.name)
	
    def material_refill(self):
        self._storagediceplate.logger.debug("%s event in %s state", self.material_refill.__name__, self.name)		
		
    def material_refill_done(self):
        self._storagediceplate.logger.debug("%s event in %s state", self.material_refill_done.__name__, self.name)
		
    def material_reset(self, parameters_list):
        self._storagediceplate.logger.debug("%s event in %s state", self.material_reset.__name__, self.name)

    def material_reset_done(self):
        self._storagediceplate.logger.debug("%s event in %s state", self.material_reset_done.__name__, self.name)		
		
    def error(self):
        self._storagediceplate.logger.debug("%s event in %s state", self.error.__name__, self.name)

    def acknowledge(self):
        self._storagediceplate.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)
        self._storagediceplate_sm.set_state(self._storagediceplate_sm.waitforjob_state)

    def timeout(self):
        self._storagediceplate.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

		
class StorageDicePlateStateMachine(object):
    """ Context class for the ResetDicePlateService state machine """

    def __init__(self, storagediceplateservice, enable_timeout, timeout_interval, storageracklist):
        self._name = self.__class__.__name__
		
        self._storagediceplateservice = storagediceplateservice
        self._enable_timeout = enable_timeout
        self._timeout_interval = timeout_interval
		
        self._storageracklist = storageracklist
		
        self._waitforjob_state = WaitForJob(self, self._storagediceplateservice)
        self._refill_diceplate_state = RefillDicePlate(self, self._storagediceplateservice)		
        self._reset_diceplate_state = ResetDicePlate(self, self._storagediceplateservice)
        self._error_state = Error(self, self._storagediceplateservice)		
		
        self._parameters_list = ("")

        # timeout monitoring timer
        if self._enable_timeout:
            self.service_timeout_timer = MonitoringTimer(name="StorageDicePlateServiceTimeoutTimer",
                                                         interval=self._timeout_interval,
                                                         callback_fnc=self.timeout_handler,
                                                         logger=self._storagediceplateservice.logger)
        else:
            self.service_timeout_timer = None			

        self.init_required = False  # to show that an init is needed after the error
			
        self._current_service_user = 0
        self._current_state = self._waitforjob_state

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
    def refill_diceplate_state(self):
        return self._refill_diceplate_state		
		
    @property
    def reset_diceplate_state(self):
        return self._reset_diceplate_state
		
    @property
    def error_state(self):
        return self._error_state
		
    def set_parameters(self, parameters_list):
        self._storagediceplateservice.logger.debug("Setting parameters %s to service %s", parameters_list, self._name)
        self._parameters_list = parameters_list

    def parameters_list(self):
        return self._parameters_list
		
    def set_state(self, state):
        self._storagediceplateservice.logger.debug("Switching from state %s to state %s", self.current_state.name, state.name)

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
        self._storagediceplateservice.publisher.publish(topic="StationErrorCode",
                                                        value=hex(error_code),
                                                        sender=self._storagediceplateservice.name)
        self._storagediceplateservice.publisher.publish(topic="StationErrorDescription",
                                                        value=error_codes.code_to_text[error_code],
                                                        sender=self._storagediceplateservice.name)

    def publish_message(self, message_code):
        self._storagediceplateservice.publisher.publish(topic="StationMessageCode",
                                                        value=hex(message_code),
                                                        sender=self._storagediceplateservice.name)
        self._storagediceplateservice.publisher.publish(topic="StationMessageDescription",
                                                        value=message_codes.code_to_text[message_code],
                                                        sender=self._storagediceplateservice.name)

    def timeout_handler(self):
        self.init_required = True
        timeout_event = events.GenericServiceEvent(eventID=events.GenericServiceEvents.Timeout,
                                                   sender=self._storagediceplateservice.name)
        self.dispatch(event=timeout_event)			
			
    def dispatch(self, *args, **kwargs):

        self._storagediceplateservice.logger.debug("%s has received a message: %s", self.name, kwargs)

        try:
		
            # topics coming from the publishers
            topic = kwargs["topic"]
            value = kwargs["value"]
            sender = kwargs["sender"]

            if sender == "Station":

                if topic == "Ack":
                    if value:
                        self._current_state.acknowledge()
                    else:
                        pass
						
			# tbd: sender = StorageRack 1 - 6- check if necessary or replaceable with generic interface	
            else:
			
                if topic == "State": # Check if changeable with event
				
                    if value == "MaterialRefillDone":
                        self._storagerackposition = int(self._parameters_list[0]) - 1
                        if sender == (self._storageracklist[self._storagerackposition].name):
                            self._current_state.material_refill_done()
                    elif value == "MaterialResetDone":
                        self._storagerackposition = int(self._parameters_list[0]) - 1
                        if sender == (self._storageracklist[self._storagerackposition].name):
                            self._current_state.material_reset_done()
                    elif value == "Error":
                        self._current_state.error()
                    else:
                        pass

        except KeyError:
            event = kwargs["event"]

            eventID = event.eventID
            sender = event.sender
            service_index = event.service_index

            if eventID == events.GenericServiceEvents.Execute:  # this a part of the service generic interface
                if event.service_process == "refill":
                    self._current_state.material_refill(parameters_list=event.parameters_list)
                elif event.service_process == "reset":
                    self._current_state.material_reset(parameters_list=event.parameters_list)
                self._current_service_user = service_index
            elif eventID == events.GenericServiceEvents.Cancel:
                pass
            elif eventID == events.GenericServiceEvents.Done:  # for callable services
                pass

            elif eventID == events.GenericServiceEvents.Timeout:  # timeout event comes from the service itself ???
                self._current_state.timeout()

