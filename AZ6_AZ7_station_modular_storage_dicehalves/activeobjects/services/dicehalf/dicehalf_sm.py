import abc
from communication import events
from threading import Timer
import config
from utils import error_codes
from utils import message_codes
from utils.monitoring_timer import MonitoringTimer

class ProvideDicehalfState(metaclass=abc.ABCMeta):
    """ Abstract State class for a ProvideHalfDice Service SM """

    def __init__(self, isSubstate=False):
        self._isSubstate = isSubstate

    @property
    def isSubstate(self):
        return self._isSubstate

    @abc.abstractmethod
    def start_service(self):
        raise NotImplemented

    @abc.abstractmethod
    def carriage_is_atrack(self):
        raise NotImplemented

    @abc.abstractmethod
    def move_to_front(self):
        raise NotImplemented

    @abc.abstractmethod
    def carriage_is_atfront(self):
        raise NotImplemented

    @abc.abstractmethod
    def dispatch_empty(self):
        raise NotImplemented

    @abc.abstractmethod
    def dispatch_occupied(self):
        raise NotImplemented

    @abc.abstractmethod
    def rack_is_empty(self):
        raise NotImplemented

    @abc.abstractmethod
    def rack_not_empty(self):
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


class EmptyRack(ProvideDicehalfState):
    """ Concrete State class for representing EmptyRack State. """

    def __init__(self, providehalfdice_sm, providehalfdice, super_sm=None, isSubstate=False):
        super(EmptyRack, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._providehalfdice_sm = providehalfdice_sm
        self._providehalfdice = providehalfdice
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._providehalfdice.logger.debug("Entering the %s state", self.name)
        self._providehalfdice.serviceState = "EmptyRack"
        self._providehalfdice.publisher.publish(topic="ProvideDicehalfServiceState", value="EmptyRack", sender=self._providehalfdice.name)

        # blinking
        led_blinking_start = events.BlinkerEvent(events.BlinkerEvents.Start, self._providehalfdice.name)
        self._providehalfdice.blinker.handle_event(event=led_blinking_start)

    def start_service(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.start_service.__name__, self.name)

        # empty rack message to the server :
        self._providehalfdice_sm.publish_message(message_codes.StationMessageCodes.RackEmpty)

    def carriage_is_atrack(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.carriage_is_atrack.__name__, self.name)

    def move_to_front(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.move_to_front.__name__, self.name)

    def carriage_is_atfront(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.carriage_is_atfront.__name__, self.name)

    def dispatch_empty(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.dispatch_occupied.__name__, self.name)

    def dispatch_occupied(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.dispatch_empty.__name__, self.name)

    def rack_is_empty(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.rack_is_empty.__name__, self.name)

        # blinking
        led_blinking_start = events.BlinkerEvent(events.BlinkerEvents.Start, self._providehalfdice.name)
        self._providehalfdice.blinker.handle_event(event=led_blinking_start)

    def rack_not_empty(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.rack_not_empty.__name__, self.name)

        # stop blinking
        led_blinking_stop = events.BlinkerEvent(events.BlinkerEvents.Stop, self._providehalfdice.name)
        self._providehalfdice.blinker.handle_event(event=led_blinking_stop)

        self._providehalfdice_sm.set_state(self._providehalfdice_sm.waitforjob_state)

    def error(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.error.__name__, self.name)

        # stop blinking
        led_blinking_stop = events.BlinkerEvent(events.BlinkerEvents.Stop, self._providehalfdice.name)
        self._providehalfdice.blinker.handle_event(event=led_blinking_stop)

        self._providehalfdice_sm.set_state(self._providehalfdice_sm.error_state)

    def acknowledge(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def resetjob(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.resetjob.__name__, self.name)

    def timeout(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.timeout.__name__, self.name)


class DispatchOccupied(ProvideDicehalfState):
    """ Concrete State class for representing DispatchOccupied State. """

    def __init__(self, providehalfdice_sm, providehalfdice, super_sm=None, isSubstate=False):
        super(DispatchOccupied, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._providehalfdice_sm = providehalfdice_sm
        self._providehalfdice = providehalfdice
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._providehalfdice.logger.debug("Entering the %s state", self.name)
        self._providehalfdice.serviceState = "DispatchOccupied"
        self._providehalfdice.publisher.publish(topic="ProvideDicehalfServiceState", value="DispatchOccupied",
                                                sender=self._providehalfdice.name)

        # blinking
        led_blinking_start = events.BlinkerEvent(events.BlinkerEvents.Start, self._providehalfdice.name)
        self._providehalfdice.blinker.handle_event(event=led_blinking_start)

    def start_service(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.start_service.__name__, self.name)

        # dispatch not empty message to the server :
        # self._providehalfdice_sm.publish_message(message_codes.StationMessageCodes.DispatchNotEmpty)

    def carriage_is_atrack(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.carriage_is_atrack.__name__, self.name)

    def move_to_front(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.move_to_front.__name__, self.name)

    def carriage_is_atfront(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.carriage_is_atfront.__name__, self.name)

    def dispatch_empty(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.dispatch_occupied.__name__, self.name)

        # stop blinking
        led_blinking_stop = events.BlinkerEvent(events.BlinkerEvents.Stop, self._providehalfdice.name)
        self._providehalfdice.blinker.handle_event(event=led_blinking_stop)

        self._providehalfdice_sm.set_state(self._providehalfdice_sm.waitforjob_state)

    def dispatch_occupied(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.dispatch_empty.__name__, self.name)

    def rack_is_empty(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.rack_is_empty.__name__, self.name)

    def rack_not_empty(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.rack_not_empty.__name__, self.name)

    def error(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.error.__name__, self.name)

        # stop blinking
        led_blinking_stop = events.BlinkerEvent(events.BlinkerEvents.Stop, self._providehalfdice.name)
        self._providehalfdice.blinker.handle_event(event=led_blinking_stop)

        self._providehalfdice_sm.set_state(self._providehalfdice_sm.error_state)

    def acknowledge(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def resetjob(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.resetjob.__name__, self.name)

    def timeout(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.timeout.__name__, self.name)


class WaitForJob(ProvideDicehalfState):
    """ Concrete State class for representing WaitForJob State. """

    def __init__(self, providehalfdice_sm, providehalfdice, super_sm=None, isSubstate=False):
        super(WaitForJob, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._providehalfdice_sm = providehalfdice_sm
        self._providehalfdice = providehalfdice
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._providehalfdice.logger.debug("Entering the %s state", self.name)
        self._providehalfdice.serviceState = "Ready"
        self._providehalfdice.publisher.publish(topic="ProvideDicehalfServiceState", value="WaitForJob",
                                                sender=self._providehalfdice.name)

        self._providehalfdice.carriage.handle_event(event=self._providehalfdice_sm.carriage_update_event)
        self._providehalfdice.rack.handle_event(event=self._providehalfdice_sm.rack_update_event)
        self._providehalfdice.sensorCarriageOccupied.handle_event(event=self._providehalfdice_sm.sensor_update_event)

    def start_service(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.start_service.__name__, self.name)

        if self._providehalfdice_sm.service_timeout_timer is not None:
            self._providehalfdice_sm.service_timeout_timer.start()

        self._providehalfdice_sm.set_state(self._providehalfdice_sm.movingtorack_state)

    def carriage_is_atrack(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.carriage_is_atrack.__name__, self.name)

    def move_to_front(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.move_to_front.__name__, self.name)

    def carriage_is_atfront(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.carriage_is_atfront.__name__, self.name)

    def dispatch_empty(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.dispatch_empty.__name__, self.name)

    def dispatch_occupied(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.dispatch_empty.__name__, self.name)
        self._providehalfdice_sm.set_state(self._providehalfdice_sm.dispatchoccupied_state)

    def rack_is_empty(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.rack_is_empty.__name__, self.name)
        self._providehalfdice_sm.set_state(self._providehalfdice_sm.emptyrack_state)

    def rack_not_empty(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.rack_not_empty.__name__, self.name)

    def error(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._providehalfdice_sm.set_state(self._providehalfdice_sm.error_state)

    def acknowledge(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def resetjob(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.resetjob.__name__, self.name)

    def timeout(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.timeout.__name__, self.name)


class MovingToRack(ProvideDicehalfState):
    """ Concrete State class for representing MovingToRack State. """

    def __init__(self, providehalfdice_sm, providehalfdice, super_sm=None, isSubstate=False):
        super(MovingToRack, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._providehalfdice_sm = providehalfdice_sm
        self._providehalfdice = providehalfdice
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._providehalfdice.logger.debug("Entering the %s state", self.name)
        self._providehalfdice.serviceState = "Busy"
        self._providehalfdice.publisher.publish(topic="ProvideDicehalfServiceState", value="MovingToRack",
                                                sender=self._providehalfdice.name)

        self._providehalfdice.carriage.handle_event(event=self._providehalfdice_sm.carriage_torack_event)

    def start_service(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.start_service.__name__, self.name)

    def carriage_is_atrack(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.carriage_is_atrack.__name__, self.name)

        self._providehalfdice_sm.set_state(self._providehalfdice_sm.waiting_halfdice_state)

    def move_to_front(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.move_to_front.__name__, self.name)

    def carriage_is_atfront(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.carriage_is_atfront.__name__, self.name)

    def dispatch_empty(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.dispatch_empty.__name__, self.name)

    def dispatch_occupied(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.dispatch_empty.__name__, self.name)

    def rack_is_empty(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.rack_is_empty.__name__, self.name)

    def rack_not_empty(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.rack_not_empty.__name__, self.name)

    def error(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.error.__name__, self.name)

        self._providehalfdice_sm.set_state(self._providehalfdice_sm.error_state)

    def acknowledge(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def resetjob(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.resetjob.__name__, self.name)

        self._providehalfdice.carriage.handle_event(event=self._providehalfdice_sm.carriage_stop_event)

        if self._providehalfdice_sm.service_timeout_timer is not None:
            self._providehalfdice_sm.service_timeout_timer.cancel()

        self._providehalfdice.service_users[self._providehalfdice_sm._current_service_user].done()

        self._providehalfdice_sm.set_state(self._providehalfdice_sm.waitforjob_state)

    def timeout(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

        self._providehalfdice_sm.publish_error(error_codes.StationErrorCodes.ProvideDicehalfServiceTimeout)
        self._providehalfdice_sm.set_state(self._providehalfdice_sm.error_state)


class WaitingHalfdice(ProvideDicehalfState):
    """ Concrete State class for representing WaitingHalfdice State. """

    def __init__(self, providehalfdice_sm, providehalfdice, super_sm=None, isSubstate=False):
        super(WaitingHalfdice, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._providehalfdice_sm = providehalfdice_sm
        self._providehalfdice = providehalfdice
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._providehalfdice.logger.debug("Entering the %s state", self.name)
        self._providehalfdice.serviceState = "Busy"
        self._providehalfdice.publisher.publish(topic="ProvideDicehalfServiceState", value="WaitingHalfdice",
                                                sender=self._providehalfdice.name)

        timeout_time = config.STATION_CONFIG['waitForDicehalfdelay']
        Timer(timeout_time, self._providehalfdice_sm.timeout_move_to_front).start()

    def start_service(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.start_service.__name__, self.name)

    def carriage_is_atrack(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.carriage_is_atrack.__name__, self.name)

    def move_to_front(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.move_to_front.__name__, self.name)

        # decrease the number of the dicehalfs in the rack
        self._providehalfdice.rack.handle_event(event=self._providehalfdice_sm.rack_decrease_event)

        # update the rack's status
        self._providehalfdice.rack.handle_event(event=self._providehalfdice_sm.rack_update_event)

        self._providehalfdice_sm.set_state(self._providehalfdice_sm.movingtofront_state)

    def carriage_is_atfront(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.carriage_is_atfront.__name__, self.name)

    def dispatch_empty(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.dispatch_empty.__name__, self.name)

    def dispatch_occupied(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.dispatch_empty.__name__, self.name)

    def rack_is_empty(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.rack_is_empty.__name__, self.name)

    def rack_not_empty(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.rack_not_empty.__name__, self.name)

    def error(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._providehalfdice_sm.set_state(self._providehalfdice_sm.error_state)

    def acknowledge(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def resetjob(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.resetjob.__name__, self.name)

        self._providehalfdice.carriage.handle_event(event=self._providehalfdice_sm.carriage_stop_event)

        if self._providehalfdice_sm.service_timeout_timer is not None:
            self._providehalfdice_sm.service_timeout_timer.cancel()

        self._providehalfdice_sm.init_required = True

        self._providehalfdice_sm.set_state(self._providehalfdice_sm.error_state)

    def timeout(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

        self._providehalfdice_sm.publish_error(error_codes.StationErrorCodes.ProvideDicehalfServiceTimeout)
        self._providehalfdice_sm.set_state(self._providehalfdice_sm.error_state)


class MovingToFront(ProvideDicehalfState):
    """ Concrete State class for representing MovingToFRont State. """

    def __init__(self, providehalfdice_sm, providehalfdice, super_sm=None, isSubstate=False):
        super(MovingToFront, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._providehalfdice_sm = providehalfdice_sm
        self._providehalfdice = providehalfdice
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._providehalfdice.logger.debug("Entering the %s state", self.name)
        self._providehalfdice.serviceState = "Busy"
        self._providehalfdice.publisher.publish(topic="ProvideDicehalfServiceState", value="MovingToFront",
                                                sender=self._providehalfdice.name)

        self._providehalfdice.carriage.handle_event(event=self._providehalfdice_sm.carriage_tofront_event)


    def start_service(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.start_service.__name__, self.name)

    def carriage_is_atrack(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.carriage_is_atrack.__name__, self.name)

    def move_to_front(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.move_to_front.__name__, self.name)

    def carriage_is_atfront(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.carriage_is_atfront.__name__, self.name)

        self._providehalfdice_sm.set_state(self._providehalfdice_sm.halfdiceOut_state)

    def dispatch_empty(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.dispatch_empty.__name__, self.name)

    def dispatch_occupied(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.dispatch_empty.__name__, self.name)

    def rack_is_empty(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.rack_is_empty.__name__, self.name)

    def rack_not_empty(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.rack_not_empty.__name__, self.name)

    def error(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.error.__name__, self.name)

        self._providehalfdice_sm.set_state(self._providehalfdice_sm.error_state)

    def acknowledge(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def resetjob(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.resetjob.__name__, self.name)

        self._providehalfdice.carriage.handle_event(event=self._providehalfdice_sm.carriage_stop_event)

        if self._providehalfdice_sm.service_timeout_timer is not None:
            self._providehalfdice_sm.service_timeout_timer.cancel()

        self._providehalfdice_sm.init_required = True

        self._providehalfdice_sm.set_state(self._providehalfdice_sm.error_state)

    def timeout(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

        self._providehalfdice_sm.publish_error(error_codes.StationErrorCodes.ProvideDicehalfServiceTimeout)
        self._providehalfdice_sm.set_state(self._providehalfdice_sm.error_state)


class DicehalfOut(ProvideDicehalfState):
    """ Concrete State class for representing HalfdiceOut State. """

    def __init__(self, providehalfdice_sm, providehalfdice, super_sm=None, isSubstate=False):
        super(DicehalfOut, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._providehalfdice_sm = providehalfdice_sm
        self._providehalfdice = providehalfdice
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._providehalfdice.logger.debug("Entering the %s state", self.name)
        self._providehalfdice.serviceState = "Busy"
        self._providehalfdice.publisher.publish(topic="ProvideDicehalfServiceState", value="DicehalfOut",
                                                sender=self._providehalfdice.name)

    def start_service(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.start_service.__name__, self.name)

    def carriage_is_atrack(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.carriage_is_atrack.__name__, self.name)

    def move_to_front(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.move_to_front.__name__, self.name)

    def carriage_is_atfront(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.carriage_is_atfront.__name__, self.name)

    def dispatch_empty(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.dispatch_empty.__name__, self.name)
        self._providehalfdice_sm.set_state(self._providehalfdice_sm.waitforjob_state)

        self._providehalfdice.service_users[self._providehalfdice_sm._current_service_user].done()

    def dispatch_occupied(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.dispatch_empty.__name__, self.name)

    def rack_is_empty(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.rack_is_empty.__name__, self.name)

    def rack_not_empty(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.rack_not_empty.__name__, self.name)

    def error(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._providehalfdice_sm.set_state(self._providehalfdice_sm.error_state)

    def acknowledge(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def resetjob(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.resetjob.__name__, self.name)

        self._providehalfdice.carriage.handle_event(event=self._providehalfdice_sm.carriage_stop_event)

        if self._providehalfdice_sm.service_timeout_timer is not None:
            self._providehalfdice_sm.service_timeout_timer.cancel()

        self._providehalfdice_sm.init_required = True

        self._providehalfdice_sm.set_state(self._providehalfdice_sm.error_state)

    def timeout(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

        self._providehalfdice_sm.publish_error(error_codes.StationErrorCodes.ProvideDicehalfServiceTimeout)
        self._providehalfdice_sm.set_state(self._providehalfdice_sm.error_state)


class Error(ProvideDicehalfState):
    """ Concrete State class for representing Error State. """

    def __init__(self, providehalfdice_sm, providehalfdice, super_sm=None, isSubstate=False):
        super(Error, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._providehalfdice_sm = providehalfdice_sm
        self._providehalfdice = providehalfdice
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._providehalfdice.logger.debug("Entering the %s state", self.name)
        self._providehalfdice.serviceState = "Error"
        self._providehalfdice.publisher.publish(topic="ProvideDicehalfServiceState", value="Error",
                                                sender=self._providehalfdice.name)

        self._providehalfdice.carriage.handle_event(event=self._providehalfdice_sm.carriage_stop_event)

        if self._providehalfdice_sm.service_timeout_timer is not None:
            self._providehalfdice_sm.service_timeout_timer.cancel()

        try:
            if self._providehalfdice_sm.init_required:
                self._providehalfdice_sm.init_required = False
                self._providehalfdice.service_users[self._providehalfdice_sm._current_service_user].error(init_required=True)
            else:
                self._providehalfdice.service_users[self._providehalfdice_sm._current_service_user].error(init_required=False)
        except KeyError:
            self._providehalfdice.logger.debug("%s service was not called yet",  self.name)

    def start_service(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.start_service.__name__, self.name)

    def carriage_is_atrack(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.carriage_is_atrack.__name__, self.name)

    def move_to_front(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.move_to_front.__name__, self.name)

    def carriage_is_atfront(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.carriage_is_atfront.__name__, self.name)

    def dispatch_empty(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.dispatch_empty.__name__, self.name)

    def dispatch_occupied(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.dispatch_empty.__name__, self.name)

    def rack_is_empty(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.rack_is_empty.__name__, self.name)

    def rack_not_empty(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.rack_not_empty.__name__, self.name)

    def error(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.error.__name__, self.name)

    def acknowledge(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)
        self._providehalfdice_sm.set_state(self._providehalfdice_sm.waitforjob_state)

    def resetjob(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.resetjob.__name__, self.name)
        self._providehalfdice_sm.set_state(self._providehalfdice_sm.waitforjob_state)

    def timeout(self):
        self._providehalfdice.logger.debug("%s event in %s state", self.timeout.__name__, self.name)


class ProvideDicehalfStateMachine(object):
    """ Context class for the ProvideHalfDice state machine """
    def __init__(self, providehalfdice, enable_timeout, timeout_interval):
        self._name = self.__class__.__name__

        self._providehalfdice = providehalfdice

        self._enable_timeout = enable_timeout
        self._timeout_interval = timeout_interval

        # timeout monitoring timer
        if self._enable_timeout:
            self.service_timeout_timer = MonitoringTimer(name="ProvideDicehalfServiceTimeoutTimer",
                                                         interval=self._timeout_interval,
                                                         callback_fnc=self.timeout_handler,
                                                         logger=self._providehalfdice.logger)
        else:
            self.service_timeout_timer = None

        # events :
        self.rack_update_event = events.RackEvent(eventID=events.RackEvents.Update, sender=self._providehalfdice.name)
        self.rack_decrease_event = events.RackEvent(eventID=events.RackEvents.DecRack, sender=self._providehalfdice.name)
        self.carriage_update_event = events.CarriageEvent(eventID=events.CarriageEvents.Update,
                                                          sender=self._providehalfdice.name)
        self.sensor_update_event = events.SimpleSensorInputEvent(eventID=events.SimpleSensorInputEvents.Update,
                                                                 sender=self._providehalfdice.name)
        self.carriage_tofront_event = events.CarriageEvent(eventID=events.CarriageEvents.MoveToFrontPos,
                                                           sender=self._providehalfdice.name)
        self.carriage_torack_event = events.CarriageEvent(eventID=events.CarriageEvents.MoveToRackPos,
                                                           sender=self._providehalfdice.name)
        self.carriage_stop_event = events.CarriageEvent(eventID=events.CarriageEvents.Stop,
                                                        sender=self._providehalfdice.name)
        self.timeout_event = events.GenericServiceEvent(eventID=events.GenericServiceEvents.Timeout,
                                                        sender=self._providehalfdice.name)


        self._waitforjob_state = WaitForJob(self, self._providehalfdice)
        self._emptyrack_state = EmptyRack(self, self._providehalfdice)
        self._dispatchoccupied_state = DispatchOccupied(self, self._providehalfdice)
        self._movingtorack_state = MovingToRack(self, self._providehalfdice)
        self._waiting_halfdice_state = WaitingHalfdice(self, self._providehalfdice)
        self._movingtofront_state = MovingToFront(self, self._providehalfdice)
        self._halfdiceOut_state = DicehalfOut(self, self._providehalfdice)
        self._error_state = Error(self, self._providehalfdice)

        self._current_state = self._waitforjob_state
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
    def waitforjob_state(self):
        return self._waitforjob_state

    @property
    def emptyrack_state(self):
        return self._emptyrack_state

    @property
    def dispatchoccupied_state(self):
        return self._dispatchoccupied_state

    @property
    def movingtorack_state(self):
        return self._movingtorack_state

    @property
    def waiting_halfdice_state(self):
        return self._waiting_halfdice_state

    @property
    def movingtofront_state(self):
        return self._movingtofront_state

    @property
    def halfdiceOut_state(self):
        return self._halfdiceOut_state

    @property
    def error_state(self):
        return self._error_state

    def set_state(self, state):
        self._providehalfdice.logger.debug("Switching from state %s to state %s", self.current_state.name, state.name)

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
        self._providehalfdice.publisher.publish(topic="StationErrorCode",
                                              value=hex(error_code),
                                              sender=self._providehalfdice.name)
        self._providehalfdice.publisher.publish(topic="StationErrorDescription",
                                              value=error_codes.code_to_text[error_code],
                                              sender=self._providehalfdice.name)

    def publish_message(self, message_code):
        self._providehalfdice.publisher.publish(topic="StationMessageCode",
                                                value=hex(message_code),
                                                sender=self._providehalfdice.name)
        self._providehalfdice.publisher.publish(topic="StationMessageDescription",
                                                value=message_codes.code_to_text[message_code],
                                                sender=self._providehalfdice.name)

    def timeout_move_to_front(self):
        self._current_state.move_to_front()

    def timeout_handler(self):
        self.init_required = True
        self.dispatch(event=self.timeout_event)

    def dispatch(self, *args, **kwargs):

        self._providehalfdice.logger.debug("%s has received a message: %s", self.name, kwargs)

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
                        # self._current_state.error()
                        pass
                    elif value == "RackEmpty":
                        self._current_state.rack_is_empty()
                    elif value == "RackFilling":
                        self._current_state.rack_not_empty()
                    elif value == "RackFull":
                        self._current_state.rack_not_empty()

            elif sender == "Carriage":

                if topic == "Value":
                    pass

                elif topic == "State":

                    if value == "Error":
                        self._current_state.error()
                    elif value == "NotInitialized":
                        # self._current_state.error()
                        pass
                    elif value == "OutOfPosition":
                        pass
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
                        # self._current_state.error()
                        pass
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

