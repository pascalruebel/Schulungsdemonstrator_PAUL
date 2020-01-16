import abc
from communication import events
from threading import Timer
from utils import error_codes, message_codes
from utils.monitoring_timer import MonitoringTimer

class HomingState(metaclass=abc.ABCMeta):
    """ Abstract State class for a Homing Service SM """

    def __init__(self, isSubstate=False):
        self._isSubstate = isSubstate

    @property
    def isSubstate(self):
        return self._isSubstate

    @abc.abstractmethod
    def reference(self):
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
    def rack_is_empty(self):
        raise NotImplemented

    @abc.abstractmethod
    def rack_is_filling(self):
        raise NotImplemented

    @abc.abstractmethod
    def rack_is_full(self):
        raise NotImplemented

    @abc.abstractmethod
    def carriage_is_atfront(self):
        raise NotImplemented

    @abc.abstractmethod
    def carriage_is_atrack(self):
        raise NotImplemented

    @abc.abstractmethod
    def carriage_is_outofpos(self):
        raise NotImplemented

    @abc.abstractmethod
    def dispatch_occupied(self):
        raise NotImplemented

    @abc.abstractmethod
    def dispatch_empty(self):
        raise NotImplemented

    def enter_action(self):
        pass

    def exit_action(self):
        pass


class NotReferenced(HomingState):
    """ Concrete State class for representing NotReferenced State"""

    def __init__(self, homingservice_sm, homingservice, super_sm=None, isSubstate=False):
        super(NotReferenced, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._homingservice_sm = homingservice_sm
        self._homingservice = homingservice
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._homingservice.logger.debug("Entering the %s state", self.name)
        self._homingservice.serviceState = "Ready"
        self._homingservice.publisher.publish(topic="HomeServiceState", value="NotReferenced", sender=self._homingservice.name)

    def reference(self):
        self._homingservice.logger.debug("%s event in %s state", self.reference.__name__, self.name)

        if self._homingservice_sm.service_timeout_timer is not None:
            self._homingservice_sm.service_timeout_timer.start()

        self._homingservice_sm.set_state(self._homingservice_sm.carriagehoming_state)

    def rack_is_empty(self):
        self._homingservice.logger.debug("%s event in %s state", self.rack_is_empty.__name__, self.name)

    def rack_is_filling(self):
        self._homingservice.logger.debug("%s event in %s state", self.rack_is_filling.__name__, self.name)

    def rack_is_full(self):
        self._homingservice.logger.debug("%s event in %s state", self.rack_is_full.__name__, self.name)

    def carriage_is_atfront(self):
        self._homingservice.logger.debug("%s event in %s state", self.carriage_is_atfront.__name__, self.name)

    def carriage_is_atrack(self):
        self._homingservice.logger.debug("%s event in %s state", self.carriage_is_atrack.__name__, self.name)

    def carriage_is_outofpos(self):
        self._homingservice.logger.debug("%s event in %s state", self.carriage_is_outofpos.__name__, self.name)

    def dispatch_occupied(self):
        self._homingservice.logger.debug("%s event in %s state", self.dispatch_occupied.__name__, self.name)

    def dispatch_empty(self):
        self._homingservice.logger.debug("%s event in %s state", self.dispatch_empty.__name__, self.name)

    def error(self):
        self._homingservice.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._homingservice_sm.set_state(self._homingservice_sm.error_state)

    def acknowledge(self):
        self._homingservice.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._homingservice.logger.debug("%s event in %s state", self.timeout.__name__, self.name)


class CarriageHoming(HomingState):
    """ Concrete State class for representing CarriageHoming State"""

    def __init__(self, homingservice_sm, homingservice, super_sm=None, isSubstate=False):
        super(CarriageHoming, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._homingservice_sm = homingservice_sm
        self._homingservice = homingservice
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._homingservice.logger.debug("Entering the %s state", self.name)
        self._homingservice.serviceState = "Busy"
        self._homingservice.publisher.publish(topic="HomeServiceState", value="CarriageHoming",
                                              sender=self._homingservice.name)
        # timeout_time = 5.0
        # Timer(timeout_time, self._homingservice_sm.timeout_handler).start()

        self._homingservice.carriage.handle_event(event=self._homingservice_sm.carriage_update_event)
        # ToDo: Timeout for Homing !!!

    def reference(self):
        self._homingservice.logger.debug("%s event in %s state", self.reference.__name__, self.name)

        if self._homingservice_sm.service_timeout_timer is not None:
            self._homingservice_sm.service_timeout_timer.start()

        self._homingservice.carriage.handle_event(event=self._homingservice_sm.carriage_update_event)

        self._homingservice_sm.set_state(self._homingservice_sm.carriagehoming_state)

    def rack_is_empty(self):
        self._homingservice.logger.debug("%s event in %s state", self.rack_is_empty.__name__, self.name)

    def rack_is_filling(self):
        self._homingservice.logger.debug("%s event in %s state", self.rack_is_filling.__name__, self.name)

    def rack_is_full(self):
        self._homingservice.logger.debug("%s event in %s state", self.rack_is_full.__name__, self.name)

    def carriage_is_atfront(self):
        self._homingservice.logger.debug("%s event in %s state", self.carriage_is_atfront.__name__, self.name)
        self._homingservice_sm.set_state(self._homingservice_sm.rackDispatchHoming_state)

    def carriage_is_atrack(self):
        self._homingservice.logger.debug("%s event in %s state", self.carriage_is_atrack.__name__, self.name)
        self._homingservice_sm.set_state(self._homingservice_sm.movingToFront_state)

    def carriage_is_outofpos(self):
        self._homingservice.logger.debug("%s event in %s state", self.carriage_is_outofpos.__name__, self.name)
        self._homingservice_sm.set_state(self._homingservice_sm.movingToFront_state)

    def dispatch_occupied(self):
        self._homingservice.logger.debug("%s event in %s state", self.dispatch_occupied.__name__, self.name)

    def dispatch_empty(self):
        self._homingservice.logger.debug("%s event in %s state", self.dispatch_empty.__name__, self.name)

    def error(self):
        self._homingservice.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._homingservice_sm.set_state(self._homingservice_sm.error_state)

    def acknowledge(self):
        self._homingservice.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._homingservice.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

        self._homingservice_sm.publish_error(error_codes.StationErrorCodes.HomingServiceTimeout)
        self._homingservice_sm.set_state(self._homingservice_sm.error_state)


class CarriageMovingToFront(HomingState):
    """ Concrete State class for representing CarriageMovingToFront State"""

    def __init__(self, homingservice_sm, homingservice, super_sm=None, isSubstate=False):
        super(CarriageMovingToFront, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._homingservice_sm = homingservice_sm
        self._homingservice = homingservice
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._homingservice.logger.debug("Entering the %s state", self.name)
        self._homingservice.serviceState = "Busy"
        self._homingservice.publisher.publish(topic="HomeServiceState", value="CarriageMovingToFront",
                                              sender=self._homingservice.name)

        self._homingservice.carriage.handle_event(event=self._homingservice_sm.carriage_tofront_event)

        # ToDO : Think about timeout timer !

    def reference(self):
        self._homingservice.logger.debug("%s event in %s state", self.reference.__name__, self.name)

        self._homingservice.carriage.handle_event(event=self._homingservice_sm.carriage_stop_event)

        self._homingservice_sm.set_state(self._homingservice_sm.carriagehoming_state)

    def rack_is_empty(self):
        self._homingservice.logger.debug("%s event in %s state", self.rack_is_empty.__name__, self.name)

    def rack_is_filling(self):
        self._homingservice.logger.debug("%s event in %s state", self.rack_is_filling.__name__, self.name)

    def rack_is_full(self):
        self._homingservice.logger.debug("%s event in %s state", self.rack_is_full.__name__, self.name)

    def carriage_is_atfront(self):
        self._homingservice.logger.debug("%s event in %s state", self.carriage_is_atfront.__name__, self.name)
        self._homingservice_sm.set_state(self._homingservice_sm.rackDispatchHoming_state)

    def carriage_is_atrack(self):
        self._homingservice.logger.debug("%s event in %s state", self.carriage_is_atrack.__name__, self.name)

    def carriage_is_outofpos(self):
        self._homingservice.logger.debug("%s event in %s state", self.carriage_is_outofpos.__name__, self.name)

    def dispatch_occupied(self):
        self._homingservice.logger.debug("%s event in %s state", self.dispatch_occupied.__name__, self.name)

    def dispatch_empty(self):
        self._homingservice.logger.debug("%s event in %s state", self.dispatch_empty.__name__, self.name)

    def error(self):
        self._homingservice.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._homingservice_sm.set_state(self._homingservice_sm.error_state)

        self._homingservice.carriage.handle_event(event=self._homingservice_sm.carriage_stop_event)

    def acknowledge(self):
        self._homingservice.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._homingservice.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

        self._homingservice_sm.publish_error(error_codes.StationErrorCodes.HomingServiceTimeout)
        self._homingservice_sm.set_state(self._homingservice_sm.error_state)


class RackDispatchHoming(HomingState):
    """ Concrete State class for representing RackDispatchHoming State. """

    def __init__(self, homingservice_sm, homingservice, super_sm=None, isSubstate=False):
        super(RackDispatchHoming, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._homingservice_sm = homingservice_sm
        self._homingservice = homingservice
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._homingservice.logger.debug("Entering the %s state", self.name)
        self._homingservice.serviceState = "Busy"
        self._homingservice.publisher.publish(topic="HomeServiceState", value="RackDispatchHoming",
                                              sender=self._homingservice.name)

        self._homingservice.rack.handle_event(event=self._homingservice_sm.rack_update_event)
        self._homingservice.sensorCarriageOccupied.handle_event(event=self._homingservice_sm.sensor_update_event)

        # ToDO : Think about timeout timer !

    def reference(self):
        self._homingservice.logger.debug("%s event in %s state", self.reference.__name__, self.name)
        self._homingservice_sm.set_state(self._homingservice_sm.carriagehoming_state)

    def rack_is_empty(self):
        self._homingservice.logger.debug("%s event in %s state", self.rack_is_empty.__name__, self.name)
        self._homingservice_sm.set_state(self._homingservice_sm.rackempty_subState)

    def rack_is_filling(self):
        self._homingservice.logger.debug("%s event in %s state", self.rack_is_filling.__name__, self.name)

    def rack_is_full(self):
        self._homingservice.logger.debug("%s event in %s state", self.rack_is_full.__name__, self.name)

    def carriage_is_atfront(self):
        self._homingservice.logger.debug("%s event in %s state", self.carriage_is_atfront.__name__, self.name)

    def carriage_is_atrack(self):
        self._homingservice.logger.debug("%s event in %s state", self.carriage_is_atrack.__name__, self.name)
        self._homingservice_sm.set_state(self._homingservice_sm.error_state)

    def carriage_is_outofpos(self):
        self._homingservice.logger.debug("%s event in %s state", self.carriage_is_outofpos.__name__, self.name)
        self._homingservice_sm.set_state(self._homingservice_sm.error_state)  # ToDo : ???

    def dispatch_occupied(self):
        self._homingservice.logger.debug("%s event in %s state", self.dispatch_occupied.__name__, self.name)

    def dispatch_empty(self):
        self._homingservice.logger.debug("%s event in %s state", self.dispatch_empty.__name__, self.name)
        self._homingservice_sm.set_state(self._homingservice_sm.dispatchEmpty_subState)

    def error(self):
        self._homingservice.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._homingservice_sm.set_state(self._homingservice_sm.error_state)

    def acknowledge(self):
        self._homingservice.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._homingservice.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

        self._homingservice_sm.publish_error(error_codes.StationErrorCodes.HomingServiceTimeout)
        self._homingservice_sm.set_state(self._homingservice_sm.error_state)


class RackEmpty(HomingState):
    """ Concrete State class for representing RackEmpty State. """

    def __init__(self, homingservice_sm, homingservice, super_sm=None, isSubstate=False):
        super(RackEmpty, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._homingservice_sm = homingservice_sm
        self._homingservice = homingservice
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._homingservice.logger.debug("Entering the %s state", self.name)
        self._homingservice.serviceState = "Busy"
        self._homingservice.publisher.publish(topic="HomeServiceState", value="Homing: RackEmpty",
                                              sender=self._homingservice.name)

        self._homingservice.rack.handle_event(event=self._homingservice_sm.rack_update_event)
        self._homingservice.sensorCarriageOccupied.handle_event(event=self._homingservice_sm.sensor_update_event)

        # ToDO : Think about timeout timer !

    def reference(self):
        self._homingservice.logger.debug("%s event in %s state", self.reference.__name__, self.name)
        self._homingservice_sm.set_state(self._homingservice_sm.carriagehoming_state)

    def rack_is_empty(self):
        self._homingservice.logger.debug("%s event in %s state", self.rack_is_empty.__name__, self.name)

    def rack_is_filling(self):
        self._homingservice.logger.debug("%s event in %s state", self.rack_is_filling.__name__, self.name)
        self._homingservice_sm.set_state(self._homingservice_sm.rackDispatchHoming_state)

    def rack_is_full(self):
        self._homingservice.logger.debug("%s event in %s state", self.rack_is_full.__name__, self.name)
        self._homingservice_sm.set_state(self._homingservice_sm.rackDispatchHoming_state)

    def carriage_is_atfront(self):
        self._homingservice.logger.debug("%s event in %s state", self.carriage_is_atfront.__name__, self.name)

    def carriage_is_atrack(self):
        self._homingservice.logger.debug("%s event in %s state", self.carriage_is_atrack.__name__, self.name)
        self._homingservice_sm.set_state(self._homingservice_sm.error_state)

    def carriage_is_outofpos(self):
        self._homingservice.logger.debug("%s event in %s state", self.carriage_is_outofpos.__name__, self.name)
        self._homingservice_sm.set_state(self._homingservice_sm.error_state)

    def dispatch_occupied(self):
        self._homingservice.logger.debug("%s event in %s state", self.dispatch_occupied.__name__, self.name)

    def dispatch_empty(self):
        self._homingservice.logger.debug("%s event in %s state", self.dispatch_empty.__name__, self.name)
        self._homingservice_sm.set_state(self._homingservice_sm.allReferenced_subState)

    def error(self):
        self._homingservice.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._homingservice_sm.set_state(self._homingservice_sm.error_state)

    def acknowledge(self):
        self._homingservice.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._homingservice.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

        self._homingservice_sm.publish_error(error_codes.StationErrorCodes.HomingServiceTimeout)
        self._homingservice_sm.set_state(self._homingservice_sm.error_state)


class DispatchEmpty(HomingState):
    """ Concrete State class for representing DispatchEmpty State. """

    def __init__(self, homingservice_sm, homingservice, super_sm=None, isSubstate=False):
        super(DispatchEmpty, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._homingservice_sm = homingservice_sm
        self._homingservice = homingservice
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._homingservice.logger.debug("Entering the %s state", self.name)
        self._homingservice.serviceState = "Busy"
        self._homingservice.publisher.publish(topic="HomeServiceState", value="Homing: Dispatch empty",
                                              sender=self._homingservice.name)

        self._homingservice.rack.handle_event(event=self._homingservice_sm.rack_update_event)
        self._homingservice.sensorCarriageOccupied.handle_event(event=self._homingservice_sm.sensor_update_event)

        # ToDO : Think about timeout timer !

    def reference(self):
        self._homingservice.logger.debug("%s event in %s state", self.reference.__name__, self.name)
        self._homingservice_sm.set_state(self._homingservice_sm.carriagehoming_state)

    def rack_is_empty(self):
        self._homingservice.logger.debug("%s event in %s state", self.rack_is_empty.__name__, self.name)
        self._homingservice_sm.set_state(self._homingservice_sm.allReferenced_subState)

    def rack_is_filling(self):
        self._homingservice.logger.debug("%s event in %s state", self.rack_is_filling.__name__, self.name)

    def rack_is_full(self):
        self._homingservice.logger.debug("%s event in %s state", self.rack_is_full.__name__, self.name)

    def carriage_is_atfront(self):
        self._homingservice.logger.debug("%s event in %s state", self.carriage_is_atfront.__name__, self.name)

    def carriage_is_atrack(self):
        self._homingservice.logger.debug("%s event in %s state", self.carriage_is_atrack.__name__, self.name)
        self._homingservice_sm.set_state(self._homingservice_sm.error_state)

    def carriage_is_outofpos(self):
        self._homingservice.logger.debug("%s event in %s state", self.carriage_is_outofpos.__name__, self.name)
        self._homingservice_sm.set_state(self._homingservice_sm.error_state)

    def dispatch_occupied(self):
        self._homingservice.logger.debug("%s event in %s state", self.dispatch_occupied.__name__, self.name)
        self._homingservice_sm.set_state(self._homingservice_sm.rackDispatchHoming_state)

    def dispatch_empty(self):
        self._homingservice.logger.debug("%s event in %s state", self.dispatch_empty.__name__, self.name)

    def error(self):
        self._homingservice.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._homingservice_sm.set_state(self._homingservice_sm.error_state)

    def acknowledge(self):
        self._homingservice.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._homingservice.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

        self._homingservice_sm.publish_error(error_codes.StationErrorCodes.HomingServiceTimeout)
        self._homingservice_sm.set_state(self._homingservice_sm.error_state)

class AllReferenced(HomingState):
    """ Concrete State class for representing AllReferenced State. """

    def __init__(self, homingservice_sm, homingservice, super_sm=None, isSubstate=False):
        super(AllReferenced, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._homingservice_sm = homingservice_sm
        self._homingservice = homingservice
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._homingservice.logger.debug("Entering the %s state", self.name)
        self._homingservice.serviceState = "Busy"
        self._homingservice.publisher.publish(topic="HomeServiceState", value="Homing: Done",
                                              sender=self._homingservice.name)

        if self._homingservice_sm.service_timeout_timer is not None:
            self._homingservice_sm.service_timeout_timer.cancel()

        self._homingservice.service_users[self._homingservice_sm._current_service_user].done()

    def reference(self):
        self._homingservice.logger.debug("%s event in %s state", self.reference.__name__, self.name)
        self._homingservice_sm.set_state(self._homingservice_sm.carriagehoming_state)

    def rack_is_empty(self):
        self._homingservice.logger.debug("%s event in %s state", self.rack_is_empty.__name__, self.name)

    def rack_is_filling(self):
        self._homingservice.logger.debug("%s event in %s state", self.rack_is_filling.__name__, self.name)

    def rack_is_full(self):
        self._homingservice.logger.debug("%s event in %s state", self.rack_is_full.__name__, self.name)

    def carriage_is_atfront(self):
        self._homingservice.logger.debug("%s event in %s state", self.carriage_is_atfront.__name__, self.name)

    def carriage_is_atrack(self):
        self._homingservice.logger.debug("%s event in %s state", self.carriage_is_atrack.__name__, self.name)

    def carriage_is_outofpos(self):
        self._homingservice.logger.debug("%s event in %s state", self.carriage_is_outofpos.__name__, self.name)

    def dispatch_occupied(self):
        self._homingservice.logger.debug("%s event in %s state", self.dispatch_occupied.__name__, self.name)

    def dispatch_empty(self):
        self._homingservice.logger.debug("%s event in %s state", self.dispatch_empty.__name__, self.name)

    def error(self):
        self._homingservice.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._homingservice_sm.set_state(self._homingservice_sm.error_state)

    def acknowledge(self):
        self._homingservice.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._homingservice.logger.debug("%s event in %s state", self.timeout.__name__, self.name)


class Error(HomingState):
    """ Concrete State class for representing Error State. """

    def __init__(self, homingservice_sm, homingservice, super_sm=None, isSubstate=False):
        super(Error, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._homingservice_sm = homingservice_sm
        self._homingservice = homingservice
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._homingservice.logger.debug("Entering the %s state", self.name)
        self._homingservice.serviceState = "Error"
        self._homingservice.publisher.publish(topic="HomeServiceState", value="Error",
                                              sender=self._homingservice.name)

        self._homingservice.carriage.handle_event(event=self._homingservice_sm.carriage_stop_event)

        if self._homingservice_sm.service_timeout_timer is not None:
            self._homingservice_sm.service_timeout_timer.cancel()

        try:
            if self._homingservice_sm.init_required:
                self._homingservice_sm.init_required = False
                self._homingservice.service_users[self._homingservice_sm._current_service_user].error(init_required=True)
            else:
                self._homingservice.service_users[self._homingservice_sm._current_service_user].error(init_required=False)
        except KeyError:
            self._homingservice.logger.debug("%s service was not called yet",  self.name)

    def reference(self):
        self._homingservice.logger.debug("%s event in %s state", self.reference.__name__, self.name)
        self._homingservice_sm.set_state(self._homingservice_sm.carriagehoming_state)

    def rack_is_empty(self):
        self._homingservice.logger.debug("%s event in %s state", self.rack_is_empty.__name__, self.name)

    def rack_is_filling(self):
        self._homingservice.logger.debug("%s event in %s state", self.rack_is_filling.__name__, self.name)

    def rack_is_full(self):
        self._homingservice.logger.debug("%s event in %s state", self.rack_is_full.__name__, self.name)

    def carriage_is_atfront(self):
        self._homingservice.logger.debug("%s event in %s state", self.carriage_is_atfront.__name__, self.name)

    def carriage_is_atrack(self):
        self._homingservice.logger.debug("%s event in %s state", self.carriage_is_atrack.__name__, self.name)

    def carriage_is_outofpos(self):
        self._homingservice.logger.debug("%s event in %s state", self.carriage_is_outofpos.__name__, self.name)

    def dispatch_occupied(self):
        self._homingservice.logger.debug("%s event in %s state", self.dispatch_occupied.__name__, self.name)

    def dispatch_empty(self):
        self._homingservice.logger.debug("%s event in %s state", self.dispatch_empty.__name__, self.name)

    def error(self):
        self._homingservice.logger.debug("%s event in %s state", self.error.__name__, self.name)

    def acknowledge(self):
        self._homingservice.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)
        self._homingservice_sm.set_state(self._homingservice_sm.notreferenced_state)

    def timeout(self):
        self._homingservice.logger.debug("%s event in %s state", self.timeout.__name__, self.name)


class HomingServiceStateMachine(object):
    """ Context class for the Init Service state machine """

    def __init__(self, homingservice, enable_timeout, timeout_interval):
        self._name = self.__class__.__name__

        self._homingservice = homingservice

        self._enable_timeout = enable_timeout
        self._timeout_interval = timeout_interval

        # timeout monitoring timer
        if self._enable_timeout:
            self.service_timeout_timer = MonitoringTimer(name="HomingServiceTimeoutTimer",
                                                         interval=self._timeout_interval,
                                                         callback_fnc=self.timeout_handler,
                                                         logger=self._homingservice.logger)
        else:
            self.service_timeout_timer = None

        # events :
        self.sensor_update_event = events.SimpleSensorInputEvent(eventID=events.SimpleSensorInputEvents.Update,sender=self._homingservice.name)
        self.rack_update_event = events.RackEvent(eventID=events.RackEvents.Update, sender=self._homingservice.name)
        self.carriage_update_event = events.CarriageEvent(eventID=events.CarriageEvents.Update, sender=self._homingservice.name)
        self.carriage_tofront_event = events.CarriageEvent(eventID=events.CarriageEvents.MoveToFrontPos, sender=self._homingservice.name)
        self.carriage_stop_event = events.CarriageEvent(eventID=events.CarriageEvents.Stop, sender=self._homingservice.name)
        self.timeout_event = events.GenericServiceEvent(eventID=events.GenericServiceEvents.Timeout, sender=self._homingservice.name)


        self._notreferenced_state = NotReferenced(self, self._homingservice)
        self._carriagehoming_state = CarriageHoming(self, self._homingservice)
        self._movingToFront_state = CarriageMovingToFront(self, self._homingservice)
        self._rackDispatchHoming_state = RackDispatchHoming(self, self._homingservice)
        self._rackempty_subState = RackEmpty(self, self._homingservice)
        self._dispatchEmpty_subState = DispatchEmpty(self, self._homingservice)
        self._allReferenced_subState = AllReferenced(self, self._homingservice)
        self._error_state = Error(self, self._homingservice)

        self._current_state = self._notreferenced_state
        self.set_state(self._current_state)

        self._current_service_user = 0

        self.init_required = False  # to show that an init is needed after the error

    # properties
    @property
    def current_state(self):
        return self._current_state

    @property
    def name(self):
        return self._name

    @property
    def notreferenced_state(self):
        return self._notreferenced_state

    @property
    def carriagehoming_state(self):
        return self._carriagehoming_state

    @property
    def movingToFront_state(self):
        return self._movingToFront_state

    @property
    def rackDispatchHoming_state(self):
        return self._rackDispatchHoming_state

    @property
    def rackempty_subState(self):
        return self._rackempty_subState

    @property
    def dispatchEmpty_subState(self):
        return self._dispatchEmpty_subState

    @property
    def allReferenced_subState(self):
        return self._allReferenced_subState

    @property
    def error_state(self):
        return self._error_state

    def set_state(self, state):
        self._homingservice.logger.debug("Switching from state %s to state %s", self.current_state.name, state.name)

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
        self._homingservice.publisher.publish(topic="StationErrorCode",
                                                value=hex(error_code),
                                                sender=self._homingservice.name)
        self._homingservice.publisher.publish(topic="StationErrorDescription",
                                                value=error_codes.code_to_text[error_code],
                                                sender=self._homingservice.name)

    def publish_message(self, message_code):
        self._homingservice.publisher.publish(topic="StationMessageCode",
                                                value=hex(message_code),
                                                sender=self._homingservice.name)
        self._homingservice.publisher.publish(topic="StationMessageDescription",
                                                value=message_codes.code_to_text[message_code],
                                                sender=self._homingservice.name)

    def dispatch(self, *args, **kwargs):

        self._homingservice.logger.debug("%s has received a message: %s", self.name, kwargs)

        try:
            # topics coming from the publishers
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
                        pass
                        # self._current_state.error()
                    elif value == "RackEmpty":
                        self._current_state.rack_is_empty()
                    elif value == "RackFilling":
                        self._current_state.rack_is_filling()
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
                        self._current_state.carriage_is_outofpos()
                    elif value == "AtFrontPosition":
                        self._current_state.carriage_is_atfront()
                    elif value == "AtRackPosition":
                        self._current_state.carriage_is_atrack()

            elif sender == "SensorCarriageOccupied":

                if topic == "Value":
                    if value:
                        self._current_state.dispatch_occupied()
                    else:
                        self._current_state.dispatch_empty()

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
                self._current_state.reference()
                self._current_service_user = service_index
            elif eventID == events.GenericServiceEvents.Cancel:
                self._homingservice.logger.debug("Cancel service was not implemented for the %s service", self._homingservice.name)
            elif eventID == events.GenericServiceEvents.Done:  # for callable services
                pass

            elif eventID == events.GenericServiceEvents.Timeout:  # timeout event comes from the service itself ???
                self._current_state.timeout()
