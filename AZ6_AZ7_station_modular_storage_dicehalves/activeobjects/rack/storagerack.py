import logging
from activeobjects.actor import Actor, event_decorator
from communication import events
from communication.pubsub import Publisher
from activeobjects.rack.storagerack_sm import RackStateMachine


class Rack(Actor):
    """ Rack class class as an active object """
    def __init__(self, name, sensor_top, sensor_bottom, dicehalfs_maximun=10, topics=None):
        super(Rack, self).__init__(name=name)
        self._name = name
        self.__dicehalfs_maximun = dicehalfs_maximun

        self.rackState = "notInitialized"
        self.allowed_topics = ('RackState', 'State', 'NumberOfCurrentlyStoredDicehalves',
                               'StationErrorCode','StationErrorDescription',
                               'StationMessageCode', 'StationMessageDescription')
        if topics is None:
            self.topics = self.allowed_topics
        else:
            self.topics = topics

        self.rackSensorTop = sensor_top  # rack's top sensor ref
        self.rackSensorBottom = sensor_bottom  # rack's bottom sensor ref

        self.logger = logging.getLogger(name)
        self.publisher = Publisher(self.topics, logger=self.logger,  name=name)  # publisher object

        self.dicehalfs_number = 0

        self.rack_events = events.RackEvent(events.RackEvents.NoEvent, self._name)

        self._rackStateMachine = RackStateMachine(self)  # rack's active state machine object

    @property
    def name(self):
        return self._name

    @property
    def topics(self):
        return self._topics

    @topics.setter
    def topics(self, new_topics):
        for topic in new_topics:
            if topic not in self.allowed_topics:
                raise ValueError("Unknown topic: {0}".format(topic))
        self._topics = new_topics

    def register_subscribers(self, topic, who, callback=None):
        self.publisher.register(topic, who, callback)

    @property
    def dicehalfs_number(self):
        return self._dicehalfs_number

    @property
    def dicehalfs_maximun(self):
        return self.__dicehalfs_maximun

    @dicehalfs_number.setter
    def dicehalfs_number(self, new_number):
        if (new_number <= self.__dicehalfs_maximun) and (new_number >= 0):
            self._dicehalfs_number = new_number

        self.publisher.publish(topic="NumberOfCurrentlyStoredDicehalves", value=self.dicehalfs_number, sender=self.name)

    def inc_dicehalfs(self):
        if self.dicehalfs_number >= self.__dicehalfs_maximun:
            self.dicehalfs_number = self.__dicehalfs_maximun
        else:
            self.dicehalfs_number = self.dicehalfs_number + 1

    def dec_dicehalfs(self):
        if self.dicehalfs_number >= 1:
            self.dicehalfs_number = self.dicehalfs_number - 1
        else:
            self.dicehalfs_number = 0

    @event_decorator
    def handle_event(self, *args, **kwargs):
        self._rackStateMachine.dispatch(*args, **kwargs)






