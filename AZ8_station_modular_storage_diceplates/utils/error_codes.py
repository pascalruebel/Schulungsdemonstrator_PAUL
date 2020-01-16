import config

class StationErrorCodes(object):
    NoError = 0
    InitServiceTimeout = 0x8001
    ProvideDiceplateServiceTimeout = 0x8002
    StorageDiceplateServiceTimeout = 0x8003

class SensorErrorCodes(object):
    NoError = 0
    SensorTimeoutError = 0x0001
    SensorError2  = 0x0002
    SensorError3 = 0x0003

class ActuatorErrorCodes(object):
    NoError = 0
    RgbLedTimeoutError = 0x0101
    RgbLedError2  = 0x0102
    RgbLedError3 = 0x0103

class RackErrorCodes(object):
    NoError = 0
    RackTimeout = 0x0201
    RackNegDiceplateNum = 0x0202 #If less quantity than 0
    RackEmptyDiceplateNum = 0x0203
    RackDiceplateNumMaximum = 0x0204 #If more quantity than max
    RackDiceplateNumMinimum = 0x0205
    WrongNumRackFull = 0x0206
    WrongDiceplateColor = 0x0207

code_to_text = {

    0: ('NoError', 'There are no errors.'),

    0x8000: ('Estop', 'The safety switch was pressed.'),
    0x8001: ('InitServiceTimeout', 'The timeout has happened during the initialization service execution.'),
    0x8002: ('ProvideDiceplateServiceTimeout', 'The timeout has happened during the provide-diceplate-service execution.'),
    0x8004: ('StorageDiceplateServiceTimeout', 'The timeout has happened during the storage-diceplate-service execution.'),

    0x0001: ('SensorTimeout', 'The timeout has happened during the sensor work.'),
    0x0002: ('SensorError2', 'The sensor error 2.'),
    0x0003: ('SensorError3', 'The sensor error 3.'),

    0x0101: ('RgbLedTimeout', 'The timeout has happened by the rgbled.'),
    0x0102: ('RgbLedError2', 'The rgbled error 2.'),
    0x0103: ('RgbLedError3', 'The rgbled error 3.'),

    0x0201: ('RackTimeout', 'The timeout has happened at the storaerack.'),
    0x0202: ('RackNegDiceplateNum', 'The diceplates number should be greater then zero.'),
    0x0203: ('RackEmptyDiceplateNum', 'Wrong diceplates number. The rack is empty.'),
    0x0204: ('RackDiceplateNumMaximum', "The diceplates number should be less then rack's max capacity {0}.".format(config.STATION_CONFIG['storageRackMaxCapacity'])),
    0x0205: ('RackDiceplateNumMinimum', 'The requested diceplate quantity for the material will lead to an negative storagerack quantity.'),
    0x0206: ('WrongNumRackFull', 'Wrong diceplates number. The rack is full.'),
    0x0207: ('WrongDiceplateColor', 'Wrong diceplates color. The color is not available.')
	
}