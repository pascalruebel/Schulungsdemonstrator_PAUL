import logging
from activeobjects.actor import Actor, event_decorator
from communication import events
from communication.pubsub import Publisher
from activeobjects.storagerack.storagerack_sm import RackStateMachine


class StorageRack(Actor):
    """ Rack class class as an active object """
    def __init__(self, name, station, rgbled, blinker, presencesensor, diceplate_symbol, topics):
        super(StorageRack, self).__init__(name=name)

        self._name = name
        self._diceplate_symbol = diceplate_symbol
		
		#TBD Loading of information from CSV
        self.diceplate_color1 = ""
        self.diceplate_color1_quantity = 0
        self.diceplate_color2 = ""
        self.diceplate_color2_quantity = 0
        self.diceplate_color3 = ""
        self.diceplate_color3_quantity = 0

        self.__allowed_topics = ("State", "Value", "StationErrorCode", "StationErrorDescription", "StationMessageCode", "StationMessageDescription", 
		                         "PlateColor1", "QuantityOfPlateColor1", "PlateColor2", "QuantityOfPlateColor2", "PlateColor3", "QuantityOfPlateColor3")
        self.topics = topics

        self.logger = logging.getLogger(name)
        self.publisher = Publisher(self.topics, logger=self.logger,  name=name)       # publisher instance
        self.input_events = events.StorageStationInputEvent(events.StorageStationInputEvents.NoEvent, self._name) #TBD -> Use a specific event class, if needed

        self._station = station # storages rack
        self._presenceSensor = presencesensor  # rack's top sensor ref
        self._rgbLed = rgbled  # rack's bottom sensor ref
        self._blinker = blinker

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
            if topic not in self.__allowed_topics:
                raise ValueError("Unknown topic: {0}".format(topic))
        self._topics = new_topics

    def register_subscribers(self, topic, who, callback=None):
        self.publisher.register(topic, who, callback)

    @event_decorator
    def handle_event(self, *args, **kwargs):
        self._rackStateMachine.dispatch(*args, **kwargs)
