SERVER_CONFIG = {
    'uri': 'http://basicstation.edukitv2.smartfactorykl.de',
    'servername': 'AZ5_OPCUA_Server'
}

STATION_CONFIG = {
    'stationName' : 'AZ5_Station',
    'initServiceTimeoutInterval': 300.0,  # timeout intervals for the services
    'inPosBlinksNum': 4,        # number of blinks when in position
    'onTime': 0.5,              # on-time for blinking when in position
    'offTime': 0.5              # off-time for blinking when in position
}

DATABASE_CONFIG = {
    'database_url': 'mongodb://192.168.1.123:27017',
    'database_name': 'myapp',
    'database_collection': 'opcua_servers',
    'check_connection_address': 'http://192.168.1.123:3000',
    #''check_connection_address': 'http://216.58.192.142',  # a url to check the internet connection (is needed for mongodb)
    'check_connection_timeout': 5
}