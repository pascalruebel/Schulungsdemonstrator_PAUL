SERVER_CONFIG = {
    'uri': 'http://basicstation.edukitv2.smartfactorykl.de',
    'servername': 'AZ8_OPCUA_Server'
}

STATION_CONFIG = {
    'stationName': 'AZ8_Station',
    'storageRackMaxCapacity': 90,        # maximum diceplates in the storagerack
    'initServiceTimeoutInterval': 60.0,  # timeout intervals for the services
    'provideDiceplateTimeoutInterval': 300.0,
    'storageDiceplateTimeoutInterval': 600.0
}

DATABASE_CONFIG = {
    'database_url': 'mongodb://192.168.1.123:27017',
    'database_name': 'myapp',
    'database_collection': 'opcua_servers',
    'check_connection_address': 'http://192.168.1.123:3000',
    'check_connection_timeout': 5
}
