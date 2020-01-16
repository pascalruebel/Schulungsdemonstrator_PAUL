SERVER_CONFIG = {
    'uri': 'http://basicstation.edukitv2.smartfactorykl.de',
    'servername': 'AZ9_OPCUA_Server'
}

STATION_CONFIG = {
    'stationName' : 'AZ9_Station',
    'initServiceTimeoutInterval':   300.0,     # timeout intervals for the services
    'homeServiceTimeoutInterval':   300.0,     # timeout intervals for the services
    'pressServiceTimeoutInterval':  600.0,     # timeout intervals for the services
    'tofrontServiceTimeoutInterval':  600.0,   # timeout intervals for the services
    'pressTimeout': 2.0,                       # timeout interval for the press
    'pressMoveTimeout': 9.0,               # press movement to the front/rack monitoring time
    'waitForClampDelay': 1.0,               # clamping waiting time when pressing
    'pressingTime': 0.5,                    # pressing time
    'pressingSetpoint': 200                 # pressing setpoint presumably in gramms
}

DATABASE_CONFIG = {
    'database_url': 'mongodb://192.168.1.123:27017',
    'database_name': 'myapp',
    'database_collection': 'opcua_servers',
    'check_connection_address': 'http://192.168.1.123:3000',
    #''check_connection_address': 'http://216.58.192.142',  # a url to check the internet connection (is needed for mongodb)
    'check_connection_timeout': 5
}