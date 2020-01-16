import definitions
from communication.server import AZ8UAServer, UaObjectSubscriber
from activeobjects.sensors.presencesensor import PresenceSensor
from activeobjects.sensors.interactionsensor import InteractionSensor
from activeobjects.actuators.rgb_led import RGB_LED
from activeobjects.actuators.blinker import Blinker
from activeobjects.actuators.blinker_led_adapter import BlinkerLedAdapter
from activeobjects.storagerack.storagerack import StorageRack
from activeobjects.station.station import StorageStation
from activeobjects.services.interface import ServiceInterface
from activeobjects.services.initialization.init_service import InitService
from activeobjects.services.diceplate.diceplate import ProvideDicePlateService
from activeobjects.services.storage.storage_service import StorageDicePlateService
from communication import events, conn_monitor, network_util
from communication.server_publisher import ServerPublisher

import revpimodio2
import config
import logging.config
import json
import socket

from subprocess import call

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

		# The sub-methods of class RevPiModIO supports event handling by using the 
		# methodes io.__reg_xevent, modio.mainloop and helper.eventcallback.
		
        self.revpiioDriver = revpimodio2.RevPiModIO(autorefresh=True)

        self.connMonitor = conn_monitor.ConnMonitor(name='ConnMonitor',
                                                    logger=self.logger,
                                                    conn_alive_cb=self.conn_alive_event,
                                                    conn_broken_cb=self.conn_broken_event)

		
        self.logger.debug("Building the station's active objects...")

        # Building station objects -----------------------------------------------------

        # Sensors -----------------------------------------------------------------------
		
        self.presenceSensor1 = PresenceSensor("PresenceSensor1",
                                              "-BG1",
                                              topics=["State", "Value"],
                                              inputobj=self.revpiioDriver.io["I_6"],
                                              normally_open=True)
							 
        self.presenceSensor2 = PresenceSensor(name="PresenceSensor2",
                                              id="-BG2",
                                              topics=["State", "Value"],
                                              inputobj=self.revpiioDriver.io["I_8"],
                                              normally_open=True)
							 
        self.presenceSensor3 = PresenceSensor(name="PresenceSensor3",
                                              id="-BG3",
                                              topics=["State", "Value"],
                                              inputobj=self.revpiioDriver.io["I_10"],
                                              normally_open=True)							 

        self.presenceSensor4 = PresenceSensor(name="PresenceSensor4",
                                              id="-BG4",
                                              topics=["State", "Value"],
                                              inputobj=self.revpiioDriver.io["I_13"],
                                              normally_open=True)
							 
        self.presenceSensor5 = PresenceSensor(name="PresenceSensor5",
                                              id="-BG5",
                                              topics=["State", "Value"],
                                              inputobj=self.revpiioDriver.io["I_2"],
                                              normally_open=True)
							 
        self.presenceSensor6 = PresenceSensor(name="PresenceSensor6",
                                              id="-BG6",
                                              topics=["State", "Value"],
                                              inputobj=self.revpiioDriver.io["I_4"],
                                              normally_open=True)	

        self.interactionSensor1 = InteractionSensor(name="InteractionSensor1",
                                                    id="-SF1",
                                                    topics=["State", "Value"],
                                                    inputobj=self.revpiioDriver.io["I_12"],
                                                    normally_open=True)
							 
        self.interactionSensor2 = InteractionSensor(name="InteractionSensor2",
                                                    id="-SF2",
                                                    topics=["State", "Value"],
                                                    inputobj=self.revpiioDriver.io["I_14"],
                                                    normally_open=True)										  

        # actuators (rgbled's) ---------------------------------------------------------------

        # storageRack1LED
		
        self.blinker_led1_adapter = BlinkerLedAdapter(hw_output_red=self.revpiioDriver.io["O_5"],
                                                      hw_output_green=self.revpiioDriver.io["O_7"],
                                                      hw_output_blue=self.revpiioDriver.io["O_9"])
		
        self.storageRack1LED = RGB_LED(name="RgbLed1",
                                       id="-PF1",
                                       revpi_red=self.blinker_led1_adapter.red,
                                       revpi_green=self.blinker_led1_adapter.green,
                                       revpi_blue=self.blinker_led1_adapter.blue,
                                       topics=["State", "Value"])

        self.storageRack1Blinker = Blinker(name="StorageRack1 Blinker", shutter=self.blinker_led1_adapter, ontime=0.5, offtime=0.5)	
		
        # storageRack2LED		
		
        self.blinker_led2_adapter = BlinkerLedAdapter(hw_output_red=self.revpiioDriver.io["O_14"],
                                                      hw_output_green=self.revpiioDriver.io["O_1"],
                                                      hw_output_blue=self.revpiioDriver.io["O_3"])
		
        self.storageRack2LED = RGB_LED(name="RgbLed2",
                                       id="-PF2",
                                       revpi_red=self.blinker_led2_adapter.red,
                                       revpi_green=self.blinker_led2_adapter.green,
                                       revpi_blue=self.blinker_led2_adapter.blue,
                                       topics=["State", "Value"])

        self.storageRack2Blinker = Blinker(name="StorageRack2 Blinker", shutter=self.blinker_led2_adapter, ontime=0.5, offtime=0.5)	
									   
        # storageRack3LED									   

        self.blinker_led3_adapter = BlinkerLedAdapter(hw_output_red=self.revpiioDriver.io["O_8"],
                                                      hw_output_green=self.revpiioDriver.io["O_10"],
                                                      hw_output_blue=self.revpiioDriver.io["O_12"])
					
        self.storageRack3LED = RGB_LED(name="RgbLed3",
                                       id="-PF3",
                                       revpi_red=self.blinker_led3_adapter.red,
                                       revpi_green=self.blinker_led3_adapter.green,
                                       revpi_blue=self.blinker_led3_adapter.blue,
                                       topics=["State", "Value"])						   

        self.storageRack3Blinker = Blinker(name="StorageRack3 Blinker", shutter=self.blinker_led3_adapter, ontime=0.5, offtime=0.5)										   
									   
        # storageRack4LED									   

        self.blinker_led4_adapter = BlinkerLedAdapter(hw_output_red=self.revpiioDriver.io["O_10_i03"],
                                                      hw_output_green=self.revpiioDriver.io["O_12_i03"],
                                                      hw_output_blue=self.revpiioDriver.io["O_14_i03"])
		
        self.storageRack4LED = RGB_LED(name="RgbLed4",
                                       id="-PF4",
                                       revpi_red=self.blinker_led4_adapter.red,
                                       revpi_green=self.blinker_led4_adapter.green,
                                       revpi_blue=self.blinker_led4_adapter.blue,
                                       topics=["State", "Value"])

        self.storageRack4Blinker = Blinker(name="StorageRack4 Blinker", shutter=self.blinker_led4_adapter, ontime=0.5, offtime=0.5)										   
									   
        # storageRack5LED									   

        self.blinker_led5_adapter = BlinkerLedAdapter(hw_output_red=self.revpiioDriver.io["O_4_i03"],
                                                      hw_output_green=self.revpiioDriver.io["O_6_i03"],
                                                      hw_output_blue=self.revpiioDriver.io["O_8_i03"])		
		
        self.storageRack5LED = RGB_LED(name="RgbLed5",
                                       id="-PF5",
                                       revpi_red=self.blinker_led5_adapter.red,
                                       revpi_green=self.blinker_led5_adapter.green,
                                       revpi_blue=self.blinker_led5_adapter.blue,
                                       topics=["State", "Value"])

        self.storageRack5Blinker = Blinker(name="StorageRack5 Blinker", shutter=self.blinker_led5_adapter, ontime=0.5, offtime=0.5)										   
									   
        # storageRack6LED									   

        self.blinker_led6_adapter = BlinkerLedAdapter(hw_output_red=self.revpiioDriver.io["O_11"],
                                                      hw_output_green=self.revpiioDriver.io["O_13"],
                                                      hw_output_blue=self.revpiioDriver.io["O_2_i03"])			
		
        self.storageRack6LED = RGB_LED(name="RgbLed6",
                                       id="-PF6",
                                       revpi_red=self.blinker_led6_adapter.red,
                                       revpi_green=self.blinker_led6_adapter.green,
                                       revpi_blue=self.blinker_led6_adapter.blue,
                                       topics=["State", "Value"])

        self.storageRack6Blinker = Blinker(name="StorageRack6 Blinker", shutter=self.blinker_led6_adapter, ontime=0.5, offtime=0.5)											   
									   
        # status (led's) ---------------------------------------------------------------
		
        self.blinker_led_adapter = BlinkerLedAdapter(hw_output_red=self.revpiioDriver.io["O_2"],
                                                     hw_output_green=self.revpiioDriver.io["O_4"],
                                                     hw_output_blue=self.revpiioDriver.io["O_6"])
									   								   
        self.statusLED = RGB_LED(name="RgbLed", 
                                 id="-PF7",
                                 revpi_red=self.blinker_led_adapter.red,
                                 revpi_green=self.blinker_led_adapter.green,
                                 revpi_blue=self.blinker_led_adapter.blue,
                                 topics=["State", "Value"])

        self.blinker = Blinker(name="Blinker", shutter=self.blinker_led_adapter, ontime=0.5, offtime=0.5)						   
							   
        # Station parts
								
        self.storageStation = StorageStation("Station",
                                             status_led=self.statusLED,
                                             blinker=self.blinker,
                                             topics=["StationState", "Ack", "StationErrorCode", "StationErrorDescription", "StationMessageCode", "StationMessageDescription"])

        self.storageRack1 = StorageRack(name="StorageRack1",
                                        station=self.storageStation,
                                        rgbled=self.storageRack1LED,
                                        blinker=self.storageRack1Blinker,
                                        presencesensor=self.presenceSensor1,
                                        diceplate_symbol=1,
                                        topics=["State", "Value", "PlateColor1", "QuantityOfPlateColor1", "PlateColor2", 
                                                "QuantityOfPlateColor2", "PlateColor3", "QuantityOfPlateColor3",
												"StationErrorCode", "StationErrorDescription","StationMessageCode", "StationMessageDescription"])

        self.storageRack2 = StorageRack(name="StorageRack2",
                                        station=self.storageStation,
                                        rgbled=self.storageRack2LED,
                                        blinker=self.storageRack2Blinker,
                                        presencesensor=self.presenceSensor2,
                                        diceplate_symbol=2,
                                        topics=["State", "Value", "PlateColor1", "QuantityOfPlateColor1", "PlateColor2", 
                                                "QuantityOfPlateColor2", "PlateColor3", "QuantityOfPlateColor3",
												"StationErrorCode", "StationErrorDescription","StationMessageCode", "StationMessageDescription"])
										
        self.storageRack3 = StorageRack(name="StorageRack3",
                                        station=self.storageStation,
                                        rgbled=self.storageRack3LED,
                                        blinker=self.storageRack3Blinker,
                                        presencesensor=self.presenceSensor3,
                                        diceplate_symbol=3,
                                        topics=["State", "Value", "PlateColor1", "QuantityOfPlateColor1", "PlateColor2", 
                                                "QuantityOfPlateColor2", "PlateColor3", "QuantityOfPlateColor3",
												"StationErrorCode", "StationErrorDescription","StationMessageCode", "StationMessageDescription"])
										
        self.storageRack4 = StorageRack(name="StorageRack4",
                                        station=self.storageStation,
                                        rgbled=self.storageRack4LED,
                                        blinker=self.storageRack4Blinker,
                                        presencesensor=self.presenceSensor4,
                                        diceplate_symbol=4,
                                        topics=["State", "Value", "PlateColor1", "QuantityOfPlateColor1", "PlateColor2", 
                                                "QuantityOfPlateColor2", "PlateColor3", "QuantityOfPlateColor3",
												"StationErrorCode", "StationErrorDescription","StationMessageCode", "StationMessageDescription"])

        self.storageRack5 = StorageRack(name="StorageRack5",
                                        station=self.storageStation,
                                        rgbled=self.storageRack5LED,
                                        blinker=self.storageRack5Blinker,
                                        presencesensor=self.presenceSensor5,
                                        diceplate_symbol=5,
                                        topics=["State", "Value", "PlateColor1", "QuantityOfPlateColor1", "PlateColor2", 
                                                "QuantityOfPlateColor2", "PlateColor3", "QuantityOfPlateColor3",
												"StationErrorCode", "StationErrorDescription","StationMessageCode", "StationMessageDescription"])

        self.storageRack6 = StorageRack(name="StorageRack6",
                                        station=self.storageStation,
                                        rgbled=self.storageRack6LED,
                                        blinker=self.storageRack6Blinker,
                                        presencesensor=self.presenceSensor6,
                                        diceplate_symbol=6,
                                        topics=["State", "Value", "PlateColor1", "QuantityOfPlateColor1", "PlateColor2", 
                                                "QuantityOfPlateColor2", "PlateColor3", "QuantityOfPlateColor3",
												"StationErrorCode", "StationErrorDescription","StationMessageCode", "StationMessageDescription"])
											 
        # Building and registering services -----------------------------------------------

        # Service 0: Initialization service
		
        # create a service
		
        self.dev_list = [self.presenceSensor1, self.presenceSensor2, self.presenceSensor3, self.presenceSensor4, self.presenceSensor5, self.presenceSensor6, 
                         self.interactionSensor1, self.interactionSensor2,
                         self.storageRack1LED, self.storageRack2LED, self.storageRack3LED, self.storageRack4LED, self.storageRack5LED, self.storageRack6LED, 
                         self.storageRack1, self.storageRack2, self.storageRack3, self.storageRack4, self.storageRack5, self.storageRack6]
		
        self.initService = InitService(name='InitializationService', 
                                       dev_list=self.dev_list,
                                       enable_timeout=True,
                                       timeout_interval=config.STATION_CONFIG['initServiceTimeoutInterval'],
                                       topics=['eventID', 'StationErrorCode', 'StationErrorDescription', 'StationMessageCode', 'StationMessageDescription', 'InitServiceState'])

	    # Storage Station initializes itself by using OPCUA-Init All, so start here the init of all other components
        # create a service interface
        self.initializationServiceInterface = ServiceInterface(service_user=self.storageStation,
                                                               service=self.initService,
                                                               service_index=0)
															   
        # set the service
        self.initService.setup_service(service_index=0, service_interface=self.initializationServiceInterface)									   
        
		# regester the service by the service user
        self.storageStation.register_services(service_index=0, service_interface=self.initializationServiceInterface)									   
        
		
        # Service 1: Provide diceplate service

        # create a service
		
        storageracklist = [self.storageRack1, self.storageRack2, self.storageRack3, self.storageRack4, self.storageRack5, self.storageRack6]
		
        self.provideDicePlateService = ProvideDicePlateService(name="ProvideDiceplateService",
                                                               storageracklist=storageracklist,
                                                               enable_timeout=True,
                                                               timeout_interval=config.STATION_CONFIG['provideDiceplateTimeoutInterval'],
                                                               topics=['eventID', 'StationErrorCode', 'StationErrorDescription', 'StationMessageCode', 'StationMessageDescription', 'ProvideMaterialState'])
        # create a service interface
        self.provideDicePlateServiceInterface = ServiceInterface(service_user=self.storageStation,
                                                                 service=self.provideDicePlateService,
                                                                 service_index=1)
        # set the service
        self.provideDicePlateService.setup_service(service_index=1, service_interface=self.provideDicePlateServiceInterface)

        # regester the service by the service user
        self.storageStation.register_services(service_index=1, service_interface=self.provideDicePlateServiceInterface)


        # Service 2: Storage diceplate service (refill and reset)

        # create a service
		
        self.storageDicePlateService = StorageDicePlateService(name="StorageDiceplateService",
                                                               storageracklist=storageracklist,
                                                               enable_timeout=True,
                                                               timeout_interval=config.STATION_CONFIG['storageDiceplateTimeoutInterval'],
                                                               topics=['eventID', 'StationErrorCode', 'StationErrorDescription', 'StationMessageCode', 'StationMessageDescription', 'StorageMaterialState'])
        # create a service interface
        self.storageDicePlateServiceInterface = ServiceInterface(service_user=self.storageStation,
                                                                 service=self.storageDicePlateService,
                                                                 service_index=2)
        # set the service
        self.storageDicePlateService.setup_service(service_index=2, service_interface=self.storageDicePlateServiceInterface)

        # regester the service by the service user
        self.storageStation.register_services(service_index=2, service_interface=self.storageDicePlateServiceInterface)		
	
	
        # Starting active objects ------------------------------------

		# Storage Box Presence Sensors
		
        self.presenceSensor1.start()
        self.logger.info("%s has started", self.presenceSensor1.name)

        self.presenceSensor2.start()
        self.logger.info("%s has started", self.presenceSensor2.name)

        self.presenceSensor3.start()
        self.logger.info("%s has started", self.presenceSensor3.name)

        self.presenceSensor4.start()
        self.logger.info("%s has started", self.presenceSensor4.name)

        self.presenceSensor5.start()
        self.logger.info("%s has started", self.presenceSensor5.name)

        self.presenceSensor6.start()
        self.logger.info("%s has started", self.presenceSensor6.name)

		# Storage Box Interaction Sensors		
		
        self.interactionSensor1.start()
        self.logger.info("%s has started", self.interactionSensor1.name)

        self.interactionSensor2.start()
        self.logger.info("%s has started", self.interactionSensor2.name)		

		# Storage Box LEDs
		
        self.storageRack1LED.start()
        self.storageRack1Blinker.start()
        self.logger.info("%s with %s has started", self.storageRack1LED.name, self.storageRack1Blinker)
		
        self.storageRack2LED.start()
        self.storageRack2Blinker.start()
        self.logger.info("%s with %s has started", self.storageRack2LED.name, self.storageRack2Blinker)

        self.storageRack3LED.start()
        self.storageRack3Blinker.start()
        self.logger.info("%s with %s has started", self.storageRack3LED.name, self.storageRack3Blinker)

        self.storageRack4LED.start()
        self.storageRack4Blinker.start()
        self.logger.info("%s with %s has started", self.storageRack4LED.name, self.storageRack4Blinker)

        self.storageRack5LED.start()
        self.storageRack5Blinker.start()
        self.logger.info("%s with %s has started", self.storageRack5LED.name, self.storageRack5Blinker)

        self.storageRack6LED.start()
        self.storageRack6Blinker.start()
        self.logger.info("%s with %s has started", self.storageRack6LED.name, self.storageRack6Blinker)	

        self.statusLED.start()
        self.logger.info("%s has started", self.statusLED.name)

        self.blinker.start()
        self.logger.info("%s has started", self.blinker.name)
		
		# Storage Box Racks
		
        self.storageRack1.start()
        self.logger.info("%s has started", self.storageRack1.name)

        self.storageRack2.start()
        self.logger.info("%s has started", self.storageRack2.name)

        self.storageRack3.start()
        self.logger.info("%s has started", self.storageRack3.name)

        self.storageRack4.start()
        self.logger.info("%s has started", self.storageRack4.name)
		
        self.storageRack5.start()
        self.logger.info("%s has started", self.storageRack5.name)		
		
        self.storageRack6.start()
        self.logger.info("%s has started", self.storageRack6.name)		
		
        self.storageStation.start()
        self.logger.info("%s has started", self.storageStation.name)

		# Services
		
        self.initService.start()
        self.logger.info("%s has started", self.initService.name)

        self.provideDicePlateService.start()
        self.logger.info("%s has started", self.provideDicePlateService.name)

        self.storageDicePlateService.start()
        self.logger.info("%s has started", self.storageDicePlateService.name)			
		

        # opcua server ------------------------------------------------------------------
		
        ip_str = self.get_ip()
		
        servername = config.SERVER_CONFIG['servername']		
        uri = config.SERVER_CONFIG['uri']
		
        #endpoint = config.SERVER_CONFIG['endpoint']
        endpoint = 'opc.tcp://' + ip_str + ':4840/' + servername + '/'
		
        self.logger.debug("Building an OPCUA server: %s ", servername)
		
		# NOTE: servername parameter is used in the stations-object state machine
        self.server = AZ8UAServer(endpoint=endpoint, name=servername, uri=uri, station=self.storageStation, revpiobj=self.revpiioDriver).server
        self.server_publisher = ServerPublisher(server_name=servername, endpoint=endpoint, logger=self.logger)
		
		#Note: CommentOUT
        self.server_publisher.publish()
		
		#Note: CommentIN
        #if self.server_publisher.check_connection():
        #    self.server_publisher.publish()
        #else:
        #    self.logger.info("No connection to the database. OPCUA server was not registered.")
		
        # setting pub-sub system ---------------------------------------------------------
        self.logger.info("Setting events pub-sub system...")

		#.get_browse_name().
		
        # presence sensor's 1 subscribers :
        sensorUaNode = self.server.nodes.objects.get_child(["2:Sensor", "2:PresenceSensor1"])
        self.PresenceSensor1UaSubscriber = UaObjectSubscriber(self.server, sensorUaNode)

        self.presenceSensor1.register_subscribers(topic="State",
                                                  who=self.PresenceSensor1UaSubscriber,
                                                  callback=self.PresenceSensor1UaSubscriber.update)

        self.presenceSensor1.register_subscribers(topic="Value",
                                                  who=self.PresenceSensor1UaSubscriber,
                                                  callback=self.PresenceSensor1UaSubscriber.update)

		# Registering is correct solution
												  
        self.presenceSensor1.register_subscribers(topic="State",
                                                  who=self.storageRack1,
                                                  callback=self.storageRack1.handle_event)

        self.presenceSensor1.register_subscribers(topic="Value",
                                                  who=self.storageRack1,
                                                  callback=self.storageRack1.handle_event)
												  
        self.presenceSensor1.register_subscribers(topic="State",
                                                  who=self.initService,
                                                  callback=self.initService.handle_event)
												  
		#tbd Sensors subscription to init_Service										  
												  
        # presence sensor's 2 subscribers :
        sensorUaNode = self.server.nodes.objects.get_child(["2:Sensor", "2:PresenceSensor2"])
        self.PresenceSensor2UaSubscriber = UaObjectSubscriber(self.server, sensorUaNode)

        self.presenceSensor2.register_subscribers(topic="State",
                                                  who=self.PresenceSensor2UaSubscriber,
                                                  callback=self.PresenceSensor2UaSubscriber.update)

        self.presenceSensor2.register_subscribers(topic="Value",
                                                  who=self.PresenceSensor2UaSubscriber,
                                                  callback=self.PresenceSensor2UaSubscriber.update)
												  
        self.presenceSensor2.register_subscribers(topic="State",
                                                  who=self.storageRack2,
                                                  callback=self.storageRack2.handle_event)

        self.presenceSensor2.register_subscribers(topic="Value",
                                                  who=self.storageRack2,
                                                  callback=self.storageRack2.handle_event)			
												  
        self.presenceSensor2.register_subscribers(topic="State",
                                                  who=self.initService,
                                                  callback=self.initService.handle_event)
												  							  
        # presence sensor's 3 subscribers :
        sensorUaNode = self.server.nodes.objects.get_child(["2:Sensor", "2:PresenceSensor3"])
        self.PresenceSensor3UaSubscriber = UaObjectSubscriber(self.server, sensorUaNode)

        self.presenceSensor3.register_subscribers(topic="State",
                                                  who=self.PresenceSensor3UaSubscriber,
                                                  callback=self.PresenceSensor3UaSubscriber.update)

        self.presenceSensor3.register_subscribers(topic="Value",
                                                  who=self.PresenceSensor3UaSubscriber,
                                                  callback=self.PresenceSensor3UaSubscriber.update)
												  
        self.presenceSensor3.register_subscribers(topic="State",
                                                  who=self.storageRack3,
                                                  callback=self.storageRack3.handle_event)

        self.presenceSensor3.register_subscribers(topic="Value",
                                                  who=self.storageRack3,
                                                  callback=self.storageRack3.handle_event)
												  
        self.presenceSensor3.register_subscribers(topic="State",
                                                  who=self.initService,
                                                  callback=self.initService.handle_event)												  
												  
        # presence sensor's 4 subscribers :
        sensorUaNode = self.server.nodes.objects.get_child(["2:Sensor", "2:PresenceSensor4"])
        self.PresenceSensor4UaSubscriber = UaObjectSubscriber(self.server, sensorUaNode)

        self.presenceSensor4.register_subscribers(topic="State",
                                                  who=self.PresenceSensor4UaSubscriber,
                                                  callback=self.PresenceSensor4UaSubscriber.update)

        self.presenceSensor4.register_subscribers(topic="Value",
                                                  who=self.PresenceSensor4UaSubscriber,
                                                  callback=self.PresenceSensor4UaSubscriber.update)		

        self.presenceSensor4.register_subscribers(topic="State",
                                                  who=self.storageRack4,
                                                  callback=self.storageRack4.handle_event)

        self.presenceSensor4.register_subscribers(topic="Value",
                                                  who=self.storageRack4,
                                                  callback=self.storageRack4.handle_event)												  
												  
        self.presenceSensor4.register_subscribers(topic="State",
                                                  who=self.initService,
                                                  callback=self.initService.handle_event)														
        # presence sensor's 5 subscribers :
        sensorUaNode = self.server.nodes.objects.get_child(["2:Sensor", "2:PresenceSensor5"])
        self.PresenceSensor5UaSubscriber = UaObjectSubscriber(self.server, sensorUaNode)

        self.presenceSensor5.register_subscribers(topic="State",
                                                  who=self.PresenceSensor5UaSubscriber,
                                                  callback=self.PresenceSensor5UaSubscriber.update)

        self.presenceSensor5.register_subscribers(topic="Value",
                                                  who=self.PresenceSensor5UaSubscriber,
                                                  callback=self.PresenceSensor5UaSubscriber.update)			
												  
        self.presenceSensor5.register_subscribers(topic="State",
                                                  who=self.storageRack5,
                                                  callback=self.storageRack5.handle_event)

        self.presenceSensor5.register_subscribers(topic="Value",
                                                  who=self.storageRack5,
                                                  callback=self.storageRack5.handle_event)		
												  
        self.presenceSensor5.register_subscribers(topic="State",
                                                  who=self.initService,
                                                  callback=self.initService.handle_event)
												  
        # presence sensor's 6 subscribers :
        sensorUaNode = self.server.nodes.objects.get_child(["2:Sensor", "2:PresenceSensor6"])
        self.PresenceSensor6UaSubscriber = UaObjectSubscriber(self.server, sensorUaNode)

        self.presenceSensor6.register_subscribers(topic="State",
                                                  who=self.PresenceSensor6UaSubscriber,
                                                  callback=self.PresenceSensor6UaSubscriber.update)

        self.presenceSensor6.register_subscribers(topic="Value",
                                                  who=self.PresenceSensor6UaSubscriber,
                                                  callback=self.PresenceSensor6UaSubscriber.update)									
												  
        self.presenceSensor6.register_subscribers(topic="State",
                                                  who=self.storageRack6,
                                                  callback=self.storageRack6.handle_event)

        self.presenceSensor6.register_subscribers(topic="Value",
                                                  who=self.storageRack6,
                                                  callback=self.storageRack6.handle_event)
												  
        self.presenceSensor6.register_subscribers(topic="State",
                                                  who=self.initService,
                                                  callback=self.initService.handle_event)												  

        # interaction sensor's 1 subscribers :
        sensorUaNode = self.server.nodes.objects.get_child(["2:Sensor", "2:InteractionSensor1"])
        self.InteractionSensor1UaSubscriber = UaObjectSubscriber(self.server, sensorUaNode)

        self.interactionSensor1.register_subscribers(topic="State",
                                                     who=self.InteractionSensor1UaSubscriber,
                                                     callback=self.InteractionSensor1UaSubscriber.update)

        self.interactionSensor1.register_subscribers(topic="Value",
                                                     who=self.InteractionSensor1UaSubscriber,
                                                     callback=self.InteractionSensor1UaSubscriber.update)									
												  
        self.interactionSensor1.register_subscribers(topic="State",
                                                     who=self.initService,
                                                     callback=self.initService.handle_event)
													 
        self.interactionSensor1.register_subscribers(topic="Value",
                                                     who=self.storageRack1,
                                                     callback=self.storageRack1.handle_event)											 
													 
        self.interactionSensor1.register_subscribers(topic="Value",
                                                     who=self.storageRack2,
                                                     callback=self.storageRack2.handle_event)														 
													 
        self.interactionSensor1.register_subscribers(topic="Value",
                                                     who=self.storageRack3,
                                                     callback=self.storageRack3.handle_event)											 
													 
        self.interactionSensor1.register_subscribers(topic="Value",
                                                     who=self.storageRack4,
                                                     callback=self.storageRack4.handle_event)
													 
        self.interactionSensor1.register_subscribers(topic="Value",
                                                     who=self.storageRack5,
                                                     callback=self.storageRack5.handle_event)
													 
        self.interactionSensor1.register_subscribers(topic="Value",
                                                     who=self.storageRack6,
                                                     callback=self.storageRack6.handle_event)													 
													 
        # interaction sensor's 2 subscribers :
        sensorUaNode = self.server.nodes.objects.get_child(["2:Sensor", "2:InteractionSensor2"])
        self.InteractionSensor2UaSubscriber = UaObjectSubscriber(self.server, sensorUaNode)

        self.interactionSensor2.register_subscribers(topic="State",
                                                     who=self.InteractionSensor2UaSubscriber,
                                                     callback=self.InteractionSensor2UaSubscriber.update)

        self.interactionSensor2.register_subscribers(topic="Value",
                                                     who=self.InteractionSensor2UaSubscriber,
                                                     callback=self.InteractionSensor2UaSubscriber.update)								
												  
        self.interactionSensor2.register_subscribers(topic="State",
                                                     who=self.initService,
                                                     callback=self.initService.handle_event)
													 
        self.interactionSensor2.register_subscribers(topic="Value",
                                                     who=self.storageRack1,
                                                     callback=self.storageRack1.handle_event)											 
													 
        self.interactionSensor2.register_subscribers(topic="Value",
                                                     who=self.storageRack2,
                                                     callback=self.storageRack2.handle_event)														 
													 
        self.interactionSensor2.register_subscribers(topic="Value",
                                                     who=self.storageRack3,
                                                     callback=self.storageRack3.handle_event)											 

        self.interactionSensor2.register_subscribers(topic="Value",
                                                     who=self.storageRack4,
                                                     callback=self.storageRack4.handle_event)
													 
        self.interactionSensor2.register_subscribers(topic="Value",
                                                     who=self.storageRack5,
                                                     callback=self.storageRack5.handle_event)
													 
        self.interactionSensor2.register_subscribers(topic="Value",
                                                     who=self.storageRack6,
                                                     callback=self.storageRack6.handle_event)														 
													 
		# RGBLED's subscribers for initService

        self.storageRack1LED.register_subscribers(topic="State",
                                                  who=self.initService,
                                                  callback=self.initService.handle_event)

        self.storageRack2LED.register_subscribers(topic="State",
                                                  who=self.initService,
                                                  callback=self.initService.handle_event)

        self.storageRack3LED.register_subscribers(topic="State",
                                                  who=self.initService,
                                                  callback=self.initService.handle_event)

        self.storageRack4LED.register_subscribers(topic="State",
                                                  who=self.initService,
                                                  callback=self.initService.handle_event)

        self.storageRack5LED.register_subscribers(topic="State",
                                                  who=self.initService,
                                                  callback=self.initService.handle_event)

        self.storageRack6LED.register_subscribers(topic="State",
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
												  
		# StorageRack 1

        sensorUaNode = self.server.nodes.objects.get_child(["2:Monitoring", "2:StorageRack1"])
        self.StorageRack1UaSubscriber = UaObjectSubscriber(self.server, sensorUaNode)

        self.storageRack1.register_subscribers(topic="State",
                                               who=self.StorageRack1UaSubscriber,
                                               callback=self.StorageRack1UaSubscriber.update)
											   
        self.storageRack1.register_subscribers(topic="Value",
                                               who=self.StorageRack1UaSubscriber,
                                               callback=self.StorageRack1UaSubscriber.update)
											   
        self.storageRack1.register_subscribers(topic="PlateColor1",
                                               who=self.StorageRack1UaSubscriber,
                                               callback=self.StorageRack1UaSubscriber.update)											   
											   
        self.storageRack1.register_subscribers(topic="QuantityOfPlateColor1",
                                               who=self.StorageRack1UaSubscriber,
                                               callback=self.StorageRack1UaSubscriber.update)
											   
        self.storageRack1.register_subscribers(topic="PlateColor2",
                                               who=self.StorageRack1UaSubscriber,
                                               callback=self.StorageRack1UaSubscriber.update)
											   
        self.storageRack1.register_subscribers(topic="QuantityOfPlateColor2",
                                               who=self.StorageRack1UaSubscriber,
                                               callback=self.StorageRack1UaSubscriber.update)

        self.storageRack1.register_subscribers(topic="PlateColor3",
                                               who=self.StorageRack1UaSubscriber,
                                               callback=self.StorageRack1UaSubscriber.update)											   
											   
        self.storageRack1.register_subscribers(topic="QuantityOfPlateColor3",
                                               who=self.StorageRack1UaSubscriber,
                                               callback=self.StorageRack1UaSubscriber.update)
											   
        self.storageRack1.register_subscribers(topic="State",
                                               who=self.initService,
                                               callback=self.initService.handle_event)
						   									   
        self.storageRack1.register_subscribers(topic="State",
                                               who=self.provideDicePlateService,
                                               callback=self.provideDicePlateService.handle_event)
											   
        self.storageRack1.register_subscribers(topic="State",
                                               who=self.storageDicePlateService,
                                               callback=self.storageDicePlateService.handle_event)
											   
		# StorageRack 2

        sensorUaNode = self.server.nodes.objects.get_child(["2:Monitoring", "2:StorageRack2"])
        self.StorageRack2UaSubscriber = UaObjectSubscriber(self.server, sensorUaNode)		
		
        self.storageRack2.register_subscribers(topic="State",
                                               who=self.StorageRack2UaSubscriber,
                                               callback=self.StorageRack2UaSubscriber.update)
		
        self.storageRack2.register_subscribers(topic="Value",
                                               who=self.StorageRack2UaSubscriber,
                                               callback=self.StorageRack2UaSubscriber.update)
											   
        self.storageRack2.register_subscribers(topic="PlateColor1",
                                               who=self.StorageRack2UaSubscriber,
                                               callback=self.StorageRack2UaSubscriber.update)											   
											   
        self.storageRack2.register_subscribers(topic="QuantityOfPlateColor1",
                                               who=self.StorageRack2UaSubscriber,
                                               callback=self.StorageRack2UaSubscriber.update)

        self.storageRack2.register_subscribers(topic="PlateColor2",
                                               who=self.StorageRack2UaSubscriber,
                                               callback=self.StorageRack2UaSubscriber.update)	
											   
        self.storageRack2.register_subscribers(topic="QuantityOfPlateColor2",
                                               who=self.StorageRack2UaSubscriber,
                                               callback=self.StorageRack2UaSubscriber.update)

        self.storageRack2.register_subscribers(topic="PlateColor3",
                                               who=self.StorageRack2UaSubscriber,
                                               callback=self.StorageRack2UaSubscriber.update)	
											   
        self.storageRack2.register_subscribers(topic="QuantityOfPlateColor3",
                                               who=self.StorageRack2UaSubscriber,
                                               callback=self.StorageRack2UaSubscriber.update)
											   
        self.storageRack2.register_subscribers(topic="State",
                                               who=self.initService,
                                               callback=self.initService.handle_event)
											   
        self.storageRack2.register_subscribers(topic="State",
                                               who=self.provideDicePlateService,
                                               callback=self.provideDicePlateService.handle_event)
											   
        self.storageRack2.register_subscribers(topic="State",
                                               who=self.storageDicePlateService,
                                               callback=self.storageDicePlateService.handle_event)
											   
		# StorageRack 3		   
				
        sensorUaNode = self.server.nodes.objects.get_child(["2:Monitoring", "2:StorageRack3"])
        self.StorageRack3UaSubscriber = UaObjectSubscriber(self.server, sensorUaNode)
				
        self.storageRack3.register_subscribers(topic="State",
                                               who=self.StorageRack3UaSubscriber,
                                               callback=self.StorageRack3UaSubscriber.update)
		
        self.storageRack3.register_subscribers(topic="Value",
                                               who=self.StorageRack3UaSubscriber,
                                               callback=self.StorageRack3UaSubscriber.update)

        self.storageRack3.register_subscribers(topic="PlateColor1",
                                               who=self.StorageRack3UaSubscriber,
                                               callback=self.StorageRack3UaSubscriber.update)	
											   
        self.storageRack3.register_subscribers(topic="QuantityOfPlateColor1",
                                               who=self.StorageRack3UaSubscriber,
                                               callback=self.StorageRack3UaSubscriber.update)

        self.storageRack3.register_subscribers(topic="PlateColor2",
                                               who=self.StorageRack3UaSubscriber,
                                               callback=self.StorageRack3UaSubscriber.update)	
											   
        self.storageRack3.register_subscribers(topic="QuantityOfPlateColor2",
                                               who=self.StorageRack3UaSubscriber,
                                               callback=self.StorageRack3UaSubscriber.update)

        self.storageRack3.register_subscribers(topic="PlateColor3",
                                               who=self.StorageRack3UaSubscriber,
                                               callback=self.StorageRack3UaSubscriber.update)	
											   
        self.storageRack3.register_subscribers(topic="QuantityOfPlateColor3",
                                               who=self.StorageRack3UaSubscriber,
                                               callback=self.StorageRack3UaSubscriber.update)
											   
        self.storageRack3.register_subscribers(topic="State",
                                               who=self.initService,
                                               callback=self.initService.handle_event)
											   
        self.storageRack3.register_subscribers(topic="State",
                                               who=self.provideDicePlateService,
                                               callback=self.provideDicePlateService.handle_event)
											   
        self.storageRack3.register_subscribers(topic="State",
                                               who=self.storageDicePlateService,
                                               callback=self.storageDicePlateService.handle_event)
											   
		# StorageRack 4											   
			
        sensorUaNode = self.server.nodes.objects.get_child(["2:Monitoring", "2:StorageRack4"])
        self.StorageRack4UaSubscriber = UaObjectSubscriber(self.server, sensorUaNode)
			
        self.storageRack4.register_subscribers(topic="State",
                                               who=self.StorageRack4UaSubscriber,
                                               callback=self.StorageRack4UaSubscriber.update)
		
        self.storageRack4.register_subscribers(topic="Value",
                                               who=self.StorageRack4UaSubscriber,
                                               callback=self.StorageRack4UaSubscriber.update)	

        self.storageRack4.register_subscribers(topic="PlateColor1",
                                               who=self.StorageRack4UaSubscriber,
                                               callback=self.StorageRack4UaSubscriber.update)												   
											   
        self.storageRack4.register_subscribers(topic="QuantityOfPlateColor1",
                                               who=self.StorageRack4UaSubscriber,
                                               callback=self.StorageRack4UaSubscriber.update)
	
        self.storageRack4.register_subscribers(topic="PlateColor2",
                                               who=self.StorageRack4UaSubscriber,
                                               callback=self.StorageRack4UaSubscriber.update)	
	
        self.storageRack4.register_subscribers(topic="QuantityOfPlateColor2",
                                               who=self.StorageRack4UaSubscriber,
                                               callback=self.StorageRack4UaSubscriber.update)

        self.storageRack4.register_subscribers(topic="PlateColor3",
                                               who=self.StorageRack4UaSubscriber,
                                               callback=self.StorageRack4UaSubscriber.update)	
											   
        self.storageRack4.register_subscribers(topic="QuantityOfPlateColor3",
                                               who=self.StorageRack4UaSubscriber,
                                               callback=self.StorageRack4UaSubscriber.update)											   
											   
        self.storageRack4.register_subscribers(topic="State",
                                               who=self.initService,
                                               callback=self.initService.handle_event)
											   
        self.storageRack4.register_subscribers(topic="State",
                                               who=self.provideDicePlateService,
                                               callback=self.provideDicePlateService.handle_event)
											   
        self.storageRack4.register_subscribers(topic="State",
                                               who=self.storageDicePlateService,
                                               callback=self.storageDicePlateService.handle_event)
											   
		# StorageRack 5
		
        sensorUaNode = self.server.nodes.objects.get_child(["2:Monitoring", "2:StorageRack5"])
        self.StorageRack5UaSubscriber = UaObjectSubscriber(self.server, sensorUaNode)		
		
        self.storageRack5.register_subscribers(topic="State",
                                               who=self.StorageRack5UaSubscriber,
                                               callback=self.StorageRack5UaSubscriber.update)
		
        self.storageRack5.register_subscribers(topic="Value",
                                               who=self.StorageRack5UaSubscriber,
                                               callback=self.StorageRack5UaSubscriber.update)

        self.storageRack5.register_subscribers(topic="PlateColor1",
                                               who=self.StorageRack5UaSubscriber,
                                               callback=self.StorageRack5UaSubscriber.update)												   
											   
        self.storageRack5.register_subscribers(topic="QuantityOfPlateColor1",
                                               who=self.StorageRack5UaSubscriber,
                                               callback=self.StorageRack5UaSubscriber.update)

        self.storageRack5.register_subscribers(topic="PlateColor2",
                                               who=self.StorageRack5UaSubscriber,
                                               callback=self.StorageRack5UaSubscriber.update)	
											   
        self.storageRack5.register_subscribers(topic="QuantityOfPlateColor2",
                                               who=self.StorageRack5UaSubscriber,
                                               callback=self.StorageRack5UaSubscriber.update)

        self.storageRack5.register_subscribers(topic="PlateColor3",
                                               who=self.StorageRack5UaSubscriber,
                                               callback=self.StorageRack5UaSubscriber.update)	
											   
        self.storageRack5.register_subscribers(topic="QuantityOfPlateColor3",
                                               who=self.StorageRack5UaSubscriber,
                                               callback=self.StorageRack5UaSubscriber.update)											   
											   
        self.storageRack5.register_subscribers(topic="State",
                                               who=self.initService,
                                               callback=self.initService.handle_event)
											   
        self.storageRack5.register_subscribers(topic="State",
                                               who=self.provideDicePlateService,
                                               callback=self.provideDicePlateService.handle_event)
											   
        self.storageRack5.register_subscribers(topic="State",
                                               who=self.storageDicePlateService,
                                               callback=self.storageDicePlateService.handle_event)
											   
		# StorageRack 6	
		
        sensorUaNode = self.server.nodes.objects.get_child(["2:Monitoring", "2:StorageRack6"])
        self.StorageRack6UaSubscriber = UaObjectSubscriber(self.server, sensorUaNode)		
		
        self.storageRack6.register_subscribers(topic="State",
                                               who=self.StorageRack6UaSubscriber,
                                               callback=self.StorageRack6UaSubscriber.update)
		
        self.storageRack6.register_subscribers(topic="Value",
                                               who=self.StorageRack6UaSubscriber,
                                               callback=self.StorageRack6UaSubscriber.update)	

        self.storageRack6.register_subscribers(topic="PlateColor1",
                                               who=self.StorageRack6UaSubscriber,
                                               callback=self.StorageRack6UaSubscriber.update)												   
											   
        self.storageRack6.register_subscribers(topic="QuantityOfPlateColor1",
                                               who=self.StorageRack6UaSubscriber,
                                               callback=self.StorageRack6UaSubscriber.update)

        self.storageRack6.register_subscribers(topic="PlateColor2",
                                               who=self.StorageRack6UaSubscriber,
                                               callback=self.StorageRack6UaSubscriber.update)
											   
        self.storageRack6.register_subscribers(topic="QuantityOfPlateColor2",
                                               who=self.StorageRack6UaSubscriber,
                                               callback=self.StorageRack6UaSubscriber.update)

        self.storageRack6.register_subscribers(topic="PlateColor3",
                                               who=self.StorageRack6UaSubscriber,
                                               callback=self.StorageRack6UaSubscriber.update)
											   
        self.storageRack6.register_subscribers(topic="QuantityOfPlateColor3",
                                               who=self.StorageRack6UaSubscriber,
                                               callback=self.StorageRack6UaSubscriber.update)
											   
        self.storageRack6.register_subscribers(topic="State",
                                               who=self.initService,
                                               callback=self.initService.handle_event)							

        self.storageRack6.register_subscribers(topic="State",
                                               who=self.provideDicePlateService,
                                               callback=self.provideDicePlateService.handle_event)
											   
        self.storageRack6.register_subscribers(topic="State",
                                               who=self.storageDicePlateService,
                                               callback=self.storageDicePlateService.handle_event)
											   
        # Services register subscribers for EventID
        self.initService.register_subscribers(topic="eventID",
                                              who=self.storageStation,
                                              callback=self.storageStation.handle_event)

        self.provideDicePlateService.register_subscribers(topic="eventID",
                                                          who=self.storageStation,
                                                          callback=self.storageStation.handle_event)

        self.storageDicePlateService.register_subscribers(topic="eventID",
                                                          who=self.storageStation,
                                                          callback=self.storageStation.handle_event)		
		
        # Station's subscribers :
        stationStateUaNode = self.server.nodes.objects.get_child(["2:StateMachine"])
        self.stationStateUaSubscriber = UaObjectSubscriber(self.server, stationStateUaNode)

        self.storageStation.register_subscribers(topic="StationState",
                                                 who=self.stationStateUaSubscriber,
                                                 callback=self.stationStateUaSubscriber.update)

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
												 
        self.storageStation.register_subscribers(topic="Ack",
                                                 who=self.initService,
                                                 callback=self.initService.handle_event)

        self.storageStation.register_subscribers(topic="Ack",
                                                 who=self.provideDicePlateService,
                                                 callback=self.provideDicePlateService.handle_event)

        self.storageStation.register_subscribers(topic="Ack",
                                                 who=self.storageDicePlateService,
                                                 callback=self.storageDicePlateService.handle_event)												 

        self.storageStation.register_subscribers(topic="Ack",
                                                 who=self.storageRack1,
                                                 callback=self.storageRack1.handle_event)

        self.storageStation.register_subscribers(topic="Ack",
                                                 who=self.storageRack2,
                                                 callback=self.storageRack2.handle_event)
												 
        self.storageStation.register_subscribers(topic="Ack",
                                                 who=self.storageRack3,
                                                 callback=self.storageRack3.handle_event)												 

        self.storageStation.register_subscribers(topic="Ack",
                                                 who=self.storageRack4,
                                                 callback=self.storageRack4.handle_event)

        self.storageStation.register_subscribers(topic="Ack",
                                                 who=self.storageRack5,
                                                 callback=self.storageRack5.handle_event)
												 
        self.storageStation.register_subscribers(topic="Ack",
                                                 who=self.storageRack6,
                                                 callback=self.storageRack6.handle_event)												 
												 
        self.storageStation.register_subscribers(topic="Ack",
                                                 who=self.statusLED,
                                                 callback=self.statusLED.handle_event)
												 
        self.storageStation.register_subscribers(topic="Ack",
                                                 who=self.blinker,
                                                 callback=self.blinker.handle_event)
												 
        # Subscribers for storageracks
		
		# Storagerack 1
		
        self.storageRack1.register_subscribers(topic="StationErrorCode",
                                               who=self.stationStateUaSubscriber,
                                               callback=self.stationStateUaSubscriber.update)

        self.storageRack1.register_subscribers(topic="StationErrorDescription",
                                               who=self.stationStateUaSubscriber,
                                               callback=self.stationStateUaSubscriber.update)

        self.storageRack1.register_subscribers(topic="StationMessageCode",
                                               who=self.stationStateUaSubscriber,
                                               callback=self.stationStateUaSubscriber.update)

        self.storageRack1.register_subscribers(topic="StationMessageDescription",
                                               who=self.stationStateUaSubscriber,
                                               callback=self.stationStateUaSubscriber.update)

		# Storagerack 2
											   
        self.storageRack2.register_subscribers(topic="StationErrorCode",
                                               who=self.stationStateUaSubscriber,
                                               callback=self.stationStateUaSubscriber.update)

        self.storageRack2.register_subscribers(topic="StationErrorDescription",
                                               who=self.stationStateUaSubscriber,
                                               callback=self.stationStateUaSubscriber.update)
											   
        self.storageRack2.register_subscribers(topic="StationMessageCode",
                                               who=self.stationStateUaSubscriber,
                                               callback=self.stationStateUaSubscriber.update)

        self.storageRack2.register_subscribers(topic="StationMessageDescription",
                                               who=self.stationStateUaSubscriber,
                                               callback=self.stationStateUaSubscriber.update)								 

		# Storagerack 3
		
        self.storageRack3.register_subscribers(topic="StationErrorCode",
                                               who=self.stationStateUaSubscriber,
                                               callback=self.stationStateUaSubscriber.update)

        self.storageRack3.register_subscribers(topic="StationErrorDescription",
                                               who=self.stationStateUaSubscriber,
                                               callback=self.stationStateUaSubscriber.update)
											   
        self.storageRack3.register_subscribers(topic="StationMessageCode",
                                               who=self.stationStateUaSubscriber,
                                               callback=self.stationStateUaSubscriber.update)

        self.storageRack3.register_subscribers(topic="StationMessageDescription",
                                               who=self.stationStateUaSubscriber,
                                               callback=self.stationStateUaSubscriber.update)											   

		# Storagerack 4
		
        self.storageRack4.register_subscribers(topic="StationErrorCode",
                                               who=self.stationStateUaSubscriber,
                                               callback=self.stationStateUaSubscriber.update)

        self.storageRack4.register_subscribers(topic="StationErrorDescription",
                                               who=self.stationStateUaSubscriber,
                                               callback=self.stationStateUaSubscriber.update)
											   
        self.storageRack4.register_subscribers(topic="StationMessageCode",
                                               who=self.stationStateUaSubscriber,
                                               callback=self.stationStateUaSubscriber.update)

        self.storageRack4.register_subscribers(topic="StationMessageDescription",
                                               who=self.stationStateUaSubscriber,
                                               callback=self.stationStateUaSubscriber.update)
		# Storagerack 5
		
        self.storageRack5.register_subscribers(topic="StationErrorCode",
                                               who=self.stationStateUaSubscriber,
                                               callback=self.stationStateUaSubscriber.update)

        self.storageRack5.register_subscribers(topic="StationErrorDescription",
                                               who=self.stationStateUaSubscriber,
                                               callback=self.stationStateUaSubscriber.update)
											   
        self.storageRack5.register_subscribers(topic="StationMessageCode",
                                               who=self.stationStateUaSubscriber,
                                               callback=self.stationStateUaSubscriber.update)

        self.storageRack5.register_subscribers(topic="StationMessageDescription",
                                               who=self.stationStateUaSubscriber,
                                               callback=self.stationStateUaSubscriber.update)								 

		# Storagerack 6
		
        self.storageRack6.register_subscribers(topic="StationErrorCode",
                                               who=self.stationStateUaSubscriber,
                                               callback=self.stationStateUaSubscriber.update)

        self.storageRack6.register_subscribers(topic="StationErrorDescription",
                                               who=self.stationStateUaSubscriber,
                                               callback=self.stationStateUaSubscriber.update)											   
											   
        self.storageRack6.register_subscribers(topic="StationMessageCode",
                                               who=self.stationStateUaSubscriber,
                                               callback=self.stationStateUaSubscriber.update)

        self.storageRack6.register_subscribers(topic="StationMessageDescription",
                                               who=self.stationStateUaSubscriber,
                                               callback=self.stationStateUaSubscriber.update)

        # Subscribers for services
		
		# initService
		
        self.initService.register_subscribers(topic="StationErrorCode",
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
											  
		# provideDicePlateService
		
        self.provideDicePlateService.register_subscribers(topic="StationErrorCode",
                                                          who=self.stationStateUaSubscriber,
                                                          callback=self.stationStateUaSubscriber.update)

        self.provideDicePlateService.register_subscribers(topic="StationErrorDescription",
                                                          who=self.stationStateUaSubscriber,
                                                          callback=self.stationStateUaSubscriber.update)

        self.provideDicePlateService.register_subscribers(topic="StationMessageCode",
                                                          who=self.stationStateUaSubscriber,
                                                          callback=self.stationStateUaSubscriber.update)

        self.provideDicePlateService.register_subscribers(topic="StationMessageDescription",
                                                          who=self.stationStateUaSubscriber,
                                                          callback=self.stationStateUaSubscriber.update)	

		# storageDicePlateService
		
        self.storageDicePlateService.register_subscribers(topic="StationErrorCode",
                                                          who=self.stationStateUaSubscriber,
                                                          callback=self.stationStateUaSubscriber.update)

        self.storageDicePlateService.register_subscribers(topic="StationErrorDescription",
                                                          who=self.stationStateUaSubscriber,
                                                          callback=self.stationStateUaSubscriber.update)

        self.storageDicePlateService.register_subscribers(topic="StationMessageCode",
                                                          who=self.stationStateUaSubscriber,
                                                          callback=self.stationStateUaSubscriber.update)

        self.storageDicePlateService.register_subscribers(topic="StationMessageDescription",
                                                          who=self.stationStateUaSubscriber,
                                                          callback=self.stationStateUaSubscriber.update)	
					
        # Setting RevPi driver -------------------------------------------------------------
		
        self.revpiioDriver.handlesignalend(self.shutdown)

        self.logger.debug("Registering handlers for inputs events. Start.")

		# Register the RevPi DIO-events for single sensor values (condition is boolean):
		#	Input 1 = StorageAreaSensor #1 (Object in PresenceSensorList[0])
		#	Input 2 = StorageAreaSensor #2 (Object in PresenceSensorList[1])
		#	Input 3 = StorageAreaSensor #3 (Object in PresenceSensorList[2])
		#	Input 4 = StorageAreaSensor #4 (Object in PresenceSensorList[3])
		#	Input 5 = StorageAreaSensor #5 (Object in PresenceSensorList[4])
		#	Input 6 = StorageAreaSensor #6 (Object in PresenceSensorList[5])
		#	Input 7 = safetySwitch
		
		# tbd - Implement an DIO event in the subobject
		
        self.revpiioDriver.io.I_6.reg_event(self.input1_posedge_event, edge=revpimodio2.RISING)
        self.revpiioDriver.io.I_6.reg_event(self.input1_negedge_event, edge=revpimodio2.FALLING)
        self.revpiioDriver.io.I_8.reg_event(self.input2_posedge_event, edge=revpimodio2.RISING)
        self.revpiioDriver.io.I_8.reg_event(self.input2_negedge_event, edge=revpimodio2.FALLING)
        self.revpiioDriver.io.I_10.reg_event(self.input3_posedge_event, edge=revpimodio2.RISING)
        self.revpiioDriver.io.I_10.reg_event(self.input3_negedge_event, edge=revpimodio2.FALLING)
        self.revpiioDriver.io.I_13.reg_event(self.input4_posedge_event, edge=revpimodio2.RISING)
        self.revpiioDriver.io.I_13.reg_event(self.input4_negedge_event, edge=revpimodio2.FALLING)
        self.revpiioDriver.io.I_2.reg_event(self.input5_posedge_event, edge=revpimodio2.RISING)
        self.revpiioDriver.io.I_2.reg_event(self.input5_negedge_event, edge=revpimodio2.FALLING)
        self.revpiioDriver.io.I_4.reg_event(self.input6_posedge_event, edge=revpimodio2.RISING)
        self.revpiioDriver.io.I_4.reg_event(self.input6_negedge_event, edge=revpimodio2.FALLING)
        self.revpiioDriver.io.I_12.reg_event(self.input7_posedge_event, edge=revpimodio2.RISING)
        self.revpiioDriver.io.I_12.reg_event(self.input7_negedge_event, edge=revpimodio2.FALLING)
        self.revpiioDriver.io.I_14.reg_event(self.input8_posedge_event, edge=revpimodio2.RISING)
        self.revpiioDriver.io.I_14.reg_event(self.input8_negedge_event, edge=revpimodio2.FALLING)
		
        self.logger.debug("Registering handlers for inputs events. Done.")		
		
        # Starting everything ------------------------------------------------------------
		
		# 	Starting OPCUA server
		
        self.server.start()
        self.logger.info("OPCUA server %s at %s has started", servername, endpoint)
        self.connMonitor.start()
        self.logger.info("%s has started", self.connMonitor.name)	

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
        for device in self.dev_list:
            device.stop()
        self.statusLED.stop() # in device list
        self.blinker.stop()
        self.storageStation.stop()
        self.server.stop()
        self.connMonitor.stop()
        self.initService.stop()
        self.provideDicePlateService.stop()
        self.storageDicePlateService.stop()
        self.revpiioDriver.exit()

    # Event handler for presenceSensor1 
	
    def input1_posedge_event(self, ioname, iovalue):
        self.logger.debug("Input %s : Value %s", ioname, iovalue)
        posedge_event = events.SimpleSensorInputEvent(eventID=events.SimpleSensorInputEvents.PosEdge,
                                                      sender=self._name)
        self.presenceSensor1.handle_event(event=posedge_event)

    def input1_negedge_event(self, ioname, iovalue):
        self.logger.debug("Input %s : Value %s", ioname, iovalue)
        negedge_event = events.SimpleSensorInputEvent(eventID=events.SimpleSensorInputEvents.NegEdge,
                                                      sender=self._name)
        self.presenceSensor1.handle_event(event=negedge_event)
	   
    # Event handler for presenceSensor2
												   
    def input2_posedge_event(self, ioname, iovalue):
        self.logger.debug("Input %s : Value %s", ioname, iovalue)
        posedge_event = events.SimpleSensorInputEvent(eventID=events.SimpleSensorInputEvents.PosEdge,
                                                      sender=self._name)
        self.presenceSensor2.handle_event(event=posedge_event)

    def input2_negedge_event(self, ioname, iovalue):
        self.logger.debug("Input %s : Value %s", ioname, iovalue)
        negedge_event = events.SimpleSensorInputEvent(eventID=events.SimpleSensorInputEvents.NegEdge,
                                                      sender=self._name)
        self.presenceSensor2.handle_event(event=negedge_event)

    # Event handler for presenceSensor3
												   
    def input3_posedge_event(self, ioname, iovalue):
        self.logger.debug("Input %s : Value %s", ioname, iovalue)
        posedge_event = events.SimpleSensorInputEvent(eventID=events.SimpleSensorInputEvents.PosEdge,
                                                      sender=self._name)
        self.presenceSensor3.handle_event(event=posedge_event)

    def input3_negedge_event(self, ioname, iovalue):
        self.logger.debug("Input %s : Value %s", ioname, iovalue)
        negedge_event = events.SimpleSensorInputEvent(eventID=events.SimpleSensorInputEvents.NegEdge,
                                                      sender=self._name)
        self.presenceSensor3.handle_event(event=negedge_event)

    # Event handler for presenceSensor4
												   
    def input4_posedge_event(self, ioname, iovalue):
        self.logger.debug("Input %s : Value %s", ioname, iovalue)
        posedge_event = events.SimpleSensorInputEvent(eventID=events.SimpleSensorInputEvents.PosEdge,
                                                      sender=self._name)
        self.presenceSensor4.handle_event(event=posedge_event)

    def input4_negedge_event(self, ioname, iovalue):
        self.logger.debug("Input %s : Value %s", ioname, iovalue)
        negedge_event = events.SimpleSensorInputEvent(eventID=events.SimpleSensorInputEvents.NegEdge,
                                                      sender=self._name)
        self.presenceSensor4.handle_event(event=negedge_event)

    # Event handler for presenceSensor5										   
												   
    def input5_posedge_event(self, ioname, iovalue):
        self.logger.debug("Input %s : Value %s", ioname, iovalue)
        posedge_event = events.SimpleSensorInputEvent(eventID=events.SimpleSensorInputEvents.PosEdge,
                                                      sender=self._name)
        self.presenceSensor5.handle_event(event=posedge_event)

    def input5_negedge_event(self, ioname, iovalue):
        self.logger.debug("Input %s : Value %s", ioname, iovalue)
        negedge_event = events.SimpleSensorInputEvent(eventID=events.SimpleSensorInputEvents.NegEdge,
                                                      sender=self._name)
        self.presenceSensor5.handle_event(event=negedge_event)

    # Event handler for presenceSensor6									
										
    def input6_posedge_event(self, ioname, iovalue):
        self.logger.debug("Input %s : Value %s", ioname, iovalue)
        posedge_event = events.SimpleSensorInputEvent(eventID=events.SimpleSensorInputEvents.PosEdge,
                                                      sender=self._name)
        self.presenceSensor6.handle_event(event=posedge_event)

    def input6_negedge_event(self, ioname, iovalue):
        self.logger.debug("Input %s : Value %s", ioname, iovalue)
        negedge_event = events.SimpleSensorInputEvent(eventID=events.SimpleSensorInputEvents.NegEdge,
                                                      sender=self._name)
        self.presenceSensor6.handle_event(event=negedge_event)

	# For the interaction sensors of the storage station, only the posedge event is needed
    # Event handler for interactionSensor1									
										
    def input7_posedge_event(self, ioname, iovalue):
        self.logger.debug("Input %s : Value %s", ioname, iovalue)
        posedge_event = events.SimpleSensorInputEvent(eventID=events.SimpleSensorInputEvents.PosEdge,
                                                      sender=self._name)
        self.interactionSensor1.handle_event(event=posedge_event)

    def input7_negedge_event(self, ioname, iovalue):
        self.logger.debug("Input %s : Value %s", ioname, iovalue)
        negedge_event = events.SimpleSensorInputEvent(eventID=events.SimpleSensorInputEvents.NegEdge,
                                                      sender=self._name)
        self.interactionSensor1.handle_event(event=negedge_event)		
		
    # Event handler for interactionSensor2									
										
    def input8_posedge_event(self, ioname, iovalue):
        self.logger.debug("Input %s : Value %s", ioname, iovalue)
        posedge_event = events.SimpleSensorInputEvent(eventID=events.SimpleSensorInputEvents.PosEdge,
                                                      sender=self._name)
        self.interactionSensor2.handle_event(event=posedge_event)

    def input8_negedge_event(self, ioname, iovalue):
        self.logger.debug("Input %s : Value %s", ioname, iovalue)
        negedge_event = events.SimpleSensorInputEvent(eventID=events.SimpleSensorInputEvents.NegEdge,
                                                      sender=self._name)
        self.interactionSensor2.handle_event(event=negedge_event)

    def conn_broken_event(self):
        noconn_event = events.StorageStationInputEvent(eventID=events.StorageStationInputEvents.NoConn,
                                                       sender=self._name)
        self.storageStation.handle_event(event=noconn_event)

    def conn_alive_event(self):
        connok_event = events.StorageStationInputEvent(eventID=events.StorageStationInputEvents.ConnOk,
                                                       sender=self._name)
        self.storageStation.handle_event(event=connok_event)
		
    def start(self):
        self.revpiioDriver.mainloop(blocking=False)
        self.logger.debug("RevPi driver has been started.")

        # Loop to do some work next to the event system. E.g. Switch on / off green part of LED A1
        while not self.revpiioDriver.exitsignal.wait(1.0):
            self.revpiioDriver.core.a1green.value = not self.revpiioDriver.core.a1green.value

def main():

    app = StationApp(config.STATION_CONFIG['stationName'])
    app.start()

if __name__ == '__main__':
    main()



