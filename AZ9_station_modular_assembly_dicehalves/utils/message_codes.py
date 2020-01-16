class StationMessageCodes(object):
    NoMessages = 0
    PressOnEndSwitch = 0x0001
    PressInPressPos = 0x0002
    ActiveJob = 0x0003
    CarriageOutofFrontPos = 0x0004
    PressOutofUpperPos = 0x0005


code_to_text = {
    0: ('NoMessages', 'There are no active messages.'),

    0x0001: ('PressOnEndSwitch', 'The press is on the endswitch sensor, the movement down is not possible.'),
    0x0002: ('PressInPressPos', 'The press is already in the pressing position, the movement down is not possible..'),
    0x0003: ('ActiveJob', 'Station is already executing a service.'),
    0x0004: ('CarriageOutofFrontPos', 'The pressing job cannot be started, because the carriage in not in the front position.'),
    0x0005: ('PressOutofUpperPos', 'The ToFrontPos job cannot be started, because the press in not in the upper position.')
}
