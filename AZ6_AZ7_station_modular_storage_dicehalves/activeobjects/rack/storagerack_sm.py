import abc
from communication import events
from threading import Timer
from utils import error_codes, message_codes
from utils.monitoring_timer import MonitoringTimer
import config

class RackState(metaclass=abc.ABCMeta):
    """ Abstract State class for a Rack SM """

    def __init__(self, isSubstate=False):
        self._isSubstate = isSubstate

    @property
    def isSubstate(self):
        return self._isSubstate

    @abc.abstractmethod
    def initialize(self):
        raise NotImplemented

    @abc.abstractmethod
    def postop_on(self):
        raise NotImplemented

    @abc.abstractmethod
    def postop_off(self):
        pass

    @abc.abstractmethod
    def posbottom_on(self):
        raise NotImplemented

    @abc.abstractmethod
    def posbottom_off(self):
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
    def postop_init(self):
        raise NotImplemented

    @abc.abstractmethod
    def posbottom_init(self):
        raise NotImplemented

    @abc.abstractmethod
    def update(self):
        raise NotImplemented

    @abc.abstractmethod
    def set_rack(self, new_dicehalfs_number):
        raise NotImplemented

    def enter_action(self):
        pass

    def exit_action(self):
        pass


class NotInitialized(RackState):
    """ Concrete State class for representing NotInitialized State"""

    def __init__(self, rack_sm, rack, super_sm=None, isSubstate=False):
        super(NotInitialized, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._rack = rack
        self._rack_sm = rack_sm
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._rack.rackState = "NotInitialized"
        self._rack.publisher.publish(topic="State", value="NotInitialized", sender=self._rack.name)
        self._rack.publisher.publish(topic="RackState", value=self._rack.rackState, sender=self._rack.name)

    def initialize(self):
        self._rack.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._rack_sm.set_state(self._rack_sm.initialization_state)

    def postop_on(self):
        self._rack.logger.debug("%s event in %s state", self.postop_on.__name__, self.name)

    def postop_off(self):
        self._rack.logger.debug("%s event in %s state", self.postop_off.__name__, self.name)

    def posbottom_on(self):
        self._rack.logger.debug("%s event in %s state", self.posbottom_on.__name__, self.name)

    def posbottom_off(self):
        self._rack.logger.debug("%s event in %s state", self.posbottom_off.__name__, self.name)

    def error(self):
        self._rack.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._rack_sm.set_state(self._rack_sm.error_state)

    def acknowledge(self):
        self._rack.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._rack.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def postop_init(self):
        self._rack.logger.debug("%s event in %s state", self.postop_init.__name__, self.name)

    def posbottom_init(self):
        self._rack.logger.debug("%s event in %s state", self.posbottom_init.__name__, self.name)

    def update(self):
        self._rack.logger.debug("%s event in %s state", self.update.__name__, self.name)

    def set_rack(self, new_dicehalfs_number):
        self._rack.logger.debug("%s event in %s state", self.set_rack.__name__, self.name)


class Initialization(RackState):
    """ Concrete State class for representing Initialization State. This is a composite state. """

    def __init__(self, rack_sm, rack, super_sm=None, isSubstate=False):
        super(Initialization, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._rack = rack
        self._rack_sm = rack_sm
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._rack.logger.debug("Entering the %s state", self.name)
        self._rack.rackState = "Initializing"
        self._rack.publisher.publish(topic="State", value="Initializing", sender=self._rack.name)
        self._rack.publisher.publish(topic="RackState", value=self._rack.rackState, sender=self._rack.name)

        # self._rack.dicehalfs_number = 0
        self._rack_sm.init_active = True

        # initialize sensors
        self._rack.rackSensorTop.handle_event(event=self._rack_sm.sensor_init_event)
        self._rack.rackSensorBottom.handle_event(event=self._rack_sm.sensor_init_event)

        self._rack_sm.set_state(self._rack_sm.notInit_initSubState)

    def initialize(self):
        self._rack.logger.debug("%s event in %s state", self.initialize.__name__, self.name)

    def postop_on(self):
        self._rack.logger.debug("%s event in %s state", self.postop_on.__name__, self.name)

    def postop_off(self):
        self._rack.logger.debug("%s event in %s state", self.postop_off.__name__, self.name)

    def posbottom_on(self):
        self._rack.logger.debug("%s event in %s state", self.posbottom_on.__name__, self.name)

    def posbottom_off(self):
        self._rack.logger.debug("%s event in %s state", self.posbottom_off.__name__, self.name)

    def error(self):
        self._rack.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._rack_sm.set_state(self._rack_sm.error_state)

    def acknowledge(self):
        self._rack.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._rack.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def postop_init(self):
        self._rack.logger.debug("%s event in %s state", self.postop_init.__name__, self.name)

    def posbottom_init(self):
        self._rack.logger.debug("%s event in %s state", self.posbottom_init.__name__, self.name)

    def update(self):
        self._rack.logger.debug("%s event in %s state", self.update.__name__, self.name)

    def set_rack(self, new_dicehalfs_number):
        self._rack.logger.debug("%s event in %s state", self.set_rack.__name__, self.name)


class InitSubState_NotInit(RackState):
    """ Concrete State class for representing Init Substate : NotInit"""

    def __init__(self, rack_sm, rack, super_sm=None, isSubstate=False):
        super(InitSubState_NotInit, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._rack = rack
        self._rack_sm = rack_sm
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._rack.rackState = "Init: Nothing"
        self._rack.publisher.publish(topic="RackState", value=self._rack.rackState, sender=self._rack.name)

    def initialize(self):
        self._rack.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._super_sm.initialize()

    def postop_on(self):
        self._rack.logger.debug("%s event in %s state", self.postop_on.__name__, self.name)

    def postop_off(self):
        self._rack.logger.debug("%s event in %s state", self.postop_off.__name__, self.name)

    def posbottom_on(self):
        self._rack.logger.debug("%s event in %s state", self.posbottom_on.__name__, self.name)

    def posbottom_off(self):
        self._rack.logger.debug("%s event in %s state", self.posbottom_off.__name__, self.name)

    def error(self):
        self._rack.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._super_sm.error()

    def acknowledge(self):
        self._rack.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._rack.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def postop_init(self):
        self._rack.logger.debug("%s event in %s state", self.postop_init.__name__, self.name)
        self._rack_sm.set_state(self._rack_sm.topInit_initSubState)

    def posbottom_init(self):
        self._rack.logger.debug("%s event in %s state", self.posbottom_init.__name__, self.name)
        self._rack_sm.set_state(self._rack_sm.bottomInit_initSubState)

    def update(self):
        self._rack.logger.debug("%s event in %s state", self.update.__name__, self.name)

    def set_rack(self, new_dicehalfs_number):
        self._rack.logger.debug("%s event in %s state", self.set_rack.__name__, self.name)


class InitSubState_TopInit(RackState):
    """ Concrete State class for representing Init Substate : TopInit"""

    def __init__(self, rack_sm, rack, super_sm=None, isSubstate=False):
        super(InitSubState_TopInit, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._rack = rack
        self._rack_sm = rack_sm
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._rack.rackState = "Init: TS"
        self._rack.publisher.publish(topic="RackState", value=self._rack.rackState, sender=self._rack.name)

    def initialize(self):
        self._rack.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._super_sm.initialize()

    def postop_on(self):
        self._rack.logger.debug("%s event in %s state", self.postop_on.__name__, self.name)

    def postop_off(self):
        self._rack.logger.debug("%s event in %s state", self.postop_off.__name__, self.name)

    def posbottom_on(self):
        self._rack.logger.debug("%s event in %s state", self.posbottom_on.__name__, self.name)

    def posbottom_off(self):
        self._rack.logger.debug("%s event in %s state", self.posbottom_off.__name__, self.name)

    def error(self):
        self._rack.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._super_sm.error()

    def acknowledge(self):
        self._rack.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._rack.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def postop_init(self):
        self._rack.logger.debug("%s event in %s state", self.postop_init.__name__, self.name)

    def posbottom_init(self):
        self._rack.logger.debug("%s event in %s state", self.posbottom_init.__name__, self.name)
        self._rack_sm.set_state(self._rack_sm.allInit_state)

    def update(self):
        self._rack.logger.debug("%s event in %s state", self.update.__name__, self.name)

    def set_rack(self, new_dicehalfs_number):
        self._rack.logger.debug("%s event in %s state", self.set_rack.__name__, self.name)


class InitSubState_BottomInit(RackState):
    """ Concrete State class for representing Init Substate : BottomInit"""

    def __init__(self, rack_sm, rack, super_sm=None, isSubstate=False):
        super(InitSubState_BottomInit, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._rack = rack
        self._rack_sm = rack_sm
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._rack.rackState = "Init: BS"
        self._rack.publisher.publish(topic="RackState", value=self._rack.rackState, sender=self._rack.name)

    def initialize(self):
        self._rack.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._super_sm.initialize()

    def postop_on(self):
        self._rack.logger.debug("%s event in %s state", self.postop_on.__name__, self.name)

    def postop_off(self):
        self._rack.logger.debug("%s event in %s state", self.postop_off.__name__, self.name)

    def posbottom_on(self):
        self._rack.logger.debug("%s event in %s state", self.posbottom_on.__name__, self.name)

    def posbottom_off(self):
        self._rack.logger.debug("%s event in %s state", self.posbottom_off.__name__, self.name)

    def error(self):
        self._rack.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._super_sm.error()

    def acknowledge(self):
        self._rack.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._rack.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def postop_init(self):
        self._rack.logger.debug("%s event in %s state", self.postop_init.__name__, self.name)
        self._rack_sm.set_state(self._rack_sm.allInit_state)

    def posbottom_init(self):
        self._rack.logger.debug("%s event in %s state", self.posbottom_init.__name__, self.name)

    def update(self):
        self._rack.logger.debug("%s event in %s state", self.update.__name__, self.name)

    def set_rack(self, new_dicehalfs_number):
        self._rack.logger.debug("%s event in %s state", self.set_rack.__name__, self.name)


class InitSubState_AllInit(RackState):
    """ Concrete State class for representing Init Substate : AllInit"""

    def __init__(self, rack_sm, rack, super_sm=None, isSubstate=False):
        super(InitSubState_AllInit, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._rack = rack
        self._rack_sm = rack_sm
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._rack.logger.debug("Entering the %s state", self.name)
        self._rack.rackState = "Initialized"
        self._rack.publisher.publish(topic="State", value="Initialized", sender=self._rack.name)
        self._rack.publisher.publish(topic="RackState", value=self._rack.rackState, sender=self._rack.name)
        self._rack_sm.set_state(self._rack_sm.unknownpos_state)

    def initialize(self):
        self._rack.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._super_sm.initialize()

    def postop_on(self):
        self._rack.logger.debug("%s event in %s state", self.postop_on.__name__, self.name)

    def postop_off(self):
        self._rack.logger.debug("%s event in %s state", self.postop_off.__name__, self.name)

    def posbottom_on(self):
        self._rack.logger.debug("%s event in %s state", self.posbottom_on.__name__, self.name)

    def posbottom_off(self):
        self._rack.logger.debug("%s event in %s state", self.posbottom_off.__name__, self.name)

    def error(self):
        self._rack.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._super_sm.error()

    def acknowledge(self):
        self._rack.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._rack.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def postop_init(self):
        self._rack.logger.debug("%s event in %s state", self.postop_init.__name__, self.name)

    def posbottom_init(self):
        self._rack.logger.debug("%s event in %s state", self.posbottom_init.__name__, self.name)

    def update(self):
        self._rack.logger.debug("%s event in %s state", self.update.__name__, self.name)

    def set_rack(self, new_dicehalfs_number):
        self._rack.logger.debug("%s event in %s state", self.set_rack.__name__, self.name)


class UnknownPosition(RackState):
    """ Concrete State class for representing UnknownPosition State"""

    def __init__(self, rack_sm, rack, super_sm=None, isSubstate=False):
        super(UnknownPosition, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._rack = rack
        self._rack_sm = rack_sm
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._rack.logger.debug("Entering the %s state", self.name)
        self._rack.rackState = "UpdatingSensors"
        self._rack.publisher.publish(topic="State", value="UpdatingSensors", sender=self._rack.name)
        self._rack.publisher.publish(topic="RackState", value=self._rack.rackState, sender=self._rack.name)

        # create Update event to check sensors' current states
        self._rack.rackSensorTop.handle_event(event=self._rack_sm.sensor_update_event)
        self._rack.rackSensorBottom.handle_event(event=self._rack_sm.sensor_update_event)

    def initialize(self):
        self._rack.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._rack_sm.set_state(self._rack_sm.initialization_state)

    def postop_on(self):
        self._rack.logger.debug("%s event in %s state", self.postop_on.__name__, self.name)
        self._rack_sm.set_state(self._rack_sm.checkrackfull_state)

    def postop_off(self):
        self._rack.logger.debug("%s event in %s state", self.postop_off.__name__, self.name)

    def posbottom_on(self):
        self._rack.logger.debug("%s event in %s state", self.posbottom_on.__name__, self.name)
        self._rack_sm.set_state(self._rack_sm.rackfilling_state)

    def posbottom_off(self):
        self._rack.logger.debug("%s event in %s state", self.posbottom_off.__name__, self.name)
        self._rack_sm.set_state(self._rack_sm.rackempty_state)

    def error(self):
        self._rack.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._rack_sm.set_state(self._rack_sm.error_state)

    def acknowledge(self):
        self._rack.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._rack.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def postop_init(self):
        self._rack.logger.debug("%s event in %s state", self.postop_init.__name__, self.name)

    def posbottom_init(self):
        self._rack.logger.debug("%s event in %s state", self.posbottom_init.__name__, self.name)

    def update(self):
        self._rack.logger.debug("%s event in %s state", self.update.__name__, self.name)

    def set_rack(self, new_dicehalfs_number):
        self._rack.logger.debug("%s event in %s state", self.set_rack.__name__, self.name)

        # self._rack.dicehalfs_number = new_dicehalfs_number


class RackEmpty(RackState):
    """ Concrete State class for representing RackEmpty State"""

    def __init__(self, rack_sm, rack, super_sm=None, isSubstate=False):
        super(RackEmpty, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._rack = rack
        self._rack_sm = rack_sm
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._rack.logger.debug("Entering the %s state", self.name)
        self._rack.rackState = "RackEmpty"
        self._rack.publisher.publish(topic="State", value="RackEmpty", sender=self._rack.name)
        self._rack.publisher.publish(topic="RackState", value=self._rack.rackState, sender=self._rack.name)

        self._rack.dicehalfs_number = 0

    def initialize(self):
        self._rack.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._rack_sm.set_state(self._rack_sm.initialization_state)

    def postop_on(self):
        self._rack.logger.debug("%s event in %s state", self.postop_on.__name__, self.name)

    def postop_off(self):
        self._rack.logger.debug("%s event in %s state", self.postop_off.__name__, self.name)

    def posbottom_on(self):
        self._rack.logger.debug("%s event in %s state", self.posbottom_on.__name__, self.name)

        self._rack.inc_dicehalfs()

        self._rack_sm.set_state(self._rack_sm.rackfilling_state)

    def posbottom_off(self):
        self._rack.logger.debug("%s event in %s state", self.posbottom_off.__name__, self.name)

    def error(self):
        self._rack.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._rack_sm.set_state(self._rack_sm.error_state)

    def acknowledge(self):
        self._rack.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._rack.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def postop_init(self):
        self._rack.logger.debug("%s event in %s state", self.postop_init.__name__, self.name)

    def posbottom_init(self):
        self._rack.logger.debug("%s event in %s state", self.posbottom_init.__name__, self.name)

    def update(self):
        self._rack.logger.debug("%s event in %s state", self.update.__name__, self.name)
        self._rack_sm.set_state(self._rack_sm.unknownpos_state)

    def set_rack(self, new_dicehalfs_number):
        self._rack.logger.debug("%s event in %s state", self.set_rack.__name__, self.name)

        if new_dicehalfs_number != 0:
            self._rack_sm.publish_error(error_codes.RackErrorCodes.RackEmptyDicehalfsNum)
            self._rack_sm.set_state(self._rack_sm.error_state)


class RackFilling(RackState):
    """ Concrete State class for representing RackFilling State"""

    def __init__(self, rack_sm, rack, super_sm=None, isSubstate=False):
        super(RackFilling, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._rack = rack
        self._rack_sm = rack_sm
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._rack.rackState = "RackFilling"
        self._rack.publisher.publish(topic="State", value="RackFilling", sender=self._rack.name)
        self._rack.publisher.publish(topic="RackState", value=self._rack.rackState, sender=self._rack.name)

        if self._rack.dicehalfs_number == 0:
            self._rack.inc_dicehalfs()

    def initialize(self):
        self._rack.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._rack_sm.set_state(self._rack_sm.initialization_state)

    def postop_on(self):
        self._rack.logger.debug("%s event in %s state", self.postop_on.__name__, self.name)
        self._rack_sm.set_state(self._rack_sm.checkrackfull_state)

    def postop_off(self):
        self._rack.logger.debug("%s event in %s state", self.postop_off.__name__, self.name)

    def posbottom_on(self):
        self._rack.logger.debug("%s event in %s state", self.posbottom_on.__name__, self.name)

    def posbottom_off(self):
        self._rack.logger.debug("%s event in %s state", self.posbottom_off.__name__, self.name)
        self._rack_sm.set_state(self._rack_sm.rackempty_state)

    def error(self):
        self._rack.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._rack_sm.set_state(self._rack_sm.error_state)

    def acknowledge(self):
        self._rack.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._rack.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def postop_init(self):
        self._rack.logger.debug("%s event in %s state", self.postop_init.__name__, self.name)

    def posbottom_init(self):
        self._rack.logger.debug("%s event in %s state", self.posbottom_init.__name__, self.name)

    def update(self):
        self._rack.logger.debug("%s event in %s state", self.update.__name__, self.name)
        self._rack_sm.set_state(self._rack_sm.unknownpos_state)

    def set_rack(self, new_dicehalfs_number):
        self._rack.logger.debug("%s event in %s state", self.set_rack.__name__, self.name)

        if (new_dicehalfs_number > 0) and (new_dicehalfs_number <= self._rack.dicehalfs_maximun):
            self._rack.dicehalfs_number = new_dicehalfs_number
        elif new_dicehalfs_number < 0:
            self._rack_sm.publish_error(error_codes.RackErrorCodes.RackNegDicehalfsNum)

            self._rack_sm.set_state(self._rack_sm.error_state)

        elif new_dicehalfs_number == 0:
            self._rack_sm.publish_error(error_codes.RackErrorCodes.NotEmptyRack)

            self._rack_sm.set_state(self._rack_sm.error_state)

        elif new_dicehalfs_number > self._rack.dicehalfs_maximun:
            self._rack_sm.publish_error(error_codes.RackErrorCodes.RackDicehalfsNumMaximum)

            self._rack_sm.set_state(self._rack_sm.error_state)


class CheckRackFull(RackState):
    """ Concrete State class for representing CheckRackFull State"""

    def __init__(self, rack_sm, rack, super_sm=None, isSubstate=False):
        super(CheckRackFull, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._rack = rack
        self._rack_sm = rack_sm
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._rack.logger.debug("Entering the %s state", self.name)
        self._rack.rackState = "CheckRackFull"
        self._rack.publisher.publish(topic="RackState", value=self._rack.rackState, sender=self._rack.name)

        if self._rack_sm.checkfull_timer.timer_alive():
            self._rack_sm.checkfull_timer.cancel()
        self._rack_sm.checkfull_timer.start()

    def initialize(self):
        self._rack.logger.debug("%s event in %s state", self.initialize.__name__, self.name)

        if self._rack_sm.checkfull_timer.timer_alive():
            self._rack_sm.checkfull_timer.cancel()

        self._rack_sm.set_state(self._rack_sm.initialization_state)

    def postop_on(self):
        self._rack.logger.debug("%s event in %s state", self.postop_on.__name__, self.name)

    def postop_off(self):
        self._rack.logger.debug("%s event in %s state", self.postop_off.__name__, self.name)

        if self._rack_sm.checkfull_timer.timer_alive():
            self._rack_sm.checkfull_timer.cancel()

        self._rack.inc_dicehalfs()

        self._rack_sm.set_state(self._rack_sm.rackfilling_state)

    def posbottom_on(self):
        self._rack.logger.debug("%s event in %s state", self.posbottom_on.__name__, self.name)

    def posbottom_off(self):
        self._rack.logger.debug("%s event in %s state", self.posbottom_off.__name__, self.name)

    def error(self):
        self._rack.logger.debug("%s event in %s state", self.error.__name__, self.name)

        if self._rack_sm.checkfull_timer.timer_alive():
            self._rack_sm.checkfull_timer.cancel()

        self._rack_sm.set_state(self._rack_sm.error_state)

    def acknowledge(self):
        self._rack.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._rack.logger.debug("%s event in %s state", self.timeout.__name__, self.name)
        self._rack_sm.set_state(self._rack_sm.rackfull_state)

    def postop_init(self):
        self._rack.logger.debug("%s event in %s state", self.postop_init.__name__, self.name)

    def posbottom_init(self):
        self._rack.logger.debug("%s event in %s state", self.posbottom_init.__name__, self.name)

    def update(self):
        self._rack.logger.debug("%s event in %s state", self.update.__name__, self.name)

        if self._rack_sm.checkfull_timer.timer_alive():
            self._rack_sm.checkfull_timer.cancel()

        self._rack_sm.set_state(self._rack_sm.unknownpos_state)

    def set_rack(self, new_dicehalfs_number):
        self._rack.logger.debug("%s event in %s state", self.set_rack.__name__, self.name)

        # self._rack.dicehalfs_number = new_dicehalfs_number


class RackFull(RackState):
    """ Concrete State class for representing RackFull State"""

    def __init__(self, rack_sm, rack, super_sm=None, isSubstate=False):
        super(RackFull, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._rack = rack
        self._rack_sm = rack_sm
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._rack.rackState = "RackFull"
        self._rack.publisher.publish(topic="State", value="RackFull", sender=self._rack.name)
        self._rack.publisher.publish(topic="RackState", value=self._rack.rackState, sender=self._rack.name)

        # test functionality :
        if self._rack_sm.init_active:
            self._rack_sm.init_active = False
            self._rack.dicehalfs_number = self._rack.dicehalfs_maximun
        else:
            if self._rack.dicehalfs_number < (self._rack.dicehalfs_maximun-1):
                # not in clamping position error :
                self._rack_sm.publish_error(error_codes.RackErrorCodes.RackErrorByDiceCounting)

                self._rack_sm.set_state(self._rack_sm.error_state)
            else:
                self._rack.dicehalfs_number = self._rack.dicehalfs_maximun

    def initialize(self):
        self._rack.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._rack_sm.set_state(self._rack_sm.initialization_state)

    def postop_on(self):
        self._rack.logger.debug("%s event in %s state", self.postop_on.__name__, self.name)

    def postop_off(self):
        self._rack.logger.debug("%s event in %s state", self.postop_off.__name__, self.name)
        self._rack_sm.set_state(self._rack_sm.rackfilling_state)

    def posbottom_on(self):
        self._rack.logger.debug("%s event in %s state", self.posbottom_on.__name__, self.name)

    def posbottom_off(self):
        self._rack.logger.debug("%s event in %s state", self.posbottom_off.__name__, self.name)

    def error(self):
        self._rack.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._rack_sm.set_state(self._rack_sm.error_state)

    def acknowledge(self):
        self._rack.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._rack.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def postop_init(self):
        self._rack.logger.debug("%s event in %s state", self.postop_init.__name__, self.name)

    def posbottom_init(self):
        self._rack.logger.debug("%s event in %s state", self.posbottom_init.__name__, self.name)

    def update(self):
        self._rack.logger.debug("%s event in %s state", self.update.__name__, self.name)
        self._rack_sm.set_state(self._rack_sm.unknownpos_state)

    def set_rack(self, new_dicehalfs_number):
        self._rack.logger.debug("%s event in %s state", self.set_rack.__name__, self.name)

        if new_dicehalfs_number != self._rack.dicehalfs_maximun:
            self._rack_sm.publish_error(error_codes.RackErrorCodes.WrongNumRackFull)
            self._rack_sm.set_state(self._rack_sm.error_state)


class Error(RackState):
    """ Concrete State class for representing Error State"""

    def __init__(self, rack_sm, rack, super_sm=None, isSubstate=False):
        super(Error, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._rack = rack
        self._rack_sm = rack_sm
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._rack.rackState = "Error"
        self._rack.publisher.publish(topic="State", value=self._rack.rackState, sender=self._rack.name)
        self._rack.publisher.publish(topic="RackState", value="Error", sender=self._rack.name)

        self._rack_sm.init_active = False

    def initialize(self):
        self._rack.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._rack_sm.set_state(self._rack_sm.initialization_state)

    def postop_on(self):
        self._rack.logger.debug("%s event in %s state", self.postop_on.__name__, self.name)

    def postop_off(self):
        self._rack.logger.debug("%s event in %s state", self.postop_off.__name__, self.name)

    def posbottom_on(self):
        self._rack.logger.debug("%s event in %s state", self.posbottom_on.__name__, self.name)

    def posbottom_off(self):
        self._rack.logger.debug("%s event in %s state", self.posbottom_off.__name__, self.name)

    def error(self):
        self._rack.logger.debug("%s event in %s state", self.error.__name__, self.name)

    def acknowledge(self):
        self._rack.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)
        self._rack_sm.set_state(self._rack_sm.unknownpos_state)

    def timeout(self):
        self._rack.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def postop_init(self):
        self._rack.logger.debug("%s event in %s state", self.postop_init.__name__, self.name)

    def posbottom_init(self):
        self._rack.logger.debug("%s event in %s state", self.posbottom_init.__name__, self.name)

    def update(self):
        self._rack.logger.debug("%s event in %s state", self.update.__name__, self.name)

    def set_rack(self, new_dicehalfs_number):
        self._rack.logger.debug("%s event in %s state", self.set_rack.__name__, self.name)

        # self._rack.dicehalfs_number = new_dicehalfs_number


class RackStateMachine(object):
    """ Context class for the Rack's state machine """

    def __init__(self, rack):
        self._name = self.__class__.__name__
        self.init_active = False
        self._rack = rack

        self.checkfull_timer = MonitoringTimer(name="RackCheckFulltTimer",
                                                interval=config.STATION_CONFIG['rackFullCheckInterval'],
                                                callback_fnc=self.timeout_handler,
                                                logger=self._rack.logger)



# events objects:
        self.sensor_init_event = events.SimpleSensorInputEvent(eventID=events.SimpleSensorInputEvents.Initialize,
                                                               sender=self._rack.name)
        self.sensor_update_event = events.SimpleSensorInputEvent(eventID=events.SimpleSensorInputEvents.Update,
                                                                 sender=self._rack.name)
        self.timeout_event = events.RackEvent(eventID=events.RackEvents.Timeout, sender=self._rack.name)

# rack's states instances
        self._notinit_state = NotInitialized(self, self._rack)
        self._initialization_state = Initialization(self, self._rack)

        # initialization substates :
        self._notInit_initSubState = InitSubState_NotInit(self, self._rack, super_sm=self.initialization_state, isSubstate=True)
        self._topInit_initSubState = InitSubState_TopInit(self, self._rack, super_sm=self.initialization_state, isSubstate=True)
        self._bottomInit_initSubState = InitSubState_BottomInit(self, self._rack, super_sm=self.initialization_state, isSubstate=True)
        self._allInit_state = InitSubState_AllInit(self, self._rack, super_sm=self.initialization_state, isSubstate=True)

        self._unknownpos_state = UnknownPosition(self, self._rack)
        self._rackfilling_state = RackFilling(self, self._rack)
        self._rackempty_state = RackEmpty(self, self._rack)
        self._rackfull_state = RackFull(self, self._rack)
        self._checkrackfull_state = CheckRackFull(self, self._rack)
        self._error_state = Error(self, self._rack)

        self._current_state = self._notinit_state
        self.set_state(self._current_state)

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
    def notInit_initSubState(self):
        return self._notInit_initSubState

    @property
    def topInit_initSubState(self):
        return self._topInit_initSubState

    @property
    def bottomInit_initSubState(self):
        return self._bottomInit_initSubState

    @property
    def allInit_state(self):
        return self._allInit_state

    @property
    def unknownpos_state(self):
        return self._unknownpos_state

    @property
    def rackfilling_state(self):
        return self._rackfilling_state

    @property
    def rackempty_state(self):
        return self._rackempty_state

    @property
    def rackfull_state(self):
        return self._rackfull_state

    @property
    def checkrackfull_state(self):
        return self._checkrackfull_state

    @property
    def error_state(self):
        return self._error_state

    def set_state(self, state):
        self._rack.logger.debug("Switching from state %s to state %s", self.current_state.name, state.name)

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
        self._rack.handle_event(event=self.timeout_event)

    def publish_error(self, error_code):
        self._rack.publisher.publish(topic="StationErrorCode",
                                              value=hex(error_code),
                                              sender=self._rack.name)
        self._rack.publisher.publish(topic="StationErrorDescription",
                                              value=error_codes.code_to_text[error_code],
                                              sender=self._rack.name)

    def publish_message(self, message_code):
        self._rack.publisher.publish(topic="StationMessageCode",
                                                value=hex(message_code),
                                                sender=self._rack.name)
        self._rack.publisher.publish(topic="StationMessageDescription",
                                                value=message_codes.code_to_text[message_code],
                                                sender=self._rack.name)

    def dispatch(self, *args, **kwargs):
        self._rack.logger.debug("%s has received a message: %s", self.name, kwargs)

        try:
            # topics coming from the publishers
            topic = kwargs["topic"]
            value = kwargs["value"]
            sender = kwargs["sender"]

            if sender == "SensorFillLevelPosTop":

                if topic == "Value":
                    if value:
                        self._current_state.postop_on()
                    else:
                        self._current_state.postop_off()

                elif topic == "State":

                    if value == "Error":
                        self._current_state.error()
                    elif value == "NotInitialized":
                        pass
                        # self._current_state.error()
                    elif value == "Initialized":
                        self._current_state.postop_init()

            elif sender == "SensorFillLevelPosBottom":

                if topic == "Value":
                    if value:
                        self._current_state.posbottom_on()
                    else:
                        self._current_state.posbottom_off()

                elif topic == "State":

                    if value == "Error":
                        self._current_state.error()
                    elif value == "NotInitialized":
                        pass
                        # self._current_state.error()
                    elif value == "Initialized":
                        self._current_state.posbottom_init()

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

                if eventID == self._rack.rack_events.eventIDs.Initialize:  # this a part of the service generic interface
                    self._current_state.initialize()
                elif eventID == self._rack.rack_events.eventIDs.Ack:
                    self._current_state.acknowledge()
                elif eventID == self._rack.rack_events.eventIDs.SetRack:

                    self._current_state.set_rack(new_dicehalfs_number=event.dicehalfs_number)
                    # self._rack.dicehalfs_number = event.dicehalfs_number

                elif eventID == self._rack.rack_events.eventIDs.DecRack:

                    self._rack.dec_dicehalfs()

                elif eventID == self._rack.rack_events.eventIDs.Error:
                    self._current_state.error()
                elif eventID == self._rack.rack_events.eventIDs.Timeout:
                    self._current_state.timeout()
                elif eventID == self._rack.rack_events.eventIDs.Update:
                    self._current_state.update()
                else:
                    self._rack.logger.debug("Unknown event : %s", event)

            except KeyError:
                self._rack.logger.debug("Unknown event : %s", kwargs)


