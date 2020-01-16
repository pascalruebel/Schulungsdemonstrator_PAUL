import definitions
from communication.server import UAServer, UaObjectSubscriber
from activeobjects.sensors.presencesensor import PresenceSensor
from activeobjects.sensors.safetyswitch import SafetySwitch
from activeobjects.rack.storagerack import Rack
from activeobjects.actuators.motor import Motor
from activeobjects.carriage.carriage import Carriage
from activeobjects.station.station import StorageStation
from activeobjects.actuators.rgb_led import RGB_LED
from activeobjects.actuators.blinker import Blinker
from activeobjects.actuators.blinker_led_adapter import BlinkerLedAdapter
from activeobjects.services.initialization.init_service import InitService
from activeobjects.services.interface import ServiceInterface
from activeobjects.services.homing.homing import HomingService
from activeobjects.services.dicehalf.dicehalf import ProvideDicehalfService
from activeobjects.services.refilling.refilling import RackRefillingService

import revpimodio2

import config
import logging.config
import json
import socket
from communication.server_publisher import ServerPublisher
from communication import events, conn_monitor, network_util

with open(definitions.LOGCONFIG_PATH, 'r') as logging_config_file:
    config_dict = json.load(logging_config_file)
logging.config.dictConfig(config_dict)

try:
    from IPython import embed
except ImportError:
    import code


    def embed():
        vars = globals()
        vars.update(locals())
        shell = code.InteractiveConsole(vars)
        shell.interact()


class StationApp(object):
    """ Main application for the station """

    def __init__(self, name):
        self._name = name
        self.logger = logging.getLogger(self._name)

        self.logger.debug("Building a RevPi driver...")

        self.revpiioDriver = revpimodio2.RevPiModIO(autorefresh=True)

        self.connMonitor = conn_monitor.ConnMonitor(name='ConnMonitor',
                                                    logger=self.logger,
                                                    conn_alive_cb=self.conn_alive_event,
                                                    conn_broken_cb=self.conn_broken_event)

        self.logger.debug("Buiding the station's active objects...")

        # building station objects -----------------------------------------------------

        self.safetySwitch = SafetySwitch("SafetySwitch",
                                         "-SF1",
                                         topics=["State", "Value", 'StationErrorCode', 'StationErrorDescription',
                                                             'StationMessageCode', 'StationMessageDescription'],
                                         inputobj=self.revpiioDriver.io['input5'],
                                         auto_init=True,
                                         normally_open=True)

        # actuators ---------------------------------------------------------------------

        self.led_adapter = BlinkerLedAdapter(hw_output_red=self.revpiioDriver.io['PWM_R'],
                                             hw_output_green=self.revpiioDriver.io['PWM_G'],
                                             hw_output_blue=self.revpiioDriver.io['PWM_B'])

        self.statusLED = RGB_LED("RgbLed", "-PF4",
                                 revpi_red=self.led_adapter.red,
                                 revpi_green=self.led_adapter.green,
                                 revpi_blue=self.led_adapter.blue,
                                 topics=["State", "Value", 'StationErrorCode', 'StationErrorDescription',
                                                             'StationMessageCode', 'StationMessageDescription'])

        self.blinkerStatusLED = Blinker('BlinkerStatusLED', shutter=self.led_adapter, ontime=0.5, offtime=0.5)

        self.carriageMotor = Motor("MotorCarriage", "MA1",
                                   rotate_cw=self.revpiioDriver.io['output5'],
                                   rotate_ccw=self.revpiioDriver.io['output4'],
                                   topics=["State", "Value", 'StationErrorCode', 'StationErrorDescription',
                                                             'StationMessageCode', 'StationMessageDescription'])

        # sensors -----------------------------------------------------------------------
        self.posTopRackSensor = PresenceSensor(name="SensorFillLevelPosTop",
                                               id="-BG3",
                                               topics=["State", "Value", 'StationErrorCode', 'StationErrorDescription',
                                                             'StationMessageCode', 'StationMessageDescription'],
                                               inputobj=self.revpiioDriver.io['input4'],
                                               normally_open=True)

        self.posBottomRackSensor = PresenceSensor(name="SensorFillLevelPosBottom",
                                                  id="-BG4",
                                                  topics=["State", "Value", 'StationErrorCode', 'StationErrorDescription',
                                                             'StationMessageCode', 'StationMessageDescription'],
                                                  inputobj=self.revpiioDriver.io['input6'],
                                                  normally_open=True)

        self.posAtRackSensor = PresenceSensor(name="SensorCarriagePosBack",
                                              id="-BG2",
                                              topics=["State", "Value", 'StationErrorCode', 'StationErrorDescription',
                                                             'StationMessageCode', 'StationMessageDescription'],
                                              inputobj=self.revpiioDriver.io['input2'],
                                              normally_open=False)  # this sensor is normally closed !

        self.posAtFrontSensor = PresenceSensor(name="SensorCarriagePosFront",
                                               id="-BG1",
                                               topics=["State", "Value", 'StationErrorCode', 'StationErrorDescription',
                                                             'StationMessageCode', 'StationMessageDescription'],
                                               inputobj=self.revpiioDriver.io['input1'],
                                               normally_open=False)  # this sensor is normally closed !

        self.carriageOccupiedSensor = PresenceSensor(name="SensorCarriageOccupied",
                                                     id="-BG5",
                                                     topics=["State", "Value", 'StationErrorCode', 'StationErrorDescription',
                                                             'StationMessageCode', 'StationMessageDescription'],
                                                     inputobj=self.revpiioDriver.io['input3'],
                                                     normally_open=True)

        # station parts -----------------------------------------------------------------
        self.rack = Rack(name="StorageRack",
                         sensor_top=self.posTopRackSensor,
                         sensor_bottom=self.posBottomRackSensor,
                         dicehalfs_maximun=config.STATION_CONFIG['rackMaxCapacity'],
                         topics=['RackState', 'State', 'StationErrorCode', 'StationErrorDescription',
                                'StationMessageCode', 'StationMessageDescription', 'NumberOfCurrentlyStoredDicehalves'])

        self.carriage = Carriage(name="Carriage",
                                 sensor_front=self.posAtFrontSensor,
                                 sensor_rack=self.posAtRackSensor,
                                 motor=self.carriageMotor,
                                 topics=['CarriageState','State','StationErrorCode', 'StationErrorDescription',
                                                             'StationMessageCode', 'StationMessageDescription'])

        self.storageStation = StorageStation(name="Station",
                                             motor=self.carriageMotor,
                                             carriage=self.carriage,
                                             rack=self.rack,
                                             status_led=self.statusLED,
                                             blinker=self.blinkerStatusLED,
                                             topics=['StationState', 'Ack', 'StationErrorCode',
                                                     'StationErrorDescription', 'StationSafetyState',
                                                     'StationMessageCode', 'StationMessageDescription', 'StationStateMaintenance'])

        # building and registering services -----------------------------------------------

        # 1) create an initialization service:
        dev_list = [self.safetySwitch, self.rack, self.carriage, self.carriageOccupiedSensor]

        self.initService = InitService(name='InitializationService',
                                       enable_timeout=True,
                                       timeout_interval=config.STATION_CONFIG['initServiceTimeoutInterval'],
                                       dev_list=dev_list,
                                       topics=['eventID', 'StationErrorCode', 'StationErrorDescription',
                                               'StationMessageCode', 'StationMessageDescription', 'InitServiceState'])

        # create a service interface
        self.initializationServiceInterface = ServiceInterface(service_user=self.storageStation,
                                                               service=self.initService,
                                                               service_index=0)
        # set the service
        self.initService.setup_service(service_index=0, service_interface=self.initializationServiceInterface)

        # regester the service by the service user
        self.storageStation.register_services(service_index=0, service_interface=self.initializationServiceInterface)


        # homing service:
        self.homingService = HomingService(name="HomingService",
                                           rack=self.rack,
                                           carriage=self.carriage,
                                           sensorCarriageOccupied=self.carriageOccupiedSensor,
                                           enable_timeout=True,
                                           timeout_interval=config.STATION_CONFIG['homingServiceTimfeoutInterval'],
                                           topics=['eventID', 'StationErrorCode', 'StationErrorDescription',
                                                    'StationMessageCode', 'StationMessageDescription', 'HomeServiceState'])

        self.homingServiceInterface = ServiceInterface(service_user=self.storageStation,
                                                       service=self.homingService,
                                                       service_index=1)

        self.homingService.setup_service(service_index=1, service_interface=self.homingServiceInterface)

        self.storageStation.register_services(service_index=1, service_interface=self.homingServiceInterface)


        # provide dicehalf service:
        self.provideDicehalfService = ProvideDicehalfService(name='ProvideDicehalfService',
                                                             rack=self.rack,
                                                             carriage=self.carriage,
                                                             sensorCarriageOccupied=self.carriageOccupiedSensor,
                                                             blinker=self.blinkerStatusLED,
                                                             enable_timeout=True,
                                                             timeout_interval=config.STATION_CONFIG[
                                                                 'provideDicehalfTimeoutInterval'],
                                                             topics=['eventID', 'StationErrorCode',
                                                                     'StationErrorDescription',
                                                                     'StationMessageCode', 'StationMessageDescription',
                                                                     'ProvideDicehalfServiceState'])
        # create a service interface
        self.provideDicehalfServiceInterface = ServiceInterface(service_user=self.storageStation,
                                                                service=self.provideDicehalfService,
                                                                service_index=2)
        # set the service
        self.provideDicehalfService.setup_service(service_index=2, service_interface=self.provideDicehalfServiceInterface)

        # regester the service by the service user
        self.storageStation.register_services(service_index=2, service_interface=self.provideDicehalfServiceInterface)

        # refill rack service:
        self.rackRefillingService = RackRefillingService(name='RackFillingService',
                                                         rack=self.rack,
                                                         carriage=self.carriage,
                                                         enable_timeout=True,
                                                         timeout_interval=config.STATION_CONFIG[
                                                             'refillingTimeoutInterval'],
                                                         topics=['eventID', 'StationErrorCode',
                                                                 'StationErrorDescription','StationMessageCode',
                                                                 'StationMessageDescription', 'RefillingServiceState'])

        # create a service interface
        self.rackRefillingServiceInterface = ServiceInterface(service_user=self.storageStation,
                                                              service=self.rackRefillingService,
                                                              service_index=3)
        # set the service
        self.rackRefillingService.setup_service(service_index=3, service_interface=self.rackRefillingServiceInterface)

        # regester the service by the service user
        self.storageStation.register_services(service_index=3, service_interface=self.rackRefillingServiceInterface)
        # --------------------------------------------------------------------------------

        # starting the active objects :
        self.statusLED.start()
        self.blinkerStatusLED.start()


        # opcua server ------------------------------------------------------------------
        ip_str = self.get_ip()
        servername = config.SERVER_CONFIG['servername']
        endpoint = 'opc.tcp://' + ip_str + ':4840/' + servername + '/'

        # endpoint = config.SERVER_CONFIG['endpoint']
        uri = config.SERVER_CONFIG['uri']

        self.logger.debug("Building an OPCUA server: %s ", servername)

        self.server = UAServer(endpoint=endpoint,
                               name=servername,
                               uri=uri,
                               station_app=self).server

        self.server_publisher = ServerPublisher(server_name=servername, endpoint=endpoint, logger=self.logger)
        if self.server_publisher.check_connection():
            self.server_publisher.publish()
        else:
            self.logger.info("No connection to the database. OPCUA server was not registered.")

        # setting pub-sub system ---------------------------------------------------------
        self.logger.info("Setting events pub-sub system...")

        # rack's top sensor's subscribers :
        sensorUaNode = self.server.nodes.objects.get_child(["2:Sensor", "2:PresenceSensor3"])
        self.posTopRackSensorUaSubscriber = UaObjectSubscriber(self.server, sensorUaNode)

        self.posTopRackSensor.register_subscribers(topic="State",
                                                   who=self.posTopRackSensorUaSubscriber,
                                                   callback=self.posTopRackSensorUaSubscriber.update)

        self.posTopRackSensor.register_subscribers(topic="Value",
                                                   who=self.posTopRackSensorUaSubscriber,
                                                   callback=self.posTopRackSensorUaSubscriber.update)

        self.posTopRackSensor.register_subscribers(topic="State",
                                                   who=self.rack,
                                                   callback=self.rack.handle_event)
        self.posTopRackSensor.register_subscribers(topic="Value",
                                                   who=self.rack,
                                                   callback=self.rack.handle_event)

        # rack's bottom sensor's subscribers :
        sensorUaNode = self.server.nodes.objects.get_child(["2:Sensor", "2:PresenceSensor4"])
        self.posBottomRackSensorUaSubscriber = UaObjectSubscriber(self.server, sensorUaNode)

        self.posBottomRackSensor.register_subscribers(topic="State",
                                                      who=self.posBottomRackSensorUaSubscriber,
                                                      callback=self.posBottomRackSensorUaSubscriber.update)

        self.posBottomRackSensor.register_subscribers(topic="Value",
                                                      who=self.posBottomRackSensorUaSubscriber,
                                                      callback=self.posBottomRackSensorUaSubscriber.update)

        self.posBottomRackSensor.register_subscribers(topic="State",
                                                      who=self.rack,
                                                      callback=self.rack.handle_event)
        self.posBottomRackSensor.register_subscribers(topic="Value",
                                                      who=self.rack,
                                                      callback=self.rack.handle_event)

        # carriage's back sensor's subscribers :
        sensorUaNode = self.server.nodes.objects.get_child(["2:Sensor", "2:PresenceSensor2"])
        self.posAtRackSensorUaSubscriber = UaObjectSubscriber(self.server, sensorUaNode)

        self.posAtRackSensor.register_subscribers(topic="State",
                                                  who=self.posAtRackSensorUaSubscriber,
                                                  callback=self.posAtRackSensorUaSubscriber.update)

        self.posAtRackSensor.register_subscribers(topic="Value",
                                                  who=self.posAtRackSensorUaSubscriber,
                                                  callback=self.posAtRackSensorUaSubscriber.update)

        self.posAtRackSensor.register_subscribers(topic="State",
                                                  who=self.carriage,
                                                  callback=self.carriage.handle_event)
        self.posAtRackSensor.register_subscribers(topic="Value",
                                                  who=self.carriage,
                                                  callback=self.carriage.handle_event)

        # carriage's front sensor's subscribers :
        sensorUaNode = self.server.nodes.objects.get_child(["2:Sensor", "2:PresenceSensor1"])
        self.posAtFrontSensorUaSubscriber = UaObjectSubscriber(self.server, sensorUaNode)

        self.posAtFrontSensor.register_subscribers(topic="State",
                                                   who=self.posAtFrontSensorUaSubscriber,
                                                   callback=self.posAtFrontSensorUaSubscriber.update)

        self.posAtFrontSensor.register_subscribers(topic="Value",
                                                   who=self.posAtFrontSensorUaSubscriber,
                                                   callback=self.posAtFrontSensorUaSubscriber.update)

        self.posAtFrontSensor.register_subscribers(topic="State",
                                                   who=self.carriage,
                                                   callback=self.carriage.handle_event)
        self.posAtFrontSensor.register_subscribers(topic="Value",
                                                   who=self.carriage,
                                                   callback=self.carriage.handle_event)

        # motor's subscribers :
        motorUaNode = self.server.nodes.objects.get_child(["2:Actor", "2:MotorDC"])
        self.motorUaSubscriber = UaObjectSubscriber(self.server, motorUaNode)
        self.carriageMotor.register_subscribers(topic="State",
                                                who=self.motorUaSubscriber,
                                                callback=self.motorUaSubscriber.update)

        self.carriageMotor.register_subscribers(topic="Value",
                                                who=self.motorUaSubscriber,
                                                callback=self.motorUaSubscriber.update)

        self.carriageMotor.register_subscribers(topic="State",
                                                who=self.carriage,
                                                callback=self.carriage.handle_event)

        # safety switch subscribers :
        sensorUaNode = self.server.nodes.objects.get_child(["2:Sensor", "2:SafetySwitch"])
        self.safetySwitchUaSubscriber = UaObjectSubscriber(self.server, sensorUaNode)

        self.safetySwitch.register_subscribers(topic="State",
                                               who=self.safetySwitchUaSubscriber,
                                               callback=self.safetySwitchUaSubscriber.update)

        self.safetySwitch.register_subscribers(topic="Value",
                                               who=self.safetySwitchUaSubscriber,
                                               callback=self.safetySwitchUaSubscriber.update)

        self.safetySwitch.register_subscribers(topic="State",
                                               who=self.carriage,
                                               callback=self.carriage.handle_event)
        self.safetySwitch.register_subscribers(topic="Value",
                                               who=self.carriage,
                                               callback=self.carriage.handle_event)

        self.safetySwitch.register_subscribers(topic="State",
                                               who=self.carriageMotor,
                                               callback=self.carriageMotor.handle_event)
        self.safetySwitch.register_subscribers(topic="Value",
                                               who=self.carriageMotor,
                                               callback=self.carriageMotor.handle_event)

        self.safetySwitch.register_subscribers(topic="State",
                                               who=self.storageStation,
                                               callback=self.storageStation.handle_event)
        self.safetySwitch.register_subscribers(topic="Value",
                                               who=self.storageStation,
                                               callback=self.storageStation.handle_event)

        self.safetySwitch.register_subscribers(topic="State",
                                               who=self.initService,
                                               callback=self.initService.handle_event)

        self.safetySwitch.register_subscribers(topic="State",
                                               who=self.homingService,
                                               callback=self.homingService.handle_event)

        self.safetySwitch.register_subscribers(topic="State",
                                               who=self.provideDicehalfService,
                                               callback=self.provideDicehalfService.handle_event)


        # carriage occupied sensor subscribers :
        sensorUaNode = self.server.nodes.objects.get_child(["2:Sensor", "2:PresenceSensor5"])
        self.carriageOccupiedSensorUaSubscriber = UaObjectSubscriber(self.server, sensorUaNode)

        self.carriageOccupiedSensor.register_subscribers(topic="State",
                                                         who=self.carriageOccupiedSensorUaSubscriber,
                                                         callback=self.carriageOccupiedSensorUaSubscriber.update)
        self.carriageOccupiedSensor.register_subscribers(topic="Value",
                                                         who=self.carriageOccupiedSensorUaSubscriber,
                                                         callback=self.carriageOccupiedSensorUaSubscriber.update)

        self.carriageOccupiedSensor.register_subscribers(topic="State",
                                                         who=self.initService,
                                                         callback=self.initService.handle_event)

        self.carriageOccupiedSensor.register_subscribers(topic="State",
                                                         who=self.homingService,
                                                         callback=self.homingService.handle_event)
        self.carriageOccupiedSensor.register_subscribers(topic="Value",
                                                         who=self.homingService,
                                                         callback=self.homingService.handle_event)

        self.carriageOccupiedSensor.register_subscribers(topic="Value",
                                                         who=self.provideDicehalfService,
                                                         callback=self.provideDicehalfService.handle_event)
        self.carriageOccupiedSensor.register_subscribers(topic="State",
                                                         who=self.provideDicehalfService,
                                                         callback=self.provideDicehalfService.handle_event)
        # carriage's subscribers :
        self.carriage.register_subscribers(topic="State",
                                           who=self.initService,
                                           callback=self.initService.handle_event)

        self.carriage.register_subscribers(topic="State",
                                           who=self.homingService,
                                           callback=self.homingService.handle_event)

        self.carriage.register_subscribers(topic="State",
                                           who=self.provideDicehalfService,
                                           callback=self.provideDicehalfService.handle_event)

        self.carriage.register_subscribers(topic="State",
                                           who=self.rackRefillingService,
                                           callback=self.rackRefillingService.handle_event)
        self.carriage.register_subscribers(topic="State",
                                       who=self.storageStation,
                                       callback=self.storageStation.handle_event)

        # rack's subscribers :
        self.rack.register_subscribers(topic="State",
                                       who=self.initService,
                                       callback=self.initService.handle_event)

        self.rack.register_subscribers(topic="State",
                                       who=self.homingService,
                                       callback=self.homingService.handle_event)

        self.rack.register_subscribers(topic="State",
                                       who=self.provideDicehalfService,
                                       callback=self.provideDicehalfService.handle_event)

        self.rack.register_subscribers(topic="State",
                                       who=self.rackRefillingService,
                                       callback=self.rackRefillingService.handle_event)

        self.rack.register_subscribers(topic="State",
                                       who=self.storageStation,
                                       callback=self.storageStation.handle_event)


        self.initService.register_subscribers(topic="InitServiceState",
                                              who=self.storageStation,
                                              callback=self.storageStation.handle_event)

        self.homingService.register_subscribers(topic="HomeServiceState",
                                                who=self.storageStation,
                                                callback=self.storageStation.handle_event)

        self.provideDicehalfService.register_subscribers(topic="ProvideDicehalfServiceState",
                                                         who=self.storageStation,
                                                         callback=self.storageStation.handle_event)

        self.rackRefillingService.register_subscribers(topic="RefillingServiceState",
                                                       who=self.storageStation,
                                                       callback=self.storageStation.handle_event)

        # maintenance subscribers :
        maintenanceStatusUaNode = self.server.nodes.objects.get_child(["2:Maintenance"])
        self.maintenanceStatusUaSubscriber = UaObjectSubscriber(self.server, maintenanceStatusUaNode)

        self.storageStation.register_subscribers(topic='StationStateMaintenance',
                                                 who=self.maintenanceStatusUaSubscriber,
                                                 callback=self.maintenanceStatusUaSubscriber.update)

        self.initService.register_subscribers(topic="InitServiceState",
                                              who=self.maintenanceStatusUaSubscriber,
                                              callback=self.maintenanceStatusUaSubscriber.update)

        self.homingService.register_subscribers(topic="HomeServiceState",
                                                who=self.maintenanceStatusUaSubscriber,
                                                callback=self.maintenanceStatusUaSubscriber.update)

        self.provideDicehalfService.register_subscribers(topic="ProvideDicehalfServiceState",
                                                         who=self.maintenanceStatusUaSubscriber,
                                                         callback=self.maintenanceStatusUaSubscriber.update)

        self.rackRefillingService.register_subscribers(topic="RefillingServiceState",
                                                       who=self.maintenanceStatusUaSubscriber,
                                                       callback=self.maintenanceStatusUaSubscriber.update)
        self.rack.register_subscribers(topic="RackState",
                                        who=self.maintenanceStatusUaSubscriber,
                                        callback=self.maintenanceStatusUaSubscriber.update)

        self.carriage.register_subscribers(topic="CarriageState",
                                       who=self.maintenanceStatusUaSubscriber,
                                       callback=self.maintenanceStatusUaSubscriber.update)

        # monitoring subscribers :
        monitoringStatusUaNode = self.server.nodes.objects.get_child(["2:Monitoring"])
        self.monitoringStatusUaSubscriber = UaObjectSubscriber(self.server, monitoringStatusUaNode)

        self.rack.register_subscribers(topic="NumberOfCurrentlyStoredDicehalves",
                                       who=self.monitoringStatusUaSubscriber,
                                       callback=self.monitoringStatusUaSubscriber.update)

        # Station's subscribers :
        stationStateUaNode = self.server.nodes.objects.get_child(["2:StateMachine"])
        self.stationStateUaSubscriber = UaObjectSubscriber(self.server, stationStateUaNode)

        self.storageStation.register_subscribers(topic="StationState",
                                                 who=self.stationStateUaSubscriber,
                                                 callback=self.stationStateUaSubscriber.update)

        self.storageStation.register_subscribers(topic="StationSafetyState",
                                                 who=self.stationStateUaSubscriber,
                                                 callback=self.stationStateUaSubscriber.update)


        # errors and messages pub-sub :

        self.storageStation.register_subscribers(topic="StationErrorCode",
                                                 who=self.stationStateUaSubscriber,
                                                 callback=self.stationStateUaSubscriber.update)

        self.storageStation.register_subscribers(topic="StationErrorDescription",
                                                 who=self.stationStateUaSubscriber,
                                                 callback=self.stationStateUaSubscriber.update)

        self.storageStation.register_subscribers(topic="StationMessageCode",
                                                         who=self.stationStateUaSubscriber,
                                                         callback=self.stationStateUaSubscriber.update)

        self.storageStation.register_subscribers(topic="StationMessageDescription",
                                                         who=self.stationStateUaSubscriber,
                                                         callback=self.stationStateUaSubscriber.update)

        self.carriage.register_subscribers(topic="StationErrorCode",
                                       who=self.stationStateUaSubscriber,
                                       callback=self.stationStateUaSubscriber.update)

        self.carriage.register_subscribers(topic="StationErrorDescription",
                                       who=self.stationStateUaSubscriber,
                                       callback=self.stationStateUaSubscriber.update)

        self.carriage.register_subscribers(topic="StationMessageCode",
                                       who=self.stationStateUaSubscriber,
                                       callback=self.stationStateUaSubscriber.update)

        self.carriage.register_subscribers(topic="StationMessageDescription",
                                       who=self.stationStateUaSubscriber,
                                       callback=self.stationStateUaSubscriber.update)

        self.rack.register_subscribers(topic="StationErrorCode",
                                       who=self.stationStateUaSubscriber,
                                       callback=self.stationStateUaSubscriber.update)

        self.rack.register_subscribers(topic="StationErrorDescription",
                                       who=self.stationStateUaSubscriber,
                                       callback=self.stationStateUaSubscriber.update)

        self.rack.register_subscribers(topic="StationMessageCode",
                                       who=self.stationStateUaSubscriber,
                                       callback=self.stationStateUaSubscriber.update)

        self.rack.register_subscribers(topic="StationMessageDescription",
                                       who=self.stationStateUaSubscriber,
                                       callback=self.stationStateUaSubscriber.update)

        self.initService.register_subscribers(topic="StationErrorDescription",
                                                         who=self.stationStateUaSubscriber,
                                                         callback=self.stationStateUaSubscriber.update)

        self.initService.register_subscribers(topic="StationErrorCode",
                                                         who=self.stationStateUaSubscriber,
                                                         callback=self.stationStateUaSubscriber.update)

        self.initService.register_subscribers(topic="StationMessageCode",
                                                         who=self.stationStateUaSubscriber,
                                                         callback=self.stationStateUaSubscriber.update)

        self.initService.register_subscribers(topic="StationMessageDescription",
                                                         who=self.stationStateUaSubscriber,
                                                         callback=self.stationStateUaSubscriber.update)

        self.provideDicehalfService.register_subscribers(topic="StationErrorDescription",
                                                         who=self.stationStateUaSubscriber,
                                                         callback=self.stationStateUaSubscriber.update)

        self.provideDicehalfService.register_subscribers(topic="StationErrorCode",
                                                         who=self.stationStateUaSubscriber,
                                                         callback=self.stationStateUaSubscriber.update)

        self.provideDicehalfService.register_subscribers(topic="StationMessageCode",
                                       who=self.stationStateUaSubscriber,
                                       callback=self.stationStateUaSubscriber.update)

        self.provideDicehalfService.register_subscribers(topic="StationMessageDescription",
                                                         who=self.stationStateUaSubscriber,
                                                         callback=self.stationStateUaSubscriber.update)

        self.homingService.register_subscribers(topic="StationErrorDescription",
                                                       who=self.stationStateUaSubscriber,
                                                       callback=self.stationStateUaSubscriber.update)

        self.homingService.register_subscribers(topic="StationErrorCode",
                                                       who=self.stationStateUaSubscriber,
                                                       callback=self.stationStateUaSubscriber.update)

        self.homingService.register_subscribers(topic="StationMessageCode",
                                                       who=self.stationStateUaSubscriber,
                                                       callback=self.stationStateUaSubscriber.update)

        self.homingService.register_subscribers(topic="StationMessageDescription",
                                                       who=self.stationStateUaSubscriber,
                                                       callback=self.stationStateUaSubscriber.update)

        self.rackRefillingService.register_subscribers(topic="StationErrorDescription",
                                                         who=self.stationStateUaSubscriber,
                                                         callback=self.stationStateUaSubscriber.update)

        self.rackRefillingService.register_subscribers(topic="StationErrorCode",
                                                         who=self.stationStateUaSubscriber,
                                                         callback=self.stationStateUaSubscriber.update)

        self.rackRefillingService.register_subscribers(topic="StationMessageCode",
                                                         who=self.stationStateUaSubscriber,
                                                         callback=self.stationStateUaSubscriber.update)

        self.rackRefillingService.register_subscribers(topic="StationMessageDescription",
                                                         who=self.stationStateUaSubscriber,
                                                         callback=self.stationStateUaSubscriber.update)
        # ---------------------------------------------------------------------------------------------

        self.storageStation.register_subscribers(topic="Ack",
                                                 who=self.initService,
                                                 callback=self.initService.handle_event)

        self.storageStation.register_subscribers(topic="StationState",
                                                 who=self.initService,
                                                 callback=self.initService.handle_event)

        self.storageStation.register_subscribers(topic="Ack",
                                                 who=self.homingService,
                                                 callback=self.homingService.handle_event)

        self.storageStation.register_subscribers(topic="StationState",
                                                 who=self.homingService,
                                                 callback=self.homingService.handle_event)

        self.storageStation.register_subscribers(topic="Ack",
                                                 who=self.provideDicehalfService,
                                                 callback=self.provideDicehalfService.handle_event)

        self.storageStation.register_subscribers(topic="StationState",
                                                 who=self.provideDicehalfService,
                                                 callback=self.provideDicehalfService.handle_event)

        self.storageStation.register_subscribers(topic="Ack",
                                                 who=self.rackRefillingService,
                                                 callback=self.rackRefillingService.handle_event)

        self.storageStation.register_subscribers(topic="StationState",
                                                 who=self.rackRefillingService,
                                                 callback=self.rackRefillingService.handle_event)


        self.storageStation.register_subscribers(topic="Ack",
                                                 who=self.carriageMotor,
                                                 callback=self.carriageMotor.handle_event)

        self.storageStation.register_subscribers(topic="StationState",
                                                 who=self.rack,
                                                 callback=self.rack.handle_event)

        self.storageStation.register_subscribers(topic="Ack",
                                                 who=self.rack,
                                                 callback=self.rack.handle_event)

        self.storageStation.register_subscribers(topic="Ack",
                                                 who=self.carriage,
                                                 callback=self.carriage.handle_event)

        self.storageStation.register_subscribers(topic="StationState",
                                                 who=self.carriage,
                                                 callback=self.carriage.handle_event)

        self.storageStation.register_subscribers(topic="Ack",
                                                  who=self.safetySwitch,
                                                  callback=self.safetySwitch.handle_event)

        self.storageStation.register_subscribers(topic="Ack",
                                                  who=self.statusLED,
                                                  callback=self.statusLED.handle_event)

        self.storageStation.register_subscribers(topic="Ack",
                                                 who=self.blinkerStatusLED,
                                                 callback=self.blinkerStatusLED.handle_event)

        self.storageStation.register_subscribers(topic="Ack",
                                                 who=self.carriageOccupiedSensor,
                                                 callback=self.carriageOccupiedSensor.handle_event)

        self.storageStation.register_subscribers(topic="Ack",
                                                 who=self.posAtFrontSensor,
                                                 callback=self.posAtFrontSensor.handle_event)

        self.storageStation.register_subscribers(topic="Ack",
                                                 who=self.posAtRackSensor,
                                                 callback=self.posAtRackSensor.handle_event)

        self.storageStation.register_subscribers(topic="Ack",
                                                 who=self.posBottomRackSensor,
                                                 callback=self.posBottomRackSensor.handle_event)

        self.storageStation.register_subscribers(topic="Ack",
                                                 who=self.posTopRackSensor,
                                                 callback=self.posTopRackSensor.handle_event)

        # setting RevPi driver -------------------------------------------------------------
        self.revpiioDriver.handlesignalend(self.shutdown)

        self.logger.debug("Registering handlers for inputs events...")

        self.revpiioDriver.io.input1.reg_event(self.input1_posedge_event, edge=revpimodio2.RISING)
        self.revpiioDriver.io.input1.reg_event(self.input1_negedge_event, edge=revpimodio2.FALLING)
        self.revpiioDriver.io.input2.reg_event(self.input2_posedge_event, edge=revpimodio2.RISING)
        self.revpiioDriver.io.input2.reg_event(self.input2_negedge_event, edge=revpimodio2.FALLING)
        self.revpiioDriver.io.input3.reg_event(self.input3_posedge_event, edge=revpimodio2.RISING)
        self.revpiioDriver.io.input3.reg_event(self.input3_negedge_event, edge=revpimodio2.FALLING)
        self.revpiioDriver.io.input4.reg_event(self.input4_posedge_event, edge=revpimodio2.RISING)
        self.revpiioDriver.io.input4.reg_event(self.input4_negedge_event, edge=revpimodio2.FALLING)
        self.revpiioDriver.io.input5.reg_event(self.input5_posedge_event, edge=revpimodio2.RISING)
        self.revpiioDriver.io.input5.reg_event(self.input5_negedge_event, edge=revpimodio2.FALLING)
        self.revpiioDriver.io.input6.reg_event(self.input6_posedge_event, edge=revpimodio2.RISING)
        self.revpiioDriver.io.input6.reg_event(self.input6_negedge_event, edge=revpimodio2.FALLING)

        # starting everything ------------------------------------------------------------
        self.server.start()
        self.logger.info("OPCUA server %s at %s has started", servername, endpoint)
        self.safetySwitch.start()
        self.carriageMotor.start()
        self.posTopRackSensor.start()
        self.posBottomRackSensor.start()
        self.posAtFrontSensor.start()
        self.posAtRackSensor.start()
        self.carriageOccupiedSensor.start()
        self.rack.start()
        self.carriage.start()
        self.storageStation.start()
        self.initService.start()
        self.homingService.start()
        self.provideDicehalfService.start()
        self.rackRefillingService.start()

        self.connMonitor.start()


    '''def get_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP'''
        
    def get_ip(self):
            try:
                self.network_util = network_util.NetworkUtil()
                IP = self.network_util.get_ipv4()
            except:
                IP = '127.0.0.1'
            return IP


    def shutdown(self):
        self.carriageMotor.stop()
        self.posTopRackSensor.stop()
        self.posBottomRackSensor.stop()
        self.posAtFrontSensor.stop()
        self.posAtRackSensor.stop()
        self.carriageOccupiedSensor.stop()
        self.safetySwitch.stop()
        self.rack.stop()
        self.carriage.stop()

        self.statusLED.led_off()
        self.statusLED.stop()
        self.blinkerStatusLED.stop()

        self.initService.stop()
        self.homingService.stop()
        self.provideDicehalfService.stop()
        self.rackRefillingService.stop()
        self.storageStation.stop()

        self.connMonitor.stop()

        self.server.stop()

    def input1_posedge_event(self, ioname, iovalue):
        self.logger.debug("Input %s : Value %s", ioname, iovalue)
        posedge_event = events.SimpleSensorInputEvent(eventID=events.SimpleSensorInputEvents.PosEdge,
                                                      sender=self._name)
        self.posAtFrontSensor.handle_event(event=posedge_event)

    def input1_negedge_event(self, ioname, iovalue):
        self.logger.debug("Input %s : Value %s", ioname, iovalue)
        negedge_event = events.SimpleSensorInputEvent(eventID=events.SimpleSensorInputEvents.NegEdge,
                                                      sender=self._name)
        self.posAtFrontSensor.handle_event(event=negedge_event)

    def input2_posedge_event(self, ioname, iovalue):
        self.logger.debug("Input %s : Value %s", ioname, iovalue)
        posedge_event = events.SimpleSensorInputEvent(eventID=events.SimpleSensorInputEvents.PosEdge,
                                                      sender=self._name)
        self.posAtRackSensor.handle_event(event=posedge_event)

    def input2_negedge_event(self, ioname, iovalue):
        self.logger.debug("Input %s : Value %s", ioname, iovalue)
        negedge_event = events.SimpleSensorInputEvent(eventID=events.SimpleSensorInputEvents.NegEdge,
                                                      sender=self._name)
        self.posAtRackSensor.handle_event(event=negedge_event)

    def input3_posedge_event(self, ioname, iovalue):
        self.logger.debug("Input %s : Value %s", ioname, iovalue)
        posedge_event = events.SimpleSensorInputEvent(eventID=events.SimpleSensorInputEvents.PosEdge,
                                                      sender=self._name)
        self.carriageOccupiedSensor.handle_event(event=posedge_event)

    def input3_negedge_event(self, ioname, iovalue):
        self.logger.debug("Input %s : Value %s", ioname, iovalue)
        negedge_event = events.SimpleSensorInputEvent(eventID=events.SimpleSensorInputEvents.NegEdge,
                                                      sender=self._name)
        self.carriageOccupiedSensor.handle_event(event=negedge_event)

    def input4_posedge_event(self, ioname, iovalue):
        self.logger.debug("Input %s : Value %s", ioname, iovalue)
        posedge_event = events.SimpleSensorInputEvent(eventID=events.SimpleSensorInputEvents.PosEdge,
                                                      sender=self._name)
        self.posTopRackSensor.handle_event(event=posedge_event)

    def input4_negedge_event(self, ioname, iovalue):
        self.logger.debug("Input %s : Value %s", ioname, iovalue)
        negedge_event = events.SimpleSensorInputEvent(eventID=events.SimpleSensorInputEvents.NegEdge,
                                                      sender=self._name)
        self.posTopRackSensor.handle_event(event=negedge_event)

    def input5_posedge_event(self, ioname, iovalue):
        self.logger.debug("Input %s : Value %s", ioname, iovalue)
        posedge_event = events.SimpleSensorInputEvent(eventID=events.SimpleSensorInputEvents.PosEdge,
                                                      sender=self._name)
        self.safetySwitch.handle_event(event=posedge_event)

    def input5_negedge_event(self, ioname, iovalue):
        self.logger.debug("Input %s : Value %s", ioname, iovalue)
        negedge_event = events.SimpleSensorInputEvent(eventID=events.SimpleSensorInputEvents.NegEdge,
                                                      sender=self._name)
        self.safetySwitch.handle_event(event=negedge_event)

    def input6_posedge_event(self, ioname, iovalue):
        self.logger.debug("Input %s : Value %s", ioname, iovalue)
        posedge_event = events.SimpleSensorInputEvent(eventID=events.SimpleSensorInputEvents.PosEdge,
                                                      sender=self._name)
        self.posBottomRackSensor.handle_event(event=posedge_event)

    def input6_negedge_event(self, ioname, iovalue):
        self.logger.debug("Input %s : Value %s", ioname, iovalue)
        negedge_event = events.SimpleSensorInputEvent(eventID=events.SimpleSensorInputEvents.NegEdge,
                                                      sender=self._name)
        self.posBottomRackSensor.handle_event(event=negedge_event)

    def conn_broken_event(self):
        noconn_event = events.StationInputEvent(eventID=events.StationInputEvents.NoConn,
                                                        sender=self._name)
        self.storageStation.handle_event(event=noconn_event)

    def conn_alive_event(self):
        connok_event = events.StationInputEvent(eventID=events.StationInputEvents.ConnOk,
                                                        sender=self._name)
        self.storageStation.handle_event(event=connok_event)

    def start(self):
        self.revpiioDriver.mainloop(blocking=False)
        self.logger.debug("RevPi driver has been started.")

        # Loop to do some work next to the event system. E.g. Switch on / off green part of LED A1
        while not self.revpiioDriver.exitsignal.is_set():
            self.revpiioDriver.core.a1green.value = not self.revpiioDriver.core.a1green.value

            self.revpiioDriver.exitsignal.wait(0.1)


def main():
    app = StationApp(config.STATION_CONFIG['stationName'])
    app.start()


if __name__ == '__main__':
    main()



