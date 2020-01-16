from opcua import ua, uamethod, Server
import config
from communication import events
import logging
import os,signal
from utils import message_codes


class UAServer(object):
    def __init__(self, station_app, endpoint=None, name=None, uri=None):

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

        self.station_app = station_app

        # events:
        self.init_event = events.StationEvent(eventID=events.StationEvents.Initialize, sender=self.name)
        self.ack_event = events.StationEvent(eventID=events.StationEvents.Ack, sender=self.name)
        self.do_pressing_event = events.StationEvent(eventID=events.StationEvents.Pressing, sender=self.name)
        self.tofrontpos_event = events.StationEvent(eventID=events.StationEvents.ToFrontPos, sender=self.name)


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

        analog_sensor_type = self._server.nodes.base_object_type.add_object_type(idx, "AnalogSensorType")
        analog_sensor_type.add_variable(idx, "Name", "").set_modelling_rule(True)
        analog_sensor_type.add_variable(idx, "Id", "").set_modelling_rule(True)
        analog_sensor_type.add_variable(idx, "State", "").set_modelling_rule(True)
        analog_sensor_type.add_variable(idx, "AnalogValue", 0.0, ua.VariantType.Int32).set_modelling_rule(True)

        actor_type = self._server.nodes.base_object_type.add_object_type(0, "ActorType")
        actor_type.add_variable(idx, "Name", "").set_modelling_rule(True)
        actor_type.add_variable(idx, "Id", "").set_modelling_rule(True)
        actor_type.add_variable(idx, "State", "").set_modelling_rule(True)
        actor_type.add_variable(idx, "Value", "").set_modelling_rule(True)

        # creating objects:

        # Folder Sensor:
        sensorobject = folder_sensor.add_object(idx, "PhysicalValueSensor", analog_sensor_type)
        sensorobjects = sensorobject.get_variables()
        sensorobjects[0].set_value("SensorForceAtPressing")
        sensorobjects[1].set_value("-BG1")
        sensorobjects[2].set_value("notInitialized")
        sensorobjects[3].set_value(0)
        for obj in sensorobjects:
            obj.set_read_only()

        sensorobject = folder_sensor.add_object(idx, "PresenceSensor1", sensor_type)
        sensorobjects = sensorobject.get_variables()
        sensorobjects[0].set_value("SensorDiceAtPressPos")
        sensorobjects[1].set_value("-BG2")
        sensorobjects[2].set_value("notInitialized")
        sensorobjects[3].set_value(False)
        for obj in sensorobjects:
            obj.set_read_only()

        sensorobject = folder_sensor.add_object(idx, "PresenceSensor2", sensor_type)
        sensorobjects = sensorobject.get_variables()
        sensorobjects[0].set_value("SensorSafetyPressAtMaxLength")
        sensorobjects[1].set_value("-BG3")
        sensorobjects[2].set_value("notInitialized")
        sensorobjects[3].set_value(False)
        for obj in sensorobjects:
            obj.set_read_only()

        sensorobject = folder_sensor.add_object(idx, "PresenceSensor3", sensor_type)
        sensorobjects = sensorobject.get_variables()
        sensorobjects[0].set_value("SensorDiceCarriageAtHome")
        sensorobjects[1].set_value("-BG4")
        sensorobjects[2].set_value("notInitialized")
        sensorobjects[3].set_value(False)
        for obj in sensorobjects:
            obj.set_read_only()

        sensorobject = folder_sensor.add_object(idx, "PresenceSensor4", sensor_type)
        sensorobjects = sensorobject.get_variables()
        sensorobjects[0].set_value("SensorPressAtHome")
        sensorobjects[1].set_value("-BG5")
        sensorobjects[2].set_value("notInitialized")
        sensorobjects[3].set_value(False)
        for obj in sensorobjects:
            obj.set_read_only()

        sensorobject = folder_sensor.add_object(idx, "PresenceSensor5", sensor_type)
        sensorobjects = sensorobject.get_variables()
        sensorobjects[0].set_value("SensorLinearPosOfPress")
        sensorobjects[1].set_value("-BG6")
        sensorobjects[2].set_value("notInitialized")
        sensorobjects[3].set_value(False)  # to be defined at test time
        for obj in sensorobjects:
            obj.set_read_only()

        sensorobject = folder_sensor.add_object(idx, "SafetySwitch", sensor_type)
        sensorobjects = sensorobject.get_variables()
        sensorobjects[0].set_value("SafetySwitchActive")
        sensorobjects[1].set_value("-SF1")
        sensorobjects[2].set_value("notInitialized")
        sensorobjects[3].set_value(False)
        for obj in sensorobjects:
            obj.set_read_only()

        # Folder Actor:
        actorobject = folder_actor.add_object(idx, "MotorDC", actor_type)
        actorobjects = actorobject.get_variables()
        actorobjects[0].set_value("MotorPress")
        actorobjects[1].set_value("-MA1")
        actorobjects[2].set_value("notInitialized")
        actorobjects[3].set_value("stopped")
        for obj in actorobjects:
            obj.set_read_only()

        actorobject = folder_actor.add_object(idx, "Electromagnet", actor_type)
        actorobjects = actorobject.get_variables()
        actorobjects[0].set_value("ElectromagnetAnchor")
        actorobjects[1].set_value("-MA2")
        actorobjects[2].set_value("notInitialized")
        actorobjects[3].set_value("notActive")
        for obj in actorobjects:
            obj.set_read_only()

        actorobject = folder_actor.add_object(idx, "StatusLed", actor_type)
        actorobjects = actorobject.get_variables()
        actorobjects[0].set_value("RgbLed")
        actorobjects[1].set_value("-PF1")
        actorobjects[2].set_value("noInitializationNeeded")
        actorobjects[3].set_value("off")
        for obj in actorobjects:
            obj.set_read_only()

        # create variables:

        # Folder ModelManagement
        folder_model_development.add_variable(idx, "StationVersionOpcuaModel", "0.1").set_read_only()
        folder_model_development.add_variable(idx, "StationVersionInternal", "0.1").set_read_only()

        # Folder StateMachine
        folder_state_machine.add_variable(idx, "StationState", "not initialized").set_read_only()
        folder_state_machine.add_variable(idx, "StationErrorCode", 0x0000, ua.VariantType.Byte).set_read_only()
        folder_state_machine.add_variable(idx, "StationErrorDescription", "no error").set_read_only()
        folder_state_machine.add_variable(idx, "StationSafetyState",
                                          "safetySwitchNotActivated").set_read_only()
        folder_state_machine.add_variable(idx, "StationMessageCode", 0x0000,
                                          varianttype=ua.VariantType.Byte).set_read_only()
        folder_state_machine.add_variable(idx, "StationMessageDescription", "null").set_read_only()

        # Folder Identification
        folder_ident.add_variable(idx, "StationName", "StationModularMontageWuerfelhaelften").set_read_only()
        folder_ident.add_variable(idx, "StationId", "-AZ9").set_read_only()

        # Folder Monitor
        # no monitoring at this station

        # Folder StationService: create methods

        folder_station_service.add_method(idx, "ServicePressDiceHalves", self.servicePressDiceHalves, [], [ua.VariantType.Int64])
        folder_station_service.add_method(idx, "ServiceMoveCarriageToHomePos", self.serviceMoveCarriageToHomePos, [],[ua.VariantType.Int64])
        folder_station_service.add_method(idx, "ServiceAutoInitializeStation", self.serviceAutoInitializeStation, [],[ua.VariantType.Int64])
        folder_station_service.add_method(idx, "ServiceAckAllErrors", self.serviceAckAllErrors, [],[ua.VariantType.Int64])
        folder_station_service.add_method(idx, "ServiceShutdownStationNow", self.serviceShutdownStationNow, [],[ua.VariantType.Int64])


        # Folder Maintenance
        folder_maintenance.add_variable(idx, "InitServiceState", "NotInitialized").set_read_only()
        folder_maintenance.add_variable(idx, "HomeServiceState", "WaitForJob").set_read_only()
        folder_maintenance.add_variable(idx, "PressServiceState", "WaitForJob").set_read_only()
        folder_maintenance.add_variable(idx, "ToFrontPosServiceState", "WaitForJob").set_read_only()
        folder_maintenance.add_variable(idx, "PressState", "WaitForJob").set_read_only()

        folder_maintenance.add_method(idx, "maintenanceMotorRotCW", self.maintenanceMotorRotCW, [], [ua.VariantType.Int64])
        folder_maintenance.add_method(idx, "maintenanceMotorRotCCW", self.maintenanceMotorRotCCW, [],
                                      [ua.VariantType.Int64])
        folder_maintenance.add_method(idx, "maintenanceMotorStop", self.maintenanceMotorStop, [],
                                      [ua.VariantType.Int64])
        folder_maintenance.add_method(idx, "maintenancePressStop", self.maintenancePressStop, [],
                                      [ua.VariantType.Int64])
        folder_maintenance.add_method(idx, "maintenancePressToUpperPos", self.maintenancePressToUpperPos, [],
                                      [ua.VariantType.Int64])
        folder_maintenance.add_method(idx, "maintenancePressToPressingPos", self.maintenancePressToPressingPos, [],
                                      [ua.VariantType.Int64])
        folder_maintenance.add_method(idx, "maintenanceToPressEndSwitch", self.maintenanceToPressEndSwitch, [],
                                      [ua.VariantType.Int64])
        folder_maintenance.add_method(idx, "maintenanceClampOpen", self.maintenanceClampOpen, [],
                                      [ua.VariantType.Int64])
        folder_maintenance.add_method(idx, "maintenanceClampClose", self.maintenanceClampClose, [],
                                      [ua.VariantType.Int64])
        folder_maintenance.add_method(idx, "maintenancePressDiceHalves", self.maintenanceServicePressDiceHalves,
                                          [ua.VariantType.Int32], [ua.VariantType.Int64])
        folder_maintenance.add_method(idx, "maintenanceLedOn", self.maintenanceLedOn,
                                      [ua.VariantType.String], [ua.VariantType.Int64])
        folder_maintenance.add_method(idx, "maintenanceLedOff", self.maintenanceLedOff,
                                      [], [ua.VariantType.Int64])

    @property
    def server(self):
        return self._server

    @property
    def name(self):
        return self._name

    @uamethod
    def serviceAutoInitializeStation(self, parent):
        self.station_app.assemblyStation.handle_event(event=self.init_event)
        self.logger.debug("Sender %s : Event %s", self.init_event.sender, self.init_event.eventID)

        return ua.status_codes.StatusCodes.Good

    @uamethod
    def servicePressDiceHalves(self, parent):

        if (self.station_app.assemblyStation.stationState == 'Ready') and (self.station_app.pressingService.serviceState == 'Ready'):
            self.station_app.pressing_setpoint = config.STATION_CONFIG['pressingSetpoint']
            self.station_app.assemblyStation.handle_event(event=self.do_pressing_event)

            return ua.status_codes.StatusCodes.Good
        else:
            self.logger.debug("Sender %s : Event %s didn't succeed. Station state : %s, Service state : %s ",
                              self.do_pressing_event.sender,
                              self.do_pressing_event.eventID,
                              self.station_app.assemblyStation.stationState,
                              self.station_app.pressingService.serviceState)

            message_code = message_codes.StationMessageCodes.ActiveJob

            if self.station_app.pressingService.serviceState == "NotInFrontPos":
                message_code = message_codes.StationMessageCodes.CarriageOutofFrontPos

            self.station_app.pressingService.publisher.publish(topic="StationMessageCode",
                                                                      value=hex(message_code),
                                                                      sender=self.station_app.pressingService.name)
            self.station_app.pressingService.publisher.publish(topic="StationMessageDescription",
                                                                      value=message_codes.code_to_text[message_code],
                                                                      sender=self.station_app.pressingService.name)

            return ua.status_codes.StatusCodes.Bad

    @uamethod
    def serviceMoveCarriageToHomePos(self, parent):
        if (self.station_app.assemblyStation.stationState == 'Ready') and (self.station_app.toFrontPosService.serviceState == 'Ready'):

            self.station_app.assemblyStation.handle_event(event=self.tofrontpos_event)
            self.logger.debug("Sender %s : Event %s", self.tofrontpos_event.sender, self.tofrontpos_event.eventID)

            return ua.status_codes.StatusCodes.Good
        else:
            self.logger.debug("Sender %s : Event %s didn't succeed. Station state : %s, Service state : %s ",
                              self.tofrontpos_event.sender,
                              self.tofrontpos_event.eventID,
                              self.station_app.assemblyStation.stationState,
                              self.station_app.toFrontPosService.serviceState)

            message_code = message_codes.StationMessageCodes.ActiveJob

            if self.station_app.toFrontPosService.serviceState == 'PressNotUp':
                message_code = message_codes.StationMessageCodes.PressOutofUpperPos

            self.station_app.toFrontPosService.publisher.publish(topic="StationMessageCode",
                                                               value=hex(message_code),
                                                               sender=self.station_app.toFrontPosService.name)
            self.station_app.toFrontPosService.publisher.publish(topic="StationMessageDescription",
                                                               value=message_codes.code_to_text[message_code],
                                                               sender=self.station_app.toFrontPosService.name)

            return ua.status_codes.StatusCodes.Bad

    @uamethod
    def serviceAckAllErrors(self, parent):
        self.station_app.assemblyStation.handle_event(event=self.ack_event)
        self.logger.debug("Sender %s : Event %s", self.ack_event.sender, self.ack_event.eventID)

        return ua.status_codes.StatusCodes.Good

    @uamethod
    def serviceShutdownStationNow(self, parent):
        os.kill(os.getpid(), signal.SIGINT)
        return ua.status_codes.StatusCodes.Good

    # maintenance methods :

    @uamethod
    def maintenanceServicePressDiceHalves(self, parent, pressing_setpoint):
        if (self.station_app.assemblyStation.stationState == 'Ready') \
                and (self.station_app.pressingService.serviceState == 'Ready') \
                and (pressing_setpoint > 0):

            self.station_app.pressing_setpoint = pressing_setpoint
            self.station_app.assemblyStation.handle_event(event=self.do_pressing_event)
            self.logger.debug("Sender %s : Event %s", self.do_pressing_event.sender, self.do_pressing_event.eventID)

            return ua.status_codes.StatusCodes.Good
        else:
            return ua.status_codes.StatusCodes.Bad

    @uamethod
    def maintenanceMotorRotCW(self, parent):
        motorcw_event = events.StationEvent(eventID=events.StationEvents.MaintenanceMotorCW,
                                            sender=self.name)
        self.station_app.assemblyStation.handle_event(event=motorcw_event)
        self.logger.debug("Sender %s : Event %s", motorcw_event.sender, motorcw_event.eventID)
        return ua.status_codes.StatusCodes.Good

    @uamethod
    def maintenanceMotorRotCCW(self, parent):
        motorccw_event = events.StationEvent(eventID=events.StationEvents.MaintenanceMotorCCW,
                                             sender=self.name)
        self.station_app.assemblyStation.handle_event(event=motorccw_event)
        self.logger.debug("Sender %s : Event %s", motorccw_event.sender, motorccw_event.eventID)
        return ua.status_codes.StatusCodes.Good

    @uamethod
    def maintenanceMotorStop(self, parent):
        motorstop_event = events.StationEvent(eventID=events.StationEvents.MaintenanceMotorStop,
                                              sender=self.name)
        self.station_app.assemblyStation.handle_event(event=motorstop_event)
        self.logger.debug("Sender %s : Event %s", motorstop_event.sender, motorstop_event.eventID)
        return ua.status_codes.StatusCodes.Good

    @uamethod
    def maintenancePressStop(self, parent):
        pressstop_event = events.StationEvent(eventID=events.StationEvents.MaintenancePressStop,
                                                sender=self.name)
        self.station_app.assemblyStation.handle_event(event=pressstop_event)
        self.logger.debug("Sender %s : Event %s", pressstop_event.sender, pressstop_event.eventID)
        return ua.status_codes.StatusCodes.Good

    @uamethod
    def maintenancePressToUpperPos(self, parent):
        toupperpos_event = events.StationEvent(eventID=events.StationEvents.MaintenancePressToUpperPos,
                                                sender=self.name)
        self.station_app.assemblyStation.handle_event(event=toupperpos_event)
        self.logger.debug("Sender %s : Event %s", toupperpos_event.sender, toupperpos_event.eventID)
        return ua.status_codes.StatusCodes.Good

    @uamethod
    def maintenancePressToPressingPos(self, parent):
        topressingpos_event = events.StationEvent(eventID=events.StationEvents.MaintenancePressToPressingPos,
                                                    sender=self.name)
        self.station_app.assemblyStation.handle_event(event=topressingpos_event)
        self.logger.debug("Sender %s : Event %s", topressingpos_event.sender, topressingpos_event.eventID)
        return ua.status_codes.StatusCodes.Good

    @uamethod
    def maintenanceToPressEndSwitch(self, parent):
        toendswitch_event = events.StationEvent(eventID=events.StationEvents.MaintenanceToPressEndSwitch,
                                                sender=self.name)
        self.station_app.assemblyStation.handle_event(event=toendswitch_event)
        self.logger.debug("Sender %s : Event %s", toendswitch_event.sender, toendswitch_event.eventID)
        return ua.status_codes.StatusCodes.Good

    @uamethod
    def maintenanceClampOpen(self, parent):
        openclamp_event = events.StationEvent(eventID=events.StationEvents.MaintenanceClampOpen,
                                                sender=self.name)
        self.station_app.assemblyStation.handle_event(event=openclamp_event)
        self.logger.debug("Sender %s : Event %s", openclamp_event.sender, openclamp_event.eventID)
        return ua.status_codes.StatusCodes.Good

    @uamethod
    def maintenanceClampClose(self, parent):
        closeclamp_event = events.StationEvent(eventID=events.StationEvents.MaintenanceClampClose,
                                                sender=self.name)
        self.station_app.assemblyStation.handle_event(event=closeclamp_event)
        self.logger.debug("Sender %s : Event %s", closeclamp_event.sender, closeclamp_event.eventID)
        return ua.status_codes.StatusCodes.Good

    @uamethod
    def maintenanceLedOn(self, parent, colors_string):
        rgb_event = events.RGBLEDInputEvent(events.RGBLEDInputEvents.Custom,sender=self.name,parameters_list=[colors_string])
        self.station_app.assemblyStation.handle_event(event=rgb_event)
        return ua.status_codes.StatusCodes.Good

    @uamethod
    def maintenanceLedOff(self, parent ):
        rgb_event = events.RGBLEDInputEvent(events.RGBLEDInputEvents.Off,sender=self.name)
        self.station_app.assemblyStation.handle_event(event=rgb_event)
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









