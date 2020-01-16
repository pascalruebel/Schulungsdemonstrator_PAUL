@echo off

REM Execute MongoDB
START /B mongod --replSet "rs" --bind_ip 0.0.0.0

TIMEOUT 20

REM Execute services
START /B forever start -c python ../stations-services/services/AcknowledgeAllErrorsService.py
START /B forever start -c python ../stations-services/services/AnalyticsService.py
START /B forever start -c python ../stations-services/services/AutoInitializeStationsService.py
START /B forever start -c python ../stations-services/services/ConfigureInventoryService.py
START /B forever start -c python ../stations-services/services/InventorySynchronizationService.py
START /B forever start -c python ../stations-services/services/ShutdownService.py
START /B forever start -c python ../stations-services/services/StationsStateService.py


REM Execute Production-Controller
START /B forever start -c python ../production-controller/main.py

REM Execute HMI
cd ..
cd hmi
START /B forever start -c node bin/www

REM Open chrome after stack is started
START chrome --app=http://localhost:3000