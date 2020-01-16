
class SimpleEventBaseClass(object):
    """ Simple event class """

    def __init__(self, eventID, sender):
        self.eventID = eventID
        self.sender = sender

    def __repr__(self):
        return str(self.eventID) + ',' + str(self.sender)

    @property
    def eventID(self):
        return self._eventID

    @eventID.setter
    def eventID(self, new_eventID):
        # perform some checking
        self._eventID = new_eventID

    @property
    def sender(self):
        return self._sender

    @sender.setter
    def sender(self, new_sender):
        # perform some checking
        self._sender = new_sender


class BaseInputEvents(object):
    NoEvent = 'none'
    Initialize = 'initialize'
    Ack = 'ack'
    Error = 'error'
    Timeout = 'timeout'
    Update = 'update'


class BaseInputEvent(SimpleEventBaseClass):
    """ Base events class """

    def __init__(self, eventID, sender):
        super(BaseInputEvent, self).__init__(eventID, sender)
        self._eventIDs = BaseInputEvents()

    @property
    def eventIDs(self):
        return self._eventIDs


class SimpleEventBaseClass(object):
    """ Simple event class """

    def __init__(self, eventID, sender):
        self.eventID = eventID
        self.sender = sender

    def __repr__(self):
        return str(self.eventID) + ',' + str(self.sender)

    @property
    def eventID(self):
        return self._eventID

    @eventID.setter
    def eventID(self, new_eventID):
        # perform some checking
        self._eventID = new_eventID

    @property
    def sender(self):
        return self._sender

    @sender.setter
    def sender(self, new_sender):
        # perform some checking
        self._sender = new_sender


class RGBLEDInputEvents(object):
    NoEvent = 'none'
    Initialize = 'initialize'
    Red = 'red'
    Blue = 'blue'
    Green = 'green'
    Yellow = 'yellow'
    Purple = 'purple'
    Off = 'off'
    Ack = 'ack'
    Error = 'error'
    Timeout = 'timeout'
    Update = 'update'


class RGBLEDInputEvent(SimpleEventBaseClass):
    """ RGB LED events class """

    def __init__(self, eventID, sender):
        super(RGBLEDInputEvent, self).__init__(eventID, sender)
        self._eventIDs = RGBLEDInputEvents()

    @property
    def eventIDs(self):
        return self._eventIDs


class BlinkerEvents(object):
    NoEvent = 'none'
    Initialize = 'initialize'
    Start = 'start'
    Stop = 'stop'
    Done = 'done'
    Ack = 'ack'
    Error = 'error'
    Timeout = 'timeout'
    Update = 'update'


class BlinkerEvent(SimpleEventBaseClass):
    """ Blinker event class """

    def __init__(self, eventID, sender, parameters_list=None):
        super(BlinkerEvent, self).__init__(eventID, sender)
        self._eventIDs = BlinkerEvents()
        self._blinker_parameters = dict()
        self.parameters_list = parameters_list

        self._blinker_parameters["ontime"] = 0.5
        self._blinker_parameters["offtime"] = 0.5
        self._blinker_parameters["blinks"] = 0

    @property
    def eventIDs(self):
        return self._eventIDs

    @property
    def parameters_list(self):
        return self._parameters_list

    @property
    def blinker_parameters(self):
        return self._blinker_parameters

    @parameters_list.setter
    def parameters_list(self, new_parameters_list):
        if new_parameters_list is not None:
            if not isinstance(new_parameters_list[0], str):
                ValueError("Wrong parameter: {0}. Must be a string.".format(new_parameters_list))

            blinkerpara_str_list = new_parameters_list[0].split(',')

            if (len(blinkerpara_str_list) != 3) \
                    or (float(blinkerpara_str_list[0]) < 0.0 ) \
                    or (float(blinkerpara_str_list[1]) < 0.0 ) \
                    or (int(blinkerpara_str_list[2]) < 0) :
                self._blinker_parameters["ontime"] = 1.0
                self._blinker_parameters["offtime"] = 1.0
                self._blinker_parameters["blinks"] = 0

                # ValueError("Wrong parameter: {0}. Must be a string with 3 int values from 0 to 100 for each of rgb color.".format(new_parameters_list))
            self._blinker_parameters["ontime"] = float(blinkerpara_str_list[0])
            self._blinker_parameters["offtime"] = float(blinkerpara_str_list[1])
            self._blinker_parameters["blinks"] = int(blinkerpara_str_list[2])

        self._parameters_list = new_parameters_list
		

class PresenceSensorEvent(object):
    """ Presence sensor events class """

    def __init__(self, eventID, sender):
        self._eventIDs = ('None','Initialize', 'NegativeEdge', 'PositiveEdge', 'Ack', 'Error', 'Update','Timeout')
        self.eventID = eventID
        self.sender = sender

    @property
    def eventID(self):
        return self._eventID

    @eventID.setter
    def eventID(self, new_eventID):
        if new_eventID not in self._eventIDs:
            raise ValueError("Unknown eventID")
        self._eventID = new_eventID

    @property
    def sender(self):
        return self._sender

    @sender.setter
    def sender(self, new_sender):
        # perform some checking
        self._sender = new_sender

    @property
    def eventIDs(self):
        return self._eventIDs

class InteractionSensorEvent(object):
    """ Interaction sensor events class """

    def __init__(self, eventID, sender):
        self._eventIDs = ('None','Initialize', 'NegativeEdge', 'PositiveEdge', 'Ack', 'Error', 'Update','Timeout')
        self.eventID = eventID
        self.sender = sender

    @property
    def eventID(self):
        return self._eventID

    @eventID.setter
    def eventID(self, new_eventID):
        if new_eventID not in self._eventIDs:
            raise ValueError("Unknown eventID")
        self._eventID = new_eventID

    @property
    def sender(self):
        return self._sender

    @sender.setter
    def sender(self, new_sender):
        # perform some checking
        self._sender = new_sender

    @property
    def eventIDs(self):
        return self._eventIDs


class ServiceEventBaseClass(object):
    """ Service events base class """

    def __init__(self, eventID, sender, service_index=None, parameters_list=None, service_process=None):
        self._eventID = eventID
        self._sender = sender
        self._service_index = service_index
        self._parameters_list = parameters_list
        self._service_process = service_process
		
    def __repr__(self):
        return str(self.eventID) + ',' + str(self.sender) + ',' + str(self.service_index) + ',' + str(self.parameters_list)

    @property
    def eventID(self):
        return self._eventID

    @property
    def sender(self):
        return self._sender

    @property
    def service_index(self):
        return self._service_index

    @property
    def parameters_list(self):
        return self._parameters_list
		
    @property
    def service_process(self):
        return self._service_process
		
    @service_index.setter
    def service_index(self, new_service_index):
        # perform some checking
        self._service_index = new_service_index

    @eventID.setter
    def eventID(self, new_eventID):
        # perform some checking
        self._eventID = new_eventID

    @sender.setter
    def sender(self, new_sender):
        # perform some checking
        self._sender = new_sender

    @parameters_list.setter
    def parameters_list(self, new_parameters_list):
        # perform some checking
        if isinstance(new_parameters_list, (list,)) or new_parameters_list is None:
            self._parameters_list = new_parameters_list
        else:
            raise ValueError('parameters_list attribute should be a list')

		
class GenericServiceEvents(object):
    NoEvent = 'none'
    Execute = 'execute'
    Cancel = 'cancel'
    Done = 'done'
    Error = 'error'
    Timeout = 'timeout'


class GenericServiceEvent(ServiceEventBaseClass):
    """ Generic service events class """

    def __init__(self, eventID, sender, service_index=None, parameters_list=None, service_process=None):
        super(GenericServiceEvent, self).__init__(eventID, sender, service_index, parameters_list, service_process)
        self._eventIDs = GenericServiceEvents()
        self._parameters_list = parameters_list
        self._service_process = service_process

    @property
    def parameters_list(self):
        return self._parameters_list

    @property
    def service_process(self):
        return self._service_process		
		
class StorageStationInputEvents(object):
    NoEvent = 'none'
    Initialize = 'initialize'
    Ack = 'ack'
    Done = 'done'
    Error = 'error'
    ConnOk = 'connection_ok'
    NoConn = 'no_connection'
    ProvideMaterial = 'provide'
    RefillMaterial = 'refill'
    ResetMaterial = 'reset'


class StorageStationInputEvent(ServiceEventBaseClass):
    """ Generic service events class """

    def __init__(self, eventID, sender, service_index=None, parameters_list=None):
        super(StorageStationInputEvent, self).__init__(eventID, sender, service_index, parameters_list)
        self._eventIDs = StorageStationInputEvents()
        self._parameters_list = parameters_list
		
    @property
    def eventIDs(self):
        return self._eventIDs

    @property
    def parameters_list(self):
        return self._parameters_list

    # tbd - Check: One more param class necessary for setter function?

	
class ServerEvent(object):
    """ OPC UA Server events class """

    def __init__(self, eventID, sender):
        self._eventIDs = ('Initialize', 'ProvideDicePlate', 'StorePlatesToStorageBox','ResetDicePlateAtStorageBox' 'Ack')
        self.eventID = eventID
        self.sender = sender

    @property
    def eventID(self):
        return self._event

    @property
    def eventIDs(self):
        return self._eventIDs

    @eventID.setter
    def eventID(self, new_eventID):
        if new_eventID not in self._eventIDs:
            raise ValueError("Unknown eventID")
        self._event = new_eventID

    @property
    def sender(self):
        return self._sender

    @sender.setter
    def sender(self, new_sender):
        # perform some checking
        self._sender = new_sender

class SimpleSensorInputEvents(object):
    NoEvent = 'none'
    Initialize = 'initialize'
    NegEdge = 'neg_edge'
    PosEdge = 'pos_edge'
    Ack = 'ack'
    Error = 'error'
    Timeout = 'timeout'
    Update = 'update'

class SimpleLEDEvent(object):
    """ Simple LED events class """

    def __init__(self, eventID, sender):
        self._eventIDs = ('None','Initialize', 'LedOn', 'LedOff', 'Error', 'Ack', 'Update', 'Timeout')
        self.eventID = eventID
        self.sender = sender

    @property
    def eventID(self):
        return self._eventID

    @eventID.setter
    def eventID(self, new_eventID):
        if new_eventID not in self._eventIDs:
            raise ValueError("Unknown eventID")
        self._eventID = new_eventID

    @property
    def sender(self):
        return self._sender

    @sender.setter
    def sender(self, new_sender):
        # perform some checking
        self._sender = new_sender

    @property
    def eventIDs(self):
        return self._eventIDs


class SimpleSensorInputEvent(SimpleEventBaseClass):
    """ Presence sensor events class """

    def __init__(self, eventID, sender):
        super(SimpleSensorInputEvent, self).__init__(eventID, sender)
        self._eventIDs = SimpleSensorInputEvents()

    @property
    def eventIDs(self):
        return self._eventIDs

