import configparser

def getRutIP():
    if readConfig():
        config = readConfig()
        rutIP = config.get('modbusTCP', 'rutIP')
        return rutIP
    else:
        return False

def getRutModel():
    if readConfig():
        config = readConfig()
        rutModel = config.get('modbusTCP', 'rutModel')
        return rutModel
    else:
        return False

def getModbusPort():
    if readConfig():
        config = readConfig()
        modbusPort = config.get('modbusTCP', 'modbusPort')
        return modbusPort
    else:
        return False

def getRutPass():
    if readConfig():
        config = readConfig()
        rutPass = config.get('modbusTCP', 'rutPass')
        return rutPass
    else:
        return False

def getTestGPS():
    if readConfig():
        config = readConfig()
        testGPS = config.get('modbusTCP', 'testGPS')
        return testGPS
    else:
        return False

def getTestSIM():
    if readConfig():
        config = readConfig()
        testSIM = config.get('modbusTCP', 'testSIM')
        return testSIM
    else:
        return False

def readConfig():
    config = configparser.RawConfigParser()
    config.read('config.ini')
    if len(config) == 1:
        return False
    else:
        return config

