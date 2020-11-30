import main
import error
import paramiko
import math
import struct

def testGpsCoordinates(connection, dssh, address, noOfRegisters, numberOfIterations, numberOfErrors, routerModel, coordinates, *argv):
    modbusGpsCoords = connection.read_holding_registers(address, noOfRegisters)
    if modbusGpsCoords: ## check if value was retrieved from modbus
        modbusGpsCoords = struct.pack('>HH', modbusGpsCoords[0], modbusGpsCoords[1])
        modbusGpsCoords = round(struct.unpack('>f', modbusGpsCoords)[0], 3)
        try:
            if coordinates == "Latitude":
                dssh_stdin, dssh_stdout, dssh_stderr = dssh.exec_command("gpsctl -i")
            else:
                dssh_stdin, dssh_stdout, dssh_stderr = dssh.exec_command("gpsctl -x")
            rutGpsCoords = dssh_stdout.read().decode().strip()
            rutGpsCoords = round(float(rutGpsCoords), 3)
            
            if rutGpsCoords == modbusGpsCoords:
                return True
            else:
                error.sendError("Read GPS %s" % coordinates, modbusGpsCoords, rutGpsCoords, main.getRutUptime(dssh), numberOfIterations, numberOfErrors, main.getRutRamUsage(dssh))
                return False
        except paramiko.ssh_exception.SSHException:
            error.sendError("Error retrieving GPS %s from rut" % coordinates, '', '', main.getRutUptime(dssh), numberOfIterations, numberOfErrors, main.getRutRamUsage(dssh))
            return False
    else:
        main.modbusError('GPS %s' % coordinates, dssh, numberOfIterations, numberOfErrors)
        return False        

def testGpsFixTime(connection, dssh, address, noOfRegisters, numberOfIterations, numberOfErrors, routerModel, *argv):
    modbusGpsFixTime = main.getConvertedModbusValue(connection, dssh, address, noOfRegisters, numberOfIterations, numberOfErrors, "Read GPS Fix Time")
    if modbusGpsFixTime: ## check if value was retrieved from modbus
        try:
            dssh_stdin, dssh_stdout, dssh_stderr = dssh.exec_command("gpsctl -f")
            rutGpsFixTime = dssh_stdout.read().decode().strip()

            if math.isclose(int(rutGpsFixTime), int(modbusGpsFixTime), abs_tol=1): ##check if modbus and rut results are within 1 sec
                return True
            else:
                error.sendError("Read GPS Fix Time", modbusGpsFixTime, rutGpsFixTime, main.getRutUptime(dssh), numberOfIterations, numberOfErrors, main.getRutRamUsage(dssh))
                return False
        except paramiko.ssh_exception.SSHException:
            error.sendError("Error retrieving Read GPS Fix Time from rut", '', '', main.getRutUptime(dssh), numberOfIterations, numberOfErrors, main.getRutRamUsage(dssh))
            return False
    else:
        return False

def testGpsDateTime(connection, dssh, address, noOfRegisters, numberOfIterations, numberOfErrors, routerModel, *argv):
    modbusGpsDateTime = main.getConvertedModbusValue(connection, dssh, address, noOfRegisters, numberOfIterations, numberOfErrors, "Read GPS Date and Time")
    if modbusGpsDateTime:
        try:
            dssh_stdin, dssh_stdout, dssh_stderr = dssh.exec_command("gpsctl -e")
            rutGpsDateTime = dssh_stdout.read().decode().strip()

            if math.isclose(int(rutGpsDateTime[17:18]), int(modbusGpsDateTime[17:18]), abs_tol=1): ##check if modbus and rut results are within 1 sec:
                return True
            else:
                error.sendError("Read GPS Date and Time", modbusGpsDateTime, rutGpsDateTime, main.getRutUptime(dssh), numberOfIterations, numberOfErrors, main.getRutRamUsage(dssh))
                return False
        except paramiko.ssh_exception.SSHException:
            error.sendError("Error retrieving GPS Date and Time from rut", '', '', main.getRutUptime(dssh), numberOfIterations, numberOfErrors, main.getRutRamUsage(dssh))
            return False
    else:
        return False

def testGpsSpeed(connection, dssh, address, noOfRegisters, numberOfIterations, numberOfErrors, routerModel, *argv): ##pabaigti, nesuprantu kokias reiksmes duoda modbus
    modbusGpsSpeed = connection.read_holding_registers(address, noOfRegisters)
    if modbusGpsSpeed: ## check if value was retrieved from modbus
        modbusGpsSpeed = modbusGpsSpeed[0]

        modbusGpsSpeed = bin(modbusGpsSpeed)[2:18] ##convert signal strength to binary
        modbusGpsSpeed = int(modbusGpsSpeed, 2)

def testGpsSatCount(connection, dssh, address, noOfRegisters, numberOfIterations, numberOfErrors, routerModel, *argv):
    modbusGpsSatCount = connection.read_holding_registers(address, noOfRegisters)
    if modbusGpsSatCount: ## check if value was retrieved from modbus
        modbusGpsSatCount = modbusGpsSatCount[1]
        try:
            dssh_stdin, dssh_stdout, dssh_stderr = dssh.exec_command("gpsctl -p")
            rutGpsSatCount = dssh_stdout.read().decode().strip()

            if math.isclose(modbusGpsSatCount, int(rutGpsSatCount), abs_tol=1): ##check if modbus and rut results are within 1 
                return True
            else:
                error.sendError("Read GPS Satellite Count" , modbusGpsSatCount, rutGpsSatCount, main.getRutUptime(dssh), numberOfIterations, numberOfErrors, main.getRutRamUsage(dssh))
                return False
        except paramiko.ssh_exception.SSHException:
            error.sendError("Error retrieving Read GPS Satellite Count from rut", '', '', main.getRutUptime(dssh), numberOfIterations, numberOfErrors, main.getRutRamUsage(dssh))
            return False     
    else:
        return False   


def testGpsAccuracy(connection, dssh, address, noOfRegisters, numberOfIterations, numberOfErrors, routerModel, *argv):
    modbusGpsAccuracy = connection.read_holding_registers(address, noOfRegisters)
    if modbusGpsAccuracy: ## check if value was retrieved from modbus
        modbusGpsAccuracy = struct.pack('>HH', modbusGpsAccuracy[0], modbusGpsAccuracy[1])
        modbusGpsAccuracy = round(struct.unpack('>f', modbusGpsAccuracy)[0], 1)
        try:
            dssh_stdin, dssh_stdout, dssh_stderr = dssh.exec_command("gpsctl -u")
            rutGpsAccuracy = dssh_stdout.read().decode().strip()
            rutGpsAccuracy = round(float(rutGpsAccuracy), 1)
            
            if rutGpsAccuracy == modbusGpsAccuracy:
                return True
            else:
                error.sendError("Read GPS Accuracy", modbusGpsAccuracy, rutGpsAccuracy, main.getRutUptime(dssh), numberOfIterations, numberOfErrors, main.getRutRamUsage(dssh))
                return False
        except paramiko.ssh_exception.SSHException:
            error.sendError("Error retrieving GPS Accuracy from rut", '', '', main.getRutUptime(dssh), numberOfIterations, numberOfErrors, main.getRutRamUsage(dssh))
            return False
    else:
        main.modbusError('GPS Accuracy', dssh, numberOfIterations, numberOfErrors)
        return False 