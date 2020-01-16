import abc
from communication import events
from utils.monitoring_timer import MonitoringTimer
from utils import error_codes, message_codes
import config

class PressState(metaclass=abc.ABCMeta):
    """ Abstract State class for a PressState SM """

    def __init__(self, isSubstate=False):
        self._isSubstate = isSubstate

    @property
    def isSubstate(self):
        return self._isSubstate

    # events for super states
    @abc.abstractmethod
    def initialize(self):
        """ Initialize the press"""
        raise NotImplemented

    @abc.abstractmethod
    def stop(self):
        """ Stop the press's motor """
        raise NotImplemented

    @abc.abstractmethod
    def move_up(self):
        """ Move the press up to the sensor """
        raise NotImplemented

    @abc.abstractmethod
    def move_down(self):
        """ Move the press down to the sendor"""
        raise NotImplemented

    @abc.abstractmethod
    def up_sensor_negedge(self):
        """ Negative edge event from the up sensor -> out of position """
        raise NotImplemented

    @abc.abstractmethod
    def down_sensor_negedge(self):
        """ Negative edge event from the endswitch sensor -> out of position """
        raise NotImplemented

    @abc.abstractmethod
    def up_sensor_posedge(self):
        """ Positive edge event from the up sensor -> press is in the upper pos """
        raise NotImplemented

    @abc.abstractmethod
    def down_sensor_posedge(self):
        """ Positive edge event from the endswitch sensor -> press is in the endswitch pos """
        raise NotImplemented

    @abc.abstractmethod
    def force_sensor_posedge(self):
        """ Positive edge event from the force sensor -> press is in the pressing pos """
        raise NotImplemented

    @abc.abstractmethod
    def force_sensor_negedge(self):
        """ Positive edge event from the force sensor -> out of position"""
        raise NotImplemented

    @abc.abstractmethod
    def motor_on(self):
        """ Motor ON event from the motor -> the press has started the movement """
        raise NotImplemented

    @abc.abstractmethod
    def motor_off(self):
        """ Motor OFF event from the motor -> the press has stopped """
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
    def timeout(self):
        raise NotImplemented

    @abc.abstractmethod
    def update(self):
        raise NotImplemented

    # enter/exit actions (UML specification)
    def enter_action(self):
        pass

    def exit_action(self):
        pass


class NotInitialized(PressState):
    """ Concrete State class for a NotInitialized SM """

    def __init__(self, press_sm, press, super_sm=None, isSubstate=False):
        super(NotInitialized, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._press_sm = press_sm
        self._press = press
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._press.publisher.publish(topic="PressState", value="NotInitialized", sender=self._press.name)
        self._press.publisher.publish(topic="State", value="NotInitialized", sender=self._press.name)

    def initialize(self):
        self._press_sm.set_state(self._press_sm.initialization_state)
        # self._press.logger.debug("%s event in %s state", self.initialize.__name__, self.name)

    def stop(self):
        self._press.logger.debug("%s event in %s state", self.stop.__name__, self.name)

    def move_up(self):
        self._press.logger.debug("%s event in %s state", self.move_up.__name__, self.name)

    def move_down(self):
        self._press.logger.debug("%s event in %s state", self.move_down.__name__, self.name)

    def up_sensor_negedge(self):
        self._press.logger.debug("%s event in %s state", self.up_sensor_negedge.__name__, self.name)

    def down_sensor_negedge(self):
        self._press.logger.debug("%s event in %s state", self.down_sensor_negedge.__name__, self.name)

    def up_sensor_posedge(self):
        self._press.logger.debug("%s event in %s state", self.up_sensor_posedge.__name__, self.name)

    def down_sensor_posedge(self):
        self._press.logger.debug("%s event in %s state", self.down_sensor_posedge.__name__, self.name)

    def motor_on(self):
        self._press.logger.debug("%s event in %s state", self.motor_on.__name__, self.name)

    def motor_off(self):
        self._press.logger.debug("%s event in %s state", self.motor_off.__name__, self.name)

    def error(self):
        self._press_sm.set_state(self._press_sm.error_state)
        # self._press.logger.debug("%s event in %s state", self.error.__name__, self.name)

    def acknowledge(self):
        self._press.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._press.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def force_sensor_posedge(self):
        self._press.logger.debug("%s event in %s state", self.force_sensor_posedge.__name__, self.name)

    def force_sensor_negedge(self):
        self._press.logger.debug("%s event in %s state", self.force_sensor_negedge.__name__, self.name)

    def update(self):
        self._press.logger.debug("%s event in %s state", self.update.__name__, self.name)


class Initialization(PressState):
    """ Concrete State class for representing Initialization State. This is a composite state. """

    def __init__(self, press_sm, press, super_sm=None, isSubstate=False):
        super(Initialization, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._press_sm = press_sm
        self._press = press
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._press.publisher.publish(topic="PressState", value="Initialized", sender=self._press.name)
        self._press.publisher.publish(topic="State", value="Initialized", sender=self._press.name)
        self._press_sm.set_state(self._press_sm.checkpresspos_state)

    def initialize(self):
        self._press_sm.set_state(self._press_sm.checkpresspos_state)

    def stop(self):
        self._press.logger.debug("%s event in %s state", self.stop.__name__, self.name)

    def move_up(self):
        self._press.logger.debug("%s event in %s state", self.move_up.__name__, self.name)

    def move_down(self):
        self._press.logger.debug("%s event in %s state", self.move_down.__name__, self.name)

    def up_sensor_negedge(self):
        self._press.logger.debug("%s event in %s state", self.up_sensor_negedge.__name__, self.name)

    def down_sensor_negedge(self):
        self._press.logger.debug("%s event in %s state", self.down_sensor_negedge.__name__, self.name)

    def up_sensor_posedge(self):
        self._press.logger.debug("%s event in %s state", self.up_sensor_posedge.__name__, self.name)

    def down_sensor_posedge(self):
        self._press.logger.debug("%s event in %s state", self.down_sensor_posedge.__name__, self.name)

    def motor_on(self):
        self._press.logger.debug("%s event in %s state", self.motor_on.__name__, self.name)

    def motor_off(self):
        self._press.logger.debug("%s event in %s state", self.motor_off.__name__, self.name)

    def error(self):
        self._press.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._press_sm.set_state(self._press_sm.error_state)

    def acknowledge(self):
        self._press.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._press.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def force_sensor_posedge(self):
        self._press.logger.debug("%s event in %s state", self.force_sensor_posedge.__name__, self.name)

    def force_sensor_negedge(self):
        self._press.logger.debug("%s event in %s state", self.force_sensor_negedge.__name__, self.name)

    def update(self):
        self._press.logger.debug("%s event in %s state", self.update.__name__, self.name)


class CheckPressPosition(PressState):
    """ Concrete State class for representing CheckCarriagePosition State. This is a composite state. """

    def __init__(self, press_sm, press, super_sm=None, isSubstate=False):
        super(CheckPressPosition, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._press_sm = press_sm
        self._press = press
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._press.motor.handle_event(event=self._press_sm.motor_stop_event)
        self._press.publisher.publish(topic="PressState", value="CheckPressPosition", sender=self._press.name)
        self._press.publisher.publish(topic="State", value="CheckPressPosition", sender=self._press.name)

        self._press_sm.movedown_future = False
        self._press_sm.moveup_future = False

        self._press_sm.set_state(self._press_sm.unknouwnpos_substate)

    def initialize(self):
        self._press.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._press_sm.set_state(self._press_sm.initialization_state)

    def stop(self):
        self._press.motor.handle_event(event=self._press_sm.motor_stop_event)
        self._press.logger.debug("%s event in %s state", self.stop.__name__, self.name)

    def move_up(self):
        self._press.logger.debug("%s event in %s state", self.move_up.__name__, self.name)

    def move_down(self):
        self._press.logger.debug("%s event in %s state", self.move_down.__name__, self.name)

    def up_sensor_negedge(self):
        self._press.logger.debug("%s event in %s state", self.up_sensor_negedge.__name__, self.name)

    def down_sensor_negedge(self):
        self._press.logger.debug("%s event in %s state", self.down_sensor_negedge.__name__, self.name)

    def up_sensor_posedge(self):
        self._press.logger.debug("%s event in %s state", self.up_sensor_posedge.__name__, self.name)

    def down_sensor_posedge(self):
        self._press.logger.debug("%s event in %s state", self.down_sensor_posedge.__name__, self.name)

    def motor_on(self):
        self._press.logger.debug("%s event in %s state", self.motor_on.__name__, self.name)

    def motor_off(self):
        self._press.logger.debug("%s event in %s state", self.motor_off.__name__, self.name)

    def error(self):
        self._press.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._press_sm.set_state(self._press_sm.error_state)

    def acknowledge(self):
        self._press.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._press.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def force_sensor_posedge(self):
        self._press.logger.debug("%s event in %s state", self.force_sensor_posedge.__name__, self.name)

    def force_sensor_negedge(self):
        self._press.logger.debug("%s event in %s state", self.force_sensor_negedge.__name__, self.name)

    def update(self):
        self._press.logger.debug("%s event in %s state", self.update.__name__, self.name)
        self._press_sm.set_state(self._press_sm.checkpresspos_state)


class UnknownPosition(PressState):
    """ In this state we check the upper sensor """

    def __init__(self, press_sm, press, super_sm=None, isSubstate=False):
        super(UnknownPosition, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._press_sm = press_sm
        self._press = press
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._press.uppos_sensor.handle_event(event=self._press_sm.sensor_update_event)
        self._press.publisher.publish(topic="PressState", value="CheckPressPos : UnknownPos", sender=self._press.name)
        self._press.publisher.publish(topic="State", value="CheckPressPos : UnknownPos", sender=self._press.name)

    def initialize(self):
        self._press.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._super_sm.initialize()

    def stop(self):
        self._press.motor.handle_event(event=self._press_sm.motor_stop_event)
        self._press.logger.debug("%s event in %s state", self.stop.__name__, self.name)

    def move_up(self):
        self._press.logger.debug("%s event in %s state", self.move_up.__name__, self.name)

        self._press_sm.moveup_future = True

    def move_down(self):
        self._press.logger.debug("%s event in %s state", self.move_down.__name__, self.name)

        self._press_sm.movedown_future = True

    def up_sensor_negedge(self):
        self._press.logger.debug("%s event in %s state", self.up_sensor_negedge.__name__, self.name)
        self._press_sm.set_state(self._press_sm.upsensorOff_substate)

    def down_sensor_negedge(self):
        self._press.logger.debug("%s event in %s state", self.down_sensor_negedge.__name__, self.name)

    def up_sensor_posedge(self):
        # self._press.logger.debug("%s event in %s state", self.up_sensor_posedge.__name__, self.name)
        self._press_sm.set_state(self._press_sm.inupperposition_state)

    def down_sensor_posedge(self):
        self._press.logger.debug("%s event in %s state", self.down_sensor_posedge.__name__, self.name)

    def motor_on(self):
        self._press.logger.debug("%s event in %s state", self.motor_on.__name__, self.name)

    def motor_off(self):
        self._press.logger.debug("%s event in %s state", self.motor_off.__name__, self.name)

    def error(self):
        self._press.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._super_sm.error()

    def acknowledge(self):
        self._press.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._press.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def force_sensor_posedge(self):
        self._press.logger.debug("%s event in %s state", self.force_sensor_posedge.__name__, self.name)

    def force_sensor_negedge(self):
        self._press.logger.debug("%s event in %s state", self.force_sensor_negedge.__name__, self.name)

    def update(self):
        self._press.logger.debug("%s event in %s state", self.update.__name__, self.name)
        self._super_sm.update()


class UpSensorOff(PressState):
    """ In this state we check endswitch sensor """

    def __init__(self, press_sm, press, super_sm=None, isSubstate=False):
        super(UpSensorOff, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._press_sm = press_sm
        self._press = press
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._press.endswitch_sensor.handle_event(event=self._press_sm.sensor_update_event)
        self._press.publisher.publish(topic="PressState", value="CheckPressPos : UpSensorOff", sender=self._press.name)
        self._press.publisher.publish(topic="State", value="CheckPressPos : UpSensorOff", sender=self._press.name)

    def initialize(self):
        self._press.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._super_sm.initialize()

    def stop(self):
        self._press.motor.handle_event(event=self._press_sm.motor_stop_event)
        self._press.logger.debug("%s event in %s state", self.stop.__name__, self.name)

    def move_up(self):
        self._press.logger.debug("%s event in %s state", self.move_up.__name__, self.name)

        self._press_sm.moveup_future = True

    def move_down(self):
        self._press.logger.debug("%s event in %s state", self.move_down.__name__, self.name)

        self._press_sm.movedown_future = True

    def up_sensor_negedge(self):
        self._press.logger.debug("%s event in %s state", self.up_sensor_negedge.__name__, self.name)

    def down_sensor_negedge(self):
        self._press.logger.debug("%s event in %s state", self.down_sensor_negedge.__name__, self.name)
        self._press_sm.set_state(self._press_sm.downsensorOff_substate)

    def up_sensor_posedge(self):
        self._press.logger.debug("%s event in %s state", self.up_sensor_posedge.__name__, self.name)

    def down_sensor_posedge(self):
        self._press.logger.debug("%s event in %s state", self.down_sensor_posedge.__name__, self.name)
        self._press_sm.set_state(self._press_sm.inbottomposition_state)

    def motor_on(self):
        self._press.logger.debug("%s event in %s state", self.motor_on.__name__, self.name)

    def motor_off(self):
        self._press.logger.debug("%s event in %s state", self.motor_off.__name__, self.name)

    def error(self):
        self._press.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._super_sm.error()

    def acknowledge(self):
        self._press.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._press.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def force_sensor_posedge(self):
        self._press.logger.debug("%s event in %s state", self.force_sensor_posedge.__name__, self.name)

    def force_sensor_negedge(self):
        self._press.logger.debug("%s event in %s state", self.force_sensor_negedge.__name__, self.name)

    def update(self):
        self._press.logger.debug("%s event in %s state", self.update.__name__, self.name)
        self._super_sm.update()


class DownSensorOff(PressState):
    """ In this state we check force sensor """

    def __init__(self, press_sm, press, super_sm=None, isSubstate=False):
        super(DownSensorOff, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._press_sm = press_sm
        self._press = press
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._press.force_sensor.handle_event(event=self._press_sm.sensor_update_event)
        self._press.publisher.publish(topic="PressState", value="CheckPressPos : DownSensorOff", sender=self._press.name)
        self._press.publisher.publish(topic="State", value="CheckPressPos : DownSensorOff", sender=self._press.name)

    def initialize(self):
        self._press.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._super_sm.initialize()

    def stop(self):
        self._press.motor.handle_event(event=self._press_sm.motor_stop_event)
        self._press.logger.debug("%s event in %s state", self.stop.__name__, self.name)

    def move_up(self):
        self._press.logger.debug("%s event in %s state", self.move_up.__name__, self.name)

        self._press_sm.moveup_future = True

    def move_down(self):
        self._press.logger.debug("%s event in %s state", self.move_down.__name__, self.name)

        self._press_sm.movedown_future = True

    def up_sensor_negedge(self):
        self._press.logger.debug("%s event in %s state", self.up_sensor_negedge.__name__, self.name)

    def down_sensor_negedge(self):
        self._press.logger.debug("%s event in %s state", self.down_sensor_negedge.__name__, self.name)

    def up_sensor_posedge(self):
        self._press.logger.debug("%s event in %s state", self.up_sensor_posedge.__name__, self.name)

    def down_sensor_posedge(self):
        self._press.logger.debug("%s event in %s state", self.down_sensor_posedge.__name__, self.name)

    def motor_on(self):
        self._press.logger.debug("%s event in %s state", self.motor_on.__name__, self.name)

    def motor_off(self):
        self._press.logger.debug("%s event in %s state", self.motor_off.__name__, self.name)

    def error(self):
        # self._press.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._super_sm.error()

    def acknowledge(self):
        self._press.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._press.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def force_sensor_posedge(self):
        self._press.logger.debug("%s event in %s state", self.force_sensor_posedge.__name__, self.name)
        self._press_sm.set_state(self._press_sm.inpressingpos_state)

    def force_sensor_negedge(self):
        self._press.logger.debug("%s event in %s state", self.force_sensor_negedge.__name__, self.name)
        self._press_sm.set_state(self._press_sm.outofposition_state)

    def update(self):
        self._press.logger.debug("%s event in %s state", self.update.__name__, self.name)
        self._super_sm.update()


class OutOfPosition(PressState):
    """ Concrete State class for representing OutOfPosition State. """

    def __init__(self, press_sm, press, super_sm=None, isSubstate=False):
        super(OutOfPosition, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._press_sm = press_sm
        self._press = press
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._press.publisher.publish(topic="PressState", value="OutOfPosition", sender=self._press.name)
        self._press.publisher.publish(topic="State", value="OutOfPosition", sender=self._press.name)

        if self._press_sm.movedown_future and not self._press_sm.moveup_future:
            self._press_sm.movedown_future = False
            self._press_sm._current_state.move_down()
        elif not self._press_sm.movedown_future and self._press_sm.moveup_future:
            self._press_sm.moveup_future = False
            self._press_sm._current_state.move_up()
        elif self._press_sm.moveup_future and self._press_sm.movedown_future:
            self._press_sm.movedown_future = False
            self._press_sm.moveup_future = False
            self._press_sm.set_state(self._press_sm.error_state)

    def initialize(self):
        self._press.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._press_sm.move_down = False
        self._press_sm.move_up = False
        self._press_sm.set_state(self._press_sm.initialization_state)

    def stop(self):
        self._press.motor.handle_event(event=self._press_sm.motor_stop_event)
        self._press_sm.move_down = False
        self._press_sm.move_up = False
        self._press.logger.debug("%s event in %s state", self.stop.__name__, self.name)

    def move_up(self):
        self._press.logger.debug("%s event in %s state", self.move_up.__name__, self.name)

        self._press.motor.handle_event(event=self._press_sm.motor_rotcw_event)

        if self._press_sm.service_timeout_timer is not None:
            self._press_sm.service_timeout_timer.start()

        self._press_sm.move_up = True
        self._press_sm.move_down = False

    def move_down(self):
        self._press.logger.debug("%s event in %s state", self.move_down.__name__, self.name)

        self._press.motor.handle_event(event=self._press_sm.motor_rotccw_event)

        if self._press_sm.service_timeout_timer is not None:
            self._press_sm.service_timeout_timer.start()

        self._press_sm.move_down = True
        self._press_sm.move_up = False

    def up_sensor_negedge(self):
        self._press.logger.debug("%s event in %s state", self.up_sensor_negedge.__name__, self.name)

    def down_sensor_negedge(self):
        self._press.logger.debug("%s event in %s state", self.down_sensor_negedge.__name__, self.name)

    def up_sensor_posedge(self):
        self._press.motor.handle_event(event=self._press_sm.motor_stop_event)
        self._press.logger.debug("%s event in %s state", self.up_sensor_posedge.__name__, self.name)

        if self._press_sm.service_timeout_timer is not None:
            self._press_sm.service_timeout_timer.cancel()

        self._press_sm.move_up = False

        self._press_sm.set_state(self._press_sm.inupperposition_state)

    def down_sensor_posedge(self):
        self._press.motor.handle_event(event=self._press_sm.motor_stop_event)
        self._press.logger.debug("%s event in %s state", self.down_sensor_posedge.__name__, self.name)
        self._press.logger.info("Error: The press is on the endswitch!")

        if self._press_sm.service_timeout_timer is not None:
            self._press_sm.service_timeout_timer.cancel()

        self._press_sm.move_down = False

        self._press_sm.publish_error(error_codes.PressErrorCodes.OnEndSwitchError)
        self._press_sm.init_required = True
        self._press_sm.set_state(self._press_sm.error_state)

    def motor_on(self):
        self._press.logger.debug("%s event in %s state", self.motor_on.__name__, self.name)

    def motor_off(self):
        self._press.logger.debug("%s event in %s state", self.motor_off.__name__, self.name)

    def error(self):
        self._press.logger.debug("%s event in %s state", self.error.__name__, self.name)

        if self._press_sm.service_timeout_timer is not None:
            self._press_sm.service_timeout_timer.cancel()

        self._press_sm.move_down = False
        self._press_sm.move_up = False

        self._press_sm.set_state(self._press_sm.error_state)

    def acknowledge(self):
        self._press.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._press.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

        if self._press_sm.move_down and not self._press_sm.move_up:
            self._press_sm.publish_error(error_codes.PressErrorCodes.PressMovingDownTimeout)
            self._press_sm.move_down = False
        elif self._press_sm.move_up and not self._press_sm.move_down:
            self._press_sm.publish_error(error_codes.PressErrorCodes.PressMovingUpTimeout)
            self._press_sm.move_up = False
        else:
            self._press_sm.move_down = False
            self._press_sm.move_up = False

        self._press_sm.init_required = True
        self._press_sm.set_state(self._press_sm.error_state)

    def force_sensor_posedge(self):
        self._press.logger.debug("%s event in %s state", self.force_sensor_posedge.__name__, self.name)

        self._press.motor.handle_event(event=self._press_sm.motor_stop_event)

        if self._press_sm.service_timeout_timer is not None:
            self._press_sm.service_timeout_timer.cancel()

        self._press_sm.move_down = False

        self._press_sm.set_state(self._press_sm.inpressingpos_state )

    def force_sensor_negedge(self):
        self._press.logger.debug("%s event in %s state", self.force_sensor_negedge.__name__, self.name)

    def update(self):
        self._press.logger.debug("%s event in %s state", self.update.__name__, self.name)

        if self._press_sm.service_timeout_timer is not None:
            self._press_sm.service_timeout_timer.cancel()

        self._press_sm.move_down = False
        self._press_sm.move_up = False

        self._press_sm.set_state(self._press_sm.checkpresspos_state)


class InUpperPosition(PressState):
    """ Concrete State class for a InUpperPosition SM """

    def __init__(self, press_sm, press, super_sm=None, isSubstate=False):
        super(InUpperPosition, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._press_sm = press_sm
        self._press = press
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._press.publisher.publish(topic="PressState", value="InUpperPosition", sender=self._press.name)
        self._press.publisher.publish(topic="State", value="InUpperPosition", sender=self._press.name)

        self._press_sm.move_up = False

        if self._press_sm.movedown_future and not self._press_sm.moveup_future:
            self._press_sm.movedown_future = False
            self._press_sm._current_state.move_down()
        elif not self._press_sm.movedown_future and self._press_sm.moveup_future:
            self._press_sm.moveup_future = False
            self._press_sm._current_state.move_up()
        elif self._press_sm.moveup_future and self._press_sm.movedown_future:
            self._press_sm.movedown_future = False
            self._press_sm.moveup_future = False
            self._press_sm.set_state(self._press_sm.error_state)

    def initialize(self):
        self._press.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._press_sm.move_down = False
        self._press_sm.set_state(self._press_sm.initialization_state)

    def stop(self):
        self._press.motor.handle_event(event=self._press_sm.motor_stop_event)
        self._press_sm.move_down = False
        self._press.logger.debug("%s event in %s state", self.stop.__name__, self.name)

    def move_up(self):
        self._press.logger.debug("%s event in %s state", self.move_up.__name__, self.name)
        self._press.publisher.publish(topic="State", value="InUpperPosition", sender=self._press.name)

    def move_down(self):
        self._press.logger.debug("%s event in %s state", self.move_down.__name__, self.name)

        if self._press_sm.service_timeout_timer is not None:
            self._press_sm.service_timeout_timer.start()

        self._press.motor.handle_event(event=self._press_sm.motor_rotccw_event)

        self._press_sm.move_down = True

    def up_sensor_negedge(self):
        self._press.logger.debug("%s event in %s state", self.up_sensor_negedge.__name__, self.name)

        self._press_sm.set_state(self._press_sm.outofposition_state)

    def down_sensor_negedge(self):
        self._press.logger.debug("%s event in %s state", self.down_sensor_negedge.__name__, self.name)

    def up_sensor_posedge(self):
        self._press.logger.debug("%s event in %s state", self.up_sensor_posedge.__name__, self.name)

    def down_sensor_posedge(self):
        self._press.motor.handle_event(event=self._press_sm.motor_stop_event)
        self._press.logger.debug("%s event in %s state", self.down_sensor_posedge.__name__, self.name)

        if self._press_sm.service_timeout_timer is not None:
            self._press_sm.service_timeout_timer.cancel()

        self._press_sm.move_down = False

        self._press_sm.publish_error(error_codes.PressErrorCodes.EndSwitchInUpperPos)
        self._press_sm.init_required = True
        self._press_sm.set_state(self._press_sm.error_state)

    def motor_on(self):
        self._press.logger.debug("%s event in %s state", self.motor_on.__name__, self.name)

    def motor_off(self):
        self._press.logger.debug("%s event in %s state", self.motor_off.__name__, self.name)

    def error(self):
        self._press.logger.debug("%s event in %s state", self.error.__name__, self.name)

        if self._press_sm.service_timeout_timer is not None:
            self._press_sm.service_timeout_timer.cancel()

        self._press_sm.move_down = False

        self._press_sm.set_state(self._press_sm.error_state)

    def acknowledge(self):
        self._press.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._press.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

        self._press_sm.move_down = False

        self._press_sm.publish_error(error_codes.PressErrorCodes.PressMovingDownTimeout)
        self._press_sm.init_required = True
        self._press_sm.set_state(self._press_sm.error_state)

    def force_sensor_posedge(self):
        self._press.logger.debug("%s event in %s state", self.force_sensor_posedge.__name__, self.name)

    def force_sensor_negedge(self):
        self._press.logger.debug("%s event in %s state", self.force_sensor_negedge.__name__, self.name)

    def update(self):
        self._press.logger.debug("%s event in %s state", self.update.__name__, self.name)

        self._press_sm.move_down = False

        if self._press_sm.service_timeout_timer is not None:
            self._press_sm.service_timeout_timer.cancel()

        self._press_sm.set_state(self._press_sm.checkpresspos_state)


class InBottomPosition(PressState):
    """ Concrete State class for a InBottomPosition SM """

    def __init__(self, press_sm, press, super_sm=None, isSubstate=False):
        super(InBottomPosition, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._press_sm = press_sm
        self._press = press
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._press.publisher.publish(topic="PressState", value="OnEndSwitch", sender=self._press.name)
        self._press.publisher.publish(topic="State", value="OnEndSwitch", sender=self._press.name)

        self._press_sm.move_down = False

        if self._press_sm.movedown_future and not self._press_sm.moveup_future:
            self._press_sm.movedown_future = False
            self._press_sm._current_state.move_down()
        elif not self._press_sm.movedown_future and self._press_sm.moveup_future:
            self._press_sm.moveup_future = False
            self._press_sm._current_state.move_up()
        elif self._press_sm.moveup_future and self._press_sm.movedown_future:
            self._press_sm.movedown_future = False
            self._press_sm.moveup_future = False
            self._press_sm.set_state(self._press_sm.error_state)

    def initialize(self):
        self._press.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._press_sm.set_state(self._press_sm.initialization_state)

        self._press_sm.move_up = False

    def stop(self):
        self._press.motor.handle_event(event=self._press_sm.motor_stop_event)

        self._press_sm.move_up = False

        self._press.logger.debug("%s event in %s state", self.stop.__name__, self.name)

    def move_up(self):
        self._press.logger.debug("%s event in %s state", self.move_up.__name__, self.name)

        if self._press_sm.service_timeout_timer is not None:
            self._press_sm.service_timeout_timer.start()

        self._press_sm.move_up = True

        self._press.motor.handle_event(event=self._press_sm.motor_rotcw_event)

    def move_down(self):
        self._press.logger.debug("%s event in %s state", self.move_down.__name__, self.name)
        self._press.publisher.publish(topic="State", value="OnEndSwitch", sender=self._press.name)

        self._press_sm.publish_error(error_codes.PressErrorCodes.OnEndSwitchError)
        self._press_sm.init_required = True
        self._press_sm.set_state(self._press_sm.error_state)

        # self._press_sm.publish_message(message_codes.StationMessageCodes.PressOnEndSwitch)

    def up_sensor_negedge(self):
        self._press.logger.debug("%s event in %s state", self.up_sensor_negedge.__name__, self.name)

    def down_sensor_negedge(self):
        self._press.logger.debug("%s event in %s state", self.down_sensor_negedge.__name__, self.name)
        self._press_sm.set_state(self._press_sm.outofposition_state)

    def up_sensor_posedge(self):
        self._press.logger.debug("%s event in %s state", self.up_sensor_posedge.__name__, self.name)

    def down_sensor_posedge(self):
        self._press.logger.debug("%s event in %s state", self.down_sensor_posedge.__name__, self.name)

    def motor_on(self):
        self._press.logger.debug("%s event in %s state", self.motor_on.__name__, self.name)

    def motor_off(self):
        self._press.logger.debug("%s event in %s state", self.motor_off.__name__, self.name)

    def error(self):
        self._press.logger.debug("%s event in %s state", self.error.__name__, self.name)

        if self._press_sm.service_timeout_timer is not None:
            self._press_sm.service_timeout_timer.cancel()

        self._press_sm.move_up = False

        self._press_sm.set_state(self._press_sm.error_state)

    def acknowledge(self):
        self._press.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._press.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

        self._press_sm.move_up = False

        self._press_sm.publish_error(error_codes.PressErrorCodes.PressMovingUpTimeout)
        self._press_sm.init_required = True
        self._press_sm.set_state(self._press_sm.error_state)

    def force_sensor_posedge(self):
        self._press.logger.debug("%s event in %s state", self.force_sensor_posedge.__name__, self.name)

    def force_sensor_negedge(self):
        self._press.logger.debug("%s event in %s state", self.force_sensor_negedge.__name__, self.name)

    def update(self):
        self._press.logger.debug("%s event in %s state", self.update.__name__, self.name)

        self._press_sm.move_up = False

        if self._press_sm.service_timeout_timer is not None:
            self._press_sm.service_timeout_timer.cancel()

        self._press_sm.set_state(self._press_sm.checkpresspos_state)


class InPressingPosition(PressState):
    """ Concrete State class for a InPressingPosition SM """

    def __init__(self, press_sm, press, super_sm=None, isSubstate=False):
        super(InPressingPosition, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._press_sm = press_sm
        self._press = press
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._press.logger.debug("Entering the %s state", self.name)
        self._press.publisher.publish(topic="PressState", value="InPressingPosition", sender=self._press.name)
        self._press.publisher.publish(topic="State", value="InPressingPosition", sender=self._press.name)

    def initialize(self):
        self._press.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._press_sm.set_state(self._press_sm.initialization_state)

    def stop(self):
        self._press.motor.handle_event(event=self._press_sm.motor_stop_event)
        self._press.logger.debug("%s event in %s state", self.stop.__name__, self.name)

    def move_up(self):
        self._press.logger.debug("%s event in %s state", self.move_up.__name__, self.name)

        self._press.motor.handle_event(event=self._press_sm.motor_rotcw_event)

    def move_down(self):
        self._press.logger.debug("%s event in %s state", self.move_down.__name__, self.name)
        self._press.publisher.publish(topic="State", value="InPressingPosition", sender=self._press.name)

        self._press_sm.publish_message(message_codes.StationMessageCodes.PressInPressPos)

    def up_sensor_negedge(self):
        self._press.logger.debug("%s event in %s state", self.up_sensor_negedge.__name__, self.name)

    def down_sensor_negedge(self):
        self._press.logger.debug("%s event in %s state", self.down_sensor_negedge.__name__, self.name)

    def up_sensor_posedge(self):
        self._press.logger.debug("%s event in %s state", self.up_sensor_posedge.__name__, self.name)

    def down_sensor_posedge(self):
        self._press.logger.debug("%s event in %s state", self.down_sensor_posedge.__name__, self.name)

    def motor_on(self):
        self._press.logger.debug("%s event in %s state", self.motor_on.__name__, self.name)

    def motor_off(self):
        self._press.logger.debug("%s event in %s state", self.motor_off.__name__, self.name)

    def error(self):
        self._press.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._press_sm.set_state(self._press_sm.error_state)

    def acknowledge(self):
        self._press.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._press.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def force_sensor_posedge(self):
        self._press.logger.debug("%s event in %s state", self.force_sensor_posedge.__name__, self.name)

    def force_sensor_negedge(self):
        self._press.logger.debug("%s event in %s state", self.force_sensor_negedge.__name__, self.name)
        self._press_sm.set_state(self._press_sm.outofposition_state)

    def update(self):
        self._press.logger.debug("%s event in %s state", self.update.__name__, self.name)
        self._press_sm.set_state(self._press_sm.checkpresspos_state)


class Error(PressState):
    """ Concrete State class for a Error SM """

    def __init__(self, press_sm, press, super_sm=None, isSubstate=False):
        super(Error, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._press_sm = press_sm
        self._press = press
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._press.motor.handle_event(event=self._press_sm.motor_stop_event)

        self._press.publisher.publish(topic="PressState", value="Error", sender=self._press.name)
        # self._press.publisher.publish(topic="State", value="Error", sender=self._press.name)

        self._press_sm.movedown_future = False
        self._press_sm.moveup_future = False

        if self._press_sm.init_required:
            self._press_sm.init_required = False
            self._press.publisher.publish(topic="State", value="ErrorWithInit", sender=self._press.name)
        else:
            self._press.publisher.publish(topic="State", value="Error", sender=self._press.name)


    def initialize(self):
        self._press.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._press_sm.set_state(self._press_sm.initialization_state)

    def stop(self):
        self._press.logger.debug("%s event in %s state", self.stop.__name__, self.name)

    def move_up(self):
        self._press.logger.debug("%s event in %s state", self.move_up.__name__, self.name)

    def move_down(self):
        self._press.logger.debug("%s event in %s state", self.move_down.__name__, self.name)

    def up_sensor_negedge(self):
        self._press.logger.debug("%s event in %s state", self.up_sensor_negedge.__name__, self.name)

    def down_sensor_negedge(self):
        self._press.logger.debug("%s event in %s state", self.down_sensor_negedge.__name__, self.name)

    def up_sensor_posedge(self):
        self._press.logger.debug("%s event in %s state", self.up_sensor_posedge.__name__, self.name)

    def down_sensor_posedge(self):
        self._press.logger.debug("%s event in %s state", self.down_sensor_posedge.__name__, self.name)

    def motor_on(self):
        self._press.logger.debug("%s event in %s state", self.motor_on.__name__, self.name)

    def motor_off(self):
        self._press.logger.debug("%s event in %s state", self.motor_off.__name__, self.name)

    def error(self):
        self._press.logger.debug("%s event in %s state", self.error.__name__, self.name)

    def acknowledge(self):
        self._press.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)
        self._press_sm.set_state(self._press_sm.checkpresspos_state)

    def timeout(self):
        self._press.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def force_sensor_posedge(self):
        self._press.logger.debug("%s event in %s state", self.force_sensor_posedge.__name__, self.name)

    def force_sensor_negedge(self):
        self._press.logger.debug("%s event in %s state", self.force_sensor_negedge.__name__, self.name)

    def update(self):
        self._press.logger.debug("%s event in %s state", self.update.__name__, self.name)


class PressStateMachine(object):
    """ Context class for the Station's state machine """
    def __init__(self, press, enable_timeout, timeout_interval):
        self._name = self.__class__.__name__

        self._press = press

        self._enable_timeout = enable_timeout
        self._timeout_interval = timeout_interval

        # timeout monitoring timer
        if self._enable_timeout:
            self.service_timeout_timer = MonitoringTimer(name="PressTimeoutTimer",
                                                         interval=self._timeout_interval,
                                                         callback_fnc=self.timeout_handler,
                                                         logger=self._press.logger)
        else:
            self.service_timeout_timer = None

        # event objects
        self.motor_stop_event = events.SimpleMotorInputEvent(eventID=events.SimpleMotorInputEvents.Stop,
                                                             sender=self._press.name)
        self.motor_rotcw_event = events.SimpleMotorInputEvent(eventID=events.SimpleMotorInputEvents.RotateCW,
                                                             sender=self._press.name)
        self.motor_rotccw_event = events.SimpleMotorInputEvent(eventID=events.SimpleMotorInputEvents.RotateCCW,
                                                              sender=self._press.name)
        self.sensor_update_event = events.SimpleSensorInputEvent(eventID=events.SimpleSensorInputEvents.Update,
                                                                 sender=self._press.name)
        self.timeout_event = events.PressInputEvent(eventID=events.PressInputEvents.Timeout,
                                                        sender=self._press.name)


        # state objects
        self._notinit_state = NotInitialized(self, self._press)        # rack's states instances
        self._initialization_state = Initialization(self, self._press)

        self._checkpresspos_state = CheckPressPosition(self, self._press)

        # check carriage position substates :
        self._unknouwnpos_substate = UnknownPosition(self, self._press, super_sm=self.checkpresspos_state, isSubstate=True)
        self._upsensorOff_substate = UpSensorOff(self, self._press, super_sm=self.checkpresspos_state, isSubstate=True)
        self._downsensorOff_substate = DownSensorOff(self, self._press, super_sm=self.checkpresspos_state, isSubstate=True)

        self._outofposition_state = OutOfPosition(self, self._press)
        self._inupperposition_state = InUpperPosition(self, self._press)
        self._inbottomposition_state = InBottomPosition(self, self._press)
        self._inpressingpos_state = InPressingPosition(self, self._press)

        self._error_state = Error(self, self._press)

        self._current_state = self._notinit_state
        self._current_state.enter_action()

        self.moveup_future = False
        self.movedown_future = False

        self.init_required = False  # to show that an init is needed after the error
        self.move_down = False
        self.move_up = False


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
    def checkpresspos_state(self):
        return self._checkpresspos_state

    @property
    def unknouwnpos_substate(self):
        return self._unknouwnpos_substate

    @property
    def upsensorOff_substate(self):
        return self._upsensorOff_substate

    @property
    def downsensorOff_substate(self):
        return self._downsensorOff_substate

    @property
    def outofposition_state(self):
        return self._outofposition_state

    @property
    def inupperposition_state(self):
        return self._inupperposition_state

    @property
    def inbottomposition_state(self):
        return self._inbottomposition_state

    @property
    def inpressingpos_state(self):
        return self._inpressingpos_state

    @property
    def error_state(self):
        return self._error_state

    def timeout_handler(self):
        self.init_required = True
        self.dispatch(event=self.timeout_event)

    def set_state(self, state):
        self._press.logger.debug("Switching from state %s to state %s", self.current_state.name, state.name)

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
        self._press.publisher.publish(topic="StationErrorCode",
                                                value=hex(error_code),
                                                sender=self._press.name)
        self._press.publisher.publish(topic="StationErrorDescription",
                                                value=error_codes.code_to_text[error_code],
                                                sender=self._press.name)

    def publish_message(self, message_code):
        self._press.publisher.publish(topic="StationMessageCode",
                                                value=hex(message_code),
                                                sender=self._press.name)
        self._press.publisher.publish(topic="StationMessageDescription",
                                                value=message_codes.code_to_text[message_code],
                                                sender=self._press.name)

    def dispatch(self, *args, **kwargs):

        self._press.logger.debug("%s has received a message: %s", self.name, kwargs)

        try:
            # topics coming from the publishers
            topic = kwargs["topic"]
            value = kwargs["value"]
            sender = kwargs["sender"]

            if sender == "SensorSafetyPressAtMaxLength":

                if topic == "Value":
                    if value:
                        self._current_state.down_sensor_posedge()
                    else:
                        self._current_state.down_sensor_negedge()

                elif topic == "State":

                    if value == "Error":
                        self._current_state.error()
                    elif value == "NotInitialized":
                        self._current_state.error()
                    elif value == "Initialized":
                        pass

            elif sender == "SensorLinearPosOfPress":

                if topic == "Value":
                    if value:
                        self._current_state.up_sensor_posedge()
                    else:
                        self._current_state.up_sensor_negedge()

                elif topic == "State":

                    if value == "Error":
                        self._current_state.error()
                    elif value == "NotInitialized":
                        self._current_state.error()
                    elif value == "Initialized":
                        pass

            elif sender == "SensorForceAtPressing":

                if topic == "Value":
                    if value:
                        self._current_state.force_sensor_posedge()
                    else:
                        self._current_state.force_sensor_negedge()

                elif topic == "State":

                    if value == "Error":
                        self._current_state.error()
                    elif value == "NotInitialized":
                        self._current_state.error()
                    elif value == "Initialized":
                        pass

            elif sender == "MotorPress":

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
                        self._current_state.error()
                    elif value == "Initialized":
                        pass

            elif sender == "Station":

                if topic == "Ack":
                    if value:
                        self._current_state.acknowledge()
                    else:
                        pass

        except KeyError:

            event = kwargs["event"]

            eventID = event.eventID
            sender = event.sender

            if eventID == events.PressInputEvents.Initialize:  # this a part of the service generic interface
                self._current_state.initialize()
            elif eventID == events.PressInputEvents.Ack:
                self._current_state.acknowledge()
            elif eventID == events.PressInputEvents.MoveUp:
                self._current_state.move_up()
            elif eventID == events.PressInputEvents.MoveDown:
                self._current_state.move_down()
            elif eventID == events.PressInputEvents.Stop:
                self._current_state.stop()
            elif eventID == events.PressInputEvents.Error:
                self._current_state.error()
            elif eventID == events.PressInputEvents.Timeout:
                self._current_state.timeout()
            elif eventID == events.PressInputEvents.Update:
                self._current_state.update()
            else:
                self._press.logger.debug("Unknown event : %s", event)


