import main
import error
import math
import paramiko
from random import randint

def testUptime(connection, dssh, address, noOfRegisters, numberOfIterations, numberOfErrors, *argv):
    retrieveModbus = connection.read_holding_registers(address, noOfRegisters)
    if retrieveModbus: ## check if value was retrieved from modbus
        if retrieveModbus[0] != 0: ##check if rut uptime is over 65536 seconds 
            modbusUptime = retrieveModbus[0] * 65536 + retrieveModbus[1]
        else:
            modbusUptime = retrieveModbus[1]

        rutUptime = main.getRutUptime(dssh)
        if math.isclose(int(rutUptime), modbusUptime, abs_tol=1): ##check if modbus and rut uptime results are within 1 sec
            return True
        else:
            error.sendError('Uptime', modbusUptime, rutUptime, main.getRutUptime(dssh), numberOfIterations, numberOfErrors, main.getRutRamUsage(dssh))
            return False
    else:
        main.modbusError('Uptime', dssh, numberOfIterations, numberOfErrors)
        return False

def testReadSysHostname(connection, dssh, address, noOfRegisters, numberOfIterations, numberOfErrors, *argv):
    modbusRutHostname = main.getConvertedModbusValue(connection, dssh, address, noOfRegisters, numberOfIterations, numberOfErrors, "Read Sys Hostname")
    if modbusRutHostname:
        try:
            dssh_stdin, dssh_stdout, dssh_stderr = dssh.exec_command("uci get system.system.hostname")
            rutHostname = dssh_stdout.read().decode().strip()

            if rutHostname == modbusRutHostname:
                return True
            else:
                error.sendError("Read System Hostname", modbusRutHostname, rutHostname, main.getRutUptime(dssh), numberOfIterations, numberOfErrors, main.getRutRamUsage(dssh))
                return False
        except paramiko.ssh_exception.SSHException:
            error.sendError("Error retrieving System Hostname from rut", '', '', main.getRutUptime(dssh), numberOfIterations, numberOfErrors, main.getRutRamUsage(dssh))
            return False
    else:
        return False

def testWriteSysHostname(connection, dssh, address, noOfRegisters, numberOfIterations, numberOfErrors, *argv):
    testHostnameValue = [21573, 21332] ##this is the word "TEST" coverted to hex and then decimal
    if connection.write_multiple_registers(address, testHostnameValue): 
        if testReadSysHostname(connection, dssh, address, noOfRegisters, numberOfIterations, numberOfErrors, *argv):
            return True
        else:
            error.sendError("Read System Hostname after Writing", "Look above", "Look above", main.getRutUptime(dssh), numberOfIterations, numberOfErrors, main.getRutRamUsage(dssh))
            return False
    else:
        error.sendError("Write System Hostname", "Error writing to modbus", "-", main.getRutUptime(dssh), numberOfIterations, numberOfErrors, main.getRutRamUsage(dssh))
        return False

def testSerialNo(connection, dssh, address, noOfRegisters, numberOfIterations, numberOfErrors, routerModel, *argv):
    modbusSerialNo = main.getConvertedModbusValue(connection, dssh, address, noOfRegisters, numberOfIterations, numberOfErrors, "Read Serial Number")
    if modbusSerialNo:
        try:
            if routerModel in ("RUT950", "RUT955"):
                dssh_stdin, dssh_stdout, dssh_stderr = dssh.exec_command("mnf_info sn")
            else:
                dssh_stdin, dssh_stdout, dssh_stderr = dssh.exec_command("mnf_info -s")
            rutSerialNo = dssh_stdout.read().decode().strip()

            if rutSerialNo == modbusSerialNo:
                return True
            else:
                error.sendError("Read Serial Number", modbusSerialNo, rutSerialNo, main.getRutUptime(dssh), numberOfIterations, numberOfErrors, main.getRutRamUsage(dssh))
                return False
        except paramiko.ssh_exception.SSHException:
            error.sendError("Error retrieving Serial Number from rut", '', '', main.getRutUptime(dssh), numberOfIterations, numberOfErrors, main.getRutRamUsage(dssh))
            return False
    else: 
        return False

def testLanMacAddr(connection, dssh, address, noOfRegisters, numberOfIterations, numberOfErrors, routerModel, *argv):
    modbusLanMacAddr = main.getConvertedModbusValue(connection, dssh, address, noOfRegisters, numberOfIterations, numberOfErrors, "Read LAN MAC Address")
    if modbusLanMacAddr:
        try:
            if routerModel in ("RUT950", "RUT955"):
                dssh_stdin, dssh_stdout, dssh_stderr = dssh.exec_command("mnf_info mac")
            else:
                dssh_stdin, dssh_stdout, dssh_stderr = dssh.exec_command("mnf_info -m")
            rutLanMacAddr = dssh_stdout.read().decode().strip()

            if rutLanMacAddr == modbusLanMacAddr:
                return True
            else:
                error.sendError("Read LAN MAC Address", modbusLanMacAddr, rutLanMacAddr, main.getRutUptime(dssh), numberOfIterations, numberOfErrors, main.getRutRamUsage(dssh))
                return False
        except paramiko.ssh_exception.SSHException:
            error.sendError("Error retrieving LAN MAC Address from rut", '', '', main.getRutUptime(dssh), numberOfIterations, numberOfErrors, main.getRutRamUsage(dssh))
            return False
    else:
        return False

def testRouterName(connection, dssh, address, noOfRegisters, numberOfIterations, numberOfErrors, *argv):
    modbusRouterName = main.getConvertedModbusValue(connection, dssh, address, noOfRegisters, numberOfIterations, numberOfErrors, "Read Router Name")
    if modbusRouterName:
        try:
            dssh_stdin, dssh_stdout, dssh_stderr = dssh.exec_command("uci get system.system.routername")
            rutRouterName = dssh_stdout.read().decode().strip()

            if rutRouterName == modbusRouterName:
                return True
            else:
                error.sendError("Read Router Name", modbusRouterName, rutRouterName, main.getRutUptime(dssh), numberOfIterations, numberOfErrors, main.getRutRamUsage(dssh))
                return False
        except paramiko.ssh_exception.SSHException:
            error.sendError("Error retrieving Router Name from rut", '', '', main.getRutUptime(dssh), numberOfIterations, numberOfErrors, main.getRutRamUsage(dssh))
            return False
    else:
        return False

def testWanIP(connection, dssh, address, noOfRegisters, numberOfIterations, numberOfErrors, *argv):
    modbusResult = connection.read_holding_registers(address, noOfRegisters)
    modbusWanIP = ""
    if modbusResult: ## check if value was retrieved from modbus
        for each in modbusResult:
            if each != 0:
                line = bin(each) ##convert each decimal line to binary
                line = line[2:18].zfill(16) ##filling up the binary result with zeros at the start to 16 characters, turns it into 2's complement that we need to convert
                num1 = int(line[0:8], 2) ##convert split binary numbers back to decimal
                num2 = int(line[8:16], 2)
                modbusWanIP += str(num1) + '.' + str(num2) + '.'
        modbusWanIP = modbusWanIP[:-1] ##remove the dot at the end
        try:
            dssh_stdin, dssh_stdout, dssh_stderr = dssh.exec_command("wan_info ip")
            rutWanIP = dssh_stdout.read().decode().strip()

            if rutWanIP == modbusWanIP:
                return True
            else:
                error.sendError("Read WAN IP", modbusWanIP, rutWanIP, main.getRutUptime(dssh), numberOfIterations, numberOfErrors, main.getRutRamUsage(dssh))
                return False
        except paramiko.ssh_exception.SSHException:
            error.sendError("Error retrieving WAN IP from rut", '', '', main.getRutUptime(dssh), numberOfIterations, numberOfErrors, main.getRutRamUsage(dssh))
            return False
    else:
        main.modbusError('Wan IP', dssh, numberOfIterations, numberOfErrors)
        return False

def testReadCustomRegister(connection, dssh, address, noOfRegisters, numberOfIterations, numberOfErrors, testRegisterValue):
    modbusCustomRegister = connection.read_holding_registers(address, noOfRegisters)

    if testRegisterValue == modbusCustomRegister:
        return True
    else:
        error.sendError("Read Custom Register", modbusCustomRegister, testRegisterValue, main.getRutUptime(dssh), numberOfIterations, numberOfErrors, main.getRutRamUsage(dssh))
        return False

def testWriteCustomRegister(connection, dssh, address, noOfRegisters, numberOfIterations, numberOfErrors, *argv):
    value1 = randint(10000, 20000)
    value2 = randint(10000, 20000)

    testRegisterValue = [value1, value2]
    if connection.write_multiple_registers(address, testRegisterValue): 
        if testReadCustomRegister(connection, dssh, address, noOfRegisters, numberOfIterations, numberOfErrors, testRegisterValue):
            return True
        else:
            error.sendError("Read Custom Register after Writing", "Look above", "Look above", main.getRutUptime(dssh), numberOfIterations, numberOfErrors, main.getRutRamUsage(dssh))
            return False
    else:
        error.sendError("Write Custom Register", "Error writing to modbus", "-", main.getRutUptime(dssh), numberOfIterations, numberOfErrors, main.getRutRamUsage(dssh))
        return False