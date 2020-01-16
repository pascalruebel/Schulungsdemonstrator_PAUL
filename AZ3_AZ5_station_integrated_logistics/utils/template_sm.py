""" This is a template state machine with a composite State2 """

import abc
from utils.logger import Logger

class BaseState(metaclass=abc.ABCMeta):
    """ Abstract base state class """
    def __init__(self, isSubstate=False):
        self._isSubstate = isSubstate

    @property
    def isSubstate(self):
        return self._isSubstate

    @abc.abstractmethod
    def toState1(self):
        raise NotImplemented

    @abc.abstractmethod
    def toState2(self):
        raise NotImplemented

    @abc.abstractmethod
    def toStateA(self):
        """ to State2 : SubstateA """
        raise NotImplemented

    @abc.abstractmethod
    def toStateB(self):
        """ to State2 : Substateb """
        raise NotImplemented

    def enter_action(self):
        pass

    def exit_action(self):
        pass


class State1(BaseState):
    """ Concrete class for the complex State1 """
    def __init__(self, context_sm, super_sm=None, isSubstate=False):
        super(State1, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._context_sm = context_sm
        self._super_sm = super_sm  # super or enclosing state


    def enter_action(self):
        self._context_sm._logger.debug("Entering the %s state", self.name)

    def exit_action(self):
        self._context_sm._logger.debug("Exiting the %s state", self.name)

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def toState1(self):
        self._context_sm._logger.debug("%s event in %s state", self.toState1.__name__, self.name)

    def toState2(self):
        self._context_sm._logger.debug("%s event in %s state", self.toState2.__name__, self.name)
        self._context_sm.set_state(self._context_sm.state2)

    def toStateA(self):
        self._context_sm._logger.debug("%s event in %s state", self.toStateA.__name__, self.name)

    def toStateB(self):
        self._context_sm._logger.debug("%s event in %s state", self.toStateB.__name__, self.name)


class State2(BaseState):
    """ Concrete class for State2 """
    def __init__(self, context_sm, super_sm=None, isSubstate=False):
        super(State2, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._context_sm = context_sm
        self._super_sm = super_sm  # super or enclosing state

    def enter_action(self):
        self._context_sm._logger.debug("Entering the %s state", self.name)
        self._context_sm.set_state(self._context_sm.substateA)

    def exit_action(self):
        self._context_sm._logger.debug("Exiting the %s state", self.name)

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def toState1(self):
        self._context_sm._logger.debug("%s event in %s state", self.toState1.__name__, self.name)
        self._context_sm.set_state(self._context_sm.state1)

    def toState2(self):
        self._context_sm._logger.debug("%s event in %s state", self.toState2.__name__, self.name)
        self._context_sm.set_state(self._context_sm.state2)

    def toStateA(self):
        self._context_sm._logger.debug("%s event in %s state", self.toStateA.__name__, self.name)

    def toStateB(self):
        self._context_sm._logger.debug("%s event in %s state", self.toStateB.__name__, self.name)


class SubStateA(BaseState):
    """ Concrete class for the substate A of the complex State2 """
    def __init__(self, context_sm, super_sm=None, isSubstate=False):
        super(SubStateA, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._context_sm = context_sm
        self._super_sm = super_sm  # super or enclosing state

    def enter_action(self):
        self._context_sm._logger.debug("Entering the %s state", self.name)

    def exit_action(self):
        self._context_sm._logger.debug("Exiting the %s state", self.name)

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def toState1(self):
        self._context_sm._logger.debug("%s event in %s state", self.toState1.__name__, self.name)
        self._super_sm.toState1()

    def toState2(self):
        self._context_sm._logger.debug("%s event in %s state", self.toState2.__name__, self.name)

    def toStateA(self):
        self._context_sm._logger.debug("%s event in %s state", self.toStateA.__name__, self.name)

    def toStateB(self):
        self._context_sm._logger.debug("%s event in %s state", self.toStateB.__name__, self.name)
        self._context_sm.set_state(self._context_sm.substateB)


class SubStateB(BaseState):
    """ Concrete class for the substate B of the complex State2 """
    def __init__(self, context_sm, super_sm=None, isSubstate=False):
        super(SubStateB, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._context_sm = context_sm
        self._super_sm = super_sm  # super or enclosing state

    def enter_action(self):
        self._context_sm._logger.debug("Entering the %s state", self.name)

    def exit_action(self):
        self._context_sm._logger.debug("Exiting the %s state", self.name)

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def toState1(self):
        self._context_sm._logger.debug("%s event in %s state", self.toState1.__name__, self.name)
        self._super_sm.toState1()

    def toState2(self):
        self._context_sm._logger.debug("%s event in %s state", self.toState2.__name__, self.name)
        self._super_sm.toState2()

    def toStateA(self):
        self._context_sm._logger.debug("%s event in %s state", self.toStateA.__name__, self.name)
        self._context_sm.set_state(self._context_sm.substateA)

    def toStateB(self):
        self._context_sm._logger.debug("%s event in %s state", self.toStateB.__name__, self.name)


class StateMachine(object):
    """ Context state machine """
    def __init__(self, logger):
        self._name = self.__class__.__name__

        self._logger = logger

        self._state1 = State1(self)
        self._state2 = State2(self)
        self._substateA = SubStateA(self, super_sm=self._state2, isSubstate=True)
        self._substateB = SubStateB(self, super_sm=self._state2, isSubstate=True)

        self._current_state = self.state1
        self._current_state.enter_action()


    @property
    def name(self):
        return self._name

    @property
    def current_state(self):
        return self._current_state

    @property
    def state1(self):
        return self._state1

    @property
    def state2(self):
        return self._state2

    @property
    def substateA(self):
        return self._substateA

    @property
    def substateB(self):
        return self._substateB

    def set_state(self, state):
        self._logger.debug("Switching from state %s to state %s", self.current_state.name, state.name)

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
        try:
            topic = kwargs["topic"]
            value = kwargs["value"]

            if topic == "event" and value == "toState1":
                self._current_state.toState1()
            elif topic == "event" and value == "toState2":
                self._current_state.toState2()
            elif topic == "event" and value == "toStateA":
                self._current_state.toStateA()
            elif topic == "event" and value == "toStateB":
                self._current_state.toStateB()
            else:
                raise NotImplemented

        except KeyError:
            self._logger.debug("The event was not defined properly")





logger_sm = Logger.setup_logging("Template State Machine")
templateSM = StateMachine(logger=logger_sm)


templateSM.dispatch(topic="event", value="toState2")
templateSM.dispatch(topic="event", value="toStateB")
templateSM.dispatch(topic="event", value="toState2")
templateSM.dispatch(topic="event", value="toStateB")
templateSM.dispatch(topic="event", value="toState2")
templateSM.dispatch(topic="event", value="toStateB")
templateSM.dispatch(topic="event", value="toState1")
