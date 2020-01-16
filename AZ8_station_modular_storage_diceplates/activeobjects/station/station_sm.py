import abc
from communication import events
from utils import error_codes, message_codes

class StationState(metaclass=abc.ABCMeta):
    """ Abstract State class for a Station SM """

    init_after_estop = False

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
        self._station.publisher.publish(topic="StationState", value="Starting", sender=self._station.name)

        # standby purple LED color
        standby_led_event = events.RGBLEDInputEvent(events.RGBLEDInputEvents.Purple, self._station.name)
        self._station.status_led.handle_event(event=standby_led_event)
        # blinking
        led_blinking_start = events.BlinkerEvent(events.BlinkerEvents.Start, self._station.name)
        self._station.blinker.handle_event(event=led_blinking_start)

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

    def estop(self):
        self._station.logger.debug("%s event in %s state", self.estop.__name__, self.name)
        self._station_sm.set_state(self._station_sm.estop_state)

    def estop_ok(self):
        self._station.logger.debug("%s event in %s state", self.estop_ok.__name__, self.name)

    def error(self):
        self._station.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._station_sm.set_state(self._station.error_state)

    def noconn(self):
        self._station.logger.debug("%s event in %s state", self.noconn.__name__, self.name)
        self._station_sm.set_state(self._station_sm.noconn_state)

    def conn_ok(self):
        self._station.logger.debug("%s event in %s state", self.conn_ok.__name__, self.name)
        self._station_sm.set_state(self._station_sm.notinitialized_state)

    def acknowledge(self):
        self._station.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)
        self._station.publisher.publish(topic="Ack", value=True, sender=self._station.name)

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
        self._station.publisher.publish(topic="StationState", value="Standby", sender=self._station.name)

        led_blinking_stop = events.BlinkerEvent(events.BlinkerEvents.Stop, self._station.name)
        self._station.blinker.handle_event(event=led_blinking_stop)

        # standby purple LED color
        standby_led_event = events.RGBLEDInputEvent(events.RGBLEDInputEvents.Purple, self._station.name)
        self._station.status_led.handle_event(event=standby_led_event)

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
        self._station_sm.set_state(self._station_sm.notinitialized_state)		
		
    def error(self):
        self._station.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._station.set_state(self._station.error_state)

    def acknowledge(self):
        self._station.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)
        self._station.publisher.publish(topic="Ack", value=True, sender=self._station.name)

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
        self._station.publisher.publish(topic="StationState", value="Standby", sender=self._station.name)

        self._station.callable_services[1].cancel()
        self._station.callable_services[2].cancel()

        # standby purple LED color
        standby_led_event = events.RGBLEDInputEvent(events.RGBLEDInputEvents.Purple, self._station.name)
        self._station.status_led.handle_event(event=standby_led_event)
		
        try:
            self._station.callable_services[0].execute()
        except KeyError as e:
            self._station.logger.error("No registered initialization service found. Error: %s", e)
            self._station_sm.set_state(self._station_sm.error_state)

    def initialize(self):
        self._station.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._station_sm.set_state(self._station_sm.initialization_state)

    def initialize_done(self):
        self._station.logger.debug("%s event in %s state", self.initialize_done.__name__, self.name)
        self._station_sm.set_state(self._station_sm.ready_state)
		
    def service1(self):
        self._station.logger.debug("%s event in %s state", self.service1.__name__, self.name)

    def service1_done(self):
        self._station.logger.debug("%s event in %s state", self.service1_done.__name__, self.name)

    def service2(self):
        self._station.logger.debug("%s event in %s state", self.service2.__name__, self.name)
        self._station_sm.set_state(self._station_sm.initialization_state)

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
        self._station.publisher.publish(topic="Ack", value=True, sender=self._station.name)

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
        self._station.publisher.publish(topic="StationState", value="Ready", sender=self._station.name)
		
        # ready green LED color
        ready_led_event = events.RGBLEDInputEvent(events.RGBLEDInputEvents.Green, self._station.name)
        self._station.status_led.handle_event(event=ready_led_event)
		
    def initialize(self):
        self._station.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._station_sm.set_state(self._station_sm.initialization_state)

    def initialize_done(self):
        self._station.logger.debug("%s event in %s state", self.initialize_done.__name__, self.name)

    def service1(self, parameters_list=None):
        self._station.logger.debug("%s event in %s state with parameters %s", self.service1.__name__, self.name, parameters_list)

        try:
			# Just give the execute with params to the generic service
            self._station.callable_services[1].execute(parameters_list=parameters_list)
            self._station_sm.set_state(self._station_sm.running_state)
        except KeyError as e:
            self._station.logger.error("No registered service1 service found. Error: %s", e)
            self._station_sm.set_state(self._station_sm.error_state)

    def service1_done(self):
        self._station.logger.debug("%s event in %s state", self.service1_done.__name__, self.name)

    def service2(self, parameters_list=None, service_process=None):
        self._station.logger.debug("%s event in %s state with parameters %s", self.service2.__name__, self.name, parameters_list)

        try:
			# Just give the execute with params to the generic service
            self._station.callable_services[2].execute(parameters_list=parameters_list, service_process=service_process)
            self._station_sm.set_state(self._station_sm.running_state)
        except KeyError as e:
            self._station.logger.error("No registered service2 service found. Error: %s", e)
            self._station_sm.set_state(self._station_sm.error_state)

    def service2_done(self):
        self._station.logger.debug("%s event in %s state", self.service2_done.__name__, self.name)

    def service3(self):
        self._station.logger.debug("%s event in %s state", self.service3.__name__, self.name)
        self._station_sm.set_state(self._station_sm.running_state)

        self._station.callable_services[3].execute()

    def service3_done(self):
        self._station.logger.debug("%s event in %s state", self.service3_done.__name__, self.name)

    def service4(self):
        self._station.logger.debug("%s event in %s state", self.service4.__name__, self.name)
        self._station_sm.set_state(self._station_sm.running_state)

        try:
            self._station.callable_services[4].execute()
        except KeyError as e:
            self._station.logger.error("No registered service found. Error: %s", e)
            self._station_sm.set_state(self._station_sm.error_state)

    def service4_done(self):
        self._station.logger.debug("%s event in %s state", self.service4_done.__name__, self.name)

    def service5(self):
        self._station.logger.debug("%s event in %s state", self.service5.__name__, self.name)
        self._station_sm.set_state(self._station_sm.running_state)

        try:
            self._station.callable_services[5].execute()
        except KeyError as e:
            self._station.logger.error("No registered service found. Error: %s", e)
            self._station_sm.set_state(self._station_sm.error_state)

    def service5_done(self):
        self._station.logger.debug("%s event in %s state", self.service5_done.__name__, self.name)

    def service6(self):
        self._station.logger.debug("%s event in %s state", self.service6.__name__, self.name)
        self._station_sm.set_state(self._station_sm.running_state)

        try:
            self._station.callable_services[6].execute()
        except KeyError as e:
            self._station.logger.error("No registered service found. Error: %s", e)
            self._station_sm.set_state(self._station_sm.error_state)

    def service6_done(self):
        self._station.logger.debug("%s event in %s state", self.service6_done.__name__, self.name)


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
        self._station.publisher.publish(topic="Ack", value=True, sender=self._station.name)

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
        self._station.publisher.publish(topic="StationState", value="Running", sender=self._station.name)

        # running yellow LED color
        running_led_event = events.RGBLEDInputEvent(events.RGBLEDInputEvents.Yellow, self._station.name)
        self._station.status_led.handle_event(event=running_led_event)

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
        self._station.publisher.publish(topic="Ack", value=True, sender=self._station.name)

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

        # ToDo : think if the services should be canceled in this case
        self._station.callable_services[0].cancel()
        self._station.callable_services[1].cancel()
        self._station.callable_services[2].cancel()

        # stop blinking
        led_blinking_stop = events.BlinkerEvent(events.BlinkerEvents.Stop, self._station.name)
        self._station.blinker.handle_event(event=led_blinking_stop)

        # error red LED color
        error_led_event = events.RGBLEDInputEvent(events.RGBLEDInputEvents.Red, self._station.name)
        self._station.status_led.handle_event(event=error_led_event)

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
        self._station.publisher.publish(topic="StationState", value="Error", sender=self._station.name)
        self._station.publisher.publish(topic="StationSafetyState", value="safetySwitchActivated", sender=self._station.name)

        # error red LED color
        error_led_event = events.RGBLEDInputEvent(events.RGBLEDInputEvents.Red, self._station.name)
        self._station.status_led.handle_event(event=error_led_event)

        self._station.callable_services[1].cancel()
        self._station.callable_services[2].cancel()

        self._station_sm.init_after_estop = True

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

    def estop(self):
        self._station.logger.debug("%s event in %s state", self.estop.__name__, self.name)

    def estop_ok(self):
        self._station.logger.debug("%s event in %s state", self.estop.__name__, self.name)
        self._station_sm.set_state(self._station_sm.error_state)
        self._station.publisher.publish(topic="StationSafetyState", value="safetySwitchNotActivated",
                                        sender=self._station.name)

    def noconn(self):
        self._station.logger.debug("%s event in %s state", self.noconn.__name__, self.name)

    def conn_ok(self):
        self._station.logger.debug("%s event in %s state", self.conn_ok.__name__, self.name)										
										
    def error(self):
        self._station.logger.debug("%s event in %s state", self.error.__name__, self.name)

    def acknowledge(self):
        self._station.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)
        self._station.publisher.publish(topic="Ack", value=True, sender=self._station.name)

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
        self._station.logger.debug("Entering the %s state", self.name)
        self._station.publisher.publish(topic="StationState", value=self._station.stationState, sender=self._station.name)

        # error red LED color
        error_led_event = events.RGBLEDInputEvent(events.RGBLEDInputEvents.Red, self._station.name)
        self._station.status_led.handle_event(event=error_led_event)
        led_blinking_start = events.BlinkerEvent(events.BlinkerEvents.Start, self._station.name)
        self._station.blinker.handle_event(event=led_blinking_start)

        self._station.callable_services[0].cancel()
        self._station.callable_services[1].cancel()
        self._station.callable_services[2].cancel()

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

    def estop(self):
        self._station.logger.debug("%s event in %s state", self.estop.__name__, self.name)
        led_blinking_stop = events.BlinkerEvent(events.BlinkerEvents.Stop, self._station.name)
        self._station.blinker.handle_event(event=led_blinking_stop)
        self._station_sm.set_state(self._station_sm.estop_state)

    def estop_ok(self):
        self._station.logger.debug("%s event in %s state", self.estop.__name__, self.name)
        self._station_sm.set_state(self._station_sm.error_state)
        self._station.publisher.publish(topic="StationSafetyState", value="safetySwitchNotActivated",
                                        sender=self._station.name)

    def noconn(self):
        self._station.logger.debug("%s event in %s state", self.noconn.__name__, self.name)

    def conn_ok(self):
        self._station.logger.debug("%s event in %s state", self.conn_ok.__name__, self.name)
        self._station_sm.set_state(self._station_sm.error_state)

        led_blinking_stop = events.BlinkerEvent(events.BlinkerEvents.Stop, self._station.name)
        self._station.blinker.handle_event(event=led_blinking_stop)

    def error(self):
        self._station.logger.debug("%s event in %s state", self.error.__name__, self.name)

    def acknowledge(self):
        self._station.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

        self._station_sm.noconn = False
        self._station_sm.set_state(self._station_sm.error_state)

    def timeout(self):
        self._station.logger.debug("%s event in %s state", self.timeout.__name__, self.name)
		
		
class StationStateMachine(object):
    """ Context class for the Station's state machine """
    def __init__(self, station):
        self._name = self.__class__.__name__

        self._starting_state = Starting(self, station)		
        self._notinitialized_state = NotInitialized(self, station) # an instance for tracking current state
        self._initialization_state = Initialization(self, station)
        self._ready_state = Ready(self, station)
        self._running_state = Running(self, station)
        self._estop_state = Estop(self, station)
        self._noconn_state = NoConnection(self, station)
        self._error_state = Error(self, station)  # rack's states instances

        self._station = station
        self.noconn = False

        self._current_state = self._starting_state
        self.set_state(self._current_state)

        self.init_required = False #  to show that an estop has happened and init is needed		
		
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
                    elif value == "NotInitialized":
                        self._current_state.error()
                    elif value == "Initialized":
                        pass

            elif topic == "State":

                if value == "Error":
                    self._current_state.error()

        # Usage of sendername parameter from config-file (AZ8_OPCUA_Server)
		# Dispatch in objects state machine works like "ActualStateClass.NewStateMethod"
		# In case of initialization: self._current_state = self._notinitialized_state					
					
        except KeyError:
            event = kwargs["event"]
			
			# Events from StorageStationInputEvent
			
            if event.eventID == self._station.input_events.eventIDs.Initialize:  # this a part of the service generic interface
                self._current_state.initialize()
				
			# OPCUA parameters list is set in event "StorageStationInputEvent"
            elif event.eventID == self._station.input_events.eventIDs.ProvideMaterial:
                self._current_state.service1(parameters_list=event.parameters_list)
				
            elif event.eventID == self._station.input_events.eventIDs.RefillMaterial:
                self._current_state.service2(parameters_list=event.parameters_list, service_process=event.eventID)

            elif event.eventID == self._station.input_events.eventIDs.ResetMaterial:
                self._current_state.service2(parameters_list=event.parameters_list, service_process=event.eventID)				
				
            elif event.eventID == self._station.input_events.eventIDs.Ack:
                self.ack_error()
                self.ack_message()
                self._current_state.acknowledge()
				
            elif event.eventID == self._station.input_events.eventIDs.Done:
                if event.service_index == 0:
                    self._current_state.initialize_done()
                elif event.service_index == 1:
                    self._current_state.service1_done()
                elif event.service_index == 2:
                    self._current_state.service2_done()
                elif event.service_index == 3:
                    self._current_state.service3_done()
                elif event.service_index == 4:
                    pass
                elif event.service_index == 5:
                    pass
                elif event.service_index == 6:
                    pass
					
            elif event.eventID == self._station.input_events.eventIDs.Error:
                self._current_state.error()
            elif event.eventID == self._station.input_events.eventIDs.NoConn:
                self._current_state.noconn()
            elif event.eventID == self._station.input_events.eventIDs.ConnOk:
                self._current_state.conn_ok()
            else:
                self._station.logger.debug("Unknown event : %s", event)
