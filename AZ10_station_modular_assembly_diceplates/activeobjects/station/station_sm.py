import abc, time
from communication import events
from utils import error_codes, message_codes

class StationState(metaclass=abc.ABCMeta):
    """ Abstract State class for a Station SM """

    def __init__(self, isSubstate=False):
        self._isSubstate = isSubstate

    @property
    def isSubstate(self):
        return self._isSubstate

    @abc.abstractmethod
    def initialize(self):
        raise NotImplemented

    @abc.abstractmethod
    def initialize_done(self):
        raise NotImplemented

    @abc.abstractmethod
    def service1(self):
        raise NotImplemented

    @abc.abstractmethod
    def service1_done(self):
        raise NotImplemented

    @abc.abstractmethod
    def service2(self):
        pass

    @abc.abstractmethod
    def service2_done(self):
        pass

    @abc.abstractmethod
    def service3(self):
        raise NotImplemented

    @abc.abstractmethod
    def service3_done(self):
        raise NotImplemented

    @abc.abstractmethod
    def service4(self):
        raise NotImplemented

    @abc.abstractmethod
    def service4_done(self):
        raise NotImplemented

    @abc.abstractmethod
    def service5(self):
        pass

    @abc.abstractmethod
    def service5_done(self):
        pass

    @abc.abstractmethod
    def service6(self):
        raise NotImplemented

    @abc.abstractmethod
    def service_cancel(self):
        raise NotImplemented

    @abc.abstractmethod
    def service6_done(self):
        raise NotImplemented

    @abc.abstractmethod
    def estop(self):
        raise NotImplemented

    @abc.abstractmethod
    def estop_ok(self):
        raise NotImplemented

    @abc.abstractmethod
    def noconn(self):
        raise NotImplemented

    @abc.abstractmethod
    def conn_ok(self):
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


class Starting(StationState):
    """ Concrete State class for representing Starting State"""

    def __init__(self, station_sm, station, super_sm=None, isSubstate=False):
        super(Starting, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._station_sm = station_sm
        self._station = station
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._station.stationState = "Starting"
        self._station.logger.debug("Entering the %s state", self.name)
        self._station.publisher.publish(topic="StationState", value=self._station.stationState, sender=self._station.name)
        self._station.publisher.publish(topic='StationStateMaintenance', value=self._station.stationState,
                                        sender=self._station.name)

        # standby purple LED color + blinking
        self._station.status_led.handle_event(event=self._station_sm.purple_event)
        self._station.blinker.handle_event(event=self._station_sm.blink_start_event)

    def initialize(self):
        self._station.logger.debug("%s event in %s state", self.initialize.__name__, self.name)

    def initialize_done(self):
        self._station.logger.debug("%s event in %s state", self.initialize_done.__name__, self.name)

    def service1(self):
        self._station.logger.debug("%s event in %s state", self.service1.__name__, self.name)

    def service1_done(self):
        self._station.logger.debug("%s event in %s state", self.service1_done.__name__, self.name)

    def service2(self):
        self._station.logger.debug("%s event in %s state", self.service2.__name__, self.name)

    def service2_done(self):
        self._station.logger.debug("%s event in %s state", self.service2_done.__name__, self.name)

    def service3(self):
        self._station.logger.debug("%s event in %s state", self.service3.__name__, self.name)

    def service3_done(self):
        self._station.logger.debug("%s event in %s state", self.service3_done.__name__, self.name)

    def service4(self):
        self._station.logger.debug("%s event in %s state", self.service4.__name__, self.name)

    def service4_done(self):
        self._station.logger.debug("%s event in %s state", self.service4_done.__name__, self.name)

    def service5(self):
        self._station.logger.debug("%s event in %s state", self.service5.__name__, self.name)

    def service5_done(self):
        self._station.logger.debug("%s event in %s state", self.service5_done.__name__, self.name)

    def service6(self):
        self._station.logger.debug("%s event in %s state", self.service6.__name__, self.name)

    def service6_done(self):
        self._station.logger.debug("%s event in %s state", self.service6_done.__name__, self.name)

    def service_cancel(self):
        self._station.logger.debug("%s event in %s state", self.service_cancel.__name__, self.name)

    def estop(self):
        self._station.logger.debug("%s event in %s state", self.estop.__name__, self.name)

        # blinking stop
        self._station.blinker.handle_event(event=self._station_sm.blink_stop_event)

        self._station_sm.set_state(self._station_sm.estop_state)

    def estop_ok(self):
        self._station.logger.debug("%s event in %s state", self.estop_ok.__name__, self.name)

    def error(self):
        self._station.logger.debug("%s event in %s state", self.error.__name__, self.name)

        self._station_sm.set_state(self._station.error_state)

    def noconn(self):
        self._station.logger.debug("%s event in %s state", self.noconn.__name__, self.name)

        # blinking stop
        self._station.blinker.handle_event(event=self._station_sm.blink_stop_event)

        self._station_sm.set_state(self._station_sm.noconn_state)

    def conn_ok(self):
        self._station.logger.debug("%s event in %s state", self.conn_ok.__name__, self.name)

        # blinking stop
        self._station.blinker.handle_event(event=self._station_sm.blink_stop_event)

        self._station_sm.set_state(self._station_sm.notinitialized_state)

    def acknowledge(self):
        self._station.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._station.logger.debug("%s event in %s state", self.timeout.__name__, self.name)


class NotInitialized(StationState):
    """ Concrete State class for representing NotInitialized State"""

    def __init__(self, station_sm, station, super_sm=None, isSubstate=False):
        super(NotInitialized, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._station_sm = station_sm
        self._station = station
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._station.stationState = "Standby"
        self._station.logger.debug("Entering the %s state", self.name)
        self._station.publisher.publish(topic="StationState", value=self._station.stationState, sender=self._station.name)
        self._station.publisher.publish(topic='StationStateMaintenance', value="NotInitialized",
                                        sender=self._station.name)

        # LEDs off
        self._station.status_led.handle_event(event=self._station_sm.ledoff_event)

        # standby purple status LED color
        self._station.status_led.handle_event(event=self._station_sm.purple_event)

    def initialize(self):
        self._station.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._station_sm.set_state(self._station_sm.initialization_state)

    def initialize_done(self):
        self._station.logger.debug("%s event in %s state", self.initialize_done.__name__, self.name)

    def service1(self):
        self._station.logger.debug("%s event in %s state", self.service1.__name__, self.name)

    def service1_done(self):
        self._station.logger.debug("%s event in %s state", self.service1_done.__name__, self.name)

    def service2(self):
        self._station.logger.debug("%s event in %s state", self.service2.__name__, self.name)

    def service2_done(self):
        self._station.logger.debug("%s event in %s state", self.service2_done.__name__, self.name)

    def service3(self):
        self._station.logger.debug("%s event in %s state", self.service3.__name__, self.name)

    def service3_done(self):
        self._station.logger.debug("%s event in %s state", self.service3_done.__name__, self.name)

    def service4(self):
        self._station.logger.debug("%s event in %s state", self.service4.__name__, self.name)

    def service4_done(self):
        self._station.logger.debug("%s event in %s state", self.service4_done.__name__, self.name)

    def service5(self):
        self._station.logger.debug("%s event in %s state", self.service5.__name__, self.name)

    def service5_done(self):
        self._station.logger.debug("%s event in %s state", self.service5_done.__name__, self.name)

    def service6(self):
        self._station.logger.debug("%s event in %s state", self.service6.__name__, self.name)

    def service6_done(self):
        self._station.logger.debug("%s event in %s state", self.service6_done.__name__, self.name)

    def service_cancel(self):
        self._station.logger.debug("%s event in %s state", self.service_cancel.__name__, self.name)

    def estop(self):
        self._station.logger.debug("%s event in %s state", self.estop.__name__, self.name)
        self._station_sm.set_state(self._station_sm.estop_state)

    def estop_ok(self):
        self._station.logger.debug("%s event in %s state", self.estop_ok.__name__, self.name)

    def error(self):
        self._station.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._station_sm.set_state(self._station_sm.error_state)

    def noconn(self):
        self._station.logger.debug("%s event in %s state", self.noconn.__name__, self.name)
        self._station_sm.set_state(self._station_sm.noconn_state)

    def conn_ok(self):
        self._station.logger.debug("%s event in %s state", self.conn_ok.__name__, self.name)

    def acknowledge(self):
        self._station.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._station.logger.debug("%s event in %s state", self.timeout.__name__, self.name)


class Initialization(StationState):
    """ Concrete State class for representing Init State : NotInit substate"""
    def __init__(self, station_sm, station, super_sm=None, isSubstate=False):
        super(Initialization, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._station_sm = station_sm
        self._station = station
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._station.stationState = "Standby"
        self._station.logger.debug("Entering the %s state", self.name)
        self._station.publisher.publish(topic="StationState", value=self._station.stationState, sender=self._station.name)
        self._station.publisher.publish(topic='StationStateMaintenance', value="Initialization",
                                        sender=self._station.name)

        if self._station.callable_services is not None:
            for i in self._station.callable_services:
                self._station.callable_services[i].cancel()  # reset all active services

        # standby purple status LED color + blinking
        self._station.blinker.handle_event(event=self._station_sm.blink_start_event)
        self._station.status_led.handle_event(event=self._station_sm.purple_event)

        self._station.callable_services[0].execute()  # start init service

    def initialize(self):
        self._station.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._station_sm.set_state(self._station_sm.initialization_state)

    def initialize_done(self):
        self._station.logger.debug("%s event in %s state", self.initialize_done.__name__, self.name)
        if self._station_sm._homing_required:
            self._station_sm.set_state(self._station_sm.homing_state)
        else:
            self._station_sm.set_state(self._station_sm.ready_state)

    def service1(self):
        self._station.logger.debug("%s event in %s state", self.service1.__name__, self.name)

    def service1_done(self):
        self._station.logger.debug("%s event in %s state", self.service1_done.__name__, self.name)

    def service2(self):
        self._station.logger.debug("%s event in %s state", self.service2.__name__, self.name)

    def service2_done(self):
        self._station.logger.debug("%s event in %s state", self.service2_done.__name__, self.name)

    def service3(self):
        self._station.logger.debug("%s event in %s state", self.service3.__name__, self.name)

    def service3_done(self):
        self._station.logger.debug("%s event in %s state", self.service3_done.__name__, self.name)

    def service4(self):
        self._station.logger.debug("%s event in %s state", self.service4.__name__, self.name)

    def service4_done(self):
        self._station.logger.debug("%s event in %s state", self.service4_done.__name__, self.name)

    def service5(self):
        self._station.logger.debug("%s event in %s state", self.service5.__name__, self.name)

    def service5_done(self):
        self._station.logger.debug("%s event in %s state", self.service5_done.__name__, self.name)

    def service6(self):
        self._station.logger.debug("%s event in %s state", self.service6.__name__, self.name)

    def service6_done(self):
        self._station.logger.debug("%s event in %s state", self.service6_done.__name__, self.name)
        self._station_sm.set_state(self._station_sm.ready_state)

    def service_cancel(self):
        self._station.logger.debug("%s event in %s state", self.service_cancel.__name__, self.name)

        self._station.callable_services[0].cancel()

    def estop(self):
        self._station.logger.debug("%s event in %s state", self.estop.__name__, self.name)
        self._station_sm.set_state(self._station_sm.estop_state)

    def estop_ok(self):
        self._station.logger.debug("%s event in %s state", self.estop_ok.__name__, self.name)

    def noconn(self):
        self._station.logger.debug("%s event in %s state", self.noconn.__name__, self.name)
        self._station_sm.set_state(self._station_sm.noconn_state)

    def conn_ok(self):
        self._station.logger.debug("%s event in %s state", self.conn_ok.__name__, self.name)

    def error(self):
        self._station.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._station_sm.set_state(self._station_sm.error_state)

    def acknowledge(self):
        self._station.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._station.logger.debug("%s event in %s state", self.timeout.__name__, self.name)


class Homing(StationState):
    """ Concrete State class for representing Homing State"""
    def __init__(self, station_sm, station, super_sm=None, isSubstate=False):
        super(Homing, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._station_sm = station_sm
        self._station = station
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._station.logger.debug("Entering the %s state", self.name)
        self._station.stationState = "Standby"
        self._station.publisher.publish(topic="StationState", value=self._station.stationState, sender=self._station.name)
        self._station.publisher.publish(topic='StationStateMaintenance', value="Homing",
                                        sender=self._station.name)


        self._station.callable_services[1].execute()

    def initialize(self):
        self._station.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._station_sm.set_state(self._station_sm.initialization_state)

    def initialize_done(self):
        self._station.logger.debug("%s event in %s state", self.initialize_done.__name__, self.name)

    def service1(self):
        self._station.logger.debug("%s event in %s state", self.service1.__name__, self.name)
        self._station.callable_services[1].execute()

    def service1_done(self):
        self._station.logger.debug("%s event in %s state", self.service1_done.__name__, self.name)
        self._station_sm.set_state(self._station_sm.ready_state)

    def service2(self):
        self._station.logger.debug("%s event in %s state", self.service2.__name__, self.name)

    def service2_done(self):
        self._station.logger.debug("%s event in %s state", self.service2_done.__name__, self.name)

    def service3(self):
        self._station.logger.debug("%s event in %s state", self.service3.__name__, self.name)

    def service3_done(self):
        self._station.logger.debug("%s event in %s state", self.service3_done.__name__, self.name)

    def service4(self):
        self._station.logger.debug("%s event in %s state", self.service4.__name__, self.name)

    def service4_done(self):
        self._station.logger.debug("%s event in %s state", self.service4_done.__name__, self.name)

    def service5(self):
        self._station.logger.debug("%s event in %s state", self.service5.__name__, self.name)

    def service5_done(self):
        self._station.logger.debug("%s event in %s state", self.service5_done.__name__, self.name)

    def service6(self):
        self._station.logger.debug("%s event in %s state", self.service6.__name__, self.name)

    def service6_done(self):
        self._station.logger.debug("%s event in %s state", self.service6_done.__name__, self.name)

    def service_cancel(self):
        self._station.logger.debug("%s event in %s state", self.service_cancel.__name__, self.name)

        self._station.callable_services[1].cancel()

    def estop(self):
        self._station.logger.debug("%s event in %s state", self.estop.__name__, self.name)
        self._station_sm.set_state(self._station_sm.estop_state)

    def estop_ok(self):
        self._station.logger.debug("%s event in %s state", self.estop_ok.__name__, self.name)

    def noconn(self):
        self._station.logger.debug("%s event in %s state", self.noconn.__name__, self.name)
        self._station_sm.set_state(self._station_sm.noconn_state)

    def conn_ok(self):
        self._station.logger.debug("%s event in %s state", self.conn_ok.__name__, self.name)

    def error(self):
        self._station.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._station_sm.set_state(self._station_sm.error_state)

    def acknowledge(self):
        self._station.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._station.logger.debug("%s event in %s state", self.timeout.__name__, self.name)


class Ready(StationState):
    """ Concrete State class for representing Ready State"""
    def __init__(self, station_sm, station, super_sm=None, isSubstate=False):
        super(Ready, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._station_sm = station_sm
        self._station = station
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._station.stationState = "Ready"
        self._station.logger.debug("Entering the %s state", self.name)
        self._station.publisher.publish(topic="StationState", value=self._station.stationState, sender=self._station.name)
        self._station.publisher.publish(topic='StationStateMaintenance', value="Ready",
                                        sender=self._station.name)

        # blinking stop
        self._station.blinker.handle_event(event=self._station_sm.blink_stop_event)
        # standby green status LED color
        self._station.status_led.handle_event(event=self._station_sm.green_event)

    def initialize(self):
        self._station.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._station_sm.set_state(self._station_sm.initialization_state)

    def initialize_done(self):
        self._station.logger.debug("%s event in %s state", self.initialize_done.__name__, self.name)

    def service1(self):
        self._station.logger.debug("%s event in %s state", self.service1.__name__, self.name)
        station_state = "Running : {0} service".format(self._station.callable_services[1].service_name)
        self._station.publisher.publish(topic='StationStateMaintenance', value=station_state,
                                        sender=self._station.name)

        try:
            self._station.callable_services[1].execute()
        except KeyError:
            self._station.logger.debug("Service %s s is not registered.", self.service1.__name__, self.name)

        self._station_sm.set_state(self._station_sm.running_state)

    def service1_done(self):
        self._station.logger.debug("%s event in %s state", self.service1_done.__name__, self.name)

    def service2(self):
        self._station.logger.debug("%s event in %s state", self.service2.__name__, self.name)
        station_state = "Running : {0} service".format(self._station.callable_services[2].service_name)
        self._station.publisher.publish(topic='StationStateMaintenance', value=station_state,
                                        sender=self._station.name)

        try:
            self._station.callable_services[2].execute()
        except KeyError:
            self._station.logger.debug("Service %s s is not registered.", self.service2.__name__, self.name)

        self._station_sm.set_state(self._station_sm.running_state)

    def service2_done(self):
        self._station.logger.debug("%s event in %s state", self.service2_done.__name__, self.name)

    def service3(self):
        self._station.logger.debug("%s event in %s state", self.service3.__name__, self.name)
        station_state = "Running : {0} service".format(self._station.callable_services[3].service_name)
        self._station.publisher.publish(topic='StationStateMaintenance', value=station_state,
                                        sender=self._station.name)

        try:
            self._station.callable_services[3].execute()
        except KeyError:
            self._station.logger.debug("Service %s s is not registered.", self.service3.__name__, self.name)

        self._station_sm.set_state(self._station_sm.running_state)

    def service3_done(self):
        self._station.logger.debug("%s event in %s state", self.service3_done.__name__, self.name)

    def service4(self):
        self._station.logger.debug("%s event in %s state", self.service4.__name__, self.name)
        try:
            self._station.callable_services[4].execute()
        except KeyError:
            self._station.logger.debug("Service %s s is not registered.", self.service4.__name__, self.name)

    def service4_done(self):
        self._station.logger.debug("%s event in %s state", self.service4_done.__name__, self.name)

    def service5(self):
        self._station.logger.debug("%s event in %s state", self.service5.__name__, self.name)
        try:
            self._station.callable_services[5].execute()
        except KeyError:
            self._station.logger.debug("Service %s s is not registered.", self.service5.__name__, self.name)

    def service5_done(self):
        self._station.logger.debug("%s event in %s state", self.service5_done.__name__, self.name)

    def service6(self):
        self._station.logger.debug("%s event in %s state", self.service6.__name__, self.name)
        try:
            self._station.callable_services[6].execute()
        except KeyError:
            self._station.logger.debug("Service %s s is not registered.", self.service6.__name__, self.name)

    def service6_done(self):
        self._station.logger.debug("%s event in %s state", self.service6_done.__name__, self.name)

    def service_cancel(self):
        self._station.logger.debug("%s event in %s state", self.service_cancel.__name__, self.name)

        if self._station.callable_services is not None:
            for i in self._station.callable_services:
                self._station.callable_services[i].cancel()  # reset all active services

    def estop(self):
        self._station.logger.debug("%s event in %s state", self.estop.__name__, self.name)
        self._station_sm.set_state(self._station_sm.estop_state)

    def estop_ok(self):
        self._station.logger.debug("%s event in %s state", self.estop_ok.__name__, self.name)

    def noconn(self):
        self._station.logger.debug("%s event in %s state", self.noconn.__name__, self.name)
        self._station_sm.set_state(self._station_sm.noconn_state)

    def conn_ok(self):
        self._station.logger.debug("%s event in %s state", self.conn_ok.__name__, self.name)

    def error(self):
        self._station.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._station_sm.set_state(self._station_sm.error_state)

    def acknowledge(self):
        self._station.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._station.logger.debug("%s event in %s state", self.timeout.__name__, self.name)


class Running(StationState):
    """ Concrete State class for representing Running State"""
    def __init__(self, station_sm, station, super_sm=None, isSubstate=False):
        super(Running, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._station_sm = station_sm
        self._station = station
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._station.stationState = "Running"
        self._station.logger.debug("Entering the %s state", self.name)
        self._station.publisher.publish(topic="StationState", value=self._station.stationState, sender=self._station.name)

        # running yellow LED color
        self._station.status_led.handle_event(event=self._station_sm.yellow_event)

    def initialize(self):
        self._station.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._station_sm.set_state(self._station_sm.initialization_state)

    def initialize_done(self):
        self._station.logger.debug("%s event in %s state", self.initialize_done.__name__, self.name)

    def service1(self):
        self._station.logger.debug("%s event in %s state", self.service1.__name__, self.name)

    def service1_done(self):
        self._station.logger.debug("%s event in %s state", self.service1_done.__name__, self.name)
        self._station_sm.set_state(self._station_sm.ready_state)

    def service2(self):
        self._station.logger.debug("%s event in %s state", self.service2.__name__, self.name)

    def service2_done(self):
        self._station.logger.debug("%s event in %s state", self.service2_done.__name__, self.name)
        self._station_sm.set_state(self._station_sm.ready_state)

    def service3(self):
        self._station.logger.debug("%s event in %s state", self.service3.__name__, self.name)

    def service3_done(self):
        self._station.logger.debug("%s event in %s state", self.service3_done.__name__, self.name)
        self._station_sm.set_state(self._station_sm.ready_state)

    def service4(self):
        self._station.logger.debug("%s event in %s state", self.service4.__name__, self.name)

    def service4_done(self):
        self._station.logger.debug("%s event in %s state", self.service4_done.__name__, self.name)
        self._station_sm.set_state(self._station_sm.ready_state)

    def service5(self):
        self._station.logger.debug("%s event in %s state", self.service5.__name__, self.name)

    def service5_done(self):
        self._station.logger.debug("%s event in %s state", self.service5_done.__name__, self.name)
        self._station_sm.set_state(self._station_sm.ready_state)

    def service6(self):
        self._station.logger.debug("%s event in %s state", self.service6.__name__, self.name)

    def service6_done(self):
        self._station.logger.debug("%s event in %s state", self.service6_done.__name__, self.name)
        self._station_sm.set_state(self._station_sm.ready_state)

    def service_cancel(self):
        self._station.logger.debug("%s event in %s state", self.service_cancel.__name__, self.name)

        self._station.callable_services[1].cancel()
        self._station.callable_services[2].cancel()
        self._station.callable_services[3].cancel()

    def estop(self):
        self._station.logger.debug("%s event in %s state", self.estop.__name__, self.name)
        self._station_sm.set_state(self._station_sm.estop_state)

    def estop_ok(self):
        self._station.logger.debug("%s event in %s state", self.estop_ok.__name__, self.name)

    def noconn(self):
        self._station.logger.debug("%s event in %s state", self.noconn.__name__, self.name)
        self._station_sm.set_state(self._station_sm.noconn_state)

    def conn_ok(self):
        self._station.logger.debug("%s event in %s state", self.conn_ok.__name__, self.name)

    def error(self):
        self._station.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._station_sm.set_state(self._station_sm.error_state)

    def acknowledge(self):
        self._station.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._station.logger.debug("%s event in %s state", self.timeout.__name__, self.name)


class Error(StationState):
    """ Concrete State class for representing Error State"""
    def __init__(self, station_sm, station, super_sm=None, isSubstate=False):
        super(Error, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._station_sm = station_sm
        self._station = station
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._station.stationState = "Error"
        self._station.logger.debug("Entering the %s state", self.name)
        self._station.publisher.publish(topic="StationState", value=self._station.stationState, sender=self._station.name)
        self._station.publisher.publish(topic='StationStateMaintenance', value=self._station.stationState,
                                        sender=self._station.name)

        # ToDo : think if the services should be canceled in this case
        if self._station.callable_services is not None:
            for i in self._station.callable_services:
                self._station.callable_services[i].cancel()  # reset all active services

        # LED red color + stop blinking
        self._station.blinker.handle_event(event=self._station_sm.blink_stop_event)
        self._station.status_led.handle_event(event=self._station_sm.red_event)

        if self._station_sm.noconn:
            self._station_sm.set_state(self._station_sm.noconn_state)

        elif self._station_sm.estop:
            self._station_sm.set_state(self._station_sm.estop_state)

    def initialize(self):
        self._station.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._station_sm.set_state(self._station_sm.initialization_state)

    def initialize_done(self):
        self._station.logger.debug("%s event in %s state", self.initialize_done.__name__, self.name)

    def service1(self):
        self._station.logger.debug("%s event in %s state", self.service1.__name__, self.name)

    def service1_done(self):
        self._station.logger.debug("%s event in %s state", self.service1_done.__name__, self.name)

    def service2(self):
        self._station.logger.debug("%s event in %s state", self.service2.__name__, self.name)

    def service2_done(self):
        self._station.logger.debug("%s event in %s state", self.service2_done.__name__, self.name)

    def service3(self):
        self._station.logger.debug("%s event in %s state", self.service3.__name__, self.name)

    def service3_done(self):
        self._station.logger.debug("%s event in %s state", self.service3_done.__name__, self.name)

    def service4(self):
        self._station.logger.debug("%s event in %s state", self.service4.__name__, self.name)

    def service4_done(self):
        self._station.logger.debug("%s event in %s state", self.service4_done.__name__, self.name)

    def service5(self):
        self._station.logger.debug("%s event in %s state", self.service5.__name__, self.name)

    def service5_done(self):
        self._station.logger.debug("%s event in %s state", self.service5_done.__name__, self.name)

    def service6(self):
        self._station.logger.debug("%s event in %s state", self.service6.__name__, self.name)

    def service6_done(self):
        self._station.logger.debug("%s event in %s state", self.service6_done.__name__, self.name)

    def service_cancel(self):
        self._station.logger.debug("%s event in %s state", self.service_cancel.__name__, self.name)

    def estop(self):
        self._station.logger.debug("%s event in %s state", self.estop.__name__, self.name)
        self._station_sm.set_state(self._station_sm.estop_state)

    def estop_ok(self):
        self._station.logger.debug("%s event in %s state", self.estop_ok.__name__, self.name)

    def noconn(self):
        self._station.logger.debug("%s event in %s state", self.noconn.__name__, self.name)
        self._station_sm.set_state(self._station_sm.noconn_state)

    def conn_ok(self):
        self._station.logger.debug("%s event in %s state", self.conn_ok.__name__, self.name)

    def error(self):
        self._station.logger.debug("%s event in %s state", self.error.__name__, self.name)

    def acknowledge(self):
        self._station.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

        self._station_sm.ack_error()
        self._station_sm.ack_message()

        if self._station_sm.init_required:
            self._station_sm.init_required = False
            self._station_sm.set_state(self._station_sm.notinitialized_state)
        else:
            self._station_sm.set_state(self._station_sm.ready_state)

    def timeout(self):
        self._station.logger.debug("%s event in %s state", self.timeout.__name__, self.name)


class Estop(StationState):
    """ Concrete State class for representing Estop State"""
    def __init__(self, station_sm, station, super_sm=None, isSubstate=False):
        super(Estop, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._station_sm = station_sm
        self._station = station
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._station.stationState = "Error"
        self._station.logger.debug("Entering the %s state", self.name)
        self._station.publisher.publish(topic="StationState", value=self._station.stationState, sender=self._station.name)
        self._station.publisher.publish(topic="StationSafetyState", value="safetySwitchActivated", sender=self._station.name)
        self._station.publisher.publish(topic='StationStateMaintenance', value="Error : E-Stop",
                                        sender=self._station.name)

        # rfid nok status LED red color + blinking
        self._station.blinker.handle_event(event=self._station_sm.blink_start_event)
        self._station.status_led.handle_event(event=self._station_sm.red_event)

        if self._station.callable_services is not None:
            for i in self._station.callable_services:
                self._station.callable_services[i].cancel()  # reset all active services

        self._station_sm.init_required = True

    def initialize(self):
        self._station.logger.debug("%s event in %s state", self.initialize.__name__, self.name)

    def initialize_done(self):
        self._station.logger.debug("%s event in %s state", self.initialize_done.__name__, self.name)

    def service1(self):
        self._station.logger.debug("%s event in %s state", self.service1.__name__, self.name)

    def service1_done(self):
        self._station.logger.debug("%s event in %s state", self.service1_done.__name__, self.name)

    def service2(self):
        self._station.logger.debug("%s event in %s state", self.service2.__name__, self.name)

    def service2_done(self):
        self._station.logger.debug("%s event in %s state", self.service2_done.__name__, self.name)

    def service3(self):
        self._station.logger.debug("%s event in %s state", self.service3.__name__, self.name)

    def service3_done(self):
        self._station.logger.debug("%s event in %s state", self.service3_done.__name__, self.name)

    def service4(self):
        self._station.logger.debug("%s event in %s state", self.service4.__name__, self.name)

    def service4_done(self):
        self._station.logger.debug("%s event in %s state", self.service4_done.__name__, self.name)

    def service5(self):
        self._station.logger.debug("%s event in %s state", self.service5.__name__, self.name)

    def service5_done(self):
        self._station.logger.debug("%s event in %s state", self.service5_done.__name__, self.name)

    def service6(self):
        self._station.logger.debug("%s event in %s state", self.service6.__name__, self.name)

    def service6_done(self):
        self._station.logger.debug("%s event in %s state", self.service6_done.__name__, self.name)

    def service_cancel(self):
        self._station.logger.debug("%s event in %s state", self.service_cancel.__name__, self.name)

    def estop(self):
        self._station.logger.debug("%s event in %s state", self.estop.__name__, self.name)

    def estop_ok(self):
        self._station.logger.debug("%s event in %s state", self.estop.__name__, self.name)
        self._station_sm.set_state(self._station_sm.error_state)
        self._station.publisher.publish(topic="StationSafetyState", value="safetySwitchNotActivated",
                                        sender=self._station.name)

        self._station_sm.estop = False

        self._station_sm.set_state(self._station_sm.error_state)

    def noconn(self):
        self._station.logger.debug("%s event in %s state", self.noconn.__name__, self.name)
        # self._station_sm.set_state(self._station_sm.noconn_state)
        self._station_sm.noconn = True

    def conn_ok(self):
        self._station.logger.debug("%s event in %s state", self.conn_ok.__name__, self.name)
        self._station_sm.noconn = False

    def error(self):
        self._station.logger.debug("%s event in %s state", self.error.__name__, self.name)

    def acknowledge(self):
        self._station.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._station.logger.debug("%s event in %s state", self.timeout.__name__, self.name)


class NoConnection(StationState):
    """ Concrete State class for representing NoConnection State"""
    def __init__(self, station_sm, station, super_sm=None, isSubstate=False):
        super(NoConnection, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._station_sm = station_sm
        self._station = station
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._station.stationState = "NoConnection"
        self._station.logger.debug("Entering the %s state", self.name)
        self._station.publisher.publish(topic="StationState", value=self._station.stationState,
                                        sender=self._station.name)
        self._station.publisher.publish(topic='StationStateMaintenance', value=self._station.stationState,
                                        sender=self._station.name)

        # error red status LED color + blinking
        self._station.blinker.handle_event(event=self._station_sm.blink_start_event)
        self._station.status_led.handle_event(event=self._station_sm.red_event)

        if self._station.callable_services is not None:
            for i in self._station.callable_services:
                self._station.callable_services[i].cancel()  # reset all active services

        self._station_sm.init_required = True

    def initialize(self):
        self._station.logger.debug("%s event in %s state", self.initialize.__name__, self.name)

    def initialize_done(self):
        self._station.logger.debug("%s event in %s state", self.initialize_done.__name__, self.name)

    def service1(self):
        self._station.logger.debug("%s event in %s state", self.service1.__name__, self.name)

    def service1_done(self):
        self._station.logger.debug("%s event in %s state", self.service1_done.__name__, self.name)

    def service2(self):
        self._station.logger.debug("%s event in %s state", self.service2.__name__, self.name)

    def service2_done(self):
        self._station.logger.debug("%s event in %s state", self.service2_done.__name__, self.name)

    def service3(self):
        self._station.logger.debug("%s event in %s state", self.service3.__name__, self.name)

    def service3_done(self):
        self._station.logger.debug("%s event in %s state", self.service3_done.__name__, self.name)

    def service4(self):
        self._station.logger.debug("%s event in %s state", self.service4.__name__, self.name)

    def service4_done(self):
        self._station.logger.debug("%s event in %s state", self.service4_done.__name__, self.name)

    def service5(self):
        self._station.logger.debug("%s event in %s state", self.service5.__name__, self.name)

    def service5_done(self):
        self._station.logger.debug("%s event in %s state", self.service5_done.__name__, self.name)

    def service6(self):
        self._station.logger.debug("%s event in %s state", self.service6.__name__, self.name)

    def service6_done(self):
        self._station.logger.debug("%s event in %s state", self.service6_done.__name__, self.name)

    def service_cancel(self):
        self._station.logger.debug("%s event in %s state", self.service_cancel.__name__, self.name)

    def estop(self):
        self._station.logger.debug("%s event in %s state", self.estop.__name__, self.name)

        self._station_sm.estop = True

    def estop_ok(self):
        self._station.logger.debug("%s event in %s state", self.estop.__name__, self.name)

        self._station_sm.estop = False

    def noconn(self):
        self._station.logger.debug("%s event in %s state", self.noconn.__name__, self.name)

    def conn_ok(self):
        self._station.logger.debug("%s event in %s state", self.conn_ok.__name__, self.name)

        self._station_sm.noconn = False
        self._station_sm.set_state(self._station_sm.error_state)

    def error(self):
        self._station.logger.debug("%s event in %s state", self.error.__name__, self.name)

    def acknowledge(self):
        self._station.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._station.logger.debug("%s event in %s state", self.timeout.__name__, self.name)


class StationStateMachine(object):
    """ Context class for the Station's state machine """
    def __init__(self, station, homing_required):
        self._name = self.__class__.__name__

        self._station = station
        self._homing_required = homing_required

        self.estop = False
        self.noconn = False

        #events:
        self.purple_event = events.RGBLEDInputEvent(eventID=events.RGBLEDInputEvents.Purple, sender=self._station.name)
        self.green_event = events.RGBLEDInputEvent(eventID=events.RGBLEDInputEvents.Green, sender=self._station.name)
        self.red_event = events.RGBLEDInputEvent(eventID=events.RGBLEDInputEvents.Red, sender=self._station.name)
        self.yellow_event = events.RGBLEDInputEvent(eventID=events.RGBLEDInputEvents.Yellow, sender=self._station.name)
        self.ledoff_event = events.RGBLEDInputEvent(eventID=events.RGBLEDInputEvents.Off, sender=self._station.name)
        self.blink_start_event = events.BlinkerEvent(eventID=events.BlinkerEvents.Start, sender=self._station.name)
        self.blink_stop_event = events.BlinkerEvent(eventID=events.BlinkerEvents.Stop, sender=self._station.name)

        #states
        self._starting_state = Starting(self, self._station)
        self._notinitialized_state = NotInitialized(self, self._station) # an instance for tracking current state
        self._initialization_state = Initialization(self, self._station)
        self._homing_state = Homing(self, self._station)
        self._ready_state = Ready(self, self._station)
        self._running_state = Running(self, self._station)
        self._estop_state = Estop(self, self._station)
        self._noconn_state = NoConnection(self, self._station)
        self._error_state = Error(self, self._station)  # rack's states instances

        self._current_state = self._starting_state
        self.set_state(self._current_state)

        self.init_required = False  # to show that an estop has happened and init is needed

    # properties
    @property
    def current_state(self):
        return self._current_state

    @property
    def name(self):
        return self._name

    @property
    def starting_state(self):
        return self._starting_state

    @property
    def notinitialized_state(self):
        return self._notinitialized_state

    @property
    def initialization_state(self):
        return self._initialization_state

    @property
    def homing_state(self):
        return self._homing_state

    @property
    def ready_state(self):
        return self._ready_state

    @property
    def running_state(self):
        return self._running_state

    @property
    def error_state(self):
        return self._error_state

    @property
    def estop_state(self):
        return self._estop_state

    @property
    def noconn_state(self):
        return self._noconn_state

    def set_state(self, state):
        self._station.logger.debug("Switching from state %s to state %s", self.current_state.name, state.name)

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

    def ack_error(self):
        # erase an error
        error_code = error_codes.StationErrorCodes.NoError
        self._station.publisher.publish(topic="StationErrorCode",
                                        value=hex(error_code),
                                        sender=self._station.name)
        error_description = error_codes.code_to_text[error_code]
        self._station.publisher.publish(topic="StationErrorDescription",
                                        value=error_description,
                                        sender=self._station.name)
        # propagate ACK to the others
        self._station.publisher.publish(topic="Ack", value=True, sender=self._station.name)

    def ack_message(self):
        # erase a message
        messsage_code = message_codes.StationMessageCodes.NoMessages
        self._station.publisher.publish(topic="StationMessageCode",
                                        value=hex(messsage_code),
                                        sender=self._station.name)
        message_description = message_codes.code_to_text[messsage_code]
        self._station.publisher.publish(topic="StationMessageDescription",
                                        value=message_description,
                                        sender=self._station.name)

    def publish_error(self, error_code):
        self._station.publisher.publish(topic="StationErrorCode",
                                                value=hex(error_code),
                                                sender=self._station.name)
        self._station.publisher.publish(topic="StationErrorDescription",
                                                value=error_codes.code_to_text[error_code],
                                                sender=self._station.name)

    def publish_message(self, message_code):
        self._station.publisher.publish(topic="StationMessageCode",
                                                value=hex(message_code),
                                                sender=self._station.name)
        self._station.publisher.publish(topic="StationMessageDescription",
                                                value=message_codes.code_to_text[message_code],
                                                sender=self._station.name)

    def dispatch(self, *args, **kwargs):

        self._station.logger.debug("%s has received a message: %s", self.name, kwargs)

        try:
            topic = kwargs["topic"]
            value = kwargs["value"]
            sender = kwargs["sender"]

            if sender == "SafetySwitch":

                if topic == "Value":
                    if value:
                        self._current_state.estop()
                    else:
                        self._current_state.estop_ok()

            elif topic == "State":
                if value == "Error":
                    self._current_state.error()
                elif value == "ErrorWithInit":
                    self.init_required = True
                    self._current_state.error()
                elif value == "NotInitialized":
                    pass
                    # self._current_state.error()
                elif value == "Initialized":
                    pass

        except KeyError:
            event = kwargs["event"]

            if event.eventID == events.StationEvents.Initialize:  # this a part of the service generic interface
                self._current_state.initialize()
            elif event.eventID == events.StationEvents.Assemble:
                self._current_state.service1()
            elif event.eventID == events.StationEvents.Ack:
                self._current_state.acknowledge()

            elif event.eventID == events.StationEvents.Done:
                if event.service_index == 0:
                    self._current_state.initialize_done()
                elif event.service_index == 1:
                    self._current_state.service1_done()
                elif event.service_index == 2:
                    pass
                elif event.service_index == 3:
                    pass
                elif event.service_index == 4:
                    pass
                elif event.service_index == 5:
                    pass
                elif event.service_index == 6:
                    pass

            elif event.eventID == events.StationEvents.Error:
                if event.init_required:
                    self.init_required = True
                self._current_state.error()
            elif event.eventID == events.StationEvents.NoConn:
                self._current_state.noconn()
            elif event.eventID == events.StationEvents.ConnOk:
                self._current_state.conn_ok()
            elif event.eventID == events.StationEvents.FatalError:
                self.publish_error(error_code=error_codes.StationErrorCodes.FatalError)
                self._current_state.estop()
            elif event.eventID == events.StationEvents.NoEvent:
                self._station.logger.debug("Empty event : %s", event)
            else:
                self._station.logger.debug("Unknown event : %s", event)
