import abc
from communication import events
from threading import Timer
from utils import error_codes, message_codes
import config
import json
import io

class RackState(metaclass=abc.ABCMeta):
    """ Abstract State class for a Rack SM """

    def __init__(self, isSubstate=False):
        self._isSubstate = isSubstate

    @property
    def isSubstate(self):
        return self._isSubstate

    @abc.abstractmethod
    def initialize(self):
        raise NotImplemented

    @abc.abstractmethod
    def error(self):
        raise NotImplemented

    @abc.abstractmethod
    def acknowledge(self):
        raise NotImplemented

    @abc.abstractmethod
    def timeout(self):
        raise NotImplemented

    @abc.abstractmethod
    def provide_material(self):
        pass
		
    @abc.abstractmethod
    def movement_in_progress(self):
        pass	

    @abc.abstractmethod
    def store_material(self):
        pass
		
    @abc.abstractmethod
    def movement_confirmed(self):
        pass
		
    @abc.abstractmethod
    def update(self):
        raise NotImplemented

    def enter_action(self):
        pass

    def exit_action(self):
        pass


class NotInitialized(RackState):
    """ Concrete State class for representing NotInitialized State"""

    def __init__(self, rack_sm, rack, super_sm=None, isSubstate=False):
        super(NotInitialized, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._rack = rack
        self._rack_sm = rack_sm
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._rack.logger.debug("Entering the %s state", self.name)
        self._rack.publisher.publish(topic="State", value="NotInitialized", sender=self._rack.name)

    def initialize(self):
        self._rack.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._rack_sm.set_state(self._rack_sm.initialization_state)

    def provide_material(self):
        self._rack.logger.debug("%s event in %s state", self.provide_material.__name__, self.name)
		
    def movement_in_progress(self, action=None):
        self._rack.logger.debug("%s event in %s state", self.movement_in_progress.__name__, self.name)	
		
    def store_material(self, parameters_list, action=None):
        self._rack.logger.debug("%s event in %s state", self.store_material.__name__, self.name)
		
    def movement_confirmed(self, action=None):
        self._rack.logger.debug("%s event in %s state", self.movement_confirmed.__name__, self.name)
		
    def error(self):
        self._rack.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._rack_sm.set_state(self._rack_sm.error_state)

    def acknowledge(self):
        self._rack.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._rack.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def update(self):
        self._rack.logger.debug("%s event in %s state", self.update.__name__, self.name)


class Initialization(RackState):
    """ Concrete State class for representing Initialization State. This is a composite state. """

    def __init__(self, rack_sm, rack, super_sm=None, isSubstate=False):
        super(Initialization, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._rack = rack
        self._rack_sm = rack_sm
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._rack.logger.debug("Entering the %s state", self.name)
        self._rack.publisher.publish(topic="State", value="Initialized", sender=self._rack.name)

        # Load material storage data into a list from json-file
        self._storagefilename = ('/home/pi/station_modular_storage_diceplates/activeobjects/storagerack/' + self._rack.name + '.json')
		
		# handling if not available
        with open(self._storagefilename) as data_file:
            data_loaded = json.load(data_file)
			
        data_file.close
		
		# Update material storage data into the active object
        self._rack.diceplate_color1=data_loaded["PlateColor1"]
        self._rack.diceplate_color1_quantity=data_loaded["PlateColor1Quantity"]
        self._rack.diceplate_color2=data_loaded["PlateColor2"]
        self._rack.diceplate_color2_quantity=data_loaded["PlateColor2Quantity"]
        self._rack.diceplate_color3=data_loaded["PlateColor3"]
        self._rack.diceplate_color3_quantity=data_loaded["PlateColor3Quantity"]

        # Publish colors 1-3 and the corresponding total quantity to OPCUA-Server
        self._rack.publisher.publish(topic="PlateColor1", value=self._rack.diceplate_color1, sender=self._rack.name)
        self._rack.publisher.publish(topic="QuantityOfPlateColor1", value=self._rack.diceplate_color1_quantity, sender=self._rack.name)
        self._rack.publisher.publish(topic="PlateColor2", value=self._rack.diceplate_color2, sender=self._rack.name)
        self._rack.publisher.publish(topic="QuantityOfPlateColor2", value=self._rack.diceplate_color2_quantity, sender=self._rack.name)		
        self._rack.publisher.publish(topic="PlateColor3", value=self._rack.diceplate_color3, sender=self._rack.name)
        self._rack.publisher.publish(topic="QuantityOfPlateColor3", value=self._rack.diceplate_color3_quantity, sender=self._rack.name)		
		
        self._rack.logger.debug("Material storage data loaded from JSON-File %s", self._storagefilename)
		
	# Publish in same state provides same initialized event
    def initialize(self):
        self._rack.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._rack.publisher.publish(topic="State", value="Initialized", sender=self._rack.name)
		
    def provide_material(self, parameters_list):
		
		# First set the current used parameters list to the service object,
        self._rack_sm.set_parameters(parameters_list)
		
        # Check if the requested color is available in the current storageracks
        if str(self._rack.diceplate_color1) == parameters_list[1]:
		
            # Check of diceplate color 1 quantity
            if (self._rack.diceplate_color1_quantity - 1) >= 0:
			
                self._rack.logger.debug("%s event in %s state", self.provide_material.__name__, self.name)
                self._rack_sm.set_state(self._rack_sm._provide_material_state)
				
            else:
                self._rack_sm.publish_error(error_codes.RackErrorCodes.RackDiceplateNumMinimum)
                self._rack_sm.set_state(self._rack_sm._error_state)
				
        elif str(self._rack.diceplate_color2) == parameters_list[1]:
		
            # Check of diceplate color 2 quantity
            if (self._rack.diceplate_color2_quantity - 1) >= 0:
				
                self._rack.logger.debug("%s event in %s state", self.provide_material.__name__, self.name)
                self._rack_sm.set_state(self._rack_sm._provide_material_state)	

            else:
                self._rack_sm.publish_error(error_codes.RackErrorCodes.RackDiceplateNumMinimum)
                self._rack_sm.set_state(self._rack_sm._error_state)				
				
        elif str(self._rack.diceplate_color3) == parameters_list[1]:	
		
            # Check of diceplate color 3 quantity
            if (self._rack.diceplate_color3_quantity - 1) >= 0:
                	
                self._rack.logger.debug("%s event in %s state", self.provide_material.__name__, self.name)
                self._rack_sm.set_state(self._rack_sm._provide_material_state)	

            else:
                self._rack_sm.publish_error(error_codes.RackErrorCodes.RackDiceplateNumMinimum)
                self._rack_sm.set_state(self._rack_sm._error_state)				
				
        else:
            self._rack_sm.publish_error(error_codes.RackErrorCodes.WrongDiceplateColor)
            self._rack_sm.set_state(self._rack_sm._error_state)

    def movement_in_progress(self, action=None):
        self._rack.logger.debug("%s event in %s state", self.movement_in_progress.__name__, self.name)	

		# The method must differ between two points in time (Process Start / Finish)
        if action == "Start":
            self._led_blinkerevents = events.BlinkerEvents.Start
            self._rgbledevents = events.RGBLEDInputEvents.Red
			 
        else:
            self._led_blinkerevents = events.BlinkerEvents.Stop
            self._rgbledevents = events.RGBLEDInputEvents.Off
			
        # If presence if invalid, set the corresponding led to red (storagerack without state ProvideMaterial)
        self._presencevalid_led_event = events.RGBLEDInputEvent(self._rgbledevents, self._rack.name)
        self._rack._rgbLed.handle_event(event=self._presencevalid_led_event)
	
        self._presencevalid_blinker_event = events.BlinkerEvent(self._led_blinkerevents, self._rack.name)
        self._rack._blinker.handle_event(event=self._presencevalid_blinker_event)
	
    def store_material(self, parameters_list, action=None):
        self._rack.logger.debug("%s event in %s state", self.store_material.__name__, self.name)	

		# First set the current used parameters list to the service object,
        self._rack_sm.set_parameters(parameters_list)
		
        if action == "Refill":

            # Validation if the refill service-request is valid to the maximum capacity of the storagerack.		
            if ((self._rack.diceplate_color1_quantity + int(parameters_list[2])) <= (config.STATION_CONFIG['storageRackMaxCapacity'])) and ((self._rack.diceplate_color2_quantity + int(parameters_list[4])) <= (config.STATION_CONFIG['storageRackMaxCapacity'])) and ((self._rack.diceplate_color3_quantity + int(parameters_list[6])) <= (config.STATION_CONFIG['storageRackMaxCapacity'])): 
			
                self._rack.logger.debug("%s event in %s state", self.store_material.__name__, self.name)
                self._rack_sm.set_state(self._rack_sm._refill_material_state)

            else:
                self._rack_sm.publish_error(error_codes.RackErrorCodes.RackDiceplateNumMaximum)
                self._rack_sm.set_state(self._rack_sm._error_state)
				
        elif action == "Reset":

            # Validation if the reset service-request is valid to the maximum capacity of the storagerack.
            if (int(parameters_list[2]) <= (config.STATION_CONFIG['storageRackMaxCapacity'])) and (int(parameters_list[4]) <= (config.STATION_CONFIG['storageRackMaxCapacity'])) and (int(parameters_list[6]) <= (config.STATION_CONFIG['storageRackMaxCapacity'])):
			
                self._rack.logger.debug("%s event in %s state", self.store_material.__name__, self.name)
                self._rack_sm.set_state(self._rack_sm._reset_material_state)
			
            else:
                self._rack_sm.publish_error(error_codes.RackErrorCodes.RackDiceplateNumMaximum)
                self._rack_sm.set_state(self._rack_sm._error_state)
			
    def movement_confirmed(self, action=None):
        self._rack.logger.debug("%s event in %s state", self.movement_confirmed.__name__, self.name)		
		
    def error(self):
        self._rack.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._rack_sm.set_state(self._rack_sm.error_state)

    def acknowledge(self):
        self._rack.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._rack.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def update(self):
        self._rack.logger.debug("%s event in %s state", self.update.__name__, self.name)


class ProvideMaterial(RackState):
    """ Concrete State class for representing RackFull State"""

    def __init__(self, rack_sm, rack, super_sm=None, isSubstate=False):
        super(ProvideMaterial, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._rack = rack
        self._rack_sm = rack_sm
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._rack.logger.debug("Entering the %s state", self.name)
		
		# Get the actual parameters setting
        self._parameters_list = self._rack_sm.parameters_list()
		
		# Activate storage box rgbled to show that an interaction should be done
        providematerial_led_event = events.RGBLEDInputEvent(events.RGBLEDInputEvents.Yellow, self._rack.name)
        self._rack._rgbLed.handle_event(event=providematerial_led_event)

		# Start blinker event in state provide material
        self._presencevalid_blinker_event = events.BlinkerEvent(events.BlinkerEvents.Start, self._rack.name)
        self._rack._blinker.handle_event(event=self._presencevalid_blinker_event)

    def provide_material(self):
        self._rack.logger.debug("%s event in %s state", self.provide_material.__name__, self.name)
		
    def initialize(self):
        self._rack.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._rack_sm.set_state(self._rack_sm.initialization_state)

    def error(self):
        self._rack.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._rack_sm.set_state(self._rack_sm.error_state)

    def acknowledge(self):
        self._rack.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._rack.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def movement_in_progress(self, action=None):
        self._rack.logger.debug("%s event in %s state", self.movement_in_progress.__name__, self.name)

		# The method must differ between two points in time (Process Start / Finish)
        if action == "Start":
            self._rgbledevents = events.RGBLEDInputEvents.Green
			
        else:
            self._rgbledevents = events.RGBLEDInputEvents.Off

		# Stop blinker event before changing led value
        self._presencevalid_blinker_event = events.BlinkerEvent(events.BlinkerEvents.Stop, self._rack.name)
        self._rack._blinker.handle_event(event=self._presencevalid_blinker_event)
			
        # If presence if valid, set the corresponding led to green
        self._presencevalid_led_event = events.RGBLEDInputEvent(self._rgbledevents, self._rack.name)
        self._rack._rgbLed.handle_event(event=self._presencevalid_led_event)			
		
        # Optional: Switch this action into an own state in this state machine (own class MaterialWithdrawal)
        if action == "Finish":

            # Get the actual parameters setting
            self._parameters_list = self._rack_sm.parameters_list()
		
            # Check which color has been requested to provide it from the storagerack
            if str(self._rack.diceplate_color1) == self._parameters_list[1]:	
			
                self._rack.logger.debug("Provide color %s diceplate quantity &s with quantity 1", self._parameters_list[1])                
                self._rack.diceplate_color1_quantity = (self._rack.diceplate_color1_quantity - 1)
								
                # Publish total quantity of color 1 to OPCUA-Server
                self._rack.publisher.publish(topic="QuantityOfPlateColor1", value=self._rack.diceplate_color1_quantity, sender=self._rack.name)

            # Check which color has been requested to provide it from the storagerack
            elif str(self._rack.diceplate_color2) == self._parameters_list[1]:	
			
                self._rack.logger.debug("Provide color %s diceplate quantity &s with quantity 1", self._parameters_list[1])                
                self._rack.diceplate_color2_quantity = (self._rack.diceplate_color2_quantity - 1)
								
                # Publish total quantity of color 2 to OPCUA-Server
                self._rack.publisher.publish(topic="QuantityOfPlateColor2", value=self._rack.diceplate_color2_quantity, sender=self._rack.name)				

            # Check which color has been requested to provide it from the storagerack
            elif str(self._rack.diceplate_color3) == self._parameters_list[1]:	
			
                self._rack.logger.debug("Provide color %s diceplate quantity &s with quantity 1", self._parameters_list[1])                
                self._rack.diceplate_color3_quantity = (self._rack.diceplate_color3_quantity - 1)
								
                # Publish total quantity of color 3 to OPCUA-Server
                self._rack.publisher.publish(topic="QuantityOfPlateColor3", value=self._rack.diceplate_color3_quantity, sender=self._rack.name)		
				
            # Save material storage data into a list for export them into json
            self._storagedata = {'PlateColor1': self._rack.diceplate_color1,
                                 'PlateColor1Quantity': self._rack.diceplate_color1_quantity,
                                 'PlateColor2': self._rack.diceplate_color2,
                                 'PlateColor2Quantity': self._rack.diceplate_color2_quantity,
                                 'PlateColor3': self._rack.diceplate_color3,
                                 'PlateColor3Quantity': self._rack.diceplate_color3_quantity}
			
            # Save the storage data in an own storage-rack json-file
            try:
                self._to_unicode = unicode
            except NameError:
                self._to_unicode = str
				
            self._storagefilename = ('/home/pi/station_modular_storage_diceplates/activeobjects/storagerack/' + self._rack.name + '.json')
			
            with io.open(self._storagefilename, 'w', encoding='utf8') as outfile:
                self.datastream = json.dumps(self._storagedata,
                                             indent=4, sort_keys=True,
                                             separators=(',', ': '), ensure_ascii=False)
                outfile.write(self._to_unicode(self.datastream))
            outfile.close				
				
			# Note: Broadcast event to all subscribed objects
            self._rack.publisher.publish(topic="State", value="MaterialWithdrawalDone", sender=self._rack.name)
            self._rack_sm.set_state(self._rack_sm.initialization_state)

    def store_material(self, parameters_list, action=None):
        self._rack.logger.debug("%s event in %s state", self.store_material.__name__, self.name)		
		
    def movement_confirmed(self, action=None):
        self._rack.logger.debug("%s event in %s state", self.movement_confirmed.__name__, self.name)		
		
    def update(self):
        self._rack.logger.debug("%s event in %s state", self.update.__name__, self.name)
		
		
class RefillMaterial(RackState):
    """ Concrete State class for representing RefillMaterial State"""

    def __init__(self, rack_sm, rack, super_sm=None, isSubstate=False):
        super(RefillMaterial, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._rack = rack
        self._rack_sm = rack_sm
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._rack.logger.debug("Entering the %s state", self.name)
		
		# Get the actual parameters setting
        self._parameters_list = self._rack_sm.parameters_list()
		
		# Activate storage box rgbled to show that an interaction should be done
        storagematerial_led_event = events.RGBLEDInputEvent(events.RGBLEDInputEvents.Yellow, self._rack.name)
        self._rack._rgbLed.handle_event(event=storagematerial_led_event)
		
		# Start blinker event in state reset / refill material
        self._presencevalid_blinker_event = events.BlinkerEvent(events.BlinkerEvents.Start, self._rack.name)
        self._rack._blinker.handle_event(event=self._presencevalid_blinker_event)
		
    def provide_material(self):
        self._rack.logger.debug(("%s event in %s state", self.provide_material.__name__, self.name))
		
    def initialize(self):
        self._rack.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._rack_sm.set_state(self._rack_sm.initialization_state)
		
    def movement_in_progress(self, action=None):
        self._rack.logger.debug("%s event in %s state", self.movement_in_progress.__name__, self.name)

    def store_material(self, parameters_list, action=None):
        self._rack.logger.debug("%s event in %s state", self.store_material.__name__, self.name)		
		
    def movement_confirmed(self, action=None):
        self._rack.logger.debug("%s event in %s state", self.movement_confirmed.__name__, self.name)	
		
		# Refill service has been finished successful
        if action == "Finish":
		
	        # Get the actual parameters setting
            self._parameters_list = self._rack_sm.parameters_list()

            if  str(self._rack.diceplate_color1) == self._parameters_list[1] and str(self._rack.diceplate_color2) == str(self._parameters_list[3]) and str(self._rack.diceplate_color3) == str(self._parameters_list[5]):
                
				# Refill of quantity of diceplate color 1
                #self._rack.logger.debug("Refill color %s diceplate quantity &s with new quantity %s", self._parameters_list[1], str(self._rack.diceplate_color1_quantity), str(self._parameters_list[2]))                
                self._rack.diceplate_color1_quantity = (self._rack.diceplate_color1_quantity + int(self._parameters_list[2]))
								
                # Publish total quantity of color 1 to OPCUA-Server
                self._rack.publisher.publish(topic="QuantityOfPlateColor1", value=self._rack.diceplate_color1_quantity, sender=self._rack.name)
			
                # Refill of quantity of diceplate color 2
                #self._rack.logger.debug("Refill color %s diceplate quantity &s with new quantity %s", self._parameters_list[3], str(self._rack.diceplate_color2_quantity), str(self._parameters_list[4]))                
                self._rack.diceplate_color2_quantity = (self._rack.diceplate_color2_quantity + int(self._parameters_list[4]))
			
                # Publish total quantity of color 2 to OPCUA-Server
                self._rack.publisher.publish(topic="QuantityOfPlateColor2", value=self._rack.diceplate_color2_quantity, sender=self._rack.name)

                # Refill of quantity of diceplate color 3
                #self._rack.logger.debug("Refill color %s diceplate quantity &s with new quantity %s", self._parameters_list[5], str(self._rack.diceplate_color3_quantity), str(self._parameters_list[6]))               
                self._rack.diceplate_color3_quantity = (self._rack.diceplate_color3_quantity + int(self._parameters_list[6]))
				
                # Publish total quantity of color 3 to OPCUA-Server
                self._rack.publisher.publish(topic="QuantityOfPlateColor3", value=self._rack.diceplate_color3_quantity, sender=self._rack.name)
					
                # Save material storage data into a list for export them into json
                self._storagedata = {'PlateColor1': self._rack.diceplate_color1,
                                     'PlateColor1Quantity': self._rack.diceplate_color1_quantity,
                                     'PlateColor2': self._rack.diceplate_color2,
                                     'PlateColor2Quantity': self._rack.diceplate_color2_quantity,
                                     'PlateColor3': self._rack.diceplate_color3,
                                     'PlateColor3Quantity': self._rack.diceplate_color3_quantity}
			
                # Save the storage data in an own storage-rack json-file
                try:
                    self._to_unicode = unicode
                except NameError:
                    self._to_unicode = str
				
                self._storagefilename = ('/home/pi/station_modular_storage_diceplates/activeobjects/storagerack/' + self._rack.name + '.json')
			
                with io.open(self._storagefilename, 'w', encoding='utf8') as outfile:
                    self.datastream = json.dumps(self._storagedata,
                                                 indent=4, sort_keys=True,
                                                 separators=(',', ': '), ensure_ascii=False)
                    outfile.write(self._to_unicode(self.datastream))
                outfile.close
				
                self._rack.logger.debug("Material storage data saved into JSON-File %s", self._storagefilename)		

		    # Refill service has been cancelled
            else:
                self._rack_sm.publish_message(message_codes.StationMessageCodes.CancelJob)
                self._rack.logger.debug("Refill diceplate quantity cancelled")

		# Stop blinker event before changing led value
        self._presencevalid_blinker_event = events.BlinkerEvent(events.BlinkerEvents.Stop, self._rack.name)
        self._rack._blinker.handle_event(event=self._presencevalid_blinker_event)
			
        # Switch led value to off
        movement_confirmed_led_event = events.RGBLEDInputEvent(events.RGBLEDInputEvents.Off, self._rack.name)
        self._rack._rgbLed.handle_event(event=movement_confirmed_led_event)
		
		# Note: Broadcast event to all subscribed objects
        self._rack.publisher.publish(topic="State", value="MaterialRefillDone", sender=self._rack.name)
		
        self._rack_sm.set_state(self._rack_sm.initialization_state)
		
    def error(self):
        self._rack.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._rack_sm.set_state(self._rack_sm.error_state)

    def acknowledge(self):
        self._rack.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._rack.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def update(self):
        self._rack.logger.debug("%s event in %s state", self.update.__name__, self.name)

		
class ResetMaterial(RackState):
    """ Concrete State class for representing ResetMaterial State"""

    def __init__(self, rack_sm, rack, super_sm=None, isSubstate=False):
        super(ResetMaterial, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._rack = rack
        self._rack_sm = rack_sm
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._rack.logger.debug("Entering the %s state", self.name)

		# Activate storage box rgbled to show that an interaction should be done
        #storagematerial_led_event = events.RGBLEDInputEvent(events.RGBLEDInputEvents.Yellow, self._rack.name)
        #self._rack._rgbLed.handle_event(event=storagematerial_led_event)
		
		# Start blinker event in state reset / refill material
        #self._presencevalid_blinker_event = events.BlinkerEvent(events.BlinkerEvents.Start, self._rack.name)
        #self._rack._blinker.handle_event(event=self._presencevalid_blinker_event)
		
		# Direct reset of the quantity
        self.movement_confirmed(action="Finish")
		
    def provide_material(self):
        self._rack.logger.debug(("%s event in %s state", self.provide_material.__name__, self.name))
		
    def initialize(self):
        self._rack.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._rack_sm.set_state(self._rack_sm.initialization_state)
		
    def movement_in_progress(self, action=None):
        self._rack.logger.debug("%s event in %s state", self.movement_in_progress.__name__, self.name)

    def store_material(self, parameters_list, action=None):
        self._rack.logger.debug("%s event in %s state", self.store_material.__name__, self.name)		
		
    def movement_confirmed(self, action=None):
        self._rack.logger.debug("%s event in %s state", self.movement_confirmed.__name__, self.name)	
		
		# Reset service has been finished successful		
        if action == "Finish":
		
	        # Get the actual parameters setting
            self._parameters_list = self._rack_sm.parameters_list()
	
            # Reset of diceplate color 1 and its corresponding quantity
            self._rack.diceplate_color1 = self._parameters_list[1]
            self._rack.diceplate_color1_quantity = int(self._parameters_list[2])
            self._rack.logger.debug("Reset %s diceplate quantity with value %s", self._parameters_list[1], self._parameters_list[2])
            
            # Publish color 1 and the corresponding total quantity to OPCUA-Server
            self._rack.publisher.publish(topic="PlateColor1", value=self._rack.diceplate_color1, sender=self._rack.name)
            self._rack.publisher.publish(topic="QuantityOfPlateColor1", value=self._rack.diceplate_color1_quantity, sender=self._rack.name)			
			
            # Reset of diceplate color 2 and its corresponding quantity
            self._rack.diceplate_color2 = self._parameters_list[3]
            self._rack.diceplate_color2_quantity = int(self._parameters_list[4])
            self._rack.logger.debug("Reset %s diceplate quantity with value %s", self._parameters_list[3], self._parameters_list[4])

            # Publish color 2 and the corresponding total quantity to OPCUA-Server
            self._rack.publisher.publish(topic="PlateColor2", value=self._rack.diceplate_color2, sender=self._rack.name)
            self._rack.publisher.publish(topic="QuantityOfPlateColor2", value=self._rack.diceplate_color2_quantity, sender=self._rack.name)

            # Reset of diceplate color 3 and its corresponding quantity			
            self._rack.diceplate_color3 = self._parameters_list[5]
            self._rack.diceplate_color3_quantity = int(self._parameters_list[6])
            self._rack.logger.debug("Reset %s diceplate quantity with value %s", self._parameters_list[5], self._parameters_list[6])

            # Publish color 3 and the corresponding total quantity to OPCUA-Server
            self._rack.publisher.publish(topic="PlateColor3", value=self._rack.diceplate_color3, sender=self._rack.name)
            self._rack.publisher.publish(topic="QuantityOfPlateColor3", value=self._rack.diceplate_color3_quantity, sender=self._rack.name)			
				
            # Save material storage data into a list for export them into json
            self._storagedata = {'PlateColor1': self._rack.diceplate_color1,
                                 'PlateColor1Quantity': self._rack.diceplate_color1_quantity,
                                 'PlateColor2': self._rack.diceplate_color2,
                                 'PlateColor2Quantity': self._rack.diceplate_color2_quantity,
                                 'PlateColor3': self._rack.diceplate_color3,
                                 'PlateColor3Quantity': self._rack.diceplate_color3_quantity}
			
            # Save the storage data in an own storage-rack json-file
            try:
                self._to_unicode = unicode
            except NameError:
                self._to_unicode = str
				
            self._storagefilename = ('/home/pi/station_modular_storage_diceplates/activeobjects/storagerack/' + self._rack.name + '.json')
			
            with io.open(self._storagefilename, 'w', encoding='utf8') as outfile:
                self.datastream = json.dumps(self._storagedata,
                                             indent=4, sort_keys=True,
                                             separators=(',', ': '), ensure_ascii=False)
                outfile.write(self._to_unicode(self.datastream))
            outfile.close
				
            self._rack.logger.debug("Material storage data saved into JSON-File %s", self._storagefilename)		
		
		# Reset service has been cancelled
        else:
            self._rack_sm.publish_message(message_codes.StationMessageCodes.CancelJob)
            self._rack.logger.debug("Reset diceplate quantity cancelled")

		# Stop blinker event before changing led value
        self._presencevalid_blinker_event = events.BlinkerEvent(events.BlinkerEvents.Stop, self._rack.name)
        self._rack._blinker.handle_event(event=self._presencevalid_blinker_event)
			
        # Switch led value to off
        movement_confirmed_led_event = events.RGBLEDInputEvent(events.RGBLEDInputEvents.Off, self._rack.name)
        self._rack._rgbLed.handle_event(event=movement_confirmed_led_event)
		
		# Publish event to all subscribed objects (Broadcast)
        self._rack.publisher.publish(topic="State", value="MaterialResetDone", sender=self._rack.name)
		
        self._rack_sm.set_state(self._rack_sm.initialization_state)
		
    def error(self):
        self._rack.logger.debug("%s event in %s state", self.error.__name__, self.name)
        self._rack_sm.set_state(self._rack_sm.error_state)

    def acknowledge(self):
        self._rack.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)

    def timeout(self):
        self._rack.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def update(self):
        self._rack.logger.debug("%s event in %s state", self.update.__name__, self.name)


class Error(RackState):
    """ Concrete State class for representing Error State"""

    def __init__(self, rack_sm, rack, super_sm=None, isSubstate=False):
        super(Error, self).__init__(isSubstate)
        self._name = self.__class__.__name__

        self._rack = rack
        self._rack_sm = rack_sm
        self._super_sm = super_sm  # super or enclosing state

    @property
    def name(self):
        return self._name

    @property
    def super_sm(self):
        return self._super_sm

    def enter_action(self):
        self._rack.publisher.publish(topic="State", value="Error", sender=self._rack.name)

    def initialize(self):
        self._rack.logger.debug("%s event in %s state", self.initialize.__name__, self.name)
        self._rack_sm.set_state(self._rack_sm.initialization_state)	
		
    def provide_material(self):
        self._rack.logger.debug(("%s event in %s state", self.provide_material.__name__, self.name))
		
    def movement_in_progress(self, action=None):
        self._rack.logger.debug("%s event in %s state", self.movement_in_progress.__name__, self.name)

    def store_material(self, parameters_list, action=None):
        self._rack.logger.debug("%s event in %s state", self.store_material.__name__, self.name)	
		
    def movement_confirmed(self, action=None):
        self._rack.logger.debug("%s event in %s state", self.movement_confirmed.__name__, self.name)	
		
    def error(self):
        self._rack.logger.debug("%s event in %s state", self.error.__name__, self.name)

    def acknowledge(self):
        self._rack.logger.debug("%s event in %s state", self.acknowledge.__name__, self.name)
        self._rack_sm.set_state(self._rack_sm._initialization_state)

    def timeout(self):
        self._rack.logger.debug("%s event in %s state", self.timeout.__name__, self.name)

    def update(self):
        self._rack.logger.debug("%s event in %s state", self.update.__name__, self.name)


class RackStateMachine(object):
    """ Context class for the Rack's state machine """
    def __init__(self, rack):
        self._name = self.__class__.__name__

        self._notinitialized_state = NotInitialized(self, rack) # an instance for tracking current state
        self._initialization_state = Initialization(self, rack)
        self._provide_material_state = ProvideMaterial(self, rack)
        self._refill_material_state = RefillMaterial(self, rack)
        self._reset_material_state = ResetMaterial(self, rack)
		
        self._error_state = Error(self, rack)
        self._parameters_list = ("")

        self._rack = rack

        self._current_state = self._notinitialized_state
        self.set_state(self._current_state)

# properties
    @property
    def name(self):
        return self._name

    @property
    def current_state(self):
        return self._current_state

    @property
    def notinitialized_state(self):
        return self._notinitialized_state

    @property
    def initialization_state(self):
        return self._initialization_state

    @property
    def provide_material_state(self):
        return self._provide_material_state

    @property
    def refill_material_state(self):
        return self._provide_material_state		
		
    @property
    def reset_material_state(self):
        return self._provide_material_state	
		
    def set_parameters(self, parameters_list):
        self._rack.logger.debug("Setting parameters %s to service %s", parameters_list, self._name)
        self._parameters_list = parameters_list

    def parameters_list(self):
        return self._parameters_list

    @property
    def error_state(self):
        return self._error_state

    def set_state(self, state):
        self._rack.logger.debug("Switching from state %s to state %s", self.current_state.name, state.name)

        if not self.current_state.isSubstate and state.isSubstate:
            # only enter action of the substate should be called
            self._current_state = state
            self._current_state.enter_action()
        elif self.current_state.isSubstate and not state.isSubstate:
            # first exit-action in current sub-state, then exit-action in super-state,
            # then set new state, at last enter-action in new state
            self._current_state.exit_action()
            self._current_state.super_sm.exit_action()
            self._current_state = state
            self._current_state.enter_action()
        else:
            # normal case: exit action, new state, enter action
            self._current_state.exit_action()
            self._current_state = state
            self._current_state.enter_action()

    def timeout_handler(self, *args, **kwargs):
        self._rack.handle_event(*args, **kwargs)

    def publish_error(self, error_code):
        self._rack.publisher.publish(topic="StationErrorCode",
                                     value=hex(error_code),
                                     sender=self._rack.name)
        self._rack.publisher.publish(topic="StationErrorDescription",
                                     value=error_codes.code_to_text[error_code],
                                     sender=self._rack.name)

    def publish_message(self, message_code):
        self._rack.publisher.publish(topic="StationMessageCode",
                                     value=hex(message_code),
                                     sender=self._rack.name)
        self._rack.publisher.publish(topic="StationMessageDescription",
                                     value=message_codes.code_to_text[message_code],
                                     sender=self._rack.name)
			
    def dispatch(self, *args, **kwargs):

        self._rack.logger.debug("%s has received a message: %s", self.name, kwargs)

        try:
            # topics coming from the publishers
            topic = kwargs["topic"]
            value = kwargs["value"]
            sender = kwargs["sender"]
			
			# Note: Matches-Function and state
            if sender == self._rack._presenceSensor.name:
			    
                if topic == "Value":
				
                    if value:
                        self._current_state.movement_in_progress(action="Start")
                    else:
                        self._current_state.movement_in_progress(action="Finish")

            elif sender == "InteractionSensor1":
			
                if topic == "Value":
                    if value:
                        self._current_state.movement_confirmed(action="Finish")
						
            elif sender == "InteractionSensor2":
			
                if topic == "Value":
                    if value:
                        self._current_state.movement_confirmed(action="Cancel")
						
            elif sender == "Station":

                if topic == "Ack":
                    if value:
                        self._current_state.acknowledge()
                    else:
                        pass

        except KeyError:
            event = kwargs["event"]

            if event.eventID == self._rack.input_events.eventIDs.Initialize:  # this a part of the service generic interface
                self._current_state.initialize()
            
			# Call of provide_material is intended for status initialized
            elif event.eventID == self._rack.input_events.eventIDs.ProvideMaterial:  
                self._current_state.provide_material(parameters_list=event.parameters_list)
				
            # Call of refill_material is intended for status initialized
            elif event.eventID == self._rack.input_events.eventIDs.RefillMaterial: 
                self._current_state.store_material(parameters_list=event.parameters_list, action="Refill")
				
            # Call of reset_material is intended for status initialized
            elif event.eventID == self._rack.input_events.eventIDs.ResetMaterial: 
                self._current_state.store_material(parameters_list=event.parameters_list, action="Reset")
				
            elif event.eventID == self._rack.input_events.eventIDs.Ack:
                self._current_state.acknowledge()
				
            elif event.eventID == self._rack.input_events.eventIDs.Update:
                self._current_state.update()
            else:
                self._station.logger.debug("Unknown event : %s", event)
