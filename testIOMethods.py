import main
import paramiko
import error
import json
import rutModel
import math
from random import randint


def testReadIO(connection, dssh, address, noOfRegisters, numberOfIterations, numberOfErrors, routerModel, IO, *argv):
    modbusIO = connection.read_holding_registers(address, noOfRegisters)
    if modbusIO:
        if noOfRegisters == 2: ## DIN1, DIN2 addresses return two registers, state value is in second
            modbusIO = modbusIO[1]
        else: ## DIN3 address returns one register
            modbusIO = modbusIO[0]
        try:
            if IO == "Analog":
                dssh_stdin, dssh_stdout, dssh_stderr = dssh.exec_command("cat /sys/class/hwmon/hwmon0/device/in0_input")
                rutIO = dssh_stdout.read().decode().strip()
                modbusIO = connection.read_holding_registers(address, noOfRegisters)[1]
            else:
                if routerModel in ("RUT950", "RUT955"):
                    dssh_stdin, dssh_stdout, dssh_stderr = dssh.exec_command("gpio.sh get %s" % IO)
                    rutIO = dssh_stdout.read().decode().strip()
                else: ## RUTX
                    dssh_stdin, dssh_stdout, dssh_stderr = dssh.exec_command("ubus call ioman.gpio.%s status" % IO.lower())
                    rutIO = json.loads(dssh_stdout.read().decode().strip())
                    rutIO = str(rutIO["value"])

            if IO == "Analog":
                if math.isclose(int(rutIO), modbusIO, abs_tol=15):
                    return True
                else:
                    error.sendError("Read %s state" % IO, modbusIO, rutIO, main.getRutUptime(dssh), numberOfIterations, numberOfErrors, main.getRutRamUsage(dssh))
                    return False
            else:
                if int(rutIO) == modbusIO:
                    return True
                else:
                    error.sendError("Read %s state" % IO, modbusIO, rutIO, main.getRutUptime(dssh), numberOfIterations, numberOfErrors, main.getRutRamUsage(dssh))
                    return False
        except paramiko.ssh_exception.SSHException:
            error.sendError("Error retrieving %s state from rut (SSH error)" % IO, '', '', main.getRutUptime(dssh), numberOfIterations, numberOfErrors, main.getRutRamUsage(dssh))
            return False
        except json.decoder.JSONDecodeError:
            error.sendError("Error retrieving %s state from rut (JSON error, possibly ubus)" % IO, '', '', main.getRutUptime(dssh), numberOfIterations, numberOfErrors, main.getRutRamUsage(dssh))
            return False
    else:
        main.modbusError('%s state' % IO, dssh, numberOfIterations, numberOfErrors)
        return False

def testWriteIO(connection, dssh, address, noOfRegisters, numberOfIterations, numberOfErrors, routerModel, IO, *argv):
    if connection.write_single_register(address, randint(0, 1)):
        if testReadIO(connection, dssh, address, noOfRegisters, numberOfIterations, numberOfErrors, routerModel, IO):
            return True
        else:
            error.sendError("Read %s state" % IO, 'Look above', 'Look above', main.getRutUptime(dssh), numberOfIterations, numberOfErrors, main.getRutRamUsage(dssh))
            return False
    else:
        error.sendError("Write %s state" % IO, "Error writing to modbus", "-", main.getRutUptime(dssh), numberOfIterations, numberOfErrors, main.getRutRamUsage(dssh))
        return False