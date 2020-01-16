import abc
from communication import events
from utils import error_codes, message_codes
import config


class ToPosState(metaclass=abc.ABCMeta):
    """ Abstract State class for a ToPosition Service SM """

    def __init__(self, isSubstate=False):
        self._isSubstate = isSubstate

    @property
    def isSubstate(self):
        return self._isSubstate

    @abc.abstractmethod
    def to_position(self):
        raise NotImplemented

    @abc.abstractmethod
    def in_position(self):
        raise NotImplemented

    @abc.abstractmethod
    def out_of_position(self):
        raise NotImplemented

    @abc.abstractmethod
    def blinking_done(self):
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


class WaitForJob(ToPosState):
    """ Concrete State class for representing WaitForJob State. """

    def __init__(self, toposition_service_sm, toposition_service, super_sm=None, isSubstate=False):
        super(WaitForJob, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._toposition_service_sm = toposition_service_sm
        self._toposition_service = toposition_service
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._toposition_service.logger.debug("Entering the %s state", self.name)
        self._toposition_service.publisher.publish(topic="eventID", value="Ready", sender=self._toposition_service.name)
        self._toposition_service.publisher.publish(topic=self._toposition_service.name+"ServiceState", value="WaifForJob",
                                            sender=self._toposition_service.name)

        #  LED Off
        self._toposition_service.led.handle_event(event=self._toposition_service_sm.ledoff_event)

    def to_position(self):
        self._toposition_service.logger.debug("%s event in %s state", self.to_position.__name__, self.name)
        self._toposition_service_sm.set_state(self._toposition_service_sm.busy_state)

    def in_position(self):
        self._toposition_service.logger.debug("%s event in %s state", self.to_position.__name__, self.name)

    def out_of_position(self):
        self._toposition_service.logger.debug("%s event in %s state", self.out_of_position.__name__, self.name)

    def blinking_done(self):
        self._toposition_service.logger.debug("%s event in %s state", self.blinking_done.__name__, self.name)

    def error(self):
        self._toposition_service.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._toposition_service_sm.set_state(self._toposition_service_sm.error_state)

    def acknowledge(self):
        self._toposition_service.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def resetjob(self):
        self._toposition_service.logger.debug("%s event in %s state", self.resetjob.__name__, self.name)

    def timeout(self):
        self._toposition_service.logger.debug("%s event in %s state", self.timeout.__name__, self.name)


class Busy(ToPosState):
    """ Concrete State class for representing WaitPos State. """

    def __init__(self, toposition_service_sm, toposition_service, super_sm=None, isSubstate=False):
        super(Busy, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._toposition_service_sm = toposition_service_sm
        self._toposition_service = toposition_service
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._toposition_service.logger.debug("Entering the %s state", self.name)
        self._toposition_service.publisher.publish(topic="eventID", value="Busy", sender=self._toposition_service.name)
        self._toposition_service.publisher.publish(topic=self._toposition_service.name+"ServiceState", value="Busy",
                                                   sender=self._toposition_service.name)

        self._toposition_service_sm.set_state(self._toposition_service_sm.waitpos_busySubState)

    def to_position(self):
        self._toposition_service.logger.debug("%s event in %s state", self.to_position.__name__, self.name)

    def in_position(self):
        self._toposition_service.logger.debug("%s event in %s state", self.to_position.__name__, self.name)

    def out_of_position(self):
        self._toposition_service.logger.debug("%s event in %s state", self.out_of_position.__name__, self.name)

    def blinking_done(self):
        self._toposition_service.logger.debug("%s event in %s state", self.blinking_done.__name__, self.name)

    def error(self):
        self._toposition_service.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._toposition_service_sm.set_state(self._toposition_service_sm.error_state)

    def acknowledge(self):
        self._toposition_service.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def resetjob(self):
        self._toposition_service.logger.debug("%s event in %s state", self.resetjob.__name__, self.name)

        self._toposition_service_sm.set_state(self._toposition_service_sm.waitforjob_state)

    def timeout(self):
        self._toposition_service.logger.debug("%s event in %s state", self.timeout.__name__, self.name)


class WaitPos_BusySubState(ToPosState):
    """ Concrete State class for representing WaitPos State. """

    def __init__(self, toposition_service_sm, toposition_service, super_sm=None, isSubstate=False):
        super(WaitPos_BusySubState, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._toposition_service_sm = toposition_service_sm
        self._toposition_service = toposition_service
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._toposition_service.logger.debug("Entering the %s state", self.name)
        self._toposition_service.publisher.publish(topic=self._toposition_service.name+"ServiceState", value="Busy: WaitPosition",
                                                   sender=self._toposition_service.name)
        # sensor Update event
        self._toposition_service.sensorPos.handle_event(event=self._toposition_service_sm.sensor_update_event)
        #  LED Yellow
        self._toposition_service.led.handle_event(event=self._toposition_service_sm.yellow_event)

    def to_position(self):
        self._toposition_service.logger.debug("%s event in %s state", self.to_position.__name__, self.name)

    def in_position(self):
        self._toposition_service.logger.debug("%s event in %s state", self.to_position.__name__, self.name)
        self._toposition_service_sm.set_state(self._toposition_service_sm.blinking_busySubState)

    def out_of_position(self):
        self._toposition_service.logger.debug("%s event in %s state", self.out_of_position.__name__, self.name)

    def blinking_done(self):
        self._toposition_service.logger.debug("%s event in %s state", self.blinking_done.__name__, self.name)

    def error(self):
        self._toposition_service.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._super_sm.error()

    def acknowledge(self):
        self._toposition_service.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def resetjob(self):
        self._toposition_service.logger.debug("%s event in %s state", self.resetjob.__name__, self.name)
        self._super_sm.resetjob()

    def timeout(self):
        self._toposition_service.logger.debug("%s event in %s state", self.timeout.__name__, self.name)


class Blinking_BusySubState(ToPosState):
    """ Concrete State class for representing BlinkingPos1 State. """

    def __init__(self, toposition_service_sm, toposition_service, super_sm=None, isSubstate=False):
        super(Blinking_BusySubState, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._toposition_service_sm = toposition_service_sm
        self._toposition_service = toposition_service
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._toposition_service.logger.debug("Entering the %s state", self.name)
        self._toposition_service.publisher.publish(topic=self._toposition_service.name+"ServiceState", value="Busy: Blinking",
                                                   sender=self._toposition_service.name)

        #  LED Green
        self._toposition_service.led.handle_event(event=self._toposition_service_sm.green_event)
        # blinking
        self._toposition_service_sm.blink_start_event.parameters_list = self._toposition_service_sm.get_blinking_parameters()
        self._toposition_service.blinker.handle_event(event=self._toposition_service_sm.blink_start_event)

    def to_position(self):
        self._toposition_service.logger.debug("%s event in %s state", self.to_position.__name__, self.name)

    def in_position(self):
        self._toposition_service.logger.debug("%s event in %s state", self.to_position.__name__, self.name)

    def out_of_position(self):
        self._toposition_service.logger.debug("%s event in %s state", self.out_of_position.__name__, self.name)

        # stop blinking
        self._toposition_service.blinker.handle_event(event=self._toposition_service_sm.blink_stop_event)

        self._toposition_service_sm.set_state(self._toposition_service_sm.waitpos_busySubState)

    def blinking_done(self):
        self._toposition_service.logger.debug("%s event in %s state", self.blinking_done.__name__, self.name)

        self._toposition_service.service_users[self._toposition_service_sm._current_service_user].done()

        self._toposition_service_sm.set_state(self._toposition_service_sm.waitforjob_state)

    def error(self):
        self._toposition_service.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._super_sm.error()

    def acknowledge(self):
        self._toposition_service.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def resetjob(self):
        self._toposition_service.logger.debug("%s event in %s state", self.resetjob.__name__, self.name)
        self._super_sm.resetjob()

    def timeout(self):
        self._toposition_service.logger.debug("%s event in %s state", self.timeout.__name__, self.name)


class Error(ToPosState):
    """ Concrete State class for representing Error State. """

    def __init__(self, toposition_service_sm, toposition_service, super_sm=None, isSubstate=False):
        super(Error, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._toposition_service_sm = toposition_service_sm
        self._toposition_service = toposition_service
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._toposition_service.logger.debug("Entering the %s state", self.name)
        self._toposition_service.publisher.publish(topic="eventID", value="Error", sender=self._toposition_service.name)
        self._toposition_service.publisher.publish(topic=self._toposition_service.name+"ServiceState", value="Error",
                                                   sender=self._toposition_service.name)

        try:
            self._toposition_service.service_users[self._toposition_service_sm._current_service_user].error()
        except KeyError:
            self._toposition_service.logger.debug("%s service was not called yet",  self.name)


    def to_position(self):
        self._toposition_service.logger.debug("%s event in %s state", self.to_position.__name__, self.name)

    def in_position(self):
        self._toposition_service.logger.debug("%s event in %s state", self.to_position.__name__, self.name)

    def out_of_position(self):
        self._toposition_service.logger.debug("%s event in %s state", self.out_of_position.__name__, self.name)

    def blinking_done(self):
        self._toposition_service.logger.debug("%s event in %s state", self.blinking_done.__name__, self.name)

    def error(self):
        self._toposition_service.logger.debug("%s event in %s state", self.error.__name__, self.name)

    def acknowledge(self):
        self._toposition_service.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)
        self._toposition_service_sm.set_state(self._toposition_service_sm.waitforjob_state)

    def resetjob(self):
        self._toposition_service.logger.debug("%s event in %s state", self.resetjob.__name__, self.name)
        # self._toposition_service_sm.set_state(self._toposition_service_sm.waitforjob_state)

    def timeout(self):
        self._toposition_service.logger.debug("%s event in %s state", self.timeout.__name__, self.name)


class ToPosStateMachine(object):
    """ Context class for the ToPosition state machine """

    def __init__(self, toposition_service):
        self._name = self.__class__.__name__

        self._toposition_service = toposition_service

        # events:
        self.green_event = events.RGBLEDInputEvent(eventID=events.RGBLEDInputEvents.Green, sender=self._toposition_service.name)
        self.yellow_event = events.RGBLEDInputEvent(eventID=events.RGBLEDInputEvents.Yellow, sender=self._toposition_service.name)
        self.ledoff_event = events.RGBLEDInputEvent(eventID=events.RGBLEDInputEvents.Off, sender=self._toposition_service.name)
        self.blink_start_event = events.BlinkerEvent(eventID=events.BlinkerEvents.Start, sender=self._toposition_service.name)
        self.blink_stop_event = events.BlinkerEvent(eventID=events.BlinkerEvents.Stop, sender=self._toposition_service.name)
        self.sensor_update_event = events.ComplexSensorEvent(eventID=events.ComplexSensorEvents.Update,sender=self._toposition_service.name)

        # states
        self._waitforjob_state = WaitForJob(self, self._toposition_service)
        self._busy_state = Busy(self, self._toposition_service)

        self._waitpos_busySubState = WaitPos_BusySubState(self, self._toposition_service,
                                                          super_sm=self.busy_state,
                                                          isSubstate=True)
        self._blinking_busySubState = Blinking_BusySubState(self, self._toposition_service,
                                                            super_sm=self.busy_state,
                                                            isSubstate=True)

        self._error_state = Error(self, self._toposition_service)


        self._current_state = self._waitforjob_state

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
    def busy_state(self):
        return self._busy_state

    @property
    def waitpos_busySubState(self):
        return self._waitpos_busySubState

    @property
    def blinking_busySubState(self):
        return self._blinking_busySubState

    @property
    def error_state(self):
        return self._error_state

    def get_blinking_parameters(self):
        para_str = str(config.STATION_CONFIG['onTime'])+', '+str(config.STATION_CONFIG['offTime'])+', '+str(config.STATION_CONFIG['inPosBlinksNum'])
        para_list = list()
        para_list.append(para_str)
        return para_list

    def set_state(self, state):
        self._toposition_service.logger.debug("Switching from state %s to state %s", self.current_state.name,
                                              state.name)

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

        self._toposition_service.logger.debug("%s has received a message: %s", self.name, kwargs)

        try:  # topics coming from the publishers
            topic = kwargs["topic"]
            value = kwargs["value"]
            sender = kwargs["sender"]

            if sender.lower().find("rfid") != -1:
                sender = "rfid"
            elif sender.lower().find("blinker") != -1:
                sender = "blinker"

            if sender == "rfid":
                if topic == "Value":
                    if value:
                        self._current_state.in_position()
                    else:
                        self._current_state.out_of_position()

                elif topic == "State":

                    if value == "Error":
                        self._current_state.error()
                    elif value == "StatusNOK":
                        self._current_state.error()
                    elif value == "NotInitialized":
                        pass
                    elif value == "Initialized":
                        pass
            elif sender == "blinker":
                if topic == "Value":
                    if value:
                        pass
                    else:
                        self._current_state.blinking_done()

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
            elif topic == "StationState" and value == "Error":
                self._current_state.error()

        except KeyError:
            event = kwargs["event"]

            eventID = event.eventID
            sender = event.sender
            service_index = event.service_index

            if eventID == events.GenericServiceEvents.Execute:  # this a part of the service generic interface
                self._current_state.to_position()
                self._current_service_user = service_index
            elif eventID == events.GenericServiceEvents.Cancel:
                self._current_state.resetjob()
            elif eventID == events.GenericServiceEvents.Done:  # for callable services
                pass

            elif eventID == events.GenericServiceEvents.Timeout:  # timeout event comes from the service itself ???
                self._current_state.timeout()