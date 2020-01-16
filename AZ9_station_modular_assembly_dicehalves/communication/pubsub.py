from utils.logger import Logger

class Publisher(object,):
    """ Simple publisher class for the observer pattern"""
    def __init__(self, topics, logger, name=None):
        # creating an empty subscribers dict for every topic
        self.topics = {topic: dict() for topic in topics}
        self._name = name
        self._logger = logger

    def register(self, topic, who, callback=None):
        if callback is None:
            callback = who.update
        self._logger.debug("%s is subscribed on topic: %s, from %s", who.name, topic, self._name)
        subscribers = self.topics[topic]
        subscribers[who] = callback

    def publish(self, *args, **kwargs):
        # ToDo error handling with try ?
        # self._logger.debug("%s publishes %s", self._name,  kwargs)
        topic = kwargs["topic"]
        subscribers = self.topics[topic]
        for subscriber, callback in subscribers.items():
            callback(*args, **kwargs)




