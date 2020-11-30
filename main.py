from pyModbusTCP.client import ModbusClient
from sys import argv
import subprocess
import time
import paramiko
import addresses
import math
import error
import binascii
import config
import rutModel
import datetime
import struct
import json
import sqlite3
import testGlobalMethods
import testIOMethods
import testGpsMethods
import testSimGlobalMethods
import testSimDataMethods
from scp import SCPClient


def informationPrint(numberOfIterations, numberOfErrors, rutRamUsage, getRutUptime):
    info = "Number of iterations: %d | Number of errors: %d | Current RAM usage: %r MB | RUT Uptime: %r" % (numberOfIterations, numberOfErrors - 1, rutRamUsage, str(datetime.timedelta(seconds=int(getRutUptime))))
    return info

def getRutUptime(dssh):
    try:
        dssh_stdin, dssh_stdout, dssh_stderr = dssh.exec_command("cat /proc/uptime")
        uptime = dssh_stdout.read().decode().strip().split(" ")
        uptime = uptime[0].split(".")[0]
        return uptime
    except paramiko.ssh_exception.SSHException:
        return "Error retrieving uptime."
    except AttributeError:
        return "Error retrieving uptime."

def getRutRamUsage(dssh):
    try:
        dssh_stdin, dssh_stdout, dssh_stderr = dssh.exec_command("free -m | grep \"Mem\" | awk \'{ print $3 }\'")
        rutRamUsage = dssh_stdout.read().decode().strip()
        rutRamUsage = round((int(rutRamUsage) / 1024), 2)
        return rutRamUsage
    except paramiko.ssh_exception.SSHException:
        return "Error retrieving ram usage."

def modbusError(parameter, dssh, numberOfIterations, numberOfErrors):
    error.sendError(parameter, "Couldn't retrieve modbus value", "-", getRutUptime(dssh), numberOfIterations, numberOfErrors, getRutRamUsage(dssh))

def convertFromDecimal(modbusResult):
    result = ""
    for each in modbusResult:
        if each != 0:
            line = str(hex(each)) ##convert each decimal line to hex
            line = bytearray.fromhex(line[2:6]).decode() ##then convert the hex value to ASCII
            result += line
    return result

def getConvertedModbusValue(connection, dssh, address, noOfRegisters, numberOfIterations, numberOfErrors, parameter):
    modbusResult = connection.read_holding_registers(address, noOfRegisters)
    modbusConvertedValue = ""
    if modbusResult: ## check if value was retrieved from modbus
        modbusConvertedValue = convertFromDecimal(modbusResult)
        modbusConvertedValue = modbusConvertedValue.replace("\x00", "", -1) ##remove null characters if result is odd number of characters
        return modbusConvertedValue
    else:
        modbusError(parameter, dssh, numberOfIterations, numberOfErrors)
        return False

def twos_comp(value, bits):
    if (value & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        value = value - (1 << bits)        # compute negative value
    return value     

def mobileInterfaceOff(dssh, numberOfIterations, numberOfErrors, routerModel, rutIP, rutPass):
    while True:
        try:
            if rutModel.findRutModel(rutIP, connection) in ("RUT950", "RUT955"):
                dssh.exec_command("uci set network.ppp.enabled=0")
                dssh.exec_command("uci commit network")
                dssh.exec_command("/etc/init.d/network restart")
            else:
                dssh.exec_command("uci set network.mob1s1a1.auto=0")
                dssh.exec_command("uci set network.mob1s2a1.auto=0")
                dssh.exec_command("uci commit network")
                dssh.exec_command("/etc/init.d/network restart")
            dssh.close()
            if routerModel in ("RUT950", "RUT955"):
                time.sleep(15) ##wait for interfaces to go down
            else:
                time.sleep(10) ##wait for interfaces to go down
            dssh.connect(rutIP, username='root', password=rutPass)
            scp = SCPClient(dssh.get_transport())
            scp.get('/tmp/mdcollectd.db', local_path="")
            break
        except paramiko.ssh_exception.SSHException:
            error.sendError("Error disabling Mobile Interfaces", "", "", getRutUptime(dssh), numberOfIterations, numberOfErrors, getRutRamUsage(dssh))
        except TimeoutError:
            error.sendError("Timed out while disabling Mobile Interfaces", "", "", getRutUptime(dssh), numberOfIterations, numberOfErrors, getRutRamUsage(dssh))
            dssh.connect(rutIP, username='root', password=rutPass)
        except:
            error.sendError("Error retrieving mdcollectd.db from rut", '', '', getRutUptime(dssh), numberOfIterations, numberOfErrors, getRutRamUsage(dssh))

def mobileInterfaceOn(dssh, numberOfIterations, numberOfErrors, routerModel, rutIP, rutPass, testSIM):
    while True:
        try:
            if rutModel.findRutModel(rutIP, connection) in ("RUT950", "RUT955"):
                if testSIM == 2: ##only switch SIMs if config is setup for two sim slots
                    dssh.exec_command("sim_switch change")
                dssh.exec_command("uci set network.ppp.enabled=1")
                dssh.exec_command("uci commit network")
                dssh.exec_command("/etc/init.d/network restart")
                dssh.close()
                time.sleep(25) ##wait for interfaces to go up and SIM to change
            else:
                if testSIM == 2: ##only switch SIMs if config is setup for two sim slots 
                    dssh.exec_command("gsmctl -Y")
                dssh.exec_command("uci set network.mob1s1a1.auto=1")
                dssh.exec_command("uci set network.mob1s2a1.auto=1")
                dssh.exec_command("uci commit network")
                dssh.exec_command("/etc/init.d/network restart")
                dssh.close()
                time.sleep(15) ##wait for interfaces to go up and SIM to change
            dssh.connect(rutIP, username='root', password=rutPass)
            break
        except paramiko.ssh_exception.SSHException:
            error.sendError("Error enabling Mobile Interfaces or switching SIM", "", "", getRutUptime(dssh), numberOfIterations, numberOfErrors, getRutRamUsage(dssh))
            dssh.connect(rutIP, username='root', password=rutPass)
        except TimeoutError:
            error.sendError("Error enabling Mobile Interfaces or switching SIM", "", "", getRutUptime(dssh), numberOfIterations, numberOfErrors, getRutRamUsage(dssh))
            dssh.connect(rutIP, username='root', password=rutPass)
        except:
            error.sendError("Error enabling Mobile Interfaces or switching SIM", "", "", getRutUptime(dssh), numberOfIterations, numberOfErrors, getRutRamUsage(dssh))
            dssh.connect(rutIP, username='root', password=rutPass)
    time.sleep(3) ## wait for a few secs to have some mobile data run through

def testAnyMethod(connection, dssh, address, noOfRegisters, testMethod, numberOfIterations, numberOfErrors, routerModel, *argv):
    testMethod = testMethod.split(".")
    try:
        testMethod = getattr(eval(testMethod[0]), testMethod[1])(connection, dssh, address, noOfRegisters, numberOfIterations, numberOfErrors, routerModel, *argv)
    except AttributeError:
        print("%s module has no method %s. Check addresses.json at %d address." % (testMethod[0], testMethod[1], address))
        exit()
    return testMethod

def main():
    configCorrect = True
    global rutIP
    if config.getRutIP():
        rutIP = config.getRutIP()
    else:
        print("Couldn't find router's IP in config.ini.")
        configCorrect = False
    if config.getRutPass():
        rutPass = config.getRutPass()
    else:
        print("Couldn't find router's password in config.ini.")
        configCorrect = False
    if config.getModbusPort(): 
        modbusPort = config.getModbusPort()
    else:
        print("Couldn't find router's modbus port in config.ini.")
        configCorrect = False
    if config.getTestSIM(): 
        testSIM = int(config.getTestSIM())
    else:
        print("Couldn't find SIM test setting in config.ini. Defaulting to 0.")
        testSIM = 0
    if config.getTestGPS(): 
        testGPS = int(config.getTestGPS())
    else:
        print("Couldn't find GPS test setting in config.ini. Defaulting to 0.")
        testGPS = True
    ##else: ## otherwise ask for user input
        ##rutIP = input("Enter you router's LAN IP > ")
        ##rutPass = input("Enter your router's admin password > ")
    modbusSetup = True
    if configCorrect:
        while True:
            try: ##configure router's modbus
                global dssh
                dssh = paramiko.SSHClient()
                dssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                dssh.connect(rutIP, username='root', password=rutPass)
                dssh.exec_command("uci set modbus.modbus.enabled=\'1\'")
                dssh.exec_command("uci set modbus.modbus.clientregs=\'1\'")
                dssh.exec_command("uci set modbus.modbus.regfile=\'/tmp/regfile\'")
                dssh.exec_command("uci set modbus.modbus.regfilestart=\'1025\'") 
                dssh.exec_command("uci set modbus.modbus.regfilesize=\'128\'")
                dssh.exec_command("uci set modbus.modbus.port=\'502\'")
                dssh.exec_command("uci commit modbus")
                dssh.exec_command("/etc/init.d/modbusd restart")
                if testGPS == 1:
                    dssh.exec_command("uci set gps.gpsd.enabled=\'1\'")
                    dssh.exec_command("uci set gps.gpsd.galileo_sup=\'1\'")
                    dssh.exec_command("uci set gps.gpsd.glonass_sup=\'7\'")
                    dssh.exec_command("uci set gps.gpsd.beidou_sup=\'3\'") 
                    dssh.exec_command("uci commit gps")
                    dssh.exec_command("/etc/init.d/gpsd restart")
                    time.sleep(8) ##wait for GPS to restart
                break
            except paramiko.ssh_exception.AuthenticationException:
                print("Authentication failed. Check if rut pass is correct in config.ini")
                modbusSetup = False
                break
            except BlockingIOError:
                print("Connection timed out.")
                modbusSetup = False
                break
            except paramiko.ssh_exception.socket.gaierror:
                print("Wrong IP address.")
                modbusSetup = False
                break
            except OSError:
                print("Network is unreachable. Check rutIP in config.")
                modbusSetup = False
                break
            except:
                print("Unknown error occured.")
                modbusSetup = False
                break
        if modbusSetup:
            global connection
            try:
                connection = ModbusClient(host=rutIP, port=modbusPort , auto_open=True, auto_close=True) ## create a modbus connection object, hosts file
                if connection.open(): ## check if modbus connection was successful
                    pass
                else:
                    print("Failed to connect to modbus")
                    modbusSetup = False
            except ValueError:
                print("Error with host or port parameters. Check config.ini")
                modbusSetup = False
        scp = SCPClient(dssh.get_transport())
        scp.get('/tmp/mdcollectd.db', local_path="")
        if modbusSetup:
            routerModel = rutModel.findRutModel(connection, rutIP)
            print("RAM Usage at the start of test: %r MB" % getRutRamUsage(dssh)) 
            adressDict = addresses.findAddresses(rutIP, connection, testGPS, testSIM)
            numberOfIterations = 0
            numberOfErrors = 1
            cont = True
            while cont:
                if testSIM in (1, 2):
                    for simCard in range(2):
                        if testSIM == 1:
                            simCard = 0 ##dont switch sim card testing if config is set up for 1 sim
                        numberOfIterations += 1
                        for each in adressDict:
                            print(f'\r', end=informationPrint(numberOfIterations, numberOfErrors, getRutRamUsage(dssh), getRutUptime(dssh)))
                            
                            address = adressDict[each]['address']
                            noOfRegisters = adressDict[each]['registers']
                            testMethod = adressDict[each]['testMethod']
                            testType = adressDict[each]['type']
                            try:
                                extraArg = adressDict[each]['extraArg']
                            except KeyError:
                                extraArg = None
                                pass
                            if address == 185: ## turn off mobile interfaces before testing data values
                                connection.close()
                                mobileInterfaceOff(dssh, numberOfIterations, numberOfErrors, routerModel, rutIP, rutPass)
                                connection.open()
                                if connection.open(): ## check if modbus connection was successful
                                    pass
                                else:
                                    time.sleep(3)
                                    connection.open()
                            try:
                                if simCard == 0 and testType != "sim2":
                                    if extraArg:
                                        testPassed = testAnyMethod(connection, dssh, address, noOfRegisters, testMethod, numberOfIterations, numberOfErrors, routerModel, extraArg, simCard)
                                    else:
                                        testPassed = testAnyMethod(connection, dssh, address, noOfRegisters, testMethod, numberOfIterations, numberOfErrors, routerModel, simCard)
                                elif simCard == 1 and testType != "sim1":
                                    if extraArg:
                                        testPassed = testAnyMethod(connection, dssh, address, noOfRegisters, testMethod, numberOfIterations, numberOfErrors, routerModel, extraArg, simCard)
                                    else:
                                        testPassed = testAnyMethod(connection, dssh, address, noOfRegisters, testMethod, numberOfIterations, numberOfErrors, routerModel, simCard)
                            except KeyboardInterrupt:
                                print("Interrupted.")
                                exit()
                            if testPassed == False:
                                numberOfErrors += 1
                            if address == 322: ## turn on mobile interfaces before testing data values
                                connection.close()
                                mobileInterfaceOn(dssh, numberOfIterations, numberOfErrors, routerModel, rutIP, rutPass, testSIM)
                                connection.open()
                else: ##if testSIM = 0
                    numberOfIterations += 1
                    for each in adressDict:
                        print(f'\r', end=informationPrint(numberOfIterations, numberOfErrors, getRutRamUsage(dssh), getRutUptime(dssh)))
                        testPassed = True
                        address = adressDict[each]['address']
                        noOfRegisters = adressDict[each]['registers']
                        testMethod = adressDict[each]['testMethod']
                        try:
                            extraArg = adressDict[each]['extraArg']
                        except KeyError: ## if no extra argument found, leave empty
                            extraArg = None
                            pass
                        try:
                            if extraArg:
                                testPassed = testAnyMethod(connection, dssh, address, noOfRegisters, testMethod, numberOfIterations, numberOfErrors, routerModel, extraArg)
                            else:
                                testPassed = testAnyMethod(connection, dssh, address, noOfRegisters, testMethod, numberOfIterations, numberOfErrors, routerModel)
                        except KeyboardInterrupt:
                            print("Interrupted.")
                            exit()
                        if testPassed == False:
                            numberOfErrors += 1
    return True

if __name__ == "__main__":
    main()
    