from opcua import ua, uamethod, Server
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

        self.station_app = station_app # ref to the StationApp object (main)

        # creating folders:
        folder_model_development = self._server.nodes.objects.add_folder(idx, "ModelManagement")
        folder_state_machine = self._server.nodes.objects.add_folder(idx, "StateMachine")
        folder_ident = self._server.nodes.objects.add_folder(idx, "Identification")
        folder_station_service = self._server.nodes.objects.add_folder(idx, "StationService")
        folder_sensor = self._server.nodes.objects.add_folder(idx, "Sensor")
        folder_actor = self._server.nodes.objects.add_folder(idx, "Actor")
        folder_monitor = self._server.nodes.objects.add_folder(idx, "Monitoring")
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
        sensorobject = folder_sensor.add_object(idx, "PresenceSensor1", sensor_type)
        sensorobjects = sensorobject.get_variables()
        sensorobjects[0].set_value("SensorCarriagePosFront")
        sensorobjects[1].set_value("-BG1")
        sensorobjects[2].set_value("notInitilized")
        sensorobjects[3].set_value(False)
        for obj in sensorobjects:
            obj.set_read_only()

        sensorobject = folder_sensor.add_object(idx, "PresenceSensor2", sensor_type)
        sensorobjects = sensorobject.get_variables()
        sensorobjects[0].set_value("SensorCarriagePosBack")
        sensorobjects[1].set_value("-BG2")
        sensorobjects[2].set_value("notInitilized")
        sensorobjects[3].set_value(False)
        for obj in sensorobjects:
            obj.set_read_only()

        sensorobject = folder_sensor.add_object(idx, "PresenceSensor3", sensor_type)
        sensorobjects = sensorobject.get_variables()
        sensorobjects[0].set_value("SensorFillLevelPosTop")
        sensorobjects[1].set_value("-BG3")
        sensorobjects[2].set_value("notInitilized")
        sensorobjects[3].set_value(False)
        for obj in sensorobjects:
            obj.set_read_only()

        sensorobject = folder_sensor.add_object(idx, "PresenceSensor4", sensor_type)
        sensorobjects = sensorobject.get_variables()
        sensorobjects[0].set_value("SensorFillLevelPosBottom")
        sensorobjects[1].set_value("-BG4")
        sensorobjects[2].set_value("notInitilized")
        sensorobjects[3].set_value(False)
        for obj in sensorobjects:
            obj.set_read_only()

        sensorobject = folder_sensor.add_object(idx, "PresenceSensor5", sensor_type)
        sensorobjects = sensorobject.get_variables()
        sensorobjects[0].set_value("SensorCarriageOccupied")
        sensorobjects[1].set_value("-BG5")
        sensorobjects[2].set_value("notInitilized")
        sensorobjects[3].set_value(False)
        for obj in sensorobjects:
            obj.set_read_only()

        sensorobject = folder_sensor.add_object(idx, "SafetySwitch", sensor_type)
        sensorobjects = sensorobject.get_variables()
        sensorobjects[0].set_value("SafetySwitchActive")
        sensorobjects[1].set_value("-SF1")
        sensorobjects[2].set_value("notInitilized")
        sensorobjects[3].set_value(False)
        for obj in sensorobjects:
            obj.set_read_only()

        # Folder Actor:
        actorobject = folder_actor.add_object(idx, "MotorDC", actor_type)
        actorobjects = actorobject.get_variables()
        actorobjects[0].set_value("MotorCarriage")
        actorobjects[1].set_value("-MA1")
        actorobjects[2].set_value("notInitialized")
        actorobjects[3].set_value("stopped")
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
        folder_state_machine.add_variable(idx, "StationState", "Standby").set_read_only()
        folder_state_machine.add_variable(idx, "StationErrorCode", 0x0000, varianttype=ua.VariantType.Byte).set_read_only()
        folder_state_machine.add_variable(idx, "StationErrorDescription", "null").set_read_only()
        folder_state_machine.add_variable(idx, "StationSafetyState",
                                               "safetySwitchNotActivated").set_read_only()
        folder_state_machine.add_variable(idx, "StationMessageCode", 0x0000,
                                          varianttype=ua.VariantType.Byte).set_read_only()
        folder_state_machine.add_variable(idx, "StationMessageDescription", "null").set_read_only()

        # Folder Identification
        folder_ident.add_variable(idx, "StationName", "StationModularLagerWuerfelhaelftenA").set_read_only()
        folder_ident.add_variable(idx, "StationId", "-AZ6").set_read_only()

        # Folder Monitor
        folder_monitor.add_variable(idx, "ColorOfStoredDicehalvesAtThisStation", "blue").set_read_only()
        folder_monitor.add_variable(idx, "NumberOfCurrentlyStoredDicehalves", 0).set_read_only()

        # Folder Maintenance

        folder_maintenance.add_variable(idx, 'StationStateMaintenance', "NotInitialized").set_read_only()
        folder_maintenance.add_variable(idx, "InitServiceState", "NotInitialized").set_read_only()
        folder_maintenance.add_variable(idx, "HomeServiceState", "NotReferenced").set_read_only()
        folder_maintenance.add_variable(idx, "ProvideDicehalfServiceState", "WaitForJob").set_read_only()
        folder_maintenance.add_variable(idx, "RefillingServiceState", "WaitForJob").set_read_only()
        folder_maintenance.add_variable(idx, "RackState", "NotInitialized").set_read_only()
        folder_maintenance.add_variable(idx, "CarriageState", "NotInitialized").set_read_only()

        # create methods
        folder_station_service.add_method(idx, "ProvideDicehalf", self.provideDicehalf,[],[ua.VariantType.Int64])
        folder_station_service.add_method(idx, "RefillWithDicehalvesTillFull", self.refillWithDicehalvesTillFull, [],[ua.VariantType.Int64])
        folder_station_service.add_method(idx, "ServiceAutoInitializeStation", self.serviceAutoInitializeStation, [],[ua.VariantType.Int64])
        folder_station_service.add_method(idx, "ServiceCancel", self.serviceCancel, [], [ua.VariantType.Int64])
        folder_station_service.add_method(idx, "ServiceAckAllErrors", self.acknowledge, [], [ua.VariantType.Int64])
        folder_station_service.add_method(idx, "ServiceShutdownStationNow", self.stationshutdown, [],[ua.VariantType.Int64])
        folder_station_service.add_method(idx, "SetDicehalfNumber", self.setRack, [ua.VariantType.Int64], [ua.VariantType.Int64])

        folder_maintenance.add_method(idx, "MoveCarriageRack", self.moveCarriageRack)
        folder_maintenance.add_method(idx, "MoveCarriageFront", self.moveCarriageFront)
        folder_maintenance.add_method(idx, "StopCarriage", self.stopCarriage)
        folder_maintenance.add_method(idx, "MotorRotateCW", self.motorRotCW)
        folder_maintenance.add_method(idx, "MotorRotateCCW", self.motorRotCCW)
        folder_maintenance.add_method(idx, "MotorStop", self.motorStop)

    @property
    def server(self):
        return self._server

    @property
    def name(self):
        return self._name

    @uamethod
    def serviceAutoInitializeStation(self, parent):
        init_event = events.StationInputEvent(eventID=events.StationInputEvents.Initialize,
                                                      sender=self.name)
        self.station_app.storageStation.handle_event(event=init_event)
        self.logger.debug("Sender %s : Event %s", init_event.sender, init_event.eventID)

        return ua.status_codes.StatusCodes.Good

    @uamethod
    def serviceCancel(self, parent):
        cancel_event = events.StationInputEvent(eventID=events.StationInputEvents.CancelService,
                                              sender=self.name)
        self.station_app.storageStation.handle_event(event=cancel_event)
        self.logger.debug("Sender %s : Event %s", cancel_event.sender, cancel_event.eventID)

        return ua.status_codes.StatusCodes.Good

    @uamethod
    def setRack(self, parent, dicehalfs_number):
        if dicehalfs_number >= 0:

            setrack_event = events.RackEvent(eventID=events.RackEvents.SetRack, sender=self.name, parameters_list=[dicehalfs_number])
            self.station_app.rack.handle_event(event=setrack_event)
            self.logger.debug("Sender %s : Event %s", setrack_event.sender, setrack_event.eventID)

            return ua.status_codes.StatusCodes.Good
        else:
            return ua.status_codes.StatusCodes.Bad

    @uamethod
    def provideDicehalf(self, parent):
        if (self.station_app.storageStation.stationState == 'Ready') and (self.station_app.provideDicehalfService.serviceState == 'Ready'):

            getdice_event = events.StationInputEvent(eventID=events.StationInputEvents.ProvideDicehalf,
                                                  sender=self.name)
            self.station_app.storageStation.handle_event(event=getdice_event)
            self.logger.debug("Sender %s : Event %s", getdice_event.sender, getdice_event.eventID)

            return ua.status_codes.StatusCodes.Good
        else:
            message_code = message_codes.StationMessageCodes.ActiveJob

            if self.station_app.provideDicehalfService.serviceState == 'EmptyRack':
                message_code = message_codes.StationMessageCodes.RackEmpty
            elif self.station_app.provideDicehalfService.serviceState == 'DispatchOccupied':
                message_code = message_codes.StationMessageCodes.DispatchNotEmpty

            self.station_app.provideDicehalfService.publisher.publish(topic="StationMessageCode",
                                                    value=hex(message_code),
                                                    sender=self.station_app.provideDicehalfService.name)
            self.station_app.provideDicehalfService.publisher.publish(topic="StationMessageDescription",
                                                    value=message_codes.code_to_text[message_code],
                                                    sender=self.station_app.provideDicehalfService.name)

            return ua.status_codes.StatusCodes.Bad

    @uamethod
    def refillWithDicehalvesTillFull(self, parent):
        if self.station_app.storageStation.stationState == 'Ready' \
                and (self.station_app.rackRefillingService.serviceState == 'Ready'):

            refill_event = events.StationInputEvent(eventID=events.StationInputEvents.RefillRack,
                                                     sender=self.name)
            self.station_app.storageStation.handle_event(event=refill_event)
            self.logger.debug("Sender %s : Event %s", refill_event.sender, refill_event.eventID)

            return ua.status_codes.StatusCodes.Good
        else:
            return ua.status_codes.StatusCodes.Bad

    @uamethod
    def acknowledge(self, parent):

        ack_event = events.StationInputEvent(eventID=events.StationInputEvents.Ack,
                                                     sender=self.name)
        self.station_app.storageStation.handle_event(event=ack_event)
        self.logger.debug("Sender %s : Event %s", ack_event.sender, ack_event.eventID)

        return ua.status_codes.StatusCodes.Good

    @uamethod
    def stationshutdown(self, parent):
        os.kill(os.getpid(), signal.SIGINT)
        return ua.status_codes.StatusCodes.Good

    @uamethod
    def moveCarriageRack(self, parent):
        torack_event = events.StationInputEvent(eventID=events.StationInputEvents.MaintenanceCarriageToRack,
                                                 sender=self.name)
        self.station_app.storageStation.handle_event(event=torack_event)
        self.logger.debug("Sender %s : Event %s", torack_event.sender, torack_event.eventID)

        return ua.status_codes.StatusCodes.Good

    @uamethod
    def moveCarriageFront(self, parent): # Testing
        tofront_event = events.StationInputEvent(eventID=events.StationInputEvents.MaintenanceCarriageToFront,
                                                sender=self.name)
        self.station_app.storageStation.handle_event(event=tofront_event)
        self.logger.debug("Sender %s : Event %s", tofront_event.sender, tofront_event.eventID)

        return ua.status_codes.StatusCodes.Good

    @uamethod
    def stopCarriage(self, parent): # Testing
        stop_event = events.StationInputEvent(eventID=events.StationInputEvents.MaintenanceCarriageStop,
                                                 sender=self.name)
        self.station_app.storageStation.handle_event(event=stop_event)
        self.logger.debug("Sender %s : Event %s", stop_event.sender, stop_event.eventID)

        return ua.status_codes.StatusCodes.Good

    @uamethod
    def motorRotCW(self, parent):
        motorcw_event = events.StationInputEvent(eventID=events.StationInputEvents.MaintenanceMotorCW,
                                                         sender=self.name)
        self.station_app.storageStation.handle_event(event=motorcw_event)
        self.logger.debug("Sender %s : Event %s", motorcw_event.sender, motorcw_event.eventID)

        return ua.status_codes.StatusCodes.Good

    @uamethod
    def motorRotCCW(self, parent):
        motorccw_event = events.StationInputEvent(eventID=events.StationInputEvents.MaintenanceMotorCCW,
                                                          sender=self.name)
        self.station_app.storageStation.handle_event(event=motorccw_event)
        self.logger.debug("Sender %s : Event %s", motorccw_event.sender, motorccw_event.eventID)

        return ua.status_codes.StatusCodes.Good

    @uamethod
    def motorStop(self, parent):
        motorstop_event = events.StationInputEvent(eventID=events.StationInputEvents.MaintenanceMotorStop,
                                                    sender=self.name)
        self.station_app.storageStation.handle_event(event=motorstop_event)
        self.logger.debug("Sender %s : Event %s", motorstop_event.sender, motorstop_event.eventID)

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







