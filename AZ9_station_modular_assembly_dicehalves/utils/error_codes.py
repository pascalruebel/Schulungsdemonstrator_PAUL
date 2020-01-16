
class StationErrorCodes(object):
    NoError = 0
    Estop = 0x8000
    InitServiceTimeout = 0x8001
    HomingServiceTimeout = 0x8002
    PressingServiceTimeout = 0x8003
    ToFrontposServiceTimeout = 0x8004


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


class PressErrorCodes(object):
    NoError = 0
    OnEndSwitchError = 0x0201
    EndSwitchInUpperPos = 0x0202
    PressMovingUpTimeout = 0x0203
    PressMovingDownTimeout = 0x0204


class HomingErrorCodes(object):
    NoError = 0
    HomingTimeoutError = 0x0301

class PressingServiceErrorCodes(object):
    NoError = 0
    NotInClampPosError = 0x0401


code_to_text = {
    0: ('NoError', 'There are no errors.'),

    0x8000: ('Estop', 'The safety switch was pressed.'),
    0x8001: ('InitServiceTimeout', 'The timeout has happened during the initialization service execution.'),
    0x8002: ('HomingServiceTimeout', 'The timeout has happened during the homing service execution.'),
    0x8003: ('PressingServiceTimeout', 'The timeout has happened during the pressing service execution.'),
    0x8004: ('ToFrontposServiceTimeout', 'The timeout has happened during the to-front-position service execution.'),

    0x0001: ('SensorTimeout', 'The timeout has happened during the sensor work.'),
    0x0002: ('SensorError2', 'The sensor error 2.'),
    0x0003: ('SensorError3', 'The sensor error 3.'),

    0x0101: ('MotorTimeout', 'The timeout has happened by the motor.'),
    0x0102: ('MotorError2', 'The motor error 2.'),
    0x0103: ('MotorError3', 'The motor error 3.'),

    0x0201: ('OnEndSwitchError', 'The press is on the endswitch sensor.'),
    0x0202: ('EndSwitchInUpperPos', 'The endswitch sensor trigered while the press being in the upper position, check the sensors.'),
    0x0203: ('PressMovingUpTimeout', 'The timeout has happened during the press moving up. Check the press and the sensors.'),
    0x0204: ('PressMovingDownTimeout', 'The timeout has happened during the press moving down. Check the press and the sensors.'),

    0x0301: ('HomingTimeout', 'The timeout has happened during homing.'),
    0x0302: ('HomingError2', 'The Homing error 2.'),
    0x0303: ('HomingError3', 'The Homing error 3.'),

    0x0401: ('NotInClampPosError', 'The carriage appeared to be out of clamp position during the pressing. Check the sensor.'),
    0x0402: ('PressingServiceError2', 'The PressingService error 2.'),
    0x0403: ('PressingServiceError3', 'The PressingService error 3.')

}