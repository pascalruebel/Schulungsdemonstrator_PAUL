from opcua import ua, uamethod, Server
from communication import events
# from utils.logger import Logger
import logging
import os,signal

class UAServer(object):
    def __init__(self, station, revpiobj, endpoint=None, name=None, uri=None):

        if name is None:
            self._name = "EduKit Test OPC UA Server"
        else:
            self._name = name

        if endpoint is None:
            self._endpoint = "opc.tcp://localhost:4840/TestUAServer/"
        else:
            self._endpoint = endpoint

        if uri is None:
            self._uri = "http://basicstation.edukitv2.smartfactorykl.de"
        else:
            self._uri = uri

        self.logger = logging.getLogger(self._name)

        self._server = Server()

        self._server.set_endpoint(self._endpoint)
        self._server.set_server_name(self._name)
        idx = self._server.register_namespace(self._uri)

        self._station = station # Station ref

        self.revpiobj = revpiobj

        # events:
        self.init_event = events.StationInputEvent(eventID=events.StationInputEvents.Initialize, sender=self.name)
        self.ack_event = events.StationInputEvent(eventID=events.StationInputEvents.Ack, sender=self.name)
        self.topos1_event = events.StationInputEvent(eventID=events.StationInputEvents.ToPosition1, sender=self.name)
        self.topos2_event = events.StationInputEvent(eventID=events.StationInputEvents.ToPosition2, sender=self.name)
        self.topos3_event = events.StationInputEvent(eventID=events.StationInputEvents.ToPosition3, sender=self.name)
        self.color_event = events.RGBLEDInputEvent(eventID=events.RGBLEDInputEvents.Custom, sender=self.name)
        self.ledoff_event = events.RGBLEDInputEvent(eventID=events.RGBLEDInputEvents.Off, sender=self.name)
        self.blink_start_event = events.BlinkerEvent(eventID=events.BlinkerEvents.Start, sender=self.name)
        self.blink_stop_event = events.BlinkerEvent(eventID=events.BlinkerEvents.Stop, sender=self.name)

        self.topos_events = {1: self.topos1_event, 2: self.topos2_event,3: self.topos3_event}


        # creating folders:
        folder_model_development = self._server.nodes.objects.add_folder(idx, "ModelManagement")
        folder_state_machine = self._server.nodes.objects.add_folder(idx, "StateMachine")
        folder_ident = self._server.nodes.objects.add_folder(idx, "Identification")
        folder_station_service = self._server.nodes.objects.add_folder(idx, "StationService")
        folder_sensor = self._server.nodes.objects.add_folder(idx, "Sensor")
        folder_actor = self._server.nodes.objects.add_folder(idx, "Actor")
        # folder_monitor = self._server.nodes.objects.add_folder(idx, "Monitoring")
        folder_maintenance = self._server.nodes.objects.add_folder(idx, "Maintenance")

        # creating types:
        sensor_type = self._server.nodes.base_object_type.add_object_type(idx, "SensorType")
        sensor_type.add_variable(idx, "Name", "").set_modelling_rule(True)
        sensor_type.add_variable(idx, "Id", "").set_modelling_rule(True)
        sensor_type.add_variable(idx, "State", "").set_modelling_rule(True)
        sensor_type.add_variable(idx, "Value", True).set_modelling_rule(True)

        actor_type = self._server.nodes.base_object_type.add_object_type(0, "ActorType")
        actor_type.add_variable(idx, "Name", "").set_modelling_rule(True)
        actor_type.add_variable(idx, "Id", "").set_modelling_rule(True)
        actor_type.add_variable(idx, "State", "").set_modelling_rule(True)
        actor_type.add_variable(idx, "Value", "").set_modelling_rule(True)

        # creating objects:

        # Folder Sensor:
        sensorobject = folder_sensor.add_object(idx, "RfidReader1", sensor_type)
        sensorobjects = sensorobject.get_variables()
        sensorobjects[0].set_value("RfidReader1")
        sensorobjects[1].set_value("-BG1")
        sensorobjects[2].set_value("notInitialized")
        sensorobjects[3].set_value("0")
        for obj in sensorobjects:
            obj.set_read_only()

        sensorobject = folder_sensor.add_object(idx, "RfidReader2", sensor_type)
        sensorobjects = sensorobject.get_variables()
        sensorobjects[0].set_value("RfidReader2")
        sensorobjects[1].set_value("-BG2")
        sensorobjects[2].set_value("notInitialized")
        sensorobjects[3].set_value("0")
        for obj in sensorobjects:
            obj.set_read_only()

        sensorobject = folder_sensor.add_object(idx, "RfidReader3", sensor_type)
        sensorobjects = sensorobject.get_variables()
        sensorobjects[0].set_value("RfidReader3")
        sensorobjects[1].set_value("-BG3")
        sensorobjects[2].set_value("notInitialized")
        sensorobjects[3].set_value("0")
        for obj in sensorobjects:
            obj.set_read_only()

        # Folder Actor:
        actorobject = folder_actor.add_object(idx, "LedStrip1", actor_type)
        actorobjects = actorobject.get_variables()
        actorobjects[0].set_value("LedStrip1")
        actorobjects[1].set_value("-PF1")
        actorobjects[2].set_value("notInitialized")
        actorobjects[3].set_value("off")
        for obj in actorobjects:
            obj.set_read_only()

        actorobject = folder_actor.add_object(idx, "LedStrip2", actor_type)
        actorobjects = actorobject.get_variables()
        actorobjects[0].set_value("LedStrip2")
        actorobjects[1].set_value("-PF2")
        actorobjects[2].set_value("notInitialized")
        actorobjects[3].set_value("off")
        for obj in actorobjects:
            obj.set_read_only()

        actorobject = folder_actor.add_object(idx, "LedStrip3", actor_type)
        actorobjects = actorobject.get_variables()
        actorobjects[0].set_value("LedStrip3")
        actorobjects[1].set_value("-PF3")
        actorobjects[2].set_value("notInitialized")
        actorobjects[3].set_value("off")
        for obj in actorobjects:
            obj.set_read_only()

        actorobject = folder_actor.add_object(idx, "StatusLed", actor_type)
        actorobjects = actorobject.get_variables()
        actorobjects[0].set_value("RgbLed")
        actorobjects[1].set_value("-PF4")
        actorobjects[2].set_value("notInitialized")
        actorobjects[3].set_value("off")
        for obj in actorobjects:
            obj.set_read_only()

        # create variables:

        # Folder ModelManagement
        folder_model_development.add_variable(idx, "StationVersionOpcuaModel", "0.1").set_read_only()
        folder_model_development.add_variable(idx, "StationVersionInternal", "0.1").set_read_only()

        # Folder StateMachine
        folder_state_machine.add_variable(idx, "StationState", "initializing").set_read_only()
        folder_state_machine.add_variable(idx, "StationErrorCode", "null").set_read_only()
        folder_state_machine.add_variable(idx, "StationErrorDescription", "null").set_read_only()
        folder_state_machine.add_variable(idx, "StationMessageCode", "null").set_read_only()
        folder_state_machine.add_variable(idx, "StationMessageDescription", "null").set_read_only()
        folder_state_machine.add_variable(idx, "StationSafetyState",
                                          "noSafetySwitchAvailable").set_read_only()

        # Folder Identification
        folder_ident.add_variable(idx, "StationName", "StationIntegriertLogistik").set_read_only()
        folder_ident.add_variable(idx, "StationId", "-AZ3").set_read_only()

        # Folder Maintenance
        folder_maintenance.add_variable(idx, "StationStateMaintenance", "Starting").set_read_only()
        folder_maintenance.add_variable(idx, "InitServiceState", "NotInitialized").set_read_only()
        folder_maintenance.add_variable(idx, "ToPosition1ServiceState", "WaitForJob").set_read_only()
        folder_maintenance.add_variable(idx, "ToPosition2ServiceState", "WaitForJob").set_read_only()
        folder_maintenance.add_variable(idx, "ToPosition3ServiceState", "WaitForJob").set_read_only()

        # Folder Monitor
        # no monitoring at this station

        # Folder StationService: create methods
        target_position = ua.Argument()
        target_position.Name = "Position"
        target_position.DataType = ua.NodeId(ua.ObjectIds.UInt32)
        target_position.ValueRank = -1
        target_position.ArrayDimensions = []
        target_position.Description = ua.LocalizedText("Position (1,2,3) regarding station 1-3 from left to right")
        folder_station_service.add_method(idx, "ServiceDriveToPosition", self.serviceDriveToPosition, [target_position], [ua.VariantType.Int64])


        folder_station_service.add_method(idx, "ServiceAutoInitializeStation", self.serviceAutoInitializeStation, [],[ua.VariantType.Int64])
        folder_station_service.add_method(idx, "ServiceAckAllErrors", self.serviceAckAllErrors, [],[ua.VariantType.Int64])
        folder_station_service.add_method(idx, "ServiceShutdownStationNow", self.serviceShutdownStationNow, [],[ua.VariantType.Int64])

        folder_maintenance.add_method(idx, "maintenanceLedOn", self.maintenanceLedOn,
                                      [ua.VariantType.String], [ua.VariantType.Int64])
        folder_maintenance.add_method(idx, "maintenanceLedOff", self.maintenanceLedOff,
                                      [], [ua.VariantType.Int64])
        folder_maintenance.add_method(idx, "maintenanceBlinkerOn", self.maintenanceBlinkerOn,
                                      [ua.VariantType.String], [ua.VariantType.Int64])
        folder_maintenance.add_method(idx, "maintenanceBlinkerOff", self.maintenanceBlinkerOff,
                                      [], [ua.VariantType.Int64])


    @property
    def server(self):
        return self._server

    @property
    def name(self):
        return self._name

    @uamethod
    def serviceAutoInitializeStation(self, parent):
        self._station.handle_event(event=self.init_event)
        self.logger.debug("Sender %s : Event %s", self.init_event.sender, self.init_event.eventID)

        return ua.status_codes.StatusCodes.Good

    @uamethod
    def serviceDriveToPosition(self, parent, target_position):
        if self._station.stationState == 'Ready':
            self._station.handle_event(event=self.topos_events[target_position])
            self.logger.debug("Sender %s : Event %s", self.topos_events[target_position].sender, self.topos_events[target_position].eventID)

            return ua.status_codes.StatusCodes.Good
        else:
            return ua.status_codes.StatusCodes.Bad

    @uamethod
    def serviceAckAllErrors(self, parent):
        self._station.handle_event(event=self.ack_event)
        self.logger.debug("Sender %s : Event %s", self.ack_event.sender, self.ack_event.eventID)

        return ua.status_codes.StatusCodes.Good

    @uamethod
    def serviceShutdownStationNow(self, parent):
        os.kill(os.getpid(), signal.SIGINT)
        return ua.status_codes.StatusCodes.Good

    @uamethod
    def maintenanceLedOn(self, parent, colors_string):
        self.color_event.parameters_list = [colors_string]
        self.revpiobj.positionLED1.handle_event(event=self.color_event)
        return ua.status_codes.StatusCodes.Good

    @uamethod
    def maintenanceLedOff(self, parent ):
        rgb_event = events.RGBLEDInputEvent(events.RGBLEDInputEvents.Off,sender=self.name)
        self.revpiobj.positionLED1.handle_event(event=rgb_event)
        return ua.status_codes.StatusCodes.Good

    @uamethod
    def maintenanceBlinkerOn(self, parent, blinker_parastring):
        self.blink_start_event.parameters_list = [blinker_parastring]
        self._station.blinker.handle_event(event=self.blink_start_event)
        return ua.status_codes.StatusCodes.Good

    @uamethod
    def maintenanceBlinkerOff(self, parent):
        self._station.blinker.handle_event(event=self.blink_stop_event)
        return ua.status_codes.StatusCodes.Good



class SubHandler(object):
    """
    Subscription Handler. To receive events from server for a subscription.
    The handler forwards updates to it's referenced python object
    Taken from the example
    """

    def __init__(self, obj):
        self.obj = obj

    def datachange_notification(self, node, val, data):
        # print("Python: New data change event", node, val, data)

        _node_name = node.get_browse_name()
        setattr(self.obj, _node_name.Name, data.monitored_item.Value.Value.Value)

    def event_notification(self, event): # implement if necessary
        pass

    def status_change_notification(self, status): # implement if necessary
        pass


class UaObjectPubSub(object):
    """
     Creates Publisher and Subscriber interfaces for the UA Object.
     Child UA variables/properties are auto subscribed.
     Python can write to children via write method.
     Taken from the example.
    """

    def __init__(self, opcua_server, ua_node):
        self.opcua_server = opcua_server
        self.nodes = {}
        self.b_name = ua_node.get_browse_name().Name

        # keep track of the children of this object (in case python needs to write, or get more info from UA server)
        for _child in ua_node.get_children():
            _child_name = _child.get_browse_name()
            self.nodes[_child_name.Name] = _child

        # find all children which can be subscribed to (python object is kept up to date via subscription)
        sub_children = ua_node.get_properties()
        sub_children.extend(ua_node.get_variables())

        # subscribe to properties/variables
        handler = SubHandler(self)
        sub = opcua_server.create_subscription(500, handler)
        handle = sub.subscribe_data_change(sub_children)

    def write(self, attr=None):
        # if a specific attr isn't passed to write, write all OPC UA children
        if attr is None:
            for k, node in self.nodes.items():
                node_class = node.get_node_class()
                if node_class == ua.NodeClass.Variable:
                    node.set_value(getattr(self, k))
        # only update a specific attr
        else:
            self.nodes[attr].set_value(getattr(self, attr))


class UaObjectSubscriber(object):
    """
    Updates the values of the UA Node
    """

    def __init__(self, opcua_server, ua_node):
        self.opcua_server = opcua_server
        self.nodes = {}
        self.b_name = ua_node.get_browse_name().Name
        self._name = self.b_name

        # keep track of the children of this object
        for _child in ua_node.get_children():
            _child_name = _child.get_browse_name()
            self.nodes[_child_name.Name] = _child

    @property
    def name(self):
        return self._name

    def write(self, attr=None):
        # if a specific attr isn't passed to write, write all OPC UA children
        if attr is None:
            for k, node in self.nodes.items():
                node_class = node.get_node_class()
                if node_class == ua.NodeClass.Variable:
                    node.set_value(getattr(self, k))
        # only update a specific attr
        else:
            self.nodes[attr].set_value(getattr(self, attr))

    def update(self, *args, **kwargs):
        kwargs = kwargs
        if "topic" not in kwargs or "value" not in kwargs:
            raise ValueError("OPCUA server : Bad argument")
        self.nodes[kwargs["topic"]].set_value(kwargs["value"])









