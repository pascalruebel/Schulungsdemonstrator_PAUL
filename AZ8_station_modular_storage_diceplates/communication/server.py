from opcua import ua, uamethod, Server
from communication import events
import logging
import os,signal



class AZ8UAServer(object):
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
        #self.server_events = ServerEvent('Initialize', name) tbd
		
        self.revpiobj = revpiobj

        # creating folders:

        folder_model_development = self._server.nodes.objects.add_folder(idx, "ModelManagement")
        folder_state_machine = self._server.nodes.objects.add_folder(idx, "StateMachine")
        folder_ident = self._server.nodes.objects.add_folder(idx, "Identification")
        folder_station_service = self._server.nodes.objects.add_folder(idx, "StationService")
        folder_sensor = self._server.nodes.objects.add_folder(idx, "Sensor")
        folder_actor = self._server.nodes.objects.add_folder(idx, "Actor")
        folder_monitor = self._server.nodes.objects.add_folder(idx, "Monitoring")

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

        mechanics_type = self._server.nodes.base_object_type.add_object_type(idx, "MechanicsType")
        mechanics_type.add_variable(idx, "Name", "").set_modelling_rule(True)
        mechanics_type.add_variable(idx, "State", "").set_modelling_rule(True)
        mechanics_type.add_variable(idx, "PlateSymbol", "").set_modelling_rule(True)
        mechanics_type.add_variable(idx, "MaxCapacityPlates", 0).set_modelling_rule(True)
        mechanics_type.add_variable(idx, "PlateColor1", "").set_modelling_rule(True)
        mechanics_type.add_variable(idx, "QuantityOfPlateColor1", 0).set_modelling_rule(True)
        mechanics_type.add_variable(idx, "PlateColor2", "").set_modelling_rule(True)
        mechanics_type.add_variable(idx, "QuantityOfPlateColor2", 0).set_modelling_rule(True)
        mechanics_type.add_variable(idx, "PlateColor3", "").set_modelling_rule(True)
        mechanics_type.add_variable(idx, "QuantityOfPlateColor3", 0).set_modelling_rule(True)

        # creating objects:

        # Folder Sensor:
        sensorobject = folder_sensor.add_object(idx, "PresenceSensor1", sensor_type)
        sensorobjects = sensorobject.get_variables()
        sensorobjects[0].set_value("SensorPresenceAtBox1")
        sensorobjects[1].set_value("-BG1")
        sensorobjects[2].set_value("notInitialized")
        sensorobjects[3].set_value(False)
        for obj in sensorobjects:
            obj.set_read_only()

        sensorobject = folder_sensor.add_object(idx, "PresenceSensor2", sensor_type)
        sensorobjects = sensorobject.get_variables()
        sensorobjects[0].set_value("SensorPresenceAtBox2")
        sensorobjects[1].set_value("-BG2")
        sensorobjects[2].set_value("notInitialized")
        sensorobjects[3].set_value(False)
        for obj in sensorobjects:
            obj.set_read_only()

        sensorobject = folder_sensor.add_object(idx, "PresenceSensor3", sensor_type)
        sensorobjects = sensorobject.get_variables()
        sensorobjects[0].set_value("SensorPresenceAtBox3")
        sensorobjects[1].set_value("-BG3")
        sensorobjects[2].set_value("notInitialized")
        sensorobjects[3].set_value(False)
        for obj in sensorobjects:
            obj.set_read_only()

        sensorobject = folder_sensor.add_object(idx, "PresenceSensor4", sensor_type)
        sensorobjects = sensorobject.get_variables()
        sensorobjects[0].set_value("SensorPresenceAtBox4")
        sensorobjects[1].set_value("-BG4")
        sensorobjects[2].set_value("notInitialized")
        sensorobjects[3].set_value(False)
        for obj in sensorobjects:
            obj.set_read_only()

        sensorobject = folder_sensor.add_object(idx, "PresenceSensor5", sensor_type)
        sensorobjects = sensorobject.get_variables()
        sensorobjects[0].set_value("SensorPresenceAtBox5")
        sensorobjects[1].set_value("-BG5")
        sensorobjects[2].set_value("notInitialized")
        sensorobjects[3].set_value(False)
        for obj in sensorobjects:
            obj.set_read_only()

        sensorobject = folder_sensor.add_object(idx, "PresenceSensor6", sensor_type)
        sensorobjects = sensorobject.get_variables()
        sensorobjects[0].set_value("SensorPresenceAtBox6")
        sensorobjects[1].set_value("-BG6")
        sensorobjects[2].set_value("notInitialized")
        sensorobjects[3].set_value(False)
        for obj in sensorobjects:
            obj.set_read_only()

        sensorobject = folder_sensor.add_object(idx, "InteractionSensor1", sensor_type)
        sensorobjects = sensorobject.get_variables()
        sensorobjects[0].set_value("SensorButtonProductionDone")
        sensorobjects[1].set_value("-SF1")
        sensorobjects[2].set_value("notInitialized")
        sensorobjects[3].set_value(False)
        for obj in sensorobjects:
            obj.set_read_only()

        sensorobject = folder_sensor.add_object(idx, "InteractionSensor2", sensor_type)
        sensorobjects = sensorobject.get_variables()
        sensorobjects[0].set_value("SensorButtonProductionError")
        sensorobjects[1].set_value("-SF2")
        sensorobjects[2].set_value("notInitialized")
        sensorobjects[3].set_value(False)
        for obj in sensorobjects:
            obj.set_read_only()

        # Folder Actor:
        actorobject = folder_actor.add_object(idx, "LedStrip1", actor_type)
        actorobjects = actorobject.get_variables()
        actorobjects[0].set_value("LedStripForPickByLightAtBox1")
        actorobjects[1].set_value("-PF1")
        actorobjects[2].set_value("notInitialized")
        actorobjects[3].set_value("off")
        for obj in actorobjects:
            obj.set_read_only()

        actorobject = folder_actor.add_object(idx, "LedStrip2", actor_type)
        actorobjects = actorobject.get_variables()
        actorobjects[0].set_value("LedStripForPickByLightAtBox2")
        actorobjects[1].set_value("-PF2")
        actorobjects[2].set_value("notInitialized")
        actorobjects[3].set_value("off")
        for obj in actorobjects:
            obj.set_read_only()

        actorobject = folder_actor.add_object(idx, "LedStrip3", actor_type)
        actorobjects = actorobject.get_variables()
        actorobjects[0].set_value("LedStripForPickByLightAtBox3")
        actorobjects[1].set_value("-PF3")
        actorobjects[2].set_value("notInitialized")
        actorobjects[3].set_value("off")
        for obj in actorobjects:
            obj.set_read_only()

        actorobject = folder_actor.add_object(idx, "LedStrip4", actor_type)
        actorobjects = actorobject.get_variables()
        actorobjects[0].set_value("LedStripForPickByLightAtBox4")
        actorobjects[1].set_value("-PF4")
        actorobjects[2].set_value("notInitialized")
        actorobjects[3].set_value("off")
        for obj in actorobjects:
            obj.set_read_only()

        actorobject = folder_actor.add_object(idx, "LedStrip5", actor_type)
        actorobjects = actorobject.get_variables()
        actorobjects[0].set_value("LedStripForPickByLightAtBox5")
        actorobjects[1].set_value("-PF5")
        actorobjects[2].set_value("notInitialized")
        actorobjects[3].set_value("off")
        for obj in actorobjects:
            obj.set_read_only()

        actorobject = folder_actor.add_object(idx, "LedStrip6", actor_type)
        actorobjects = actorobject.get_variables()
        actorobjects[0].set_value("LedStripForPickByLightAtBox6")
        actorobjects[1].set_value("-PF6")
        actorobjects[2].set_value("notInitialized")
        actorobjects[3].set_value("off")
        for obj in actorobjects:
            obj.set_read_only()

        actorobject = folder_actor.add_object(idx, "StatusLed", actor_type)
        actorobjects = actorobject.get_variables()
        actorobjects[0].set_value("RgbLed")
        actorobjects[1].set_value("-PF7")
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
        folder_ident.add_variable(idx, "StationName", "StationModularLagerWuerfelPlatten").set_read_only()
        folder_ident.add_variable(idx, "StationId", "-AZ8").set_read_only()

        # Folder Monitor
        mechanicsobject = folder_monitor.add_object(idx, "StorageRack1", mechanics_type)
        mechanicsobjects = mechanicsobject.get_variables()
        mechanicsobjects[0].set_value("StorageBoxNumber1")
        mechanicsobjects[1].set_value("off")
        mechanicsobjects[2].set_value("1")
        mechanicsobjects[3].set_value(90)
        mechanicsobjects[4].set_value("white")
        mechanicsobjects[5].set_value(0)
        mechanicsobjects[6].set_value("yellow")
        mechanicsobjects[7].set_value(0)
        mechanicsobjects[8].set_value("red")
        mechanicsobjects[9].set_value(0)
        for obj in mechanicsobjects:
            obj.set_read_only()

        mechanicsobject = folder_monitor.add_object(idx, "StorageRack2", mechanics_type)
        mechanicsobjects = mechanicsobject.get_variables()
        mechanicsobjects[0].set_value("StorageBoxNumber2")
        mechanicsobjects[1].set_value("off")
        mechanicsobjects[2].set_value("2")
        mechanicsobjects[3].set_value(90)
        mechanicsobjects[4].set_value("white")
        mechanicsobjects[5].set_value(0)
        mechanicsobjects[6].set_value("yellow")
        mechanicsobjects[7].set_value(0)
        mechanicsobjects[8].set_value("red")
        mechanicsobjects[9].set_value(0)
        for obj in mechanicsobjects:
            obj.set_read_only()

        mechanicsobject = folder_monitor.add_object(idx, "StorageRack3", mechanics_type)
        mechanicsobjects = mechanicsobject.get_variables()
        mechanicsobjects[0].set_value("StorageBoxNumber3")
        mechanicsobjects[1].set_value("off")
        mechanicsobjects[2].set_value("3")
        mechanicsobjects[3].set_value(90)
        mechanicsobjects[4].set_value("white")
        mechanicsobjects[5].set_value(0)
        mechanicsobjects[6].set_value("yellow")
        mechanicsobjects[7].set_value(0)
        mechanicsobjects[8].set_value("red")
        mechanicsobjects[9].set_value(0)
        for obj in mechanicsobjects:
            obj.set_read_only()

        mechanicsobject = folder_monitor.add_object(idx, "StorageRack4", mechanics_type)
        mechanicsobjects = mechanicsobject.get_variables()
        mechanicsobjects[0].set_value("StorageBoxNumber4")
        mechanicsobjects[1].set_value("off")
        mechanicsobjects[2].set_value("4")
        mechanicsobjects[3].set_value(90)
        mechanicsobjects[4].set_value("white")
        mechanicsobjects[5].set_value(0)
        mechanicsobjects[6].set_value("yellow")
        mechanicsobjects[7].set_value(0)
        mechanicsobjects[8].set_value("red")
        mechanicsobjects[9].set_value(0)
        for obj in mechanicsobjects:
            obj.set_read_only()

        mechanicsobject = folder_monitor.add_object(idx, "StorageRack5", mechanics_type)
        mechanicsobjects = mechanicsobject.get_variables()
        mechanicsobjects[0].set_value("StorageBoxNumber5")
        mechanicsobjects[1].set_value("off")
        mechanicsobjects[2].set_value("5")
        mechanicsobjects[3].set_value(90)
        mechanicsobjects[4].set_value("white")
        mechanicsobjects[5].set_value(0)
        mechanicsobjects[6].set_value("yellow")
        mechanicsobjects[7].set_value(0)
        mechanicsobjects[8].set_value("red")
        mechanicsobjects[9].set_value(0)
        for obj in mechanicsobjects:
            obj.set_read_only()

        mechanicsobject = folder_monitor.add_object(idx, "StorageRack6", mechanics_type)
        mechanicsobjects = mechanicsobject.get_variables()
        mechanicsobjects[0].set_value("StorageBoxNumber6")
        mechanicsobjects[1].set_value("off")
        mechanicsobjects[2].set_value("6")
        mechanicsobjects[3].set_value(90)
        mechanicsobjects[4].set_value("white")
        mechanicsobjects[5].set_value(0)
        mechanicsobjects[6].set_value("yellow")
        mechanicsobjects[7].set_value(0)
        mechanicsobjects[8].set_value("red")
        mechanicsobjects[9].set_value(0)
        for obj in mechanicsobjects:
            obj.set_read_only()


        # Folder StationService: create methods
        insymbolProv = ua.Argument()
        insymbolProv.Name = "Plate Symbol"
        insymbolProv.DataType = ua.NodeId(ua.ObjectIds.String)
        insymbolProv.ValueRank = -1
        insymbolProv.ArrayDimensions = []
        insymbolProv.Description = ua.LocalizedText("Plate symbol to provide regarding available StorageBoxes")
        incolorProv = ua.Argument()
        incolorProv.Name = "Plate Color"
        incolorProv.DataType = ua.NodeId(ua.ObjectIds.String)
        incolorProv.ValueRank = -1
        incolorProv.ArrayDimensions = []
        incolorProv.Description = ua.LocalizedText("Plate color to provide regarding available StorageBoxes")

        # target of plateSymbol and therefore of box
        intargetPlateSymbol = ua.Argument()
        intargetPlateSymbol.Name = "Target plate symbol"
        intargetPlateSymbol.DataType = ua.NodeId(ua.ObjectIds.String)
        intargetPlateSymbol.ValueRank = -1
        intargetPlateSymbol.ArrayDimensions = []
        #Colorname of plates
        incolor1 = ua.Argument()
        incolor1.Name = "Plate Color1 to change in Box"
        incolor1.DataType = ua.NodeId(ua.ObjectIds.String)
        incolor1.ValueRank = -1
        incolor1.ArrayDimensions = []
        incolor2 = ua.Argument()
        incolor2.Name = "Plate Color2 to change in Box"
        incolor2.DataType = ua.NodeId(ua.ObjectIds.String)
        incolor2.ValueRank = -1
        incolor2.ArrayDimensions = []
        incolor3 = ua.Argument()
        incolor3.Name = "Plate Color3 to change in Box"
        incolor3.DataType = ua.NodeId(ua.ObjectIds.String)
        incolor3.ValueRank = -1
        incolor3.ArrayDimensions = []
        #Number of plates
        innumberColor1 = ua.Argument()
        innumberColor1.Name = "Number of plates of Color1 to change in Box"
        innumberColor1.DataType = ua.NodeId(ua.ObjectIds.UInt32)
        innumberColor1.ValueRank = -1
        innumberColor1.ArrayDimensions = []
        innumberColor2 = ua.Argument()
        innumberColor2.Name = "Number of Plates of Color2 to change in Box"
        innumberColor2.DataType = ua.NodeId(ua.ObjectIds.UInt32)
        innumberColor2.ValueRank = -1
        innumberColor2.ArrayDimensions = []
        innumberColor3 = ua.Argument()
        innumberColor3.Name = "Number of Plates of Color3 to change in Box"
        innumberColor3.DataType = ua.NodeId(ua.ObjectIds.UInt32)
        innumberColor3.ValueRank = -1
        innumberColor3.ArrayDimensions = []

		# Service index 0: Initialization
        folder_station_service.add_method(idx,"ServiceAutoInitializeStation", self.serviceAutoInitializeStation,[],[ua.VariantType.Int64])
		
		# Service index 1: ProvideDicePlate - Input parameters: symbol and color
        folder_station_service.add_method(idx, "ServiceProvideDicePlate", self.serviceProvideDicePlate, [insymbolProv, incolorProv],[ua.VariantType.Int64])
		
        # Service index 2: StorageDicePlate - Refill
        folder_station_service.add_method(idx,"ServiceStorePlatesToStorageBox",self.serviceStorePlatesToStorageBox,
                                          [intargetPlateSymbol, incolor1, innumberColor1, incolor2, innumberColor2, incolor3, innumberColor3],[ua.VariantType.Int64])
										  
        # Service index 2: StorageDicePlate - Reset
        folder_station_service.add_method(idx, "ServiceResetDicePlateAtStorageBox", self.serviceResetDicePlateAtStorageBox,
                                          [intargetPlateSymbol, incolor1, innumberColor1, incolor2, innumberColor2, incolor3, innumberColor3],[ua.VariantType.Int64])

        folder_station_service.add_method(idx, "ServiceAckAllErrors",self.serviceAckAllErrors,[],[ua.VariantType.Int64])
        folder_station_service.add_method(idx, "ServiceShutdownStationNow", self.serviceShutdownStationNow,[],[ua.VariantType.Int64])

    @property
    def server(self):
        return self._server

    @property
    def name(self):
        return self._name

	# The methods in this class are for dispatching the OPCUA-services into active objects. 
	# Parameter self._name comes from input-parameters (from _init_).
	
    @uamethod
    def serviceAutoInitializeStation(self, parent):
	
        # If initialization has been called during an error state, acknowledge all error automatically.
        ack_event = events.StorageStationInputEvent(eventID=events.StorageStationInputEvents.Ack,
                                                    sender=self.name)
        self._station.handle_event(event=ack_event)
        self.logger.debug("Sender %s : Event %s", ack_event.sender, ack_event.eventID)
		
        init_event = events.StorageStationInputEvent(eventID=events.StorageStationInputEvents.Initialize, sender=self._name)
        self._station.handle_event(event=init_event)
        self.logger.debug("Sender %s : Event %s", init_event.sender, init_event.eventID)

        return ua.status_codes.StatusCodes.Good
		
    @uamethod
    def serviceProvideDicePlate(self, parent, symbol, color):
        if ( self._station.stationState == 'Ready' ):
		
			# Provide the parameters to the event
            providematerial_event = events.StorageStationInputEvent(eventID=events.StorageStationInputEvents.ProvideMaterial, sender=self._name, parameters_list=[symbol, color])
            self._station.handle_event(event=providematerial_event)
            self.logger.debug("Sender %s : Event %s", providematerial_event.sender, providematerial_event.eventID)

            return ua.status_codes.StatusCodes.Good
        else:
            return ua.status_codes.StatusCodes.Bad
			
    @uamethod
    def serviceStorePlatesToStorageBox(self, parent, targetPlateSymbolBox, color1, numberColor1, color2, numberColor2, color3, numberColor3):
		# Refill only possible if station is in status ready (loading of saved values during initialization)
        if ( self._station.stationState == 'Ready' ):
		
			# Dem Event die Parameter mitgeben
            refillmaterial_event = events.StorageStationInputEvent(eventID=events.StorageStationInputEvents.RefillMaterial, sender=self._name, parameters_list=[targetPlateSymbolBox, color1, numberColor1, color2, numberColor2, color3, numberColor3])
            self._station.handle_event(event=refillmaterial_event)
            self.logger.debug("Sender %s : Event %s", refillmaterial_event.sender, refillmaterial_event.eventID)

            return ua.status_codes.StatusCodes.Good
        else:
            return ua.status_codes.StatusCodes.Bad
			
    @uamethod
    def serviceResetDicePlateAtStorageBox(self, parent, targetPlateSymbolBox, color1, numberColor1, color2, numberColor2, color3, numberColor3):
        
		# Reset only possible if station is in status ready (loading of saved values during initialization)
        if ( self._station.stationState == 'Ready' ):
		
			# Dem Event die Parameter mitgeben
            resetmaterial_event = events.StorageStationInputEvent(eventID=events.StorageStationInputEvents.ResetMaterial, sender=self._name, parameters_list=[targetPlateSymbolBox, color1, numberColor1, color2, numberColor2, color3, numberColor3])
            self._station.handle_event(event=resetmaterial_event)
            self.logger.debug("Sender %s : Event %s", resetmaterial_event.sender, resetmaterial_event.eventID)

            return ua.status_codes.StatusCodes.Good
        else:
            return ua.status_codes.StatusCodes.Bad

    @uamethod
    def serviceAckAllErrors(self, parent):
        ack_event = events.StorageStationInputEvent(eventID=events.StorageStationInputEvents.Ack,
                                                    sender=self.name)
        self._station.handle_event(event=ack_event)
        self.logger.debug("Sender %s : Event %s", ack_event.sender, ack_event.eventID)

        return ua.status_codes.StatusCodes.Good

    @uamethod
    def serviceShutdownStationNow(self, parent):
	
        # Switch status led to value off
        led_event = events.RGBLEDInputEvent(eventID=events.RGBLEDInputEvents.Off,sender=self.name)
        self._station.status_led.handle_event(event=led_event)
		
        self.logger.debug("Station Shutdown")
        os.kill(os.getpid(), signal.SIGINT)
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

