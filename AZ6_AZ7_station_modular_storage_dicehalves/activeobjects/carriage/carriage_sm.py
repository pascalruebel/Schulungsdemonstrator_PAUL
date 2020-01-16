import abc
from communication import events
from utils.monitoring_timer import MonitoringTimer
from utils import error_codes, message_codes
import config

class CarriageState(metaclass=abc.ABCMeta):
    """ Abstract State class for a CarriageState SM """

    def __init__(self, isSubstate=False):
        self._isSubstate = isSubstate

    @property
    def isSubstate(self):
        return self._isSubstate

    # events for super states
    @abc.abstractmethod
    def initialize(self):
        """ Initialize all the objects in the carriage"""
        raise NotImplemented

    @abc.abstractmethod
    def stop(self):
        """ Stop the carriage's motor """
        raise NotImplemented

    @abc.abstractmethod
    def move_to_front(self):
        """ Move the carriage to the front position """
        raise NotImplemented

    @abc.abstractmethod
    def move_to_rack(self):
        """ Move the carriage to the rack position """
        raise NotImplemented

    @abc.abstractmethod
    def front_sensor_negedge(self):
        """ Negative edge event from the front sensor -> out of position """
        raise NotImplemented

    @abc.abstractmethod
    def rack_sensor_negedge(self):
        """ Negative edge event from the rack sensor -> out of position """
        raise NotImplemented

    @abc.abstractmethod
    def front_sensor_posedge(self):
        """ Positive edge event from the front sensor -> carriage is in front pos """
        raise NotImplemented

    @abc.abstractmethod
    def rack_sensor_posedge(self):
        """ Positive edge event from the rack sensor -> carriage is in rack pos """
        raise NotImplemented

    @abc.abstractmethod
    def motor_on(self):
        """ Motor ON event from the motor -> carriage has started the movement """
        raise NotImplemented

    @abc.abstractmethod
    def motor_off(self):
        """ Motor OFF event from the motor -> carriage has stopped """
        raise NotImplemented

    @abc.abstractmethod
    def error(self):
        """ Error event has occurred"""
        raise NotImplemented

    @abc.abstractmethod
    def acknowledge(self):
        """ Ack an error"""
        raise NotImplemented

    @abc.abstractmethod
    def timeout(self, *args, **kwargs):
        raise NotImplemented

    # events for init sub states
    @abc.abstractmethod
    def front_sensor_init(self):
        raise NotImplemented

    @abc.abstractmethod
    def rack_sensor_init(self):
        raise NotImplemented

    @abc.abstractmethod
    def motor_init(self):
        raise NotImplemented

    @abc.abstractmethod
    def update(self):
        raise NotImplemented

    # enter/exit actions (UML specification)
    def enter_action(self):
        pass

    def exit_action(self):
        pass


class NotInitialized(CarriageState):
    """ Concrete State class for a NotInitialized SM """

    def __init__(self, carriage_sm, carriage, super_sm=None, isSubstate=False):
        super(NotInitialized, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._carriage_sm = carriage_sm
        self._carriage = carriage
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._carriage.publisher.publish(topic="State", value="NotInitialized", sender=self._carriage.name)
        self._carriage.publisher.publish(topic="CarriageState", value="NotInitialized", sender=self._carriage.name)

    def initialize(self):
        self._carriage.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._carriage_sm.set_state(self._carriage_sm.initialization_state)

    def stop(self):
        self._carriage.logger.debug("%s event in %s state", self.stop.__name__, self.name)

    def move_to_front(self):
        self._carriage.logger.debug("%s event in %s state", self.move_to_front.__name__, self.name)

    def move_to_rack(self):
        self._carriage.logger.debug("%s event in %s state", self.move_to_rack.__name__, self.name)

    def front_sensor_negedge(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_negedge.__name__, self.name)

    def rack_sensor_negedge(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_negedge.__name__, self.name)

    def front_sensor_posedge(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_posedge.__name__, self.name)

    def rack_sensor_posedge(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_posedge.__name__, self.name)

    def motor_on(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_on.__name__, self.name)

    def motor_off(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_off.__name__, self.name)

    def error(self):
        self._carriage.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._carriage_sm.set_state(self._carriage_sm.error_state)

    def acknowledge(self):
        self._carriage.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self, *args, **kwargs):
        self._carriage.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def front_sensor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_init.__name__, self.name)

    def rack_sensor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_init.__name__, self.name)

    def motor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_init.__name__, self.name)

    def update(self):
        self._carriage.logger.debug("%s event in %s state", self.update.__name__, self.name)


class Initialization(CarriageState):
    """ Concrete State class for representing Initialization State. This is a composite state. """

    def __init__(self, carriage_sm, carriage, super_sm=None, isSubstate=False):
        super(Initialization, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._carriage_sm = carriage_sm
        self._carriage = carriage
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._carriage.logger.debug("Entering the %s state", self.name)
        self._carriage.publisher.publish(topic="State", value="Initializing", sender=self._carriage.name)
        self._carriage.publisher.publish(topic="CarriageState", value="Initializing", sender=self._carriage.name)

        # stop monitoring timers if they are alive
        if self._carriage_sm.movetofront_timeout_timer.timer_alive():
            self._carriage_sm.movetofront_timeout_timer.cancel()
        if self._carriage_sm.movetorack_timeout_timer.timer_alive():
            self._carriage_sm.movetorack_timeout_timer.cancel()

        # initialize sensors and motor
        self._carriage.frontSensor.handle_event(event=self._carriage_sm.sensor_init_event)
        self._carriage.rackSensor.handle_event(event=self._carriage_sm.sensor_init_event)
        self._carriage.motor.handle_event(event=self._carriage_sm.motor_init_event)

        self._carriage_sm.set_state(self._carriage_sm.allnotinitialized_state)

    def initialize(self):
        self._carriage.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._carriage_sm.set_state(self._carriage_sm.initialization_state)

    def stop(self):
        self._carriage.logger.debug("%s event in %s state", self.stop.__name__, self.name)

    def move_to_front(self):
        self._carriage.logger.debug("%s event in %s state", self.move_to_front.__name__, self.name)

    def move_to_rack(self):
        self._carriage.logger.debug("%s event in %s state", self.move_to_rack.__name__, self.name)

    def front_sensor_negedge(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_negedge.__name__, self.name)

    def rack_sensor_negedge(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_negedge.__name__, self.name)

    def front_sensor_posedge(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_posedge.__name__, self.name)

    def rack_sensor_posedge(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_posedge.__name__, self.name)

    def motor_on(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_on.__name__, self.name)

    def motor_off(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_off.__name__, self.name)

    def error(self):
        self._carriage.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._carriage_sm.set_state(self._carriage_sm.error_state)

    def acknowledge(self):
        self._carriage.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self, *args, **kwargs):
        self._carriage.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def front_sensor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_init.__name__, self.name)

    def rack_sensor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_init.__name__, self.name)

    def motor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_init.__name__, self.name)

    def update(self):
        self._carriage.logger.debug("%s event in %s state", self.update.__name__, self.name)


class NothingIsInitialized(CarriageState):
    """ Concrete State class for representing Init Substate : NothingIsInitialized """

    def __init__(self, carriage_sm, carriage, super_sm=None, isSubstate=False):
        super(NothingIsInitialized, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._carriage_sm = carriage_sm
        self._carriage = carriage
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._carriage.publisher.publish(topic="CarriageState", value="Init: Nothing", sender=self._carriage.name)

    def initialize(self):
        self._carriage.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._super_sm.initialize()

    def stop(self):
        self._carriage.logger.debug("%s event in %s state", self.stop.__name__, self.name)

    def move_to_front(self):
        self._carriage.logger.debug("%s event in %s state", self.move_to_front.__name__, self.name)

    def move_to_rack(self):
        self._carriage.logger.debug("%s event in %s state", self.move_to_rack.__name__, self.name)

    def front_sensor_negedge(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_negedge.__name__, self.name)

    def rack_sensor_negedge(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_negedge.__name__, self.name)

    def front_sensor_posedge(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_posedge.__name__, self.name)

    def rack_sensor_posedge(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_posedge.__name__, self.name)

    def motor_on(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_on.__name__, self.name)

    def motor_off(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_off.__name__, self.name)

    def error(self):
        self._carriage.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._super_sm.error()

    def acknowledge(self):
        self._carriage.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self, *args, **kwargs):
        self._carriage.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def front_sensor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_init.__name__, self.name)
        self._carriage_sm.set_state(self._carriage_sm.frontsensorinit_state)

    def rack_sensor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_init.__name__, self.name)
        self._carriage_sm.set_state(self._carriage_sm.racksensorinit_state)

    def motor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_init.__name__, self.name)
        self._carriage_sm.set_state(self._carriage_sm.motorsensorinit_state)

    def update(self):
        self._carriage.logger.debug("%s event in %s state", self.update.__name__, self.name)


class FrontSensorInit(CarriageState):
    """ Concrete State class for representing Init Substate : FrontSensorInit """

    def __init__(self, carriage_sm, carriage, super_sm=None, isSubstate=False):
        super(FrontSensorInit, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._carriage_sm = carriage_sm
        self._carriage = carriage
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    def enter_action(self):
        self._carriage.publisher.publish(topic="CarriageState", value="Init: FS", sender=self._carriage.name)

    @property
    def super_sm(self):
        return self._super_sm

    def initialize(self):
        self._carriage.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._super_sm.initialize()

    def stop(self):
        self._carriage.logger.debug("%s event in %s state", self.stop.__name__, self.name)

    def move_to_front(self):
        self._carriage.logger.debug("%s event in %s state", self.move_to_front.__name__, self.name)

    def move_to_rack(self):
        self._carriage.logger.debug("%s event in %s state", self.move_to_rack.__name__, self.name)

    def front_sensor_negedge(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_negedge.__name__, self.name)

    def rack_sensor_negedge(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_negedge.__name__, self.name)

    def front_sensor_posedge(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_posedge.__name__, self.name)

    def rack_sensor_posedge(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_posedge.__name__, self.name)

    def motor_on(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_on.__name__, self.name)

    def motor_off(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_off.__name__, self.name)

    def error(self):
        self._carriage.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._super_sm.error()

    def acknowledge(self):
        self._carriage.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self, *args, **kwargs):
        self._carriage.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def front_sensor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_init.__name__, self.name)

    def rack_sensor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_init.__name__, self.name)
        self._carriage_sm.set_state(self._carriage_sm.frontracksensorsinit_state)

    def motor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_init.__name__, self.name)
        self._carriage_sm.set_state(self._carriage_sm.motorfrontsensorinit_state)

    def update(self):
        self._carriage.logger.debug("%s event in %s state", self.update.__name__, self.name)


class RackSensorInit(CarriageState):
    """ Concrete State class for representing Init Substate : RackSensorInit """

    def __init__(self, carriage_sm, carriage, super_sm=None, isSubstate=False):
        super(RackSensorInit, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._carriage_sm = carriage_sm
        self._carriage = carriage
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._carriage.publisher.publish(topic="CarriageState", value="Init: RS", sender=self._carriage.name)

    def initialize(self):
        self._carriage.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._super_sm.initialize()

    def stop(self):
        self._carriage.logger.debug("%s event in %s state", self.stop.__name__, self.name)

    def move_to_front(self):
        self._carriage.logger.debug("%s event in %s state", self.move_to_front.__name__, self.name)

    def move_to_rack(self):
        self._carriage.logger.debug("%s event in %s state", self.move_to_rack.__name__, self.name)

    def front_sensor_negedge(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_negedge.__name__, self.name)

    def rack_sensor_negedge(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_negedge.__name__, self.name)

    def front_sensor_posedge(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_posedge.__name__, self.name)

    def rack_sensor_posedge(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_posedge.__name__, self.name)

    def motor_on(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_on.__name__, self.name)

    def motor_off(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_off.__name__, self.name)

    def error(self):
        self._carriage.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._super_sm.error()

    def acknowledge(self):
        self._carriage.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self, *args, **kwargs):
        self._carriage.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def front_sensor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_init.__name__, self.name)
        self._carriage_sm.set_state(self._carriage_sm.frontracksensorsinit_state)

    def rack_sensor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_init.__name__, self.name)

    def motor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_init.__name__, self.name)
        self._carriage_sm.set_state(self._carriage_sm.motorracksensorinit_state)

    def update(self):
        self._carriage.logger.debug("%s event in %s state", self.update.__name__, self.name)


class MotorInit(CarriageState):
    """ Concrete State class for representing Init Substate : MotorInit """

    def __init__(self, carriage_sm, carriage, super_sm=None, isSubstate=False):
        super(MotorInit, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._carriage_sm = carriage_sm
        self._carriage = carriage
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._carriage.publisher.publish(topic="CarriageState", value="Init: Motor", sender=self._carriage.name)

    def initialize(self):
        self._carriage.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._super_sm.initialize()

    def stop(self):
        self._carriage.logger.debug("%s event in %s state", self.stop.__name__, self.name)

    def move_to_front(self):
        self._carriage.logger.debug("%s event in %s state", self.move_to_front.__name__, self.name)

    def move_to_rack(self):
        self._carriage.logger.debug("%s event in %s state", self.move_to_rack.__name__, self.name)

    def front_sensor_negedge(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_negedge.__name__, self.name)

    def rack_sensor_negedge(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_negedge.__name__, self.name)

    def front_sensor_posedge(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_posedge.__name__, self.name)

    def rack_sensor_posedge(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_posedge.__name__, self.name)

    def motor_on(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_on.__name__, self.name)

    def motor_off(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_off.__name__, self.name)

    def error(self):
        self._carriage.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._super_sm.error()

    def acknowledge(self):
        self._carriage.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self, *args, **kwargs):
        self._carriage.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def front_sensor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_init.__name__, self.name)
        self._carriage_sm.set_state(self._carriage_sm.motorfrontsensorinit_state)

    def rack_sensor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_init.__name__, self.name)
        self._carriage_sm.set_state(self._carriage_sm.motorracksensorinit_state)

    def motor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_init.__name__, self.name)

    def update(self):
        self._carriage.logger.debug("%s event in %s state", self.update.__name__, self.name)


class FrontRackSensorsInit(CarriageState):
    """ Concrete State class for representing Init Substate : FrontRackSensorsInit """

    def __init__(self, carriage_sm, carriage, super_sm=None, isSubstate=False):
        super(FrontRackSensorsInit, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._carriage_sm = carriage_sm
        self._carriage = carriage
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._carriage.publisher.publish(topic="CarriageState", value="Init: FS+RS", sender=self._carriage.name)

    def initialize(self):
        self._carriage.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._super_sm.initialize()

    def stop(self):
        self._carriage.logger.debug("%s event in %s state", self.stop.__name__, self.name)

    def move_to_front(self):
        self._carriage.logger.debug("%s event in %s state", self.move_to_front.__name__, self.name)

    def move_to_rack(self):
        self._carriage.logger.debug("%s event in %s state", self.move_to_rack.__name__, self.name)

    def front_sensor_negedge(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_negedge.__name__, self.name)

    def rack_sensor_negedge(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_negedge.__name__, self.name)

    def front_sensor_posedge(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_posedge.__name__, self.name)

    def rack_sensor_posedge(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_posedge.__name__, self.name)

    def motor_on(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_on.__name__, self.name)

    def motor_off(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_off.__name__, self.name)

    def error(self):
        self._carriage.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._super_sm.error()

    def acknowledge(self):
        self._carriage.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self, *args, **kwargs):
        self._carriage.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def front_sensor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_init.__name__, self.name)

    def rack_sensor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_init.__name__, self.name)

    def motor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_init.__name__, self.name)
        self._carriage_sm.set_state(self._carriage_sm.allinitialized_state)

    def update(self):
        self._carriage.logger.debug("%s event in %s state", self.update.__name__, self.name)


class MotorFrontSensorInit(CarriageState):
    """ Concrete State class for representing Init Substate : MotorFrontSensorInit """

    def __init__(self, carriage_sm, carriage, super_sm=None, isSubstate=False):
        super(MotorFrontSensorInit, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._carriage_sm = carriage_sm
        self._carriage = carriage
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._carriage.publisher.publish(topic="CarriageState", value="Init: Motor+FS", sender=self._carriage.name)

    def initialize(self):
        self._carriage.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._super_sm.initialize()

    def stop(self):
        self._carriage.logger.debug("%s event in %s state", self.stop.__name__, self.name)

    def move_to_front(self):
        self._carriage.logger.debug("%s event in %s state", self.move_to_front.__name__, self.name)

    def move_to_rack(self):
        self._carriage.logger.debug("%s event in %s state", self.move_to_rack.__name__, self.name)

    def front_sensor_negedge(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_negedge.__name__, self.name)

    def rack_sensor_negedge(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_negedge.__name__, self.name)

    def front_sensor_posedge(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_posedge.__name__, self.name)

    def rack_sensor_posedge(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_posedge.__name__, self.name)

    def motor_on(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_on.__name__, self.name)

    def motor_off(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_off.__name__, self.name)

    def error(self):
        self._carriage.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._super_sm.error()

    def acknowledge(self):
        self._carriage.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self, *args, **kwargs):
        self._carriage.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def front_sensor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_init.__name__, self.name)

    def rack_sensor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_init.__name__, self.name)
        self._carriage_sm.set_state(self._carriage_sm.allinitialized_state)

    def motor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_init.__name__, self.name)

    def update(self):
        self._carriage.logger.debug("%s event in %s state", self.update.__name__, self.name)


class MotorRackSensorInit(CarriageState):
    """ Concrete State class for representing Init Substate : MotorRackSensorInit """

    def __init__(self, carriage_sm, carriage, super_sm=None, isSubstate=False):
        super(MotorRackSensorInit, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._carriage_sm = carriage_sm
        self._carriage = carriage
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._carriage.publisher.publish(topic="CarriageState", value="Init: Motor+RS", sender=self._carriage.name)

    def initialize(self):
        self._carriage.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._super_sm.initialize()

    def stop(self):
        self._carriage.logger.debug("%s event in %s state", self.stop.__name__, self.name)

    def move_to_front(self):
        self._carriage.logger.debug("%s event in %s state", self.move_to_front.__name__, self.name)

    def move_to_rack(self):
        self._carriage.logger.debug("%s event in %s state", self.move_to_rack.__name__, self.name)

    def front_sensor_negedge(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_negedge.__name__, self.name)

    def rack_sensor_negedge(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_negedge.__name__, self.name)

    def front_sensor_posedge(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_posedge.__name__, self.name)

    def rack_sensor_posedge(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_posedge.__name__, self.name)

    def motor_on(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_on.__name__, self.name)

    def motor_off(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_off.__name__, self.name)

    def error(self):
        self._carriage.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._super_sm.error()

    def acknowledge(self):
        self._carriage.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self, *args, **kwargs):
        self._carriage.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def front_sensor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_init.__name__, self.name)
        self._carriage_sm.set_state(self._carriage_sm.allinitialized_state)

    def rack_sensor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_init.__name__, self.name)

    def motor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_init.__name__, self.name)

    def update(self):
        self._carriage.logger.debug("%s event in %s state", self.update.__name__, self.name)


class EverythingIsInitialized(CarriageState):
    """ Concrete State class for representing Init Substate : EverythingIsInitialized """

    def __init__(self, carriage_sm, carriage, super_sm=None, isSubstate=False):
        super(EverythingIsInitialized, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._carriage_sm = carriage_sm
        self._carriage = carriage
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._carriage.logger.debug("Entering the %s state", self.name)
        self._carriage.publisher.publish(topic="State", value="Initialized", sender=self._carriage.name)
        self._carriage.publisher.publish(topic="CarriageState", value="Initialized", sender=self._carriage.name)

        self._carriage_sm.set_state(self._carriage_sm.outofposition_state)

    def initialize(self):
        self._carriage.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._super_sm.initialize()

    def stop(self):
        self._carriage.logger.debug("%s event in %s state", self.stop.__name__, self.name)

    def move_to_front(self):
        self._carriage.logger.debug("%s event in %s state", self.move_to_front.__name__, self.name)

    def move_to_rack(self):
        self._carriage.logger.debug("%s event in %s state", self.move_to_rack.__name__, self.name)

    def front_sensor_negedge(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_negedge.__name__, self.name)

    def rack_sensor_negedge(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_negedge.__name__, self.name)

    def front_sensor_posedge(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_posedge.__name__, self.name)

    def rack_sensor_posedge(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_posedge.__name__, self.name)

    def motor_on(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_on.__name__, self.name)

    def motor_off(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_off.__name__, self.name)

    def error(self):
        self._carriage.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._super_sm.error()

    def acknowledge(self):
        self._carriage.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self, *args, **kwargs):
        self._carriage.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def front_sensor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_init.__name__, self.name)

    def rack_sensor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_init.__name__, self.name)

    def motor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_init.__name__, self.name)

    def update(self):
        self._carriage.logger.debug("%s event in %s state", self.update.__name__, self.name)


class CheckCarriagePosition(CarriageState):
    """ Concrete State class for representing CheckCarriagePosition State. This is a composite state. """

    def __init__(self, carriage_sm, carriage, super_sm=None, isSubstate=False):
        super(CheckCarriagePosition, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._carriage_sm = carriage_sm
        self._carriage = carriage
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._carriage.logger.debug("Entering the %s state", self.name)
        self._carriage.publisher.publish(topic="State", value="CheckCarriagePosition", sender=self._carriage.name)
        self._carriage.publisher.publish(topic="CarriageState", value="CheckCarriagePosition", sender=self._carriage.name)

        # stop monitoring timers if they are alive
        if self._carriage_sm.movetofront_timeout_timer.timer_alive():
            self._carriage_sm.movetofront_timeout_timer.cancel()
        if self._carriage_sm.movetorack_timeout_timer.timer_alive():
            self._carriage_sm.movetorack_timeout_timer.cancel()

        # update sensors and stop motor
        self._carriage.motor.handle_event(event=self._carriage_sm.motor_stop_event)
        self._carriage.frontSensor.handle_event(event=self._carriage_sm.sensor_update_event)
        self._carriage.rackSensor.handle_event(event=self._carriage_sm.sensor_update_event)

        self._carriage_sm.set_state(self._carriage_sm.unknouwnpos_substate)

    def initialize(self):
        self._carriage.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._carriage_sm.set_state(self._carriage_sm.initialization_state)

    def stop(self):
        self._carriage.logger.debug("%s event in %s state", self.stop.__name__, self.name)

        self._carriage.motor.handle_event(event=self._carriage_sm.motor_stop_event)

    def move_to_front(self):
        self._carriage.logger.debug("%s event in %s state", self.move_to_front.__name__, self.name)

    def move_to_rack(self):
        self._carriage.logger.debug("%s event in %s state", self.move_to_rack.__name__, self.name)

    def front_sensor_negedge(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_negedge.__name__, self.name)

    def rack_sensor_negedge(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_negedge.__name__, self.name)

    def front_sensor_posedge(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_posedge.__name__, self.name)

    def rack_sensor_posedge(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_posedge.__name__, self.name)

    def motor_on(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_on.__name__, self.name)

    def motor_off(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_off.__name__, self.name)

    def error(self):
        self._carriage.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._carriage_sm.set_state(self._carriage_sm.error_state)

    def acknowledge(self):
        self._carriage.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self, *args, **kwargs):
        self._carriage.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def front_sensor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_init.__name__, self.name)

    def rack_sensor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_init.__name__, self.name)

    def motor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_init.__name__, self.name)

    def update(self):
        self._carriage.logger.debug("%s event in %s state", self.update.__name__, self.name)
        self._carriage_sm.set_state(self._carriage_sm.checkcarriagepos_state)


class UnknownPosition(CarriageState):
    """ Concrete State class for representing CheckCarriagePosition : UnknownPosition """

    def __init__(self, carriage_sm, carriage, super_sm=None, isSubstate=False):
        super(UnknownPosition, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._carriage_sm = carriage_sm
        self._carriage = carriage
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._carriage.publisher.publish(topic="CarriageState", value="CheckCarriagePosition: Unknown", sender=self._carriage.name)

    def initialize(self):
        self._carriage.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._super_sm.initialize()

    def stop(self):
        self._carriage.logger.debug("%s event in %s state", self.stop.__name__, self.name)

        self._carriage.motor.handle_event(event=self._carriage_sm.motor_stop_event)

    def move_to_front(self):
        self._carriage.logger.debug("%s event in %s state", self.move_to_front.__name__, self.name)

    def move_to_rack(self):
        self._carriage.logger.debug("%s event in %s state", self.move_to_rack.__name__, self.name)

    def front_sensor_negedge(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_negedge.__name__, self.name)
        self._carriage_sm.set_state(self._carriage_sm.frontsensorOff_substate)

    def rack_sensor_negedge(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_negedge.__name__, self.name)
        self._carriage_sm.set_state(self._carriage_sm.racksensorOff_substate)

    def front_sensor_posedge(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_posedge.__name__, self.name)
        self._carriage_sm.set_state(self._carriage_sm.atfrontposition_state)

    def rack_sensor_posedge(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_posedge.__name__, self.name)
        self._carriage_sm.set_state(self._carriage_sm.atrackposition_state)

    def motor_on(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_on.__name__, self.name)

    def motor_off(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_off.__name__, self.name)

    def error(self):
        self._carriage.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._super_sm.error()

    def acknowledge(self):
        self._carriage.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self, *args, **kwargs):
        self._carriage.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def front_sensor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_init.__name__, self.name)

    def rack_sensor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_init.__name__, self.name)

    def motor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_init.__name__, self.name)

    def update(self):
        self._carriage.logger.debug("%s event in %s state", self.update.__name__, self.name)
        self._super_sm.update()


class FrontSensorOff(CarriageState):
    """ Concrete State class for representing CheckCarriagePosition : FrontSensorOff """

    def __init__(self, carriage_sm, carriage, super_sm=None, isSubstate=False):
        super(FrontSensorOff, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._carriage_sm = carriage_sm
        self._carriage = carriage
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._carriage.publisher.publish(topic="CarriageState", value="CheckCarriagePosition: FS-Off", sender=self._carriage.name)

    def initialize(self):
        self._carriage.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._super_sm.initialize()

    def stop(self):
        self._carriage.logger.debug("%s event in %s state", self.stop.__name__, self.name)

        self._carriage.motor.handle_event(event=self._carriage_sm.motor_stop_event)

    def move_to_front(self):
        self._carriage.logger.debug("%s event in %s state", self.move_to_front.__name__, self.name)

    def move_to_rack(self):
        self._carriage.logger.debug("%s event in %s state", self.move_to_rack.__name__, self.name)

    def front_sensor_negedge(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_negedge.__name__, self.name)

    def rack_sensor_negedge(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_negedge.__name__, self.name)
        self._carriage_sm.set_state(self._carriage_sm.outofposition_state)

    def front_sensor_posedge(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_posedge.__name__, self.name)
        self._carriage_sm.set_state(self._carriage_sm.atfrontposition_state)

    def rack_sensor_posedge(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_posedge.__name__, self.name)
        self._carriage_sm.set_state(self._carriage_sm.atrackposition_state)

    def motor_on(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_on.__name__, self.name)

    def motor_off(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_off.__name__, self.name)

    def error(self):
        self._carriage.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._super_sm.error()

    def acknowledge(self):
        self._carriage.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self, *args, **kwargs):
        self._carriage.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def front_sensor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_init.__name__, self.name)

    def rack_sensor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_init.__name__, self.name)

    def motor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_init.__name__, self.name)

    def update(self):
        self._carriage.logger.debug("%s event in %s state", self.update.__name__, self.name)
        self._super_sm.update()


class RackSensorOff(CarriageState):
    """ Concrete State class for representing CheckCarriagePosition : RackSensorOff """

    def __init__(self, carriage_sm, carriage, super_sm=None, isSubstate=False):
        super(RackSensorOff, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._carriage_sm = carriage_sm
        self._carriage = carriage
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._carriage.publisher.publish(topic="CarriageState", value="CheckCarriagePosition: RS-Off", sender=self._carriage.name)

    def initialize(self):
        self._carriage.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._super_sm.initialize()

    def stop(self):
        self._carriage.logger.debug("%s event in %s state", self.stop.__name__, self.name)

        self._carriage.motor.handle_event(event=self._carriage_sm.motor_stop_event)

    def move_to_front(self):
        self._carriage.logger.debug("%s event in %s state", self.move_to_front.__name__, self.name)

    def move_to_rack(self):
        self._carriage.logger.debug("%s event in %s state", self.move_to_rack.__name__, self.name)

    def front_sensor_negedge(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_negedge.__name__, self.name)
        self._carriage_sm.set_state(self._carriage_sm.outofposition_state)

    def rack_sensor_negedge(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_negedge.__name__, self.name)

    def front_sensor_posedge(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_posedge.__name__, self.name)
        self._carriage_sm.set_state(self._carriage_sm.atfrontposition_state)

    def rack_sensor_posedge(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_posedge.__name__, self.name)
        self._carriage_sm.set_state(self._carriage_sm.atrackposition_state)

    def motor_on(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_on.__name__, self.name)

    def motor_off(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_off.__name__, self.name)

    def error(self):
        self._carriage.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._super_sm.error()

    def acknowledge(self):
        self._carriage.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self, *args, **kwargs):
        self._carriage.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def front_sensor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_init.__name__, self.name)

    def rack_sensor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_init.__name__, self.name)

    def motor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_init.__name__, self.name)

    def update(self):
        self._carriage.logger.debug("%s event in %s state", self.update.__name__, self.name)
        self._super_sm.update()


class OutOfPosition(CarriageState):
    """ Concrete State class for representing OutOfPosition State. """

    def __init__(self, carriage_sm, carriage, super_sm=None, isSubstate=False):
        super(OutOfPosition, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._carriage_sm = carriage_sm
        self._carriage = carriage
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._carriage.logger.debug("Entering the %s state", self.name)
        self._carriage.publisher.publish(topic="State", value="OutOfPosition", sender=self._carriage.name)
        self._carriage.publisher.publish(topic="CarriageState", value="OutOfPosition",
                                         sender=self._carriage.name)

    def initialize(self):
        self._carriage.logger.debug("%s event in %s state", self.initialize.__name__, self.name)

        self._carriage_sm.set_state(self._carriage_sm.initialization_state)

    def stop(self):
        self._carriage.logger.debug("%s event in %s state", self.stop.__name__, self.name)

        if self._carriage_sm.movetofront_timeout_timer.timer_alive():
            self._carriage_sm.movetofront_timeout_timer.cancel()
        if self._carriage_sm.movetorack_timeout_timer.timer_alive():
            self._carriage_sm.movetorack_timeout_timer.cancel()

        self._carriage.motor.handle_event(event=self._carriage_sm.motor_stop_event)

    def move_to_front(self):
        self._carriage.logger.debug("%s event in %s state", self.move_to_front.__name__, self.name)

        if self._carriage_sm.movetofront_timeout_timer.timer_alive():
            self._carriage_sm.movetofront_timeout_timer.cancel()
        if self._carriage_sm.movetorack_timeout_timer.timer_alive():
            self._carriage_sm.movetorack_timeout_timer.cancel()

        # start monitoring
        self._carriage_sm.movetofront_timeout_timer.start()

        self._carriage.motor.handle_event(event=self._carriage_sm.motor_rotcw_event)

    def move_to_rack(self):
        self._carriage.logger.debug("%s event in %s state", self.move_to_rack.__name__, self.name)

        if self._carriage_sm.movetofront_timeout_timer.timer_alive():
            self._carriage_sm.movetofront_timeout_timer.cancel()
        if self._carriage_sm.movetorack_timeout_timer.timer_alive():
            self._carriage_sm.movetorack_timeout_timer.cancel()

        # start monitoring
        self._carriage_sm.movetorack_timeout_timer.start()

        self._carriage.motor.handle_event(event=self._carriage_sm.motor_rotccw_event)

    def front_sensor_negedge(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_negedge.__name__, self.name)

    def rack_sensor_negedge(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_negedge.__name__, self.name)

    def front_sensor_posedge(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_posedge.__name__, self.name)

        # generate a MotorStop event to stop the motor
        self._carriage.motor.handle_event(event=self._carriage_sm.motor_stop_event)

        self._carriage_sm.set_state(self._carriage_sm.atfrontposition_state)

    def rack_sensor_posedge(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_posedge.__name__, self.name)

        # generate a MotorStop event to stop the motor
        self._carriage.motor.handle_event(event=self._carriage_sm.motor_stop_event)

        self._carriage_sm.set_state(self._carriage_sm.atrackposition_state)

    def motor_on(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_on.__name__, self.name)

    def motor_off(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_off.__name__, self.name)

    def error(self):
        self._carriage.logger.debug("%s event in %s state", self.error.__name__, self.name)

        self._carriage_sm.set_state(self._carriage_sm.error_state)

    def acknowledge(self):
        self._carriage.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self, *args, **kwargs):
        self._carriage.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

        try:
            event = kwargs["event"]
            if event.eventID == self._carriage.carriage_events.eventIDs.TimeoutToRackPos:

                self._carriage_sm.publish_error(error_codes.CarriageErrorCodes.CarriageMovingToRackTimeout)

            elif event.eventID == self._carriage.carriage_events.eventIDs.TimeoutToFrontPos:

                self._carriage_sm.publish_error(error_codes.CarriageErrorCodes.CarriageMovingToDispatchTimeout)

            self._carriage_sm.init_required = True

            self._carriage_sm.set_state(self._carriage_sm.error_state)
        except KeyError:
            pass

    def front_sensor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_init.__name__, self.name)

    def rack_sensor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_init.__name__, self.name)

    def motor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_init.__name__, self.name)

    def update(self):
        self._carriage.logger.debug("%s event in %s state", self.update.__name__, self.name)
        self._carriage_sm.set_state(self._carriage_sm.checkcarriagepos_state)


class AtFrontPosition(CarriageState):
    """ Concrete State class for a AtFrontPosition SM """

    def __init__(self, carriage_sm, carriage, super_sm=None, isSubstate=False):
        super(AtFrontPosition, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._carriage_sm = carriage_sm
        self._carriage = carriage
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._carriage.logger.debug("Entering the %s state", self.name)
        self._carriage.publisher.publish(topic="State", value="AtFrontPosition", sender=self._carriage.name)
        self._carriage.publisher.publish(topic="CarriageState", value="AtFrontPosition",
                                         sender=self._carriage.name)

        if self._carriage_sm.movetofront_timeout_timer.timer_alive():
            self._carriage_sm.movetofront_timeout_timer.cancel()

    def initialize(self):
        self._carriage.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._carriage_sm.set_state(self._carriage_sm.initialization_state)

    def stop(self):
        self._carriage.logger.debug("%s event in %s state", self.stop.__name__, self.name)

        if self._carriage_sm.movetorack_timeout_timer.timer_alive():
            self._carriage_sm.movetorack_timeout_timer.cancel()

        self._carriage.motor.handle_event(event=self._carriage_sm.motor_stop_event)

    def move_to_front(self):
        self._carriage.logger.debug("%s event in %s state", self.move_to_front.__name__, self.name)

    def move_to_rack(self):
        self._carriage.logger.debug("%s event in %s state", self.move_to_rack.__name__, self.name)

        # start monitoring
        if self._carriage_sm.movetorack_timeout_timer.timer_alive():
            self._carriage_sm.movetorack_timeout_timer.cancel()

        self._carriage_sm.movetorack_timeout_timer.start()

        self._carriage.motor.handle_event(event=self._carriage_sm.motor_rotccw_event)

    def front_sensor_negedge(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_negedge.__name__, self.name)

        self._carriage_sm.set_state(self._carriage_sm.outofposition_state)

    def rack_sensor_negedge(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_negedge.__name__, self.name)

    def front_sensor_posedge(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_posedge.__name__, self.name)

    def rack_sensor_posedge(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_posedge.__name__, self.name)

    def motor_on(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_on.__name__, self.name)

    def motor_off(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_off.__name__, self.name)

    def error(self):
        self._carriage.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._carriage_sm.set_state(self._carriage_sm.error_state)

    def acknowledge(self):
        self._carriage.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self, *args, **kwargs):
        self._carriage.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

        try:
            event = kwargs["event"]
            if event.eventID == self._carriage.carriage_events.eventIDs.TimeoutToRackPos:

                self._carriage_sm.publish_error(error_codes.CarriageErrorCodes.CarriageMovingToRackTimeout)

            elif event.eventID == self._carriage.carriage_events.eventIDs.TimeoutToFrontPos:

                self._carriage_sm.publish_error(error_codes.CarriageErrorCodes.CarriageMovingToDispatchTimeout)

            self._carriage_sm.init_required = True

            self._carriage_sm.set_state(self._carriage_sm.error_state)
        except KeyError:
            pass

    def front_sensor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_init.__name__, self.name)

    def rack_sensor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_init.__name__, self.name)

    def motor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_init.__name__, self.name)

    def update(self):
        self._carriage.logger.debug("%s event in %s state", self.update.__name__, self.name)
        self._carriage_sm.set_state(self._carriage_sm.checkcarriagepos_state)


class AtRackPosition(CarriageState):
    """ Concrete State class for a AtRackPosition SM """

    def __init__(self, carriage_sm, carriage, super_sm=None, isSubstate=False):
        super(AtRackPosition, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._carriage_sm = carriage_sm
        self._carriage = carriage
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._carriage.logger.debug("Entering the %s state", self.name)
        self._carriage.publisher.publish(topic="State", value="AtRackPosition", sender=self._carriage.name)
        self._carriage.publisher.publish(topic="CarriageState", value="AtRackPosition",
                                         sender=self._carriage.name)

        if self._carriage_sm.movetorack_timeout_timer.timer_alive():
            self._carriage_sm.movetorack_timeout_timer.cancel()

    def initialize(self):
        self._carriage.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._carriage_sm.set_state(self._carriage_sm.initialization_state)

    def stop(self):
        self._carriage.logger.debug("%s event in %s state", self.stop.__name__, self.name)

        if self._carriage_sm.movetofront_timeout_timer.timer_alive():
            self._carriage_sm.movetofront_timeout_timer.cancel()

        self._carriage.motor.handle_event(event=self._carriage_sm.motor_stop_event)

    def move_to_front(self):
        self._carriage.logger.debug("%s event in %s state", self.move_to_front.__name__, self.name)

        # start monitoring
        if self._carriage_sm.movetofront_timeout_timer.timer_alive():
            self._carriage_sm.movetofront_timeout_timer.cancel()

        self._carriage_sm.movetofront_timeout_timer.start()

        self._carriage.motor.handle_event(event=self._carriage_sm.motor_rotcw_event)

    def move_to_rack(self):
        self._carriage.logger.debug("%s event in %s state", self.move_to_rack.__name__, self.name)

    def front_sensor_negedge(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_negedge.__name__, self.name)

    def rack_sensor_negedge(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_negedge.__name__, self.name)
        self._carriage_sm.set_state(self._carriage_sm.outofposition_state)

    def front_sensor_posedge(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_posedge.__name__, self.name)

    def rack_sensor_posedge(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_posedge.__name__, self.name)

        # ToDo : normally, in this case should be error...

    def motor_on(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_on.__name__, self.name)

    def motor_off(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_off.__name__, self.name)

    def error(self):
        self._carriage.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._carriage_sm.set_state(self._carriage_sm.error_state)

    def acknowledge(self):
        self._carriage.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self, *args, **kwargs):
        self._carriage.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

        try:
            event = kwargs["event"]
            if event.eventID == self._carriage.carriage_events.eventIDs.TimeoutToRackPos:

                self._carriage_sm.publish_error(error_codes.CarriageErrorCodes.CarriageMovingToRackTimeout)

            elif event.eventID == self._carriage.carriage_events.eventIDs.TimeoutToFrontPos:

                self._carriage_sm.publish_error(error_codes.CarriageErrorCodes.CarriageMovingToDispatchTimeout)

            self._carriage_sm.init_required = True

            self._carriage_sm.set_state(self._carriage_sm.error_state)
        except KeyError:
            pass

    def front_sensor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_init.__name__, self.name)

    def rack_sensor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_init.__name__, self.name)

    def motor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_init.__name__, self.name)

    def update(self):
        self._carriage.logger.debug("%s event in %s state", self.update.__name__, self.name)
        self._carriage_sm.set_state(self._carriage_sm.checkcarriagepos_state)


class Error(CarriageState):
    """ Concrete State class for a Error SM """

    def __init__(self, carriage_sm, carriage, super_sm=None, isSubstate=False):
        super(Error, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._carriage_sm = carriage_sm
        self._carriage = carriage
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._carriage.logger.debug("Entering the %s state", self.name)

        self._carriage.publisher.publish(topic="CarriageState", value="Error",
                                         sender=self._carriage.name)

        if self._carriage_sm.init_required:
            self._carriage_sm.init_required = False
            self._carriage.publisher.publish(topic="State", value="ErrorWithInit", sender=self._carriage.name)
        else:
            self._carriage.publisher.publish(topic="State", value="Error", sender=self._carriage.name)

        # stop monitoring timers if they are alive
        if self._carriage_sm.movetofront_timeout_timer.timer_alive():
            self._carriage_sm.movetofront_timeout_timer.cancel()
        if self._carriage_sm.movetorack_timeout_timer.timer_alive():
            self._carriage_sm.movetorack_timeout_timer.cancel()

        self._carriage.motor.handle_event(event=self._carriage_sm.motor_stop_event)

    def initialize(self):
        self._carriage.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._carriage_sm.set_state(self._carriage_sm.initialization_state)

    def stop(self):
        self._carriage.logger.debug("%s event in %s state", self.stop.__name__, self.name)

    def move_to_front(self):
        self._carriage.logger.debug("%s event in %s state", self.move_to_front.__name__, self.name)

    def move_to_rack(self):
        self._carriage.logger.debug("%s event in %s state", self.move_to_rack.__name__, self.name)

    def front_sensor_negedge(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_negedge.__name__, self.name)

    def rack_sensor_negedge(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_negedge.__name__, self.name)

    def front_sensor_posedge(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_posedge.__name__, self.name)

    def rack_sensor_posedge(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_posedge.__name__, self.name)

    def motor_on(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_on.__name__, self.name)

    def motor_off(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_off.__name__, self.name)

    def error(self):
        self._carriage.logger.debug("%s event in %s state", self.error.__name__, self.name)

    def acknowledge(self):
        self._carriage.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

        # update sensors
        # self._carriage.frontSensor.handle_event(event=self._carriage_sm.sensor_update_event)
        # self._carriage.rackSensor.handle_event(event=self._carriage_sm.sensor_update_event)

        # self._carriage_sm.set_state(self._carriage_sm.outofposition_state)
        self._carriage_sm.set_state(self._carriage_sm.checkcarriagepos_state)

    def timeout(self, *args, **kwargs):
        self._carriage.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def front_sensor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.front_sensor_init.__name__, self.name)

    def rack_sensor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.rack_sensor_init.__name__, self.name)

    def motor_init(self):
        self._carriage.logger.debug("%s event in %s state", self.motor_init.__name__, self.name)

    def update(self):
        self._carriage.logger.debug("%s event in %s state", self.update.__name__, self.name)


class CarriageStateMachine(object):
    """ Context class for the Station's state machine """
    def __init__(self, carriage):
        self._name = self.__class__.__name__

        self._carriage = carriage  # ref to the carriage object

        # timeout monitoring timer with the event TimeoutToFrontPos
        movetofront_timeout_event = events.CarriageEvent(eventID=events.CarriageEvents.TimeoutToFrontPos,
                                             sender=self._carriage.name)

        self.movetofront_timeout_timer = MonitoringTimer(name="CarriageMoveToFrontTimer",
                                                         interval=config.STATION_CONFIG['carriageMoveTimeout'],
                                                         callback_fnc=self.timeout_handler,
                                                         logger=self._carriage.logger,
                                                         event=movetofront_timeout_event)

        # timeout monitoring timer with the event TimeoutToRackPos
        movetorack_timeout_event = events.CarriageEvent(eventID=events.CarriageEvents.TimeoutToRackPos,
                                                         sender=self._carriage.name)
        self.movetorack_timeout_timer = MonitoringTimer(name="CarriageMoveToRackTimer",
                                                         interval=config.STATION_CONFIG['carriageMoveTimeout'],
                                                         callback_fnc=self.timeout_handler,
                                                        logger=self._carriage.logger,
                                                        event=movetorack_timeout_event)


        # events objects:
        self.sensor_init_event = events.SimpleSensorInputEvent(eventID=events.SimpleSensorInputEvents.Initialize,
                                                               sender=self._carriage.name)
        self.motor_init_event = events.SimpleMotorInputEvent(eventID=events.SimpleMotorInputEvents.Initialize,
                                                             sender=self._carriage.name)
        self.sensor_update_event = events.SimpleSensorInputEvent(eventID=events.SimpleSensorInputEvents.Update,
                                                                 sender=self._carriage.name)
        self.motor_stop_event = events.SimpleMotorInputEvent(eventID=events.SimpleMotorInputEvents.Stop,
                                                             sender=self._carriage.name)
        self.motor_rotcw_event = events.SimpleMotorInputEvent(eventID=events.SimpleMotorInputEvents.RotateCW,
                                                             sender=self._carriage.name)
        self.motor_rotccw_event = events.SimpleMotorInputEvent(eventID=events.SimpleMotorInputEvents.RotateCCW,
                                                              sender=self._carriage.name)

        # state objects
        self._notinit_state = NotInitialized(self, carriage)        # rack's states instances
        self._initialization_state = Initialization(self, carriage)

        # initialization substates :
        self._allnotinitialized_state = NothingIsInitialized(self, carriage, super_sm=self.initialization_state, isSubstate=True)
        self._frontsensorinit_state = FrontSensorInit(self, carriage, super_sm=self.initialization_state, isSubstate=True)
        self._racksensorinit_state = RackSensorInit(self, carriage, super_sm=self.initialization_state, isSubstate=True)
        self._motorsensorinit_state = MotorInit(self, carriage, super_sm=self.initialization_state, isSubstate=True)
        self._frontracksensorsinit_state = FrontRackSensorsInit(self, carriage, super_sm=self.initialization_state, isSubstate=True)
        self._motorfrontsensorinit_state = MotorFrontSensorInit(self, carriage, super_sm=self.initialization_state, isSubstate=True)
        self._motorracksensorinit_state = MotorRackSensorInit(self, carriage, super_sm=self.initialization_state, isSubstate=True)
        self._allinitialized_state = EverythingIsInitialized(self, carriage, super_sm=self.initialization_state, isSubstate=True)

        self._checkcarriagepos_state = CheckCarriagePosition(self, carriage)

        # check carriage position substates :
        self._unknouwnpos_substate = UnknownPosition(self, carriage, super_sm=self.checkcarriagepos_state, isSubstate=True)
        self._frontsensorOff_substate = FrontSensorOff(self, carriage, super_sm=self.checkcarriagepos_state,isSubstate=True)
        self._racksensorOff_substate = RackSensorOff(self, carriage, super_sm=self.checkcarriagepos_state,isSubstate=True)

        self._outofposition_state = OutOfPosition(self, carriage)
        self._atfrontposition_state = AtFrontPosition(self, carriage)
        self._atrackposition_state = AtRackPosition(self, carriage,)
        self._error_state = Error(self, carriage)

        self._current_state = self._notinit_state
        self._current_state.enter_action()

        self.init_required = False  # to show that an init is needed after the error

# properties
    @property
    def name(self):
        return self._name

    @property
    def current_state(self):
        return self._current_state

    @property
    def notinit_state(self):
        return self._notinit_state

    @property
    def initialization_state(self):
        return self._initialization_state

    @property
    def allnotinitialized_state(self):
        return self._allnotinitialized_state

    @property
    def frontsensorinit_state(self):
        return self._frontsensorinit_state

    @property
    def racksensorinit_state(self):
        return self._racksensorinit_state

    @property
    def motorsensorinit_state(self):
        return self._motorsensorinit_state

    @property
    def frontracksensorsinit_state(self):
        return self._frontracksensorsinit_state

    @property
    def motorfrontsensorinit_state(self):
        return self._motorfrontsensorinit_state

    @property
    def motorracksensorinit_state(self):
        return self._motorracksensorinit_state

    @property
    def allinitialized_state(self):
        return self._allinitialized_state

    @property
    def checkcarriagepos_state(self):
        return self._checkcarriagepos_state

    @property
    def unknouwnpos_substate(self):
        return self._unknouwnpos_substate

    @property
    def frontsensorOff_substate(self):
        return self._frontsensorOff_substate

    @property
    def racksensorOff_substate(self):
        return self._racksensorOff_substate

    @property
    def outofposition_state(self):
        return self._outofposition_state

    @property
    def atfrontposition_state(self):
        return self._atfrontposition_state

    @property
    def atrackposition_state(self):
        return self._atrackposition_state

    @property
    def error_state(self):
        return self._error_state

    def set_state(self, state):
        self._carriage.logger.debug("Switching from state %s to state %s", self.current_state.name, state.name)

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

    def timeout_handler(self, *args, **kwargs):
        self._carriage.handle_event(*args, **kwargs)

    def publish_error(self, error_code):
        self._carriage.publisher.publish(topic="StationErrorCode",
                                                value=hex(error_code),
                                                sender=self._carriage.name)
        self._carriage.publisher.publish(topic="StationErrorDescription",
                                                value=error_codes.code_to_text[error_code],
                                                sender=self._carriage.name)

    def publish_message(self, message_code):
        self._carriage.publisher.publish(topic="StationMessageCode",
                                                value=hex(message_code),
                                                sender=self._carriage.name)
        self._carriage.publisher.publish(topic="StationMessageDescription",
                                                value=message_codes.code_to_text[message_code],
                                                sender=self._carriage.name)

    def dispatch(self, *args, **kwargs):
        self._carriage.logger.debug("%s has received a message: %s", self.name, kwargs)

        try:
            # topics coming from the publishers
            topic = kwargs["topic"]
            value = kwargs["value"]
            sender = kwargs["sender"]

            if sender == "SensorCarriagePosBack":

                if topic == "Value":
                    if value:
                        self._current_state.rack_sensor_posedge()
                    else:
                        self._current_state.rack_sensor_negedge()

                elif topic == "State":

                    if value == "Error":
                        self._current_state.error()
                    elif value == "NotInitialized":
                        pass
                        # self._current_state.error()
                    elif value == "Initialized":
                        self._current_state.rack_sensor_init()

            elif sender == "SensorCarriagePosFront":

                if topic == "Value":
                    if value:
                        self._current_state.front_sensor_posedge()
                    else:
                        self._current_state.front_sensor_negedge()

                elif topic == "State":

                    if value == "Error":
                        self._current_state.error()
                    elif value == "NotInitialized":
                        pass
                        # self._current_state.error()
                    elif value == "Initialized":
                        self._current_state.front_sensor_init()

            elif sender == "MotorCarriage":

                if topic == "Value":
                    if value:
                        self._current_state.motor_on()
                    else:
                        self._current_state.motor_off()

                elif topic == "State":

                    if value == "Error":
                        self._current_state.error()
                    elif value == "Estop":
                        self._current_state.error()
                    elif value == "NotInitialized":
                        pass
                        # self._current_state.error()
                    elif value == "Initialized":
                        self._current_state.motor_init()

            elif sender == "Station":

                if topic == "Ack":
                    if value:
                        self._current_state.acknowledge()
                    else:
                        pass
                elif topic == "StationState" and value == "Error":
                    self._current_state.error()


        except KeyError:
            try:
                event = kwargs["event"]

                eventID = event.eventID
                sender = event.sender

                if eventID == self._carriage.carriage_events.eventIDs.Initialize:  # this a part of the service generic interface
                    self._current_state.initialize()
                elif eventID == self._carriage.carriage_events.eventIDs.Ack:
                    self._current_state.acknowledge()
                elif eventID == self._carriage.carriage_events.eventIDs.MoveToFrontPos:
                    self._current_state.move_to_front()
                elif eventID == self._carriage.carriage_events.eventIDs.MoveToRackPos:
                    self._current_state.move_to_rack()
                elif eventID == self._carriage.carriage_events.eventIDs.Stop:
                    self._current_state.stop()
                elif eventID == self._carriage.carriage_events.eventIDs.Error:
                    self._current_state.error()
                elif (eventID == self._carriage.carriage_events.eventIDs.TimeoutToRackPos) \
                        or (eventID == self._carriage.carriage_events.eventIDs.TimeoutToFrontPos) :
                    self._current_state.timeout(event=event)
                elif eventID == self._carriage.carriage_events.eventIDs.Update:
                    self._current_state.update()
                else:
                    self._carriage.logger.debug("Unknown event : %s", event)
            except KeyError:
                self._carriage.logger.debug("Unknown event : %s", kwargs)
