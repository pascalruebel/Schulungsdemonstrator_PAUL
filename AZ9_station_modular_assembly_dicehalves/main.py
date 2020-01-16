import definitions
from communication.server import UAServer, UaObjectSubscriber
from activeobjects.sensors.presencesensor import PresenceSensor
from activeobjects.sensors.safetyswitch import SafetySwitch
from activeobjects.actuators.rgb_led import RGB_LED
from activeobjects.actuators.clamp import SimpleClamp
from activeobjects.actuators.motor import Motor
from activeobjects.actuators.blinker import Blinker
from activeobjects.actuators.blinker_led_adapter import BlinkerLedAdapter
from activeobjects.sensors.forceswitch import ForceSwitch
from activeobjects.press.press import Press
from activeobjects.station.station import Station
from activeobjects.services.initialization.init_service import InitService
from activeobjects.services.homing.homing import HomeService
from activeobjects.services.pressing.press_service import PressService
from activeobjects.services.to_frontpos.to_frontpos import ToFrontPosService
from activeobjects.services.interface import ServiceInterface
from communication import events, conn_monitor, network_util

import revpimodio2
import config
import logging.config
import json
import socket
from communication.server_publisher import ServerPublisher


with open(definitions.LOGCONFIG_PATH, 'r') as logging_config_file:
    config_dict = json.load(logging_config_file)
logging.config.dictConfig(config_dict)


class StationApp(object):
    """ Main application for the station """

    def __init__(self, name):
        self._name = name
        self.logger = logging.getLogger(self._name)

        self.pressing_setpoint = config.STATION_CONFIG['pressingSetpoint']

        self.revpiioDriver = revpimodio2.RevPiModIO(autorefresh=True)

        self.connMonitor = conn_monitor.ConnMonitor(name='ConnMonitor',
                                                    logger=self.logger,
                                                    conn_alive_cb=self.conn_alive_event,
                                                    conn_broken_cb=self.conn_broken_event)

        self.logger.debug("Buiding the station's active objects...")

        # building events ---------------------------------------------------------------
        self.noconn_event = events.StationEvent(eventID=events.StationEvents.NoConn,
                                                     sender='ConnMonitor')
        self.connok_event = events.StationEvent(eventID=events.StationEvents.ConnOk,
                                                     sender='ConnMonitor')

        # building station objects -----------------------------------------------------

        self.safetySwitch = SafetySwitch("SafetySwitch",
                                         "-SF1",
                                         topics=["State", "Value", 'StationErrorCode', 'StationErrorDescription',
                                                             'StationMessageCode', 'StationMessageDescription'],
                                         inputobj=self.revpiioDriver.io['input9'],
                                         auto_init=True,
                                         normally_open=True)

        # sensors -----------------------------------------------------------------------

        self.pressMotor = Motor("MotorPress", "MA1",
                                rotate_cw=self.revpiioDriver.io['output4'],
                                rotate_ccw=self.revpiioDriver.io['output5'],
                                topics=["State", "Value", 'StationErrorCode', 'StationErrorDescription',
                                        'StationMessageCode', 'StationMessageDescription'])



        self.forceSwitch = ForceSwitch("SensorForceAtPressing", "-BG1",
                                       topics=["State", "Value", "AnalogValue",'StationErrorCode',
                                                'StationErrorDescription','StationMessageCode','StationMessageDescription'],
                                                inputobj=self.revpiioDriver.io['InputValue_1'],
                                                outputobj=self.revpiioDriver.io['OutputValue_1'],
                                                force_limit=200.0,
                                                monitor_interval=0.25,  # not used in this version
                                                motor=self.pressMotor)
        # ToDo : set the real force limit


        self.atPressPosSensor = PresenceSensor("SensorDiceAtPressPos", "-BG2",
                                                topics=["State", "Value", 'StationErrorCode', 'StationErrorDescription',
                                                        'StationMessageCode', 'StationMessageDescription'],
                                                inputobj=self.revpiioDriver.io['input13'],
                                                normally_open=False)

        self.endSwitchPress = PresenceSensor("SensorSafetyPressAtMaxLength", "-BG3",
                                                topics=["State", "Value", 'StationErrorCode', 'StationErrorDescription',
                                                    'StationMessageCode', 'StationMessageDescription'],
                                                inputobj=self.revpiioDriver.io['input14'],
                                                normally_open=False)

        self.atFrontPosSensor = PresenceSensor("SensorDiceCarriageAtHome","-BG4",
                                                topics=["State", "Value",'StationErrorCode', 'StationErrorDescription',
                                                             'StationMessageCode', 'StationMessageDescription'],
                                                inputobj=self.revpiioDriver.io['input11'],
                                                normally_open=False)

        self.upPosPress = PresenceSensor("SensorLinearPosOfPress", "-BG5",
                                                topics=["State", "Value", 'StationErrorCode', 'StationErrorDescription',
                                                             'StationMessageCode', 'StationMessageDescription'],
                                               inputobj=self.revpiioDriver.io['input12'],
                                               normally_open=False)


        # actuators  --------------------------------------------------------------------



        self.clamp = SimpleClamp("ElectromagnetAnchor", "-MA2",
                                 revpi_output=self.revpiioDriver.io['output7'],
                                 topics=["State", "Value", 'StationErrorCode', 'StationErrorDescription',
                                         'StationMessageCode', 'StationMessageDescription'])


        self.blinker_led_adapter = BlinkerLedAdapter(hw_output_red=self.revpiioDriver.io['PWM_R'],
                                                     hw_output_green=self.revpiioDriver.io['PWM_G'],
                                                     hw_output_blue=self.revpiioDriver.io['PWM_B'])

        self.statusLED = RGB_LED("RgbLed", "-PF1",
                                 revpi_red=self.blinker_led_adapter.red,
                                 revpi_green=self.blinker_led_adapter.green,
                                 revpi_blue=self.blinker_led_adapter.blue,
                                 topics=["State", "Value", 'StationErrorCode', 'StationErrorDescription',
                                         'StationMessageCode', 'StationMessageDescription'])

        self.blinker = Blinker('Blinker', shutter=self.blinker_led_adapter, ontime=0.5, offtime=0.5)


        # station parts -----------------------------------------------------------------

        self.press = Press("Press", motor=self.pressMotor,
                                    uppos_sensor=self.upPosPress,
                                    endswitch_sensor=self.endSwitchPress,
                                    force_sensor=self.forceSwitch,
                                    enable_timeout=True,
                                    timeout_interval=config.STATION_CONFIG['pressMoveTimeout'],
                                    topics=["PressState", "State", 'StationErrorCode', 'StationErrorDescription',
                                                             'StationMessageCode', 'StationMessageDescription'])

        self.assemblyStation = Station("Station",
                                       status_led=self.statusLED,
                                       motor=self.pressMotor,
                                       press=self.press,
                                       clamp=self.clamp,
                                       blinker=self.blinker,
                                       safety_switch=self.safetySwitch,
                                       topics=['StationState', 'Ack', 'StationErrorCode',
                                                     'StationErrorDescription', 'StationSafetyState',
                                                     'StationMessageCode', 'StationMessageDescription', 'StationStateMaintenance'])

        # building and registering services -----------------------------------------------

        # 1) create an initialization service:

        dev_list = [self.safetySwitch, self.atPressPosSensor, self.endSwitchPress, self.atFrontPosSensor,
                    self.upPosPress, self.forceSwitch,
                    self.pressMotor, self.clamp, self.press]

        self.initService = InitService(name='InitializationService',
                                       dev_list=dev_list,
                                       enable_timeout=True,
                                       timeout_interval=config.STATION_CONFIG['initServiceTimeoutInterval'],
                                       topics=['eventID', 'StationErrorCode', 'StationErrorDescription',
                                                'StationMessageCode', 'StationMessageDescription', 'InitServiceState'])

        # create a service interface
        self.initializationServiceInterface = ServiceInterface(service_user=self.assemblyStation,
                                                               service=self.initService,
                                                               service_index=0)

        self.initService.setup_service(service_index=0, service_interface=self.initializationServiceInterface)

        self.assemblyStation.register_services(service_index=0, service_interface=self.initializationServiceInterface)


        #  homing service :
        self.homingService = HomeService(name="HomingService",
                                         press=self.press,
                                         clamp=self.clamp,
                                         frontpos_sensor=self.atFrontPosSensor,
                                         enable_timeout=True,
                                         timeout_interval=config.STATION_CONFIG['homeServiceTimeoutInterval'],
                                         topics=['eventID', 'StationErrorCode', 'StationErrorDescription',
                                                'StationMessageCode', 'StationMessageDescription', 'HomeServiceState'])

        self.homingServiceInterface = ServiceInterface(service_user=self.assemblyStation,
                                                         service=self.homingService,
                                                         service_index=1)

        self.homingService.setup_service(service_index=1, service_interface=self.homingServiceInterface)

        self.assemblyStation.register_services(service_index=1, service_interface=self.homingServiceInterface)


        #  pressing service :
        self.pressingService = PressService(name="PressService",
                                            press=self.press,
                                            clamp=self.clamp,
                                            frontpos_sensor=self.atFrontPosSensor,
                                            presspos_sensor=self.atPressPosSensor,
                                            blinker=self.blinker,
                                            enable_timeout=True,
                                            timeout_interval=config.STATION_CONFIG['pressServiceTimeoutInterval'],
                                            topics=['eventID', 'StationErrorCode', 'StationErrorDescription',
                                                     'StationMessageCode', 'StationMessageDescription', 'PressServiceState'])

        # create a service interface
        self.pressingServiceInterface = ServiceInterface(service_user=self.assemblyStation,
                                                               service=self.pressingService,
                                                               service_index=2)
        # set the service
        self.pressingService.setup_service(service_index=2, service_interface=self.pressingServiceInterface)

        # regester the service by the service user
        self.assemblyStation.register_services(service_index=2, service_interface=self.pressingServiceInterface)

        #  to front position service :
        self.toFrontPosService = ToFrontPosService(name="ToFrontPosService",
                                            press=self.press,
                                            clamp=self.clamp,
                                            frontpos_sensor=self.atFrontPosSensor,
                                            presspos_sensor=self.atPressPosSensor,
                                            blinker=self.blinker,
                                            enable_timeout=True,
                                            timeout_interval=config.STATION_CONFIG['tofrontServiceTimeoutInterval'],
                                            topics=['eventID', 'StationErrorCode', 'StationErrorDescription',
                                                     'StationMessageCode', 'StationMessageDescription', 'ToFrontPosServiceState'])

        # create a service interface
        self.toFrontPosServiceInterface = ServiceInterface(service_user=self.assemblyStation,
                                                         service=self.toFrontPosService,
                                                         service_index=3)
        # set the service
        self.toFrontPosService.setup_service(service_index=3, service_interface=self.toFrontPosServiceInterface)

        # regester the service by the service user
        self.assemblyStation.register_services(service_index=3, service_interface=self.toFrontPosServiceInterface)
        # --------------------------------------------------------------------------------

        # starting the active objects :
        self.statusLED.start()
        self.blinker.start()
        self.assemblyStation.start()

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

        # self.server_publisher = ServerPublisher(server_name=servername, endpoint=endpoint, logger=self.logger)
        # self.server_publisher.publish()
        self.server_publisher = ServerPublisher(server_name=servername, endpoint=endpoint, logger=self.logger)
        if self.server_publisher.check_connection():
            self.server_publisher.publish()
        else:
            self.logger.info("No connection to the database. OPCUA server was not registered.")

        # setting pub-sub system ---------------------------------------------------------
        self.logger.info("Setting events pub-sub system...")

        # safety switch sensor subscribers :
        sensorUaNode = self.server.nodes.objects.get_child(["2:Sensor", "2:SafetySwitch"])
        self.safetySwitchUaSubscriber = UaObjectSubscriber(self.server, sensorUaNode)

        self.safetySwitch.register_subscribers(topic="State",
                                              who=self.safetySwitchUaSubscriber,
                                              callback=self.safetySwitchUaSubscriber.update)

        self.safetySwitch.register_subscribers(topic="Value",
                                              who=self.safetySwitchUaSubscriber,
                                              callback=self.safetySwitchUaSubscriber.update)

        self.safetySwitch.register_subscribers(topic="State",
                                               who=self.pressMotor,
                                               callback=self.pressMotor.handle_event)

        self.safetySwitch.register_subscribers(topic="Value",
                                               who=self.pressMotor,
                                               callback=self.pressMotor.handle_event)

        self.safetySwitch.register_subscribers(topic="State",
                                               who=self.assemblyStation,
                                               callback=self.assemblyStation.handle_event)

        self.safetySwitch.register_subscribers(topic="Value",
                                               who=self.assemblyStation,
                                               callback=self.assemblyStation.handle_event)

        self.safetySwitch.register_subscribers(topic="State",
                                               who=self.initService,
                                               callback=self.initService.handle_event)

        self.safetySwitch.register_subscribers(topic="State",
                                               who=self.homingService,
                                               callback=self.homingService.handle_event)

        self.safetySwitch.register_subscribers(topic="State",
                                               who=self.pressingService,
                                               callback=self.pressingService.handle_event)


        # force sensor subscribers :

        self.forceSwitch.register_subscribers(topic="Value",
                                              who=self.press,
                                              callback=self.press.handle_event)

        self.forceSwitch.register_subscribers(topic="State",
                                                   who=self.initService,
                                                   callback=self.initService.handle_event)

        self.forceSwitch.register_subscribers(topic="State",
                                                  who=self.press,
                                                  callback=self.press.handle_event)

        sensorUaNode = self.server.nodes.objects.get_child(["2:Sensor", "2:PhysicalValueSensor"])
        self.physicalAnalogValueSensorUaSubscriber = UaObjectSubscriber(self.server, sensorUaNode)

        self.forceSwitch.register_subscribers(topic="State",
                                              who=self.physicalAnalogValueSensorUaSubscriber,
                                              callback=self.physicalAnalogValueSensorUaSubscriber.update)

        self.forceSwitch.register_subscribers(topic="AnalogValue",
                                              who=self.physicalAnalogValueSensorUaSubscriber,
                                              callback=self.physicalAnalogValueSensorUaSubscriber.update)

        sensorUaNode = self.server.nodes.objects.get_child(["2:Sensor", "2:PresenceSensor5"])
        self.physicalValueSensorUaSubscriber = UaObjectSubscriber(self.server, sensorUaNode)
        self.forceSwitch.register_subscribers(topic="State",
                                              who=self.physicalValueSensorUaSubscriber,
                                              callback=self.physicalValueSensorUaSubscriber.update)

        self.forceSwitch.register_subscribers(topic="Value",
                                              who=self.physicalValueSensorUaSubscriber,
                                              callback=self.physicalValueSensorUaSubscriber.update)


        # at press position sensor subscribers :
        sensorUaNode = self.server.nodes.objects.get_child(["2:Sensor", "2:PresenceSensor1"])
        self.atPressPosSensorUaSubscriber = UaObjectSubscriber(self.server, sensorUaNode)

        self.atPressPosSensor.register_subscribers(topic="State",
                                                   who=self.atPressPosSensorUaSubscriber,
                                                   callback=self.atPressPosSensorUaSubscriber.update)

        self.atPressPosSensor.register_subscribers(topic="Value",
                                                  who=self.atPressPosSensorUaSubscriber,
                                                  callback=self.atPressPosSensorUaSubscriber.update)

        self.atPressPosSensor.register_subscribers(topic="State",
                                                  who=self.initService,
                                                  callback=self.initService.handle_event)

        self.atPressPosSensor.register_subscribers(topic="State",
                                                  who=self.pressingService,
                                                  callback=self.pressingService.handle_event)
        self.atPressPosSensor.register_subscribers(topic="Value",
                                                  who=self.pressingService,
                                                  callback=self.pressingService.handle_event)

        # end switch sensor subscribers :
        sensorUaNode = self.server.nodes.objects.get_child(["2:Sensor", "2:PresenceSensor2"])
        self.upPosPressUaSubscriber = UaObjectSubscriber(self.server, sensorUaNode)

        self.endSwitchPress.register_subscribers(topic="State",
                                                 who=self.upPosPressUaSubscriber,
                                                 callback=self.upPosPressUaSubscriber.update)

        self.endSwitchPress.register_subscribers(topic="Value",
                                                 who=self.upPosPressUaSubscriber,
                                                 callback=self.upPosPressUaSubscriber.update)

        self.endSwitchPress.register_subscribers(topic="State",
                                                  who=self.initService,
                                                  callback=self.initService.handle_event)

        self.endSwitchPress.register_subscribers(topic="State",
                                                  who=self.press,
                                                  callback=self.press.handle_event)
        self.endSwitchPress.register_subscribers(topic="Value",
                                                  who=self.press,
                                                  callback=self.press.handle_event)

        # at front position sensor subscribers :
        sensorUaNode = self.server.nodes.objects.get_child(["2:Sensor", "2:PresenceSensor3"])
        self.atFrontPosSensorUaSubscriber = UaObjectSubscriber(self.server, sensorUaNode)

        self.atFrontPosSensor.register_subscribers(topic="State",
                                                   who=self.atFrontPosSensorUaSubscriber,
                                                   callback=self.atFrontPosSensorUaSubscriber.update)

        self.atFrontPosSensor.register_subscribers(topic="Value",
                                                   who=self.atFrontPosSensorUaSubscriber,
                                                   callback=self.atFrontPosSensorUaSubscriber.update)

        self.atFrontPosSensor.register_subscribers(topic="State",
                                                  who=self.initService,
                                                  callback=self.initService.handle_event)

        self.atFrontPosSensor.register_subscribers(topic="State",
                                                  who=self.homingService,
                                                  callback=self.homingService.handle_event)
        self.atFrontPosSensor.register_subscribers(topic="Value",
                                                  who=self.homingService,
                                                  callback=self.homingService.handle_event)

        self.atFrontPosSensor.register_subscribers(topic="State",
                                                   who=self.pressingService,
                                                   callback=self.pressingService.handle_event)
        self.atFrontPosSensor.register_subscribers(topic="Value",
                                                   who=self.pressingService,
                                                   callback=self.pressingService.handle_event)

        self.atFrontPosSensor.register_subscribers(topic="State",
                                                   who=self.toFrontPosService,
                                                   callback=self.toFrontPosService.handle_event)
        self.atFrontPosSensor.register_subscribers(topic="Value",
                                                   who=self.toFrontPosService,
                                                   callback=self.toFrontPosService.handle_event)

        # press's upper position sensor subscribers :
        sensorUaNode = self.server.nodes.objects.get_child(["2:Sensor", "2:PresenceSensor4"])
        self.upPosPressUaSubscriber = UaObjectSubscriber(self.server, sensorUaNode)

        self.upPosPress.register_subscribers(topic="State",
                                             who=self.upPosPressUaSubscriber,
                                             callback=self.upPosPressUaSubscriber.update)

        self.upPosPress.register_subscribers(topic="Value",
                                             who=self.upPosPressUaSubscriber,
                                             callback=self.upPosPressUaSubscriber.update)

        self.upPosPress.register_subscribers(topic="State",
                                                  who=self.initService,
                                                  callback=self.initService.handle_event)

        self.upPosPress.register_subscribers(topic="State",
                                                  who=self.press,
                                                  callback=self.press.handle_event)
        self.upPosPress.register_subscribers(topic="Value",
                                                  who=self.press,
                                                  callback=self.press.handle_event)

        # press motor subscribers :

        self.pressMotor.register_subscribers(topic="State",
                                             who=self.press,
                                             callback=self.press.handle_event)
        self.pressMotor.register_subscribers(topic="Value",
                                             who=self.press,
                                             callback=self.press.handle_event)


        ledUaNode = self.server.nodes.objects.get_child(["2:Actor", "2:MotorDC"])
        self.pressMotorUaSubscriber = UaObjectSubscriber(self.server, ledUaNode)
        self.pressMotor.register_subscribers(topic="State",
                                               who=self.pressMotorUaSubscriber,
                                               callback=self.pressMotorUaSubscriber.update)

        self.pressMotor.register_subscribers(topic="Value",
                                               who=self.pressMotorUaSubscriber,
                                               callback=self.pressMotorUaSubscriber.update)

        self.pressMotor.register_subscribers(topic="State",
                                                  who=self.initService,
                                                  callback=self.initService.handle_event)



        # maintenance subscribers :
        pressStatusUaNode = self.server.nodes.objects.get_child(["2:Maintenance"])
        self.maintenanceStatusUaSubscriber = UaObjectSubscriber(self.server, pressStatusUaNode)
        self.press.register_subscribers(topic="PressState",
                                             who=self.maintenanceStatusUaSubscriber,
                                             callback=self.maintenanceStatusUaSubscriber.update)

        self.initService.register_subscribers(topic="InitServiceState",
                                              who=self.maintenanceStatusUaSubscriber,
                                              callback=self.maintenanceStatusUaSubscriber.update)

        self.homingService.register_subscribers(topic="HomeServiceState",
                                                who=self.maintenanceStatusUaSubscriber,
                                                callback=self.maintenanceStatusUaSubscriber.update)

        self.pressingService.register_subscribers(topic="PressServiceState",
                                                  who=self.maintenanceStatusUaSubscriber,
                                                  callback=self.maintenanceStatusUaSubscriber.update)

        self.toFrontPosService.register_subscribers(topic="ToFrontPosServiceState",
                                                    who=self.maintenanceStatusUaSubscriber,
                                                    callback=self.maintenanceStatusUaSubscriber.update)

        self.initService.register_subscribers(topic="InitServiceState",
                                              who=self.assemblyStation,
                                              callback=self.assemblyStation.handle_event)

        self.homingService.register_subscribers(topic="HomeServiceState",
                                                who=self.assemblyStation,
                                                callback=self.assemblyStation.handle_event)

        self.pressingService.register_subscribers(topic="PressServiceState",
                                                  who=self.assemblyStation,
                                                  callback=self.assemblyStation.handle_event)

        self.toFrontPosService.register_subscribers(topic="ToFrontPosServiceState",
                                                    who=self.assemblyStation,
                                                    callback=self.assemblyStation.handle_event)

        # press subscribers :
        self.press.register_subscribers(topic="State",
                                        who=self.initService,
                                        callback=self.initService.handle_event)

        self.press.register_subscribers(topic="State",
                                        who=self.homingService,
                                        callback=self.homingService.handle_event)

        self.press.register_subscribers(topic="State",
                                        who=self.pressingService,
                                        callback=self.pressingService.handle_event)

        self.press.register_subscribers(topic="State",
                                        who=self.toFrontPosService,
                                        callback=self.toFrontPosService.handle_event)

        self.press.register_subscribers(topic="State",
                                        who=self.assemblyStation,
                                        callback=self.assemblyStation.handle_event)



        # clamp subscribers :
        ledUaNode = self.server.nodes.objects.get_child(["2:Actor", "2:Electromagnet"])
        self.clampUaSubscriber = UaObjectSubscriber(self.server, ledUaNode)
        self.clamp.register_subscribers(topic="State",
                                        who=self.clampUaSubscriber,
                                        callback=self.clampUaSubscriber.update)

        self.clamp.register_subscribers(topic="Value",
                                        who=self.clampUaSubscriber,
                                        callback=self.clampUaSubscriber.update)

        self.clamp.register_subscribers(topic="State",
                                               who=self.initService,
                                               callback=self.initService.handle_event)

        # RgbLed subscribers :
        ledUaNode = self.server.nodes.objects.get_child(["2:Actor", "2:StatusLed"])
        self.statusLEDUaSubscriber = UaObjectSubscriber(self.server, ledUaNode)
        self.statusLED.register_subscribers(topic="State",
                                            who=self.statusLEDUaSubscriber,
                                            callback=self.statusLEDUaSubscriber.update)

        self.statusLED.register_subscribers(topic="Value",
                                            who=self.statusLEDUaSubscriber,
                                            callback=self.statusLEDUaSubscriber.update)


        # Station's subscribers :
        stationStateUaNode = self.server.nodes.objects.get_child(["2:StateMachine"])
        self.stationStateUaSubscriber = UaObjectSubscriber(self.server, stationStateUaNode)

        self.assemblyStation.register_subscribers(topic="StationState",
                                                  who=self.stationStateUaSubscriber,
                                                  callback=self.stationStateUaSubscriber.update)

        self.assemblyStation.register_subscribers(topic="StationErrorCode",
                                                  who=self.stationStateUaSubscriber,
                                                  callback=self.stationStateUaSubscriber.update)

        self.assemblyStation.register_subscribers(topic="StationErrorDescription",
                                                  who=self.stationStateUaSubscriber,
                                                  callback=self.stationStateUaSubscriber.update)

        self.assemblyStation.register_subscribers(topic="StationMessageCode",
                                                 who=self.stationStateUaSubscriber,
                                                 callback=self.stationStateUaSubscriber.update)

        self.assemblyStation.register_subscribers(topic="StationMessageDescription",
                                                 who=self.stationStateUaSubscriber,
                                                 callback=self.stationStateUaSubscriber.update)

        self.assemblyStation.register_subscribers(topic="StationErrorCode",
                                                  who=self.stationStateUaSubscriber,
                                                  callback=self.stationStateUaSubscriber.update)

        self.initService.register_subscribers(topic="StationErrorDescription",
                                                  who=self.stationStateUaSubscriber,
                                                  callback=self.stationStateUaSubscriber.update)

        self.initService.register_subscribers(topic="StationMessageCode",
                                                  who=self.stationStateUaSubscriber,
                                                  callback=self.stationStateUaSubscriber.update)

        self.initService.register_subscribers(topic="StationMessageDescription",
                                                  who=self.stationStateUaSubscriber,
                                                  callback=self.stationStateUaSubscriber.update)

        self.initService.register_subscribers(topic="StationErrorCode",
                                                  who=self.stationStateUaSubscriber,
                                                  callback=self.stationStateUaSubscriber.update)

        self.homingService.register_subscribers(topic="StationErrorDescription",
                                                  who=self.stationStateUaSubscriber,
                                                  callback=self.stationStateUaSubscriber.update)

        self.homingService.register_subscribers(topic="StationMessageCode",
                                                  who=self.stationStateUaSubscriber,
                                                  callback=self.stationStateUaSubscriber.update)

        self.homingService.register_subscribers(topic="StationMessageDescription",
                                                  who=self.stationStateUaSubscriber,
                                                  callback=self.stationStateUaSubscriber.update)

        self.pressingService.register_subscribers(topic="StationErrorCode",
                                                who=self.stationStateUaSubscriber,
                                                callback=self.stationStateUaSubscriber.update)

        self.pressingService.register_subscribers(topic="StationErrorDescription",
                                                who=self.stationStateUaSubscriber,
                                                callback=self.stationStateUaSubscriber.update)

        self.pressingService.register_subscribers(topic="StationMessageCode",
                                                who=self.stationStateUaSubscriber,
                                                callback=self.stationStateUaSubscriber.update)

        self.pressingService.register_subscribers(topic="StationMessageDescription",
                                                who=self.stationStateUaSubscriber,
                                                callback=self.stationStateUaSubscriber.update)

        self.toFrontPosService.register_subscribers(topic="StationErrorCode",
                                                  who=self.stationStateUaSubscriber,
                                                  callback=self.stationStateUaSubscriber.update)

        self.toFrontPosService.register_subscribers(topic="StationErrorDescription",
                                                  who=self.stationStateUaSubscriber,
                                                  callback=self.stationStateUaSubscriber.update)

        self.toFrontPosService.register_subscribers(topic="StationMessageCode",
                                                  who=self.stationStateUaSubscriber,
                                                  callback=self.stationStateUaSubscriber.update)

        self.toFrontPosService.register_subscribers(topic="StationMessageDescription",
                                                  who=self.stationStateUaSubscriber,
                                                  callback=self.stationStateUaSubscriber.update)

        self.press.register_subscribers(topic="StationErrorCode",
                                                    who=self.stationStateUaSubscriber,
                                                    callback=self.stationStateUaSubscriber.update)

        self.press.register_subscribers(topic="StationErrorDescription",
                                                    who=self.stationStateUaSubscriber,
                                                    callback=self.stationStateUaSubscriber.update)

        self.press.register_subscribers(topic="StationMessageCode",
                                                    who=self.stationStateUaSubscriber,
                                                    callback=self.stationStateUaSubscriber.update)

        self.press.register_subscribers(topic="StationMessageDescription",
                                                    who=self.stationStateUaSubscriber,
                                                    callback=self.stationStateUaSubscriber.update)




        self.assemblyStation.register_subscribers(topic="StationSafetyState",
                                                  who=self.stationStateUaSubscriber,
                                                  callback=self.stationStateUaSubscriber.update)

        self.assemblyStation.register_subscribers(topic="StationState",
                                                  who=self.initService,
                                                  callback=self.initService.handle_event)

        self.assemblyStation.register_subscribers(topic="StationState",
                                                  who=self.homingService,
                                                  callback=self.homingService.handle_event)

        self.assemblyStation.register_subscribers(topic="StationState",
                                                  who=self.pressingService,
                                                  callback=self.pressingService.handle_event)

        self.assemblyStation.register_subscribers(topic="StationState",
                                                  who=self.toFrontPosService,
                                                  callback=self.toFrontPosService.handle_event)

        # ---------------------------------------------------------------------------------------------

        self.assemblyStation.register_subscribers(topic="Ack",
                                                  who=self.initService,
                                                  callback=self.initService.handle_event)

        self.assemblyStation.register_subscribers(topic="Ack",
                                                  who=self.homingService,
                                                  callback=self.homingService.handle_event)

        self.assemblyStation.register_subscribers(topic="Ack",
                                                  who=self.pressingService,
                                                  callback=self.pressingService.handle_event)

        self.assemblyStation.register_subscribers(topic="Ack",
                                                  who=self.toFrontPosService,
                                                  callback=self.toFrontPosService.handle_event)

        self.assemblyStation.register_subscribers(topic="Ack",
                                                  who=self.press,
                                                  callback=self.press.handle_event)

        self.assemblyStation.register_subscribers(topic="Ack",
                                                  who=self.pressMotor,
                                                  callback=self.pressMotor.handle_event)

        self.assemblyStation.register_subscribers(topic="Ack",
                                                  who=self.atFrontPosSensor,
                                                  callback=self.atFrontPosSensor.handle_event)

        self.assemblyStation.register_subscribers(topic="Ack",
                                                  who=self.atPressPosSensor,
                                                  callback=self.atPressPosSensor.handle_event)

        self.assemblyStation.register_subscribers(topic="Ack",
                                                  who=self.upPosPress,
                                                  callback=self.upPosPress.handle_event)

        self.assemblyStation.register_subscribers(topic="Ack",
                                                  who=self.endSwitchPress,
                                                  callback=self.endSwitchPress.handle_event)

        self.assemblyStation.register_subscribers(topic="Ack",
                                                  who=self.forceSwitch,
                                                  callback=self.forceSwitch.handle_event)

        self.assemblyStation.register_subscribers(topic="Ack",
                                                  who=self.statusLED,
                                                  callback=self.statusLED.handle_event)

        self.assemblyStation.register_subscribers(topic="Ack",
                                                  who=self.clamp,
                                                  callback=self.clamp.handle_event)

        self.assemblyStation.register_subscribers(topic="Ack",
                                                  who=self.safetySwitch,
                                                  callback=self.safetySwitch.handle_event)

        self.assemblyStation.register_subscribers(topic="Ack",
                                                  who=self.blinker,
                                                  callback=self.blinker.handle_event)


        # setting RevPi driver -------------------------------------------------------------
        self.revpiioDriver.handlesignalend(self.shutdown)

        self.revpiioDriver.io.OutputValue_1.value = 5000
        # print output value to make sure
        j = self.revpiioDriver.io.OutputValue_1.value
        self.logger.info("OutputVoltage: %sV", j/1000)

        self.logger.info("Registering handlers for inputs events...")

        self.revpiioDriver.io.input11.reg_event(self.input1_posedge_event, edge=revpimodio2.RISING)
        self.revpiioDriver.io.input11.reg_event(self.input1_negedge_event, edge=revpimodio2.FALLING)
        self.revpiioDriver.io.input12.reg_event(self.input2_posedge_event, edge=revpimodio2.RISING)
        self.revpiioDriver.io.input12.reg_event(self.input2_negedge_event, edge=revpimodio2.FALLING)
        self.revpiioDriver.io.input13.reg_event(self.input3_posedge_event, edge=revpimodio2.RISING)
        self.revpiioDriver.io.input13.reg_event(self.input3_negedge_event, edge=revpimodio2.FALLING)
        self.revpiioDriver.io.input14.reg_event(self.input4_posedge_event, edge=revpimodio2.RISING)
        self.revpiioDriver.io.input14.reg_event(self.input4_negedge_event, edge=revpimodio2.FALLING)
        self.revpiioDriver.io.input9.reg_event(self.input5_posedge_event, edge=revpimodio2.RISING)
        self.revpiioDriver.io.input9.reg_event(self.input5_negedge_event, edge=revpimodio2.FALLING)
        # self.revpiioDriver.io.input6.reg_event(self.input6_posedge_event, edge=revpimodio2.RISING)
        # self.revpiioDriver.io.input6.reg_event(self.input6_negedge_event, edge=revpimodio2.FALLING)

        # starting everything ------------------------------------------------------------
        self.server.start()
        self.logger.info("OPCUA server %s at %s has started", servername, endpoint)
        self.safetySwitch.start()
        self.forceSwitch.start()
        self.atPressPosSensor.start()
        self.atFrontPosSensor.start()
        self.upPosPress.start()
        self.endSwitchPress.start()
        self.pressMotor.start()
        self.clamp.start()
        self.press.start()
        self.initService.start()
        self.homingService.start()
        self.pressingService.start()
        self.toFrontPosService.start()

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
        self.safetySwitch.stop()
        self.forceSwitch.stop()
        self.atPressPosSensor.stop()
        self.atFrontPosSensor.stop()
        self.upPosPress.stop()
        self.endSwitchPress.stop()
        self.pressMotor.stop()
        self.clamp.stop()
        self.statusLED.led_off()
        self.statusLED.stop()
        self.press.stop()
        self.initService.stop()
        self.homingService.stop()
        self.pressingService.stop()
        self.toFrontPosService.stop()
        self.assemblyStation.stop()
        self.connMonitor.stop()
        self.blinker.stop()

        self.server.stop()

        self.revpiioDriver.exit()

    def input1_posedge_event(self, ioname, iovalue):
        self.logger.debug("Input %s : Value %s", ioname, iovalue)
        posedge_event = events.SimpleSensorInputEvent(eventID=events.SimpleSensorInputEvents.PosEdge,
                                                         sender=self._name)
        self.atFrontPosSensor.handle_event(event=posedge_event)

    def input1_negedge_event(self, ioname, iovalue):
        self.logger.debug("Input %s : Value %s", ioname, iovalue)
        negedge_event = events.SimpleSensorInputEvent(eventID=events.SimpleSensorInputEvents.NegEdge,
                                                      sender=self._name)
        self.atFrontPosSensor.handle_event(event=negedge_event)

    def input2_posedge_event(self, ioname, iovalue):
        self.logger.debug("Input %s : Value %s", ioname, iovalue)
        posedge_event = events.SimpleSensorInputEvent(eventID=events.SimpleSensorInputEvents.PosEdge,
                                                      sender=self._name)
        self.upPosPress.handle_event(event=posedge_event)

    def input2_negedge_event(self, ioname, iovalue):
        self.logger.debug("Input %s : Value %s", ioname, iovalue)

        self.logger.debug("Input %s : Value %s", ioname, iovalue)
        negedge_event = events.SimpleSensorInputEvent(eventID=events.SimpleSensorInputEvents.NegEdge,
                                                      sender=self._name)
        self.upPosPress.handle_event(event=negedge_event)

    def input3_posedge_event(self, ioname, iovalue):
        self.logger.debug("Input %s : Value %s", ioname, iovalue)
        posedge_event = events.SimpleSensorInputEvent(eventID=events.SimpleSensorInputEvents.PosEdge,
                                                      sender=self._name)
        self.atPressPosSensor.handle_event(event=posedge_event)

    def input3_negedge_event(self, ioname, iovalue):
        self.logger.debug("Input %s : Value %s", ioname, iovalue)

        self.logger.debug("Input %s : Value %s", ioname, iovalue)
        negedge_event = events.SimpleSensorInputEvent(eventID=events.SimpleSensorInputEvents.NegEdge,
                                                      sender=self._name)
        self.atPressPosSensor.handle_event(event=negedge_event)

    def input4_posedge_event(self, ioname, iovalue):
        self.logger.debug("Input %s : Value %s", ioname, iovalue)
        posedge_event = events.SimpleSensorInputEvent(eventID=events.SimpleSensorInputEvents.PosEdge,
                                                      sender=self._name)
        self.endSwitchPress.handle_event(event=posedge_event)

    def input4_negedge_event(self, ioname, iovalue):
        self.logger.debug("Input %s : Value %s", ioname, iovalue)
        negedge_event = events.SimpleSensorInputEvent(eventID=events.SimpleSensorInputEvents.NegEdge,
                                                      sender=self._name)
        self.endSwitchPress.handle_event(event=negedge_event)

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
        self.forceSwitch.handle_event(event=posedge_event)

    def input6_negedge_event(self, ioname, iovalue):
        self.logger.debug("Input %s : Value %s", ioname, iovalue)
        negedge_event = events.SimpleSensorInputEvent(eventID=events.SimpleSensorInputEvents.NegEdge,
                                                      sender=self._name)
        self.forceSwitch.handle_event(event=negedge_event)

    def conn_broken_event(self):
        self.assemblyStation.handle_event(event=self.noconn_event)

    def conn_alive_event(self):
        self.assemblyStation.handle_event(event=self.connok_event)

    def start(self):
        self.revpiioDriver.mainloop(blocking=False)
        self.logger.debug("RevPi driver has been started.")

        # Loop to do some work next to the event system. E.g. Switch on / off green part of LED A1

        triggered = False
        # measured force limit

        while not self.revpiioDriver.exitsignal.is_set():
            # self.revpiioDriver.core.a1green.value = not self.revpiioDriver.core.a1green.value
            limit = self.pressing_setpoint
            # read sensor input (force)
            i = self.revpiioDriver.io.InputValue_1.value

            self.forceSwitch.publisher.publish(topic="AnalogValue", value=i, sender=self.forceSwitch.name)
            # force reached and stop triggered
            if (i > limit and triggered == False):
                triggered = True
                # stop the motor
                self.revpiioDriver.io['output4'].set_value(False)
                self.revpiioDriver.io['output5'].set_value(False)
                self.logger.info("-------------------- Force limit was reached: %s. The motor was stopped. ---------------- ", i)
                self.input6_posedge_event('force_sensor', True)
            # if stop already triggered and force under limit
            # stop can get triggered again
            elif (i < limit and triggered == True):
                self.input6_negedge_event('force_sensor', False)
                triggered = False

            self.revpiioDriver.exitsignal.wait(0.05)


def main():
    app = StationApp(config.STATION_CONFIG['stationName'])
    app.start()



if __name__ == '__main__':
    main()