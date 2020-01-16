import logging
from activeobjects.actor import Actor, event_decorator
from activeobjects.station.station_sm import StationStateMachine
from communication.pubsub import Publisher
from communication import events


class Station(Actor):
    """ Storage Station class as an active object """
    def __init__(self, name, status_led, blinker, topics=None):
        super(Station, self).__init__(name=name)
        self._name = name
        self._stationState = "notInitialized"
        self.__allowedStationStates = ('NoConnection', 'Starting', 'notInitialized', 'Standby', 'Ready', 'Running', 'Error')

        self.callable_services = dict()  # dict of services that can be called from this service
        self.service_users = dict()  # dict of service users

        self.__allowed_topics = ('StationState', 'Ack', 'StationErrorCode', 'StationErrorDescription',
                                 'StationSafetyState', 'StationMessageCode', 'StationMessageDescription',
                                 'StationStateMaintenance')
        if topics is None:
            self.topics = self.__allowed_topics
        else:
            self.topics = topics

        self.logger = logging.getLogger(name)
        self.publisher = Publisher(self.topics, logger=self.logger, name=self._name)  # publisher instance

        self.status_led = status_led
        self.blinker = blinker

        self._homing_required = False

        self._stationStateMachine = StationStateMachine(self, self._homing_required)  # state machine instance

    @property
    def name(self):
        return self._name

    @property
    def stationState(self):
        return self._stationState

    @stationState.setter
    def stationState(self, new_stationState):
        if new_stationState not in self.__allowedStationStates:
            raise ValueError("Unknown stationState: {0}".format(new_stationState))
        self._stationState = new_stationState

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
        if topic not in self.__allowed_topics:
            raise ValueError("Unknown topic")
        self.publisher.register(topic, who, callback)

    def register_services(self, service_index, service_interface):
        """ Register services to be called from this service """
        self.callable_services[service_index] = service_interface

    def setup_service(self, service_index, service_interface):
        """ Setup of this service as callable from another service """
        self.service_users[service_index] = service_interface

    @event_decorator
    def handle_event(self, *args, **kwargs):
        self._stationStateMachine.dispatch(*args, **kwargs)




