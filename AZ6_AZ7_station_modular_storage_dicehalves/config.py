SERVER_CONFIG = {
    'uri': 'http://basicstation.edukitv2.smartfactorykl.de',
    'servername': 'AZ7_OPCUA_Server'
}

STATION_CONFIG = {
    'stationName': 'AZ7_Station',
    'rackMaxCapacity': 6,           # maximum dicehalfs in the rack
    'carriageMoveTimeout': 60.0,    # carriage movement to the front/rack monitoring time
    'waitForDicehalfdelay': 1.0,     # a delay for waiting a falling halfdice at the rack
    'rackFullCheckInterval': 3.0,     # timer interval for checking if the rack is full
    'initServiceTimeoutInterval': 60.0,  # timeout intervals for the services
    'homingServiceTimfeoutInterval': 300.0,
    'provideDicehalfTimeoutInterval': 300.0,
    'refillingTimeoutInterval': 600.0
}

DATABASE_CONFIG = {
    'database_url': 'mongodb://192.168.1.123:27017',
    'database_name': 'myapp',
    'database_collection': 'opcua_servers',
    'check_connection_address': 'http://192.168.1.123:3000',
    'check_connection_timeout': 5
}
