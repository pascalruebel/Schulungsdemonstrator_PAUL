class StationMessageCodes(object):
    NoMessages = 0
    NoActiveService = 0x0001
    ActiveJob = 0x0002
    ServiceError = 0x0003
    Message4 = 0x0004
    Message5 = 0x0005


code_to_text = {
    0: ('NoMessages', 'There are no active messages.'),

    0x0001: ('NoActiveService', 'The service has not been activated.'),
    0x0002: ('ActiveJob', 'Station is already executing a service.'),
    0x0003: ('ServiceError', 'The station is in the error state, acknowledge first.'),
    0x0004: ('Message4', 'Message4.'),
    0x0005: ('Message5', 'Message5.')
}
