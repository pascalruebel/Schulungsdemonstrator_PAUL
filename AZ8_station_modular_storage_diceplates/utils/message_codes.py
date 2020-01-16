
class StationMessageCodes(object):
    NoMessages = 0
    RackEmpty = 0x0001
    DispatchNotEmpty = 0x0002
    ActiveJob = 0x0003
    CancelJob = 0x0004


code_to_text = {
    0: ('NoMessages', 'There are no active messages.'),

    0x0001: ('RackEmpty', 'Station is not ready to provide a diceplate. The rack is empty.'),
    0x0002: ('DispatchNotEmpty', 'Station is not ready to provide a dicehalf. Dispatch is occupied.'),
    0x0003: ('ActiveJob', 'Station is already executing a service.'),
    0x0004: ('CancelJob', 'Storage process has been cancelled. No quantities are set.')
}
