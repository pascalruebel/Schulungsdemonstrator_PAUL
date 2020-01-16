import definitions
from communication.server import UAServer, UaObjectSubscriber
from activeobjects.sensors.presencesensor import PresenceSensor
from activeobjects.sensors.safetyswitch import SafetySwitch
from activeobjects.actuators.rgb_led import RGB_LED
from activeobjects.actuators.blinker import Blinker
from activeobjects.actuators.blinker_led_adapter import BlinkerLedAdapter
from activeobjects.station.station import Station
from activeobjects.services.initialization.init_service import InitService
from activeobjects.services.assemble.assemble_service import AssembleService
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
        self.active_objects = list()


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
        self.fatal_error_event = events.StationEvent(eventID=events.StationEvents.FatalError,
                                                     sender=self._name)

        # building station objects -----------------------------------------------------
        # buttons -----------------------------------------------------------------------

        self.completeButton = PresenceSensor("ButtonProductionDone", "-SF1", topics=["State", "Value"],
                                             inputobj=self.revpiioDriver.io['input4'],
                                             normally_open=True)

        self.abortButton = PresenceSensor("ButtonProductionError", "-SF2", topics=["State", "Value"],
                                          inputobj=self.revpiioDriver.io['input5'],
                                          normally_open=True)


        # actuators  --------------------------------------------------------------------
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
        self.assemblyStation = Station("Station",
                                       status_led=self.statusLED,
                                       blinker=self.blinker,
                                       topics=['StationState', 'Ack', 'StationErrorCode',
                                               'StationErrorDescription', 'StationSafetyState',
                                               'StationMessageCode', 'StationMessageDescription',
                                               'StationStateMaintenance'])

        # building and registering services -----------------------------------------------

        # 1) create an initialization service:

        dev_list = [self.completeButton, self.abortButton]

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


        #  assemble service :
        self.assembleService = AssembleService(name="AssembleService",
                                               complete_button=self.completeButton,
                                               abort_button=self.abortButton,
                                               enable_timeout=True,
                                               timeout_interval=config.STATION_CONFIG['assembleServiceTimeoutInterval'],
                                               topics=['eventID', 'StationErrorCode', 'StationErrorDescription',
                                               'StationMessageCode', 'StationMessageDescription', 'AssembleServiceState'])

        self.assembleServiceInterface = ServiceInterface(service_user=self.assemblyStation,
                                                         service=self.assembleService,
                                                         service_index=1)

        self.assembleService.setup_service(service_index=1, service_interface=self.assembleServiceInterface)

        self.assemblyStation.register_services(service_index=1, service_interface=self.assembleServiceInterface)
        # --------------------------------------------------------------------------------

        # starting the active objects :
        self.statusLED.start()
        self.active_objects.append(self.statusLED)
        self.blinker.start()
        self.active_objects.append(self.blinker)

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

        # complete button subscribers :
        sensorUaNode = self.server.nodes.objects.get_child(["2:Sensor", "2:InteractionSensor1"])
        self.completeButtonUaSubscriber = UaObjectSubscriber(self.server, sensorUaNode)

        self.completeButton.register_subscribers(topic="State",
                                                 who=self.completeButtonUaSubscriber,
                                                 callback=self.completeButtonUaSubscriber.update)

        self.completeButton.register_subscribers(topic="Value",
                                                 who=self.completeButtonUaSubscriber,
                                                 callback=self.completeButtonUaSubscriber.update)

        self.completeButton.register_subscribers(topic="State",
                                                 who=self.initService,
                                                 callback=self.initService.handle_event)

        self.completeButton.register_subscribers(topic="State",
                                                 who=self.assembleService,
                                                 callback=self.assembleService.handle_event)
        self.completeButton.register_subscribers(topic="Value",
                                                 who=self.assembleService,
                                                 callback=self.assembleService.handle_event)

        # abort buttonsubscribers :
        sensorUaNode = self.server.nodes.objects.get_child(["2:Sensor", "2:InteractionSensor2"])
        self.abortButtonUaSubscriber = UaObjectSubscriber(self.server, sensorUaNode)

        self.abortButton.register_subscribers(topic="State",
                                              who=self.abortButtonUaSubscriber,
                                              callback=self.abortButtonUaSubscriber.update)

        self.abortButton.register_subscribers(topic="Value",
                                              who=self.abortButtonUaSubscriber,
                                              callback=self.abortButtonUaSubscriber.update)

        self.abortButton.register_subscribers(topic="State",
                                              who=self.initService,
                                              callback=self.initService.handle_event)

        self.abortButton.register_subscribers(topic="State",
                                              who=self.assembleService,
                                              callback=self.assembleService.handle_event)
        self.abortButton.register_subscribers(topic="Value",
                                              who=self.assembleService,
                                              callback=self.assembleService.handle_event)


        # maintenance subscribers :
        maintenanceUaNode = self.server.nodes.objects.get_child(["2:Maintenance"])
        self.maintenanceStatusUaSubscriber = UaObjectSubscriber(self.server, maintenanceUaNode)

        self.initService.register_subscribers(topic="InitServiceState",
                                              who=self.maintenanceStatusUaSubscriber,
                                              callback=self.maintenanceStatusUaSubscriber.update)

        self.assembleService.register_subscribers(topic="AssembleServiceState",
                                                  who=self.maintenanceStatusUaSubscriber,
                                                  callback=self.maintenanceStatusUaSubscriber.update)


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

        self.assembleService.register_subscribers(topic="StationErrorCode",
                                              who=self.stationStateUaSubscriber,
                                              callback=self.stationStateUaSubscriber.update)

        self.assembleService.register_subscribers(topic="StationErrorDescription",
                                              who=self.stationStateUaSubscriber,
                                              callback=self.stationStateUaSubscriber.update)

        self.assembleService.register_subscribers(topic="StationMessageCode",
                                              who=self.stationStateUaSubscriber,
                                              callback=self.stationStateUaSubscriber.update)

        self.assembleService.register_subscribers(topic="StationMessageDescription",
                                              who=self.stationStateUaSubscriber,
                                              callback=self.stationStateUaSubscriber.update)


        self.assemblyStation.register_subscribers(topic="Ack",
                                                  who=self.initService,
                                                  callback=self.initService.handle_event)

        self.assemblyStation.register_subscribers(topic="Ack",
                                                  who=self.assembleService,
                                                  callback=self.assembleService.handle_event)

        self.assemblyStation.register_subscribers(topic="Ack",
                                                  who=self.completeButton,
                                                  callback=self.completeButton.handle_event)

        self.assemblyStation.register_subscribers(topic="Ack",
                                                  who=self.abortButton,
                                                  callback=self.abortButton.handle_event)

        self.assemblyStation.register_subscribers(topic="Ack",
                                                  who=self.statusLED,
                                                  callback=self.statusLED.handle_event)

        self.assemblyStation.register_subscribers(topic="Ack",
                                                  who=self.blinker,
                                                  callback=self.blinker.handle_event)


        self.revpiioDriver.handlesignalend(self.shutdown)

        self.logger.info("Registering handlers for inputs events...")
        self.revpiioDriver.io.input4.reg_event(self.input4_posedge_event, edge=revpimodio2.RISING)
        self.revpiioDriver.io.input4.reg_event(self.input4_negedge_event, edge=revpimodio2.FALLING)
        self.revpiioDriver.io.input5.reg_event(self.input5_posedge_event, edge=revpimodio2.RISING)
        self.revpiioDriver.io.input5.reg_event(self.input5_negedge_event, edge=revpimodio2.FALLING)

        self.server.start()
        self.logger.info("OPCUA server %s at %s has started", servername, endpoint)

        self.completeButton.start()
        self.active_objects.append(self.completeButton)
        self.abortButton.start()
        self.active_objects.append(self.abortButton)
        self.assemblyStation.start()
        self.active_objects.append(self.assemblyStation)
        self.initService.start()
        self.active_objects.append(self.initService)
        self.assembleService.start()
        self.active_objects.append(self.assembleService)
        self.connMonitor.start()
        self.active_objects.append(self.connMonitor)

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
        self.completeButton.stop()
        self.abortButton.stop()
        self.statusLED.led_off()
        self.statusLED.stop()
        self.initService.stop()
        self.assembleService.stop()
        self.assemblyStation.stop()
        self.connMonitor.stop()
        self.blinker.stop()
        self.server.stop()
        self.revpiioDriver.exit()

    def input4_posedge_event(self, ioname, iovalue):
        self.logger.debug("Input %s : Value %s", ioname, iovalue)
        posedge_event = events.SimpleSensorInputEvent(eventID=events.SimpleSensorInputEvents.PosEdge,
                                                      sender=self._name)
        self.completeButton.handle_event(event=posedge_event)

    def input4_negedge_event(self, ioname, iovalue):
        self.logger.debug("Input %s : Value %s", ioname, iovalue)

        self.logger.debug("Input %s : Value %s", ioname, iovalue)
        negedge_event = events.SimpleSensorInputEvent(eventID=events.SimpleSensorInputEvents.NegEdge,
                                                      sender=self._name)
        self.completeButton.handle_event(event=negedge_event)

    def input5_posedge_event(self, ioname, iovalue):
        self.logger.debug("Input %s : Value %s", ioname, iovalue)
        posedge_event = events.SimpleSensorInputEvent(eventID=events.SimpleSensorInputEvents.PosEdge,
                                                      sender=self._name)
        self.abortButton.handle_event(event=posedge_event)

    def input5_negedge_event(self, ioname, iovalue):
        self.logger.debug("Input %s : Value %s", ioname, iovalue)
        negedge_event = events.SimpleSensorInputEvent(eventID=events.SimpleSensorInputEvents.NegEdge,
                                                      sender=self._name)
        self.abortButton.handle_event(event=negedge_event)

    def input6_posedge_event(self, ioname, iovalue):
        self.logger.debug("Input %s : Value %s", ioname, iovalue)

    def input6_negedge_event(self, ioname, iovalue):
        self.logger.debug("Input %s : Value %s", ioname, iovalue)

    def conn_broken_event(self):
        self.assemblyStation.handle_event(event=self.noconn_event)

    def conn_alive_event(self):
        self.assemblyStation.handle_event(event=self.connok_event)

    def start(self):
        self.revpiioDriver.mainloop(blocking=False)
        self.logger.debug("RevPi driver has been started.")

        # Loop to do some work next to the event system. E.g. Switch on / off green part of LED A1
        while not self.revpiioDriver.exitsignal.is_set():
            self.revpiioDriver.core.a1green.value = not self.revpiioDriver.core.a1green.value

            for obj in self.active_objects:
                if not obj.is_alive():
                    self.assemblyStation.handle_event(event=self.fatal_error_event)
                    self.logger.info('Huston, we have a problem. The thread %s has stopped. Restart the hole thing... Sorry.', obj.name)

            self.revpiioDriver.exitsignal.wait(1.0)

def main():
    app = StationApp(config.STATION_CONFIG['stationName'])
    app.start()


if __name__ == '__main__':
    main()