# Schulungsdemonstrator PAUL - Produktion & Automatisierung erleben

## Introduction

PAUL is a use-case of "Industrie 4.0" where machines are controlled and monitored through OPC UA showing how a factory can be automatized using the production of a dice as an example.

The use-case simulates different roles related to a real factory, we have `customers` that order products, `workers` which interact with the machines and produce the dice, `managers` which analyzes the data from the machines to get some insights how to optimize the production and, finally, the `maintenance` which is responsible to check for the factory healthy and solve problems during the production.

The interaction with the machines is done via an [HMI (Human-Machine-Interface)].

The production line tasks, including all the steps/messages required to produce a dice or refill the machines are controlled by a [production controller].

The real-time station of the machines and all the other actions that the user wants to apply to them (e.g. Auto-initialize all the stations) is controlled by a [stations-controller].

The [testbed] is a simulation environment making possible to develop and test the other modules without physical machines, i.e., it simulates the behavior and the data structure of the real machines.

## Installation

1. Install MongoDB
    1. [Windows](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-windows)
    2. [Linux](https://www.digitalocean.com/community/tutorials/how-to-install-mongodb-on-ubuntu-18-04)
    3. [Mac](https://treehouse.github.io/installation-guides/mac/mongo-mac.html)
2. If you want a client for MongoDB, we recommend to install [Robo 3T](https://robomongo.org/)
    1. [Windows/Linux/Mac](https://robomongo.org/download)
3. [Configure MongoDB to use replica sets](https://hackernoon.com/using-mongodb-as-a-realtime-database-with-change-streams-213cba1dfc2a)
4. Install NodeJS
    1. [Windows](https://www.guru99.com/download-install-node-js.html)
    2. [Linux](https://linuxize.com/post/how-to-install-node-js-on-ubuntu-18.04/)
    3. [Mac](https://www.webucator.com/how-to/how-install-nodejs-on-mac.cfm)
5. Install Python 3.6+
    1. [Windows](https://www.python.org/downloads/)
    2. [Linux](https://docs.python-guide.org/starting/install3/linux/)
    3. [Mac](http://osxdaily.com/2018/06/13/how-install-update-python-3x-mac/)
6. Install PIP3
    1. [Windows](https://vgkits.org/blog/pip3-windows-howto/)
    2. [Linux](https://stackoverflow.com/questions/6587507/how-to-install-pip-with-python-3)
    3. [Mac](https://stackoverflow.com/questions/34573159/how-to-install-pip3-on-my-mac)
7. Test if all the requirements are fulfilled, all the commands below must produce a version number output. Note: some installations require to explicitly say `python3` where others not, i.e., `python` is already a Python 3 installation. If you already have a Python 3.6 linked to your `python` command, replace the `python3` to `python`.
    1. `node --version`
    2. `npm --version`
    3. `python3 --version`
    4. `pip3 --version`
8. Install hmi dependencies
    1. `cd hmi && npm install`
9. Install production-controller dependencies
    1. `cd production-controller && pip3 install -r requirements.txt`
10. Install stations-controller dependencies
    1. `cd stations-controller && pip3 install -r requirements.txt`

If you want to use the testbed:

11. Install the testbed dependencies
    1. `cd test-environment`
    2. `pip3 install -r opcua-servers/requirements.txt`
    3. `cd web && npm install`

## Usage

### With physical stations

1. Execute the initialization script

    ```bash
    C:\> bin/start.bat
    ```

2. Turn on all the tablets and stations

### With testbed

1. Execute the initialization script

    ```bash
    C:\> bin/start.bat
    ```

2. Execute the testbed initialization script

    ```bash
    C:\> testbed/opcua-servers/startAll.bat
    ```

### Step-by-step for testbed usage

1. Start MongoDB

    ```bash
    C:\> mongod --replSet "rs"
    ```

2. Initialize the testbed [start script]()

    ```bash
    C:\> testbed/opcua-servers/startAll.bat
    ```

3. Start the production controller

    ```bash
    C:\> python production-controller/main.py
    ```

4. Start the services:

    1. For tests:

        ```bash
        C:\> stations-services\start.bat
        ```

    2. For production

        ```bash
        C:\> stations-services\startProduction.bat
        ```

5. Start HMI

    ```bash
    C:\> cd hmi
    C:\hmi> npm start
    ```

6. Open `http://localhost:3000/` in a browser

### Step-by-step for physical stations usage

1. (Physical stations usage) Start MongoDB
    ```bash
    mongod --replSet "rs" --bind_ip 0.0.0.0 -v
    ```
2. Turn on all the physical stations or call
3. Start the production controller

    ```bash
    C:\> python production-controller/main.py
    ```

4. Start the services:

    1. For tests:

        ```bash
        C:\> stations-services\start.bat
        ```

    2. For production

        ```bash
        C:\> stations-services\startProduction.bat
        ```

5. Start HMI

    ```bash
    C:\> cd hmi
    C:\hmi> npm start
    ```

6. Open `http://localhost:3000/` in a browser


