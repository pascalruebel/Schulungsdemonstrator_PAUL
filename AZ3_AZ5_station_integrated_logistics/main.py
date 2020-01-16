import definitions
from communication.server import UAServer, UaObjectSubscriber
from activeobjects.sensors.nfc_sensor import NFCSensor
from activeobjects.actuators.rgb_led import RGB_LED
from activeobjects.actuators.blinker import Blinker
from activeobjects.actuators.blinker_led_adapter import BlinkerLedAdapter
from activeobjects.station.station import Station
from activeobjects.services.initialization.init_service import InitService
from activeobjects.services.interface import ServiceInterface
from activeobjects.services.to_position.to_pos import ToPosService

from utils.nfc_observer import PosReaderObserver, PosObserver
from smartcard.ReaderMonitoring import ReaderMonitor, ReaderObserver
from smartcard.CardMonitoring import CardMonitor, CardObserver

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

        # building events ---------------------------------------------------------------
        self.nfc_posedge = events.ComplexSensorEvent(eventID=events.ComplexSensorEvents.PosEdge,
                                                        sender="RfidMonitor")
        self.nfc_negedge = events.ComplexSensorEvent(eventID=events.ComplexSensorEvents.NegEdge,
                                                        sender="RfidMonitor")
        self.nfc_nok = events.ComplexSensorEvent(eventID=events.ComplexSensorEvents.StatusNOK,
                                                        sender="RfidMonitor")
        self.nfc_ok = events.ComplexSensorEvent(eventID=events.ComplexSensorEvents.StatusOK,
                                                 sender="RfidMonitor")
        self.noconn_event = events.StationInputEvent(eventID=events.StationInputEvents.NoConn,
                                                sender='ConnMonitor')
        self.connok_event = events.StationInputEvent(eventID=events.StationInputEvents.ConnOk,
                                                sender='ConnMonitor')

        # build nfc monitor -------------------------------------------------------------
        self.readermonitor = ReaderMonitor()
        self.posreaderobserver = PosReaderObserver(station_app=self)
        self.readermonitor.addObserver(self.posreaderobserver)

        self.cardmonitor = CardMonitor()
        self.posObserver = PosObserver(station_app=self)
        self.cardmonitor.addObserver(self.posObserver)

        # sensors -----------------------------------------------------------------------

        self.positionSensor1 = NFCSensor("RfidReader1", "-BG1",
                                         topics=["State", "Value", 'StationErrorCode', 'StationErrorDescription',
                                                 'StationMessageCode', 'StationMessageDescription'],
                                         hw_input=1,
                                         card_monitor=self.posObserver,
                                         reader_monitor=self.posreaderobserver,
                                         auto_init=False)

        self.positionSensor2 = NFCSensor("RfidReader2", "-BG2",
                                         topics=["State", "Value", 'StationErrorCode', 'StationErrorDescription',
                                                 'StationMessageCode', 'StationMessageDescription'],
                                         hw_input=2,
                                         card_monitor=self.posObserver,
                                         reader_monitor=self.posreaderobserver,
                                         auto_init=False)

        self.positionSensor3 = NFCSensor("RfidReader3", "-BG3",
                                         topics=["State", "Value", 'StationErrorCode', 'StationErrorDescription',
                                                 'StationMessageCode', 'StationMessageDescription'],
                                         hw_input=3,
                                         card_monitor=self.posObserver,
                                         reader_monitor=self.posreaderobserver,
                                         auto_init=False)

        # actuators (LEDs) ---------------------------------------------------------------
        self.PF1led_adapter = BlinkerLedAdapter(hw_output_red=self.revpiioDriver.io['PWM_PF1_R'],
                                                hw_output_green=self.revpiioDriver.io['PWM_PF1_G'],
                                                hw_output_blue=self.revpiioDriver.io['PWM_PF1_B'],
                                                common_anode=True)

        self.PF2led_adapter = BlinkerLedAdapter(hw_output_red=self.revpiioDriver.io['PWM_PF2_R'],
                                                hw_output_green=self.revpiioDriver.io['PWM_PF2_G'],
                                                hw_output_blue=self.revpiioDriver.io['PWM_PF2_B'],
                                                common_anode=True)

        self.PF3led_adapter = BlinkerLedAdapter(hw_output_red=self.revpiioDriver.io['PWM_PF3_R'],
                                                hw_output_green=self.revpiioDriver.io['PWM_PF3_G'],
                                                hw_output_blue=self.revpiioDriver.io['PWM_PF3_B'],
                                                common_anode=True)

        self.PF4led_adapter = BlinkerLedAdapter(hw_output_red=self.revpiioDriver.io['PWM_PF4_R'],
                                                hw_output_green=self.revpiioDriver.io['PWM_PF4_G'],
                                                hw_output_blue=self.revpiioDriver.io['PWM_PF4_B'])

        self.positionLED1 = RGB_LED("LedStrip1", "PF1",
                                    revpi_red=self.PF1led_adapter.red,
                                    revpi_green=self.PF1led_adapter.green,
                                    revpi_blue=self.PF1led_adapter.blue,
                                    common_anode=True,
                                    topics=["State", "Value"])

        self.positionLED2 = RGB_LED("LedStrip2", "PF2",
                                    revpi_red=self.PF2led_adapter.red,
                                    revpi_green=self.PF2led_adapter.green,
                                    revpi_blue=self.PF2led_adapter.blue,
                                    common_anode=True,
                                    topics=["State", "Value"])

        self.positionLED3 = RGB_LED("LedStrip3", "PF3",
                                    revpi_red=self.PF3led_adapter.red,
                                    revpi_green=self.PF3led_adapter.green,
                                    revpi_blue=self.PF3led_adapter.blue,
                                    common_anode=True,
                                    topics=["State", "Value"])

        self.statusLED = RGB_LED("RgbLed", "-PF4",
                                 revpi_red=self.PF4led_adapter.red,
                                 revpi_green=self.PF4led_adapter.green,
                                 revpi_blue=self.PF4led_adapter.blue,
                                 topics=["State", "Value"])

        self.blinkerLED1 = Blinker('BlinkerLED1', shutter=self.PF1led_adapter, ontime=0.5, offtime=0.5, blinks_number=3)

        self.blinkerLED2 = Blinker('BlinkerLED2', shutter=self.PF2led_adapter,ontime=0.5, offtime=0.5, blinks_number=3)

        self.blinkerLED3 = Blinker('BlinkerLED3', shutter=self.PF3led_adapter, ontime=0.5, offtime=0.5, blinks_number=3)

        self.blinkerStatusLED = Blinker('BlinkerStatusLED', shutter=self.PF4led_adapter, ontime=0.5, offtime=0.5)

        # station parts -----------------------------------------------------------------
        self.logisticStation = Station("Station",
                                       status_led=self.statusLED,
                                       blinker=self.blinkerStatusLED,
                                       posled1=self.positionLED1,
                                       posled2=self.positionLED2,
                                       posled3=self.positionLED3,
                                       blinkerLed1=self.blinkerLED1,
                                       blinkerLed2=self.blinkerLED2,
                                       blinkerLed3=self.blinkerLED3,
                                       nfc1=self.positionSensor1,
                                       nfc2=self.positionSensor2,
                                       nfc3=self.positionSensor3,
                                       topics=['StationState', 'Ack', 'StationErrorCode',
                                                'StationErrorDescription', 'StationSafetyState',
                                                'StationMessageCode', 'StationMessageDescription',
                                                'StationStateMaintenance'])

        # building and registering services -----------------------------------------------

        # initialization service:
        dev_list = [self.positionSensor1, self.positionSensor2, self.positionSensor3]

        self.initService = InitService(name='InitializationService',
                                       enable_timeout=True,
                                       timeout_interval=config.STATION_CONFIG['initServiceTimeoutInterval'],
                                       dev_list=dev_list,
                                       topics=['eventID', 'StationErrorCode', 'StationErrorDescription',
                                               'StationMessageCode', 'StationMessageDescription', 'InitServiceState'])

        # create a service interface
        self.initializationServiceInterface = ServiceInterface(service_user=self.logisticStation,
                                                               service=self.initService,
                                                               service_index=0)
        # set the service
        self.initService.setup_service(service_index=0, service_interface=self.initializationServiceInterface)

        # regester the service by the service user
        self.logisticStation.register_services(service_index=0, service_interface=self.initializationServiceInterface)

        # to position 1 service:
        self.toPosition1Service = ToPosService(name='ToPosition1',
                                               sensorPos=self.positionSensor1,
                                               led=self.positionLED1,
                                               blinker=self.blinkerLED1,
                                               topics=['eventID', 'StationErrorCode', 'StationErrorDescription',
                                                       'StationMessageCode', 'StationMessageDescription',
                                                       'ToPosition1ServiceState'])

        self.toPosition1Interface = ServiceInterface(service_user=self.logisticStation,
                                                       service=self.toPosition1Service,
                                                        service_index=1)

        self.toPosition1Service.setup_service(service_index=1, service_interface=self.toPosition1Interface)

        self.logisticStation.register_services(service_index=1, service_interface=self.toPosition1Interface)


        # to position 2 service:
        self.toPosition2Service = ToPosService(name='ToPosition2',
                                               sensorPos=self.positionSensor2,
                                               led=self.positionLED2,
                                               blinker=self.blinkerLED2,
                                               topics=['eventID', 'StationErrorCode', 'StationErrorDescription',
                                                       'StationMessageCode', 'StationMessageDescription',
                                                       'ToPosition2ServiceState'])

        self.toPosition2Interface = ServiceInterface(service_user=self.logisticStation,
                                                     service=self.toPosition2Service,
                                                     service_index=2)

        self.toPosition2Service.setup_service(service_index=2, service_interface=self.toPosition2Interface)

        self.logisticStation.register_services(service_index=2, service_interface=self.toPosition2Interface)


        # to position 3 service:
        self.toPosition3Service = ToPosService(name='ToPosition3',
                                               sensorPos=self.positionSensor3,
                                               led=self.positionLED3,
                                               blinker=self.blinkerLED3,
                                               topics=['eventID', 'StationErrorCode', 'StationErrorDescription',
                                                       'StationMessageCode', 'StationMessageDescription',
                                                       'ToPosition3ServiceState'])

        self.toPosition3Interface = ServiceInterface(service_user=self.logisticStation,
                                                     service=self.toPosition3Service,
                                                     service_index=3)

        self.toPosition3Service.setup_service(service_index=3, service_interface=self.toPosition3Interface)

        self.logisticStation.register_services(service_index=3, service_interface=self.toPosition3Interface)
        # --------------------------------------------------------------------------------

        # starting the active objects :
        self.positionSensor1.start()
        self.positionSensor2.start()
        self.positionSensor3.start()

        self.positionLED1.start()
        self.blinkerLED1.start()
        self.positionLED2.start()
        self.blinkerLED2.start()
        self.positionLED3.start()
        self.blinkerLED3.start()
        self.statusLED.start()
        self.blinkerStatusLED.start()

        self.logisticStation.start()
        self.initService.start()
        self.toPosition1Service.start()
        self.toPosition2Service.start()
        self.toPosition3Service.start()


        # opcua server ------------------------------------------------------------------
        ip_str = self.get_ip()
        servername = config.SERVER_CONFIG['servername']
        endpoint = 'opc.tcp://' + ip_str + ':4840/' + servername + '/'
        uri = config.SERVER_CONFIG['uri']


        self.logger.debug("Building an OPCUA server: %s ", servername)
        self.server = UAServer(endpoint=endpoint, name=servername, uri=uri, station=self.logisticStation, revpiobj=self).server

        self.server_publisher = ServerPublisher(server_name=servername, endpoint=endpoint, logger=self.logger)
        if self.server_publisher.check_connection():
            self.server_publisher.publish()
        else:
            self.logger.info("No connection to the database. OPCUA server was not registered.")

        # setting pub-sub system ---------------------------------------------------------
        self.logger.info("Setting events pub-sub system...")

        # position sensor1 subscribers :
        sensorUaNode = self.server.nodes.objects.get_child(["2:Sensor", "2:RfidReader1"])
        self.positionSensor1UaSubscriber = UaObjectSubscriber(self.server, sensorUaNode)

        self.positionSensor1.register_subscribers(topic="State",
                                                   who=self.positionSensor1UaSubscriber,
                                                   callback=self.positionSensor1UaSubscriber.update)

        self.positionSensor1.register_subscribers(topic="Value",
                                                   who=self.positionSensor1UaSubscriber,
                                                   callback=self.positionSensor1UaSubscriber.update)

        self.positionSensor1.register_subscribers(topic="State",
                                                   who=self.initService,
                                                   callback=self.initService.handle_event)

        self.positionSensor1.register_subscribers(topic="State",
                                                  who=self.toPosition1Service,
                                                  callback=self.toPosition1Service.handle_event)
        self.positionSensor1.register_subscribers(topic="Value",
                                                   who=self.toPosition1Service,
                                                   callback=self.toPosition1Service.handle_event)

        self.positionSensor1.register_subscribers(topic="State",
                                                  who=self.logisticStation,
                                                  callback=self.logisticStation.handle_event)

        # position sensor2 subscribers :
        sensorUaNode = self.server.nodes.objects.get_child(["2:Sensor", "2:RfidReader2"])
        self.positionSensor2UaSubscriber = UaObjectSubscriber(self.server, sensorUaNode)

        self.positionSensor2.register_subscribers(topic="State",
                                                  who=self.positionSensor2UaSubscriber,
                                                  callback=self.positionSensor2UaSubscriber.update)

        self.positionSensor2.register_subscribers(topic="Value",
                                                  who=self.positionSensor2UaSubscriber,
                                                  callback=self.positionSensor2UaSubscriber.update)

        self.positionSensor2.register_subscribers(topic="State",
                                                  who=self.initService,
                                                  callback=self.initService.handle_event)

        self.positionSensor2.register_subscribers(topic="State",
                                                  who=self.toPosition2Service,
                                                  callback=self.toPosition2Service.handle_event)
        self.positionSensor2.register_subscribers(topic="Value",
                                                  who=self.toPosition2Service,
                                                  callback=self.toPosition2Service.handle_event)

        self.positionSensor2.register_subscribers(topic="State",
                                                  who=self.logisticStation,
                                                  callback=self.logisticStation.handle_event)

        # position sensor3 subscribers :
        sensorUaNode = self.server.nodes.objects.get_child(["2:Sensor", "2:RfidReader3"])
        self.positionSensor3UaSubscriber = UaObjectSubscriber(self.server, sensorUaNode)

        self.positionSensor3.register_subscribers(topic="State",
                                                  who=self.positionSensor3UaSubscriber,
                                                  callback=self.positionSensor3UaSubscriber.update)

        self.positionSensor3.register_subscribers(topic="Value",
                                                  who=self.positionSensor3UaSubscriber,
                                                  callback=self.positionSensor3UaSubscriber.update)

        self.positionSensor3.register_subscribers(topic="State",
                                                  who=self.initService,
                                                  callback=self.initService.handle_event)

        self.positionSensor3.register_subscribers(topic="State",
                                                  who=self.toPosition3Service,
                                                  callback=self.toPosition3Service.handle_event)
        self.positionSensor3.register_subscribers(topic="Value",
                                                  who=self.toPosition3Service,
                                                  callback=self.toPosition3Service.handle_event)

        self.positionSensor3.register_subscribers(topic="State",
                                                  who=self.logisticStation,
                                                  callback=self.logisticStation.handle_event)

        # LED1 subscribers :
        ledUaNode = self.server.nodes.objects.get_child(["2:Actor", "2:LedStrip1"])
        self.led1UaSubscriber = UaObjectSubscriber(self.server, ledUaNode)
        self.positionLED1.register_subscribers(topic="State",
                                                who=self.led1UaSubscriber,
                                                callback=self.led1UaSubscriber.update)

        self.positionLED1.register_subscribers(topic="Value",
                                                who=self.led1UaSubscriber,
                                                callback=self.led1UaSubscriber.update)

        self.blinkerLED3.register_subscribers(topic="Value",
                                              who=self.toPosition3Service,
                                              callback=self.toPosition3Service.handle_event)

        # LED2 subscribers :
        ledUaNode = self.server.nodes.objects.get_child(["2:Actor", "2:LedStrip2"])
        self.led2UaSubscriber = UaObjectSubscriber(self.server, ledUaNode)
        self.positionLED2.register_subscribers(topic="State",
                                               who=self.led2UaSubscriber,
                                               callback=self.led2UaSubscriber.update)

        self.positionLED2.register_subscribers(topic="Value",
                                               who=self.led2UaSubscriber,
                                               callback=self.led2UaSubscriber.update)

        self.blinkerLED2.register_subscribers(topic="Value",
                                              who=self.toPosition2Service,
                                              callback=self.toPosition2Service.handle_event)

        # LED3 subscribers :
        ledUaNode = self.server.nodes.objects.get_child(["2:Actor", "2:LedStrip3"])
        self.led3UaSubscriber = UaObjectSubscriber(self.server, ledUaNode)
        self.positionLED3.register_subscribers(topic="State",
                                               who=self.led3UaSubscriber,
                                               callback=self.led3UaSubscriber.update)

        self.positionLED3.register_subscribers(topic="Value",
                                               who=self.led3UaSubscriber,
                                               callback=self.led3UaSubscriber.update)

        self.blinkerLED1.register_subscribers(topic="Value",
                                              who=self.toPosition1Service,
                                              callback=self.toPosition1Service.handle_event)


        # Publish errors and messages to the server :
        stationStateUaNode = self.server.nodes.objects.get_child(["2:StateMachine"])
        self.stationStateUaSubscriber = UaObjectSubscriber(self.server, stationStateUaNode)

        self.logisticStation.register_subscribers(topic="StationState",
                                                  who=self.stationStateUaSubscriber,
                                                  callback=self.stationStateUaSubscriber.update)

        self.logisticStation.register_subscribers(topic="StationErrorCode",
                                                  who=self.stationStateUaSubscriber,
                                                  callback=self.stationStateUaSubscriber.update)

        self.logisticStation.register_subscribers(topic="StationErrorDescription",
                                                  who=self.stationStateUaSubscriber,
                                                  callback=self.stationStateUaSubscriber.update)

        self.logisticStation.register_subscribers(topic="StationMessageCode",
                                                  who=self.stationStateUaSubscriber,
                                                  callback=self.stationStateUaSubscriber.update)

        self.logisticStation.register_subscribers(topic="StationMessageDescription",
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

        self.initService.register_subscribers(topic="StationErrorDescription",
                                              who=self.stationStateUaSubscriber,
                                              callback=self.stationStateUaSubscriber.update)

        self.toPosition1Service.register_subscribers(topic="StationErrorCode",
                                              who=self.stationStateUaSubscriber,
                                              callback=self.stationStateUaSubscriber.update)

        self.toPosition1Service.register_subscribers(topic="StationErrorDescription",
                                              who=self.stationStateUaSubscriber,
                                              callback=self.stationStateUaSubscriber.update)

        self.toPosition1Service.register_subscribers(topic="StationMessageCode",
                                                     who=self.stationStateUaSubscriber,
                                                     callback=self.stationStateUaSubscriber.update)

        self.toPosition1Service.register_subscribers(topic="StationMessageDescription",
                                                     who=self.stationStateUaSubscriber,
                                                     callback=self.stationStateUaSubscriber.update)

        self.toPosition2Service.register_subscribers(topic="StationErrorCode",
                                                     who=self.stationStateUaSubscriber,
                                                     callback=self.stationStateUaSubscriber.update)

        self.toPosition2Service.register_subscribers(topic="StationErrorDescription",
                                                     who=self.stationStateUaSubscriber,
                                                     callback=self.stationStateUaSubscriber.update)

        self.toPosition2Service.register_subscribers(topic="StationMessageCode",
                                                     who=self.stationStateUaSubscriber,
                                                     callback=self.stationStateUaSubscriber.update)

        self.toPosition2Service.register_subscribers(topic="StationMessageDescription",
                                                     who=self.stationStateUaSubscriber,
                                                     callback=self.stationStateUaSubscriber.update)

        self.toPosition3Service.register_subscribers(topic="StationErrorCode",
                                                     who=self.stationStateUaSubscriber,
                                                     callback=self.stationStateUaSubscriber.update)

        self.toPosition3Service.register_subscribers(topic="StationErrorDescription",
                                                     who=self.stationStateUaSubscriber,
                                                     callback=self.stationStateUaSubscriber.update)

        self.toPosition3Service.register_subscribers(topic="StationMessageCode",
                                                     who=self.stationStateUaSubscriber,
                                                     callback=self.stationStateUaSubscriber.update)

        self.toPosition3Service.register_subscribers(topic="StationMessageDescription",
                                                     who=self.stationStateUaSubscriber,
                                                     callback=self.stationStateUaSubscriber.update)

        self.positionSensor1.register_subscribers(topic="StationErrorCode",
                                                     who=self.stationStateUaSubscriber,
                                                     callback=self.stationStateUaSubscriber.update)

        self.positionSensor1.register_subscribers(topic="StationErrorDescription",
                                                     who=self.stationStateUaSubscriber,
                                                     callback=self.stationStateUaSubscriber.update)

        self.positionSensor1.register_subscribers(topic="StationMessageCode",
                                                     who=self.stationStateUaSubscriber,
                                                     callback=self.stationStateUaSubscriber.update)

        self.positionSensor1.register_subscribers(topic="StationMessageDescription",
                                                     who=self.stationStateUaSubscriber,
                                                     callback=self.stationStateUaSubscriber.update)

        self.positionSensor2.register_subscribers(topic="StationErrorCode",
                                                  who=self.stationStateUaSubscriber,
                                                  callback=self.stationStateUaSubscriber.update)

        self.positionSensor2.register_subscribers(topic="StationErrorDescription",
                                                  who=self.stationStateUaSubscriber,
                                                  callback=self.stationStateUaSubscriber.update)

        self.positionSensor2.register_subscribers(topic="StationMessageCode",
                                                  who=self.stationStateUaSubscriber,
                                                  callback=self.stationStateUaSubscriber.update)

        self.positionSensor2.register_subscribers(topic="StationMessageDescription",
                                                  who=self.stationStateUaSubscriber,
                                                  callback=self.stationStateUaSubscriber.update)

        self.positionSensor3.register_subscribers(topic="StationErrorCode",
                                                  who=self.stationStateUaSubscriber,
                                                  callback=self.stationStateUaSubscriber.update)

        self.positionSensor3.register_subscribers(topic="StationErrorDescription",
                                                  who=self.stationStateUaSubscriber,
                                                  callback=self.stationStateUaSubscriber.update)

        self.positionSensor3.register_subscribers(topic="StationMessageCode",
                                                  who=self.stationStateUaSubscriber,
                                                  callback=self.stationStateUaSubscriber.update)

        self.positionSensor3.register_subscribers(topic="StationMessageDescription",
                                                  who=self.stationStateUaSubscriber,
                                                  callback=self.stationStateUaSubscriber.update)


        self.logisticStation.register_subscribers(topic="StationSafetyState",
                                                  who=self.stationStateUaSubscriber,
                                                  callback=self.stationStateUaSubscriber.update)

        # maintenance subscribers :
        pressStatusUaNode = self.server.nodes.objects.get_child(["2:Maintenance"])
        self.maintenanceStatusUaSubscriber = UaObjectSubscriber(self.server, pressStatusUaNode)

        self.logisticStation.register_subscribers(topic='StationStateMaintenance',
                                                 who=self.maintenanceStatusUaSubscriber,
                                                 callback=self.maintenanceStatusUaSubscriber.update)
        self.initService.register_subscribers(topic="InitServiceState",
                                              who=self.maintenanceStatusUaSubscriber,
                                              callback=self.maintenanceStatusUaSubscriber.update)
        self.toPosition1Service.register_subscribers(topic="ToPosition1ServiceState",
                                              who=self.maintenanceStatusUaSubscriber,
                                              callback=self.maintenanceStatusUaSubscriber.update)
        self.toPosition2Service.register_subscribers(topic="ToPosition2ServiceState",
                                                     who=self.maintenanceStatusUaSubscriber,
                                                     callback=self.maintenanceStatusUaSubscriber.update)
        self.toPosition3Service.register_subscribers(topic="ToPosition3ServiceState",
                                                     who=self.maintenanceStatusUaSubscriber,
                                                     callback=self.maintenanceStatusUaSubscriber.update)

        # propagating 'Ack' through subscription
        self.logisticStation.register_subscribers(topic="Ack",
                                                  who=self.initService,
                                                  callback=self.initService.handle_event)

        self.logisticStation.register_subscribers(topic="Ack",
                                                  who=self.toPosition1Service,
                                                  callback=self.toPosition1Service.handle_event)

        self.logisticStation.register_subscribers(topic="Ack",
                                                  who=self.toPosition2Service,
                                                  callback=self.toPosition2Service.handle_event)

        self.logisticStation.register_subscribers(topic="Ack",
                                                  who=self.toPosition3Service,
                                                  callback=self.toPosition3Service.handle_event)

        self.logisticStation.register_subscribers(topic="Ack",
                                                  who=self.positionSensor1,
                                                  callback=self.positionSensor1.handle_event)

        self.logisticStation.register_subscribers(topic="Ack",
                                                  who=self.positionSensor2,
                                                  callback=self.positionSensor2.handle_event)

        self.logisticStation.register_subscribers(topic="Ack",
                                                  who=self.positionSensor3,
                                                  callback=self.positionSensor3.handle_event)

        self.logisticStation.register_subscribers(topic="Ack",
                                                  who=self.positionLED1,
                                                  callback=self.positionLED1.handle_event)

        self.logisticStation.register_subscribers(topic="Ack",
                                                  who=self.positionLED2,
                                                  callback=self.positionLED2.handle_event)

        self.logisticStation.register_subscribers(topic="Ack",
                                                  who=self.positionLED3,
                                                  callback=self.positionLED3.handle_event)

        self.logisticStation.register_subscribers(topic="Ack",
                                                  who=self.statusLED,
                                                  callback=self.statusLED.handle_event)

        self.logisticStation.register_subscribers(topic="Ack",
                                                  who=self.blinkerLED1,
                                                  callback=self.blinkerLED1.handle_event)

        self.logisticStation.register_subscribers(topic="Ack",
                                                  who=self.blinkerLED2,
                                                  callback=self.blinkerLED2.handle_event)

        self.logisticStation.register_subscribers(topic="Ack",
                                                  who=self.blinkerLED3,
                                                  callback=self.blinkerLED3.handle_event)

        self.logisticStation.register_subscribers(topic="Ack",
                                                  who=self.blinkerStatusLED,
                                                  callback=self.blinkerStatusLED.handle_event)

        # station's state to the other services
        self.logisticStation.register_subscribers(topic="StationState",
                                                 who=self.initService,
                                                 callback=self.initService.handle_event)

        self.logisticStation.register_subscribers(topic="StationState",
                                                  who=self.toPosition1Service,
                                                  callback=self.toPosition1Service.handle_event)

        self.logisticStation.register_subscribers(topic="StationState",
                                                  who=self.toPosition2Service,
                                                  callback=self.toPosition2Service.handle_event)

        self.logisticStation.register_subscribers(topic="StationState",
                                                  who=self.toPosition3Service,
                                                  callback=self.toPosition3Service.handle_event)

        # setting RevPi driver -------------------------------------------------------------
        self.revpiioDriver.handlesignalend(self.shutdown)

        # starting everything ------------------------------------------------------------
        self.server.start()
        self.logger.info("OPCUA server %s at %s has started", servername, endpoint)
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
        self.positionSensor1.stop()
        self.positionSensor2.stop()
        self.positionSensor3.stop()

        self.positionLED1.led_off()
        self.positionLED1.stop()
        self.positionLED2.led_off()
        self.positionLED2.stop()
        self.positionLED3.led_off()
        self.positionLED3.stop()
        self.statusLED.led_off()
        self.statusLED.stop()

        self.blinkerLED1.stop()
        self.blinkerLED2.stop()
        self.blinkerLED3.stop()
        self.blinkerStatusLED.stop()

        self.initService.stop()
        self.toPosition1Service.stop()
        self.toPosition2Service.stop()
        self.toPosition3Service.stop()

        self.readermonitor.deleteObserver(self.posreaderobserver)
        self.cardmonitor.deleteObserver(self.posObserver)
        self.logisticStation.stop()
        self.connMonitor.stop()

        self.server.stop()

    def nfc_pos1_posedge(self):
        if self.positionSensor1 is not None:
            self.positionSensor1.handle_event(event=self.nfc_posedge)

    def nfc_pos1_negedge(self):
        if self.positionSensor1 is not None:
            self.positionSensor1.handle_event(event=self.nfc_negedge)

    def nfc_pos1_ok(self):
        if self.positionSensor1 is not None:
            self.positionSensor1.handle_event(event=self.nfc_ok)

    def nfc_pos1_nok(self):
        if self.positionSensor1 is not None:
            self.positionSensor1.handle_event(event=self.nfc_nok)

    def nfc_pos2_posedge(self):
        if self.positionSensor2 is not None:
            self.positionSensor2.handle_event(event=self.nfc_posedge)

    def nfc_pos2_negedge(self):
        if self.positionSensor2 is not None:
            self.positionSensor2.handle_event(event=self.nfc_negedge)

    def nfc_pos2_ok(self):
        if self.positionSensor2 is not None:
            self.positionSensor2.handle_event(event=self.nfc_ok)

    def nfc_pos2_nok(self):
        if self.positionSensor2 is not None:
            self.positionSensor2.handle_event(event=self.nfc_nok)

    def nfc_pos3_posedge(self):
        if self.positionSensor3 is not None:
            self.positionSensor3.handle_event(event=self.nfc_posedge)

    def nfc_pos3_negedge(self):
        if self.positionSensor3 is not None:
            self.positionSensor3.handle_event(event=self.nfc_negedge)

    def nfc_pos3_ok(self):
        if self.positionSensor3 is not None:
            self.positionSensor3.handle_event(event=self.nfc_ok)

    def nfc_pos3_nok(self):
        if self.positionSensor3 is not None:
            self.positionSensor3.handle_event(event=self.nfc_nok)

    def conn_broken_event(self):
        self.logisticStation.handle_event(event=self.noconn_event)

    def conn_alive_event(self):
        self.logisticStation.handle_event(event=self.connok_event)

    def start(self):
        self.revpiioDriver.mainloop(blocking=False)
        self.logger.debug("RevPi driver has been started.")

        # Loop to do some work next to the event system. E.g. Switch on / off green part of LED A1
        while not self.revpiioDriver.exitsignal.is_set():
            self.revpiioDriver.core.a1green.value = not self.revpiioDriver.core.a1green.value

            self.revpiioDriver.exitsignal.wait(1.0)


def main():
    app = StationApp(config.STATION_CONFIG['stationName'])
    app.start()


if __name__ == '__main__':
    main()



