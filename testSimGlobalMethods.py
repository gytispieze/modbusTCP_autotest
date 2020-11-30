import main
import error
import paramiko
import math
import json

def testMobileSignalStrength(connection, dssh, address, noOfRegisters, numberOfIterations, numberOfErrors, routerModel, simCard):
    modbusResult = connection.read_holding_registers(address, noOfRegisters)
    if modbusResult: ## check if value was retrieved from modbus
        modbusResult = modbusResult[1]

        modbusResult = bin(modbusResult)[2:18] ##convert signal strength to binary
        invertedModbusResult = int(modbusResult, 2)
        invertedModbusResult = invertedModbusResult ^ (2 ** (len(modbusResult) + 1) - 1) ## invert bits
        modbusSignalStrength = int(bin(invertedModbusResult)[3:19], 2) + int("1") #add 1 for final signal strength

        try:
            dssh_stdin, dssh_stdout, dssh_stderr = dssh.exec_command("gsmctl -q")
            rutSignalStrength = int(dssh_stdout.read().decode().strip())

            if math.isclose(int(rutSignalStrength), -modbusSignalStrength, abs_tol=8):
                return True
            else:
                error.sendError("Mobile Signal Strength (sim%d)" % (simCard + 1), modbusSignalStrength, rutSignalStrength, main.getRutUptime(dssh), numberOfIterations, numberOfErrors, main.getRutRamUsage(dssh))
                return False
        except paramiko.ssh_exception.SSHException:
            error.sendError("Error retrieving Mobile Signal Strength from rut (sim%d)"  % (simCard + 1), '', '', main.getRutUptime(dssh), numberOfIterations, numberOfErrors, main.getRutRamUsage(dssh))
            return False
    else:
        main.modbusError("Mobile Signal Strength (sim%d)" % (simCard + 1), dssh, numberOfIterations, numberOfErrors)
        return False

def testModemTemp(connection, dssh, address, noOfRegisters, numberOfIterations, numberOfErrors, routerModel, simCard):
    modbusModemTemp = connection.read_holding_registers(address, noOfRegisters)
    if modbusModemTemp:
        modbusModemTemp = modbusModemTemp[1]

        try:
            dssh_stdin, dssh_stdout, dssh_stderr = dssh.exec_command("gsmctl -c")
            rutModemTemp = int(dssh_stdout.read().decode().strip())
            modbusModemTemp = connection.read_holding_registers(address, noOfRegisters) ## duplicated code again to try and get most recent value
            modbusModemTemp = modbusModemTemp[1]
            if math.isclose(int(rutModemTemp), modbusModemTemp, abs_tol=20): ##check if rut and modbus temps within 20 (2 C) (because temp is returned with .1, for ex.= 44,0 C = 440)
                return True
            else:
                error.sendError('Modem Temperature', modbusModemTemp, rutModemTemp, main.getRutUptime(dssh), numberOfIterations, numberOfErrors, main.getRutRamUsage(dssh))
                return False
        except paramiko.ssh_exception.SSHException:
            error.sendError("Error retrieving Modem Temperature from rut", '', '', main.getRutUptime(dssh), numberOfIterations, numberOfErrors, main.getRutRamUsage(dssh))
            return False
    else:
        main.modbusError('Modem Temperature', dshh, numberOfIterations, numberOfErrors)
        return False

def testGsmOperator(connection, dssh, address, noOfRegisters, numberOfIterations, numberOfErrors, routerModel, simCard):
    modbusGsmOperator = main.getConvertedModbusValue(connection, dssh, address, noOfRegisters, numberOfIterations, numberOfErrors, "Read GSM Operator (sim%d)"  % (simCard + 1))
    if modbusGsmOperator:

        try:
            dssh_stdin, dssh_stdout, dssh_stderr = dssh.exec_command("gsmctl -o")
            rutGsmOperator = dssh_stdout.read().decode().strip()

            if rutGsmOperator == modbusGsmOperator:
                return True
            else:
                error.sendError("Read GSM Operator (sim%d)" % (simCard + 1), modbusGsmOperator, rutGsmOperator, main.getRutUptime(dssh), numberOfIterations, numberOfErrors, main.getRutRamUsage(dssh))
                return False
        except paramiko.ssh_exception.SSHException:
            error.sendError("Error retrieving GSM Operator Name from rut (sim%d)" % (simCard + 1), '', '', main.getRutUptime(dssh), numberOfIterations, numberOfErrors, main.getRutRamUsage(dssh))
            return False
    else:
        return False

def testSimCardSlot(connection, dssh, address, noOfRegisters, numberOfIterations, numberOfErrors, routerModel, simCard):
    modbusSimCardSlot = main.getConvertedModbusValue(connection, dssh, address, noOfRegisters, numberOfIterations, numberOfErrors, "Read Active SIM Card Slot (sim%d)"  % (simCard + 1))
    if modbusSimCardSlot:
        try:
            if routerModel in ("RUT950", "RUT955"):
                dssh_stdin, dssh_stdout, dssh_stderr = dssh.exec_command("sim_switch sim")
                rutSimCardSlot = dssh_stdout.read().decode().strip()
            else:
                dssh_stdin, dssh_stdout, dssh_stderr = dssh.exec_command("ubus call sim get")
                try:
                    rutSimCardSlot = json.loads(dssh_stdout.read().decode().strip())
                    rutSimCardSlot = "sim" + str(rutSimCardSlot["sim"])
                except json.decoder.JSONDecodeError:
                    error.sendError("Error retrieving Active SIM card slot from rut (sim%d)" % (simCard + 1), modbusSimCardSlot, rutSimCardSlot, main.getRutUptime(dssh), numberOfIterations, numberOfErrors, main.getRutRamUsage(dssh))

            if rutSimCardSlot == modbusSimCardSlot:
                return True
            else:
                error.sendError("Read Active SIM Card Slot (sim%d)" % (simCard + 1), modbusSimCardSlot, rutSimCardSlot, main.getRutUptime(dssh), numberOfIterations, numberOfErrors, main.getRutRamUsage(dssh))
                return False
        except paramiko.ssh_exception.SSHException:
            error.sendError("Error retrieving Active SIM card slot from rut (sim%d)" % (simCard + 1), '', '', main.getRutUptime(dssh), numberOfIterations, numberOfErrors, main.getRutRamUsage(dssh))
            return False
    else:
        return False

def testNetworkInfo(connection, dssh, address, noOfRegisters, numberOfIterations, numberOfErrors, routerModel, simCard):
    modbusNetworkInfo = main.getConvertedModbusValue(connection, dssh, address, noOfRegisters, numberOfIterations, numberOfErrors, "Read SIM Network Info (sim%d)"  % (simCard + 1))
    if modbusNetworkInfo:
        try:
            dssh_stdin, dssh_stdout, dssh_stderr = dssh.exec_command("gsmctl -g")
            rutNetworkInfo = dssh_stdout.read().decode().strip()

            if rutNetworkInfo == modbusNetworkInfo:
                return True
            else:
                error.sendError("Read SIM Network Info (sim%d)" % (simCard + 1), modbusNetworkInfo, rutNetworkInfo, main.getRutUptime(dssh), numberOfIterations, numberOfErrors, main.getRutRamUsage(dssh))
                return False
        except paramiko.ssh_exception.SSHException:
            error.sendError("Error retrieving SIM Network Info from rut (sim%d)" % (simCard + 1), '', '', main.getRutUptime(dssh), numberOfIterations, numberOfErrors, main.getRutRamUsage(dssh))
            return False
    else:
        return False

def testNetworkType(connection, dssh, address, noOfRegisters, numberOfIterations, numberOfErrors, routerModel, simCard):
    modbusNetworkType = main.getConvertedModbusValue(connection, dssh, address, noOfRegisters, numberOfIterations, numberOfErrors, "Read SIM Network Type (sim%d)"  % (simCard + 1))
    if modbusNetworkType:
        try:
            dssh_stdin, dssh_stdout, dssh_stderr = dssh.exec_command("gsmctl -t")
            rutNetworkType = dssh_stdout.read().decode().strip()

            if rutNetworkType == modbusNetworkType:
                return True
            else:
                error.sendError("Read SIM Network Type (sim%d)" % (simCard + 1), modbusNetworkType, rutNetworkType, main.getRutUptime(dssh), numberOfIterations, numberOfErrors, main.getRutRamUsage(dssh))
                return False
        except paramiko.ssh_exception.SSHException:
            error.sendError("Error retrieving SIM Network Type from rut (sim%d)"  % (simCard + 1), '', '', main.getRutUptime(dssh), numberOfIterations, numberOfErrors, main.getRutRamUsage(dssh))
            return False     
    else:
        return False

def testIMSI(connection, dssh, address, noOfRegisters, numberOfIterations, numberOfErrors, routerModel, simCard):
    modbusIMSI = getConvertedModbusValue(connection, dssh, address, noOfRegisters, numberOfIterations, numberOfErrors, "Read IMSI")
    if modbusIMSI:
        try:
            dssh_stdin, dssh_stdout, dssh_stderr = dssh.exec_command("gsmctl -x")
            rutIMSI = dssh_stdout.read().decode().strip()

            if rutIMSI == modbusIMSI:
                return True
            else:
                error.sendError("Read IMSI", modbusIMSI, rutIMSI, main.getRutUptime(dssh), numberOfIterations, numberOfErrors, main.getRutRamUsage(dssh))
                return False
        except paramiko.ssh_exception.SSHException:
            error.sendError("Error retrieving IMSI from rut", '', '', main.getRutUptime(dssh), numberOfIterations, numberOfErrors, main.getRutRamUsage(dssh))
            return False     
    else:
        return False   