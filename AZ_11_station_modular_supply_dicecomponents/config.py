SERVER_CONFIG = {
    'uri': 'http://basicstation.edukitv2.smartfactorykl.de',
    'servername': 'AZ11_OPCUA_Server'
}

STATION_CONFIG = {
    'stationName': 'AZ11_Station',
    'initServiceTimeoutInterval':   300.0,     # timeout intervals for the services
    'assembleServiceTimeoutInterval':   600.0     # timeout intervals for the services
}

DATABASE_CONFIG = {
    'database_url': 'mongodb://192.168.1.123:27017',
    'database_name': 'myapp',
    'database_collection': 'opcua_servers',
    'check_connection_address': 'http://192.168.1.123:3000',
    'check_connection_timeout': 5
}
