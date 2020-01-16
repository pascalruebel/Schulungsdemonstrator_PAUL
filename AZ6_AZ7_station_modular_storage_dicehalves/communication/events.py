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


class SimpleSensorInputEvents(object):
    NoEvent = 'none'
    Initialize = 'initialize'
    NegEdge = 'neg_edge'
    PosEdge = 'pos_edge'
    Ack = 'ack'
    Error = 'error'
    Timeout = 'timeout'
    Update = 'update'


class SimpleSensorInputEvent(SimpleEventBaseClass):
    """ Presence sensor events class """

    def __init__(self, eventID, sender):
        super(SimpleSensorInputEvent, self).__init__(eventID, sender)
        self._eventIDs = SimpleSensorInputEvents()

    @property
    def eventIDs(self):
        return self._eventIDs


class SimpleMotorInputEvents(object):
    NoEvent = 'none'
    Initialize = 'initialize'
    RotateCW = 'rotate_cw'
    RotateCCW = 'rotate_ccw'
    Stop = 'stop'
    Ack = 'ack'
    Error = 'error'
    Timeout = 'timeout'
    Update = 'update'


class SimpleMotorInputEvent(SimpleEventBaseClass):
    """ Simple motor events class """

    def __init__(self, eventID, sender):
        super(SimpleMotorInputEvent, self).__init__(eventID, sender)
        self._eventIDs = SimpleMotorInputEvents()

    @property
    def eventIDs(self):
        return self._eventIDs


class SimpleLEDInputEvents(object):
    NoEvent = 'none'
    Initialize = 'initialize'
    LedOn = 'led_on'
    LedOff = 'led_off'
    Ack = 'ack'
    Error = 'error'
    Timeout = 'timeout'
    Update = 'update'


class SimpleLEDInputEvent(SimpleEventBaseClass):
    """ Simple LED events class """

    def __init__(self, eventID, sender):
        super(SimpleLEDInputEvent, self).__init__(eventID, sender)
        self._eventIDs = SimpleLEDInputEvents()

    @property
    def eventIDs(self):
        return self._eventIDs


class RGBLEDInputEvents(object):
    NoEvent = 'none'
    Initialize = 'initialize'
    Red = 'red'
    Green = 'green'
    Yellow = 'yellow'
    Purple = 'purple'
    Custom = 'custom'
    Off = 'off'
    Ack = 'ack'
    Error = 'error'
    Timeout = 'timeout'
    Update = 'update'


class RGBLEDInputEvent(SimpleEventBaseClass):
    """ RGB LED events class """

    def __init__(self, eventID, sender, parameters_list=None):
        super(RGBLEDInputEvent, self).__init__(eventID, sender)
        self._eventIDs = RGBLEDInputEvents()
        self.rgb_colors = dict()
        self.parameters_list = parameters_list

    @property
    def eventIDs(self):
        return self._eventIDs

    @property
    def parameters_list(self):
        return self._parameters_list

    @parameters_list.setter
    def parameters_list(self, new_parameters_list):
        if new_parameters_list is not None:
            if not isinstance(new_parameters_list[0], str ):
                ValueError("Wrong parameter: {0}. Must be a string.".format(new_parameters_list))

            rgb_str_list = new_parameters_list[0].split(',')

            if (len(rgb_str_list) != 3) \
                    or (int(rgb_str_list[0]) < 0 or int(rgb_str_list[0]) > 100)\
                    or (int(rgb_str_list[1]) < 0 or int(rgb_str_list[1]) > 100)\
                    or (int(rgb_str_list[2]) < 0 or int(rgb_str_list[2]) > 100):

                self.rgb_colors["red"] = 0
                self.rgb_colors["green"] = 0
                self.rgb_colors["blue"] = 0

                # ValueError("Wrong parameter: {0}. Must be a string with 3 int values from 0 to 100 for each of rgb color.".format(new_parameters_list))

            self.rgb_colors["red"] = int(rgb_str_list[0])
            self.rgb_colors["green"] = int(rgb_str_list[1])
            self.rgb_colors["blue"] = int(rgb_str_list[2])

        self._parameters_list = new_parameters_list


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

    def __repr__(self):
        return str(self.eventID) + ',' + str(self.sender) \
               + ', ontime:' + str(self._blinker_parameters["ontime"]) \
               + ', offtime:' + str(self._blinker_parameters["offtime"]) \
               + ', blinks:' + str(self._blinker_parameters["blinks"])

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

            self._blinker_parameters["ontime"] = float(blinkerpara_str_list[0])
            self._blinker_parameters["offtime"] = float(blinkerpara_str_list[1])
            self._blinker_parameters["blinks"] = int(blinkerpara_str_list[2])

        self._parameters_list = new_parameters_list


class CarriageEvents(object):
    NoEvent = 'none'
    Initialize = 'initialize'
    MoveToRackPos = 'to_rackpos'
    MoveToFrontPos = 'to_frontpos'
    TimeoutToRackPos = 'timeout_to_rackpos'
    TimeoutToFrontPos = 'timeout_to_frontpos'
    Stop = 'stop'
    Ack = 'ack'
    Error = 'error'
    Update = 'update'


class CarriageEvent(SimpleEventBaseClass):
    """ Carriage events class """

    def __init__(self, eventID, sender):
        super(CarriageEvent, self).__init__(eventID, sender)
        self._eventIDs = CarriageEvents()

    @property
    def eventIDs(self):
        return self._eventIDs


class RackEvents(object):
    NoEvent = 'none'
    Initialize = 'initialize'
    SetRack = 'set_rack'
    DecRack = 'dec_rack'
    Ack = 'ack'
    Error = 'error'
    Timeout = 'timeout'
    Update = 'update'


class RackEvent(SimpleEventBaseClass):
    """ Rack events class """

    def __init__(self, eventID, sender, parameters_list=None):
        super(RackEvent, self).__init__(eventID, sender)
        self._eventIDs = RackEvents()
        self.dicehalfs_number = 0
        self.parameters_list = parameters_list

    def __repr__(self):
        return str(self.eventID) + ',' + str(self.sender) + ', number of dicehalfs:' + str(self.dicehalfs_number)

    @property
    def eventIDs(self):
        return self._eventIDs

    @property
    def parameters_list(self):
        return self._parameters_list

    @parameters_list.setter
    def parameters_list(self, new_parameters_list):
        if new_parameters_list is not None:
            if not isinstance(new_parameters_list[0], int) or (new_parameters_list[0] < 0) :
                ValueError("Wrong parameter: {0}. Must be a positive integer.".format(new_parameters_list))

            self.dicehalfs_number = new_parameters_list[0]

        self._parameters_list = new_parameters_list


class ServiceEventBaseClass(object):
    """ Service events base class """

    def __init__(self, eventID, sender, service_index=None, parameters_list=None):
        self.eventID = eventID
        self.sender = sender
        self.service_index = service_index
        self.parameters_list = parameters_list

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
    Update = 'update'


class GenericServiceEvent(ServiceEventBaseClass):
    """ Generic service events class """

    def __init__(self, eventID, sender, service_index=None, parameters_list=None):
        super(GenericServiceEvent, self).__init__(eventID, sender, service_index, parameters_list)
        self._eventIDs = GenericServiceEvents()
        self.init_required = False

    def __repr__(self):
        return str(self.eventID) + ',' + str(self.sender) + ', init is required:' + str(self.init_required)

    @property
    def parameters_list(self):
        return self._parameters_list

    @property
    def init_required(self):
        return self._init_required

    @init_required.setter
    def init_required(self, new_init_required):
        self._init_required = new_init_required

    @parameters_list.setter
    def parameters_list(self, new_parameters_list):
        if new_parameters_list is not None:
            if not isinstance(new_parameters_list[0], bool) or (new_parameters_list[0] < 0):
                ValueError("Wrong parameter: {0}. Must be a boolean.".format(new_parameters_list))

            self.init_required = new_parameters_list[0]

        self._parameters_list = new_parameters_list


class StationInputEvents(object):
    NoEvent = 'none'
    Initialize = 'initialize'
    Homing = 'homing'
    ProvideDicehalf = 'provideDicehalf'
    RefillRack = 'refill'
    SetRack = 'setRack'
    CancelService = 'cancelService'
    Ack = 'ack'
    Done = 'done'
    Error = 'error'
    ConnOk = 'connection_ok'
    NoConn = 'no_connection'
    # Todo: the following events are only for testing
    MaintenanceMotorCW = 'maintenance_motor_cw'
    MaintenanceMotorCCW = 'maintenance_motor_ccw'
    MaintenanceMotorStop = 'maintenance_motor_stop'
    MaintenanceCarriageToRack = 'maintenance_carriage_toRack'
    MaintenanceCarriageToFront = 'maintenance_carriage_toFront'
    MaintenanceCarriageStop = 'maintenance_carriage_stop'


class StationInputEvent(ServiceEventBaseClass):
    """ Generic service events class """

    def __init__(self, eventID, sender, service_index=None, parameters_list=None):
        super(StationInputEvent, self).__init__(eventID, sender, service_index, parameters_list)
        self._eventIDs = StationInputEvents()

    @property
    def eventIDs(self):
        return self._eventIDs

