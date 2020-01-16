import config

class StationErrorCodes(object):
    NoError = 0
    Estop = 0x8000
    InitServiceTimeout = 0x8001
    HomingServiceTimeout  = 0x8002
    ProvideDicehalfServiceTimeout = 0x8003
    RefillingServiceTimeout = 0x8004


class SensorErrorCodes(object):
    NoError = 0
    SensorTimeoutError = 0x0001
    SensorError2  = 0x0002
    SensorError3 = 0x0003


class ActuatorErrorCodes(object):
    NoError = 0
    MotorTimeoutError = 0x0101
    MotorError2  = 0x0102
    MotorError3 = 0x0103


class RackErrorCodes(object):
    NoError = 0
    RackTimeoutError = 0x0201
    RackErrorByDiceCounting = 0x0202
    RackNegDicehalfsNum = 0x0203
    RackEmptyDicehalfsNum = 0x0204
    RackDicehalfsNumMaximum = 0x0205
    NotEmptyRack = 0x0206
    WrongNumRackFull = 0x0207


class CarriageErrorCodes(object):
    NoError = 0
    CarriageMovingToRackTimeout = 0x0301
    CarriageMovingToDispatchTimeout  = 0x0302
    RackError3 = 0x0303


code_to_text = {
    0: ('NoError', 'There are no errors.'),

    0x8000: ('Estop', 'The safety switch was pressed.'),
    0x8001: ('InitServiceTimeout', 'The timeout has happened during the initialization service execution.'),
    0x8002: ('HomingServiceTimeout', 'The timeout has happened during the homing service execution.'),
    0x8003: ('ProvideDicehalfServiceTimeout', 'The timeout has happened during the provide-dicehalf-service execution.'),
    0x8004: ('RefillingServiceTimeout', 'The timeout has happened during the refilling-service execution.'),

    0x0001: ('SensorTimeout', 'The timeout has happened during the sensor work.'),
    0x0002: ('SensorError2', 'The sensor error 2.'),
    0x0003: ('SensorError3', 'The sensor error 3.'),

    0x0101: ('MotorTimeout', 'The timeout has happened by the motor.'),
    0x0102: ('MotorError2', 'The motor error 2.'),
    0x0103: ('MotorError3', 'The motor error 3.'),

    0x0201: ('RackTimeout', 'The timeout has happened at the rack.'),
    0x0202: ('RackErrorByDiceCounting', "The discrepancy in counting the dicefalfs, check the rack's top sensor. "),
    0x0203: ('RackNegDicehalfsNum', 'The dicehalfs number should be greater then zero.'),
    0x0204: ('RackEmptyDicehalfsNum', 'Wrong dicefalfs number. The rack is empty, if not, check the sensor.'),
    0x0205: ('RackDicehalfsNumMaximum', "The dicehalfs number should be less then rack's max capacity {0}.".format(config.STATION_CONFIG['rackMaxCapacity'])),
    0x0206: ('RackNotEmptyDicehalfsZero', 'Wrong dicefalfs number. The rack is not empty, if so, check the sensor.'),
    0x0207: ('WrongNumRackFull', 'Wrong dicefalfs number. The rack is full, if not, check the sensor.'),

    0x0301: ('CarriageMovingToRackTimeout', 'The timeout by the carriage moving to the rack. Check the carriage.'),
    0x0302: ('CarriageMovingToDispatchTimeout', 'The timeout by the carriage moving to the dispatch. Check the carriage.'),
    0x0303: ('CarriageError3', 'The Carriage error 3.')

}