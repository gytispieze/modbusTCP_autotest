import main
import datetime
import sqlite3
import error

def testData(connection, dssh, address, noOfRegisters, numberOfIterations, numberOfErrors, routerModel, extraArg, simCard):
    def iterate(data, period, direction):
        rutData = 0
        for i in range(period):
            try:
                rutData += (data[i])[direction]
            except KeyError: ##end of dict
                pass
        return rutData
    
    dataType = extraArg.split(" ")
    if len(dataType) == 2:
        direction = dataType[0]
        typeOfPeriod = ""
        period = dataType[1]
    else:
        direction = dataType[0]
        typeOfPeriod = dataType[1]
        period = dataType[2]
    
    modbusData = connection.read_holding_registers(address, noOfRegisters)
    if modbusData:
        mdcollectd = sqlite3.connect('mdcollectd.db')

        now = datetime.datetime.now()
        datetill = int(datetime.datetime.timestamp(now))
        if period not in ("24h", "today"):
            if typeOfPeriod == "last":
                if period == "week":
                    datefrom = now - datetime.timedelta(7)
                elif period == "month":
                    datefrom = now - datetime.timedelta(30)
            else:
                if period == "week":
                    datefrom = now - datetime.timedelta(days=datetime.datetime.today().weekday() % 7)
                elif period == "month":
                    datefrom = now.replace(day=1)
                datefrom = datefrom.replace(hour=0, minute=0, second=0)
            datefrom = int(datetime.datetime.timestamp(datefrom))

        i = 1
        data = {}
        for row in mdcollectd.execute('SELECT rx, tx FROM days WHERE sim = %d' % (simCard + 1)):
            data[i] = row
            i += 1

        if bool(data) != False: ##if mobile data was used and is present in the dictionary
            if direction == "received":
                if typeOfPeriod == "last": ##last 24h, last week, last month
                    if period == "24h":
                        rutData = (data[len(data)])[0]
                    elif period == "week":
                        rutData = iterate(data, 7, 0)
                    elif period == "month":
                        rutData = iterate(data, 30, 0)     
                else: ## today, this week, this month
                    if period == "today":
                        rutData = (data[len(data)])[0]
                    elif period == "week":
                        rutData = iterate(data, 7, 0)
                    elif period == "month":
                        rutData = iterate(data, 30, 0)
            else: ##if sent
                if typeOfPeriod == "last":
                    if period == "24h":
                        rutData = (data[len(data)])[1]
                    elif period == "week":
                        rutData = iterate(data, 7, 1)
                    elif period == "month":
                        rutData = iterate(data, 30, 1)    
                else:
                    if period == "today": ##fix
                        rutData = (data[len(data)])[1]
                    elif period == "week":
                        rutData = iterate(data, 7, 1)
                    elif period == "month":
                        rutData = iterate(data, 30, 1)
        else: ##if mobile data wasn't used on current sim
            rutData = 0

        if modbusData[0] != 0: ##check if rut uptime is over 65536 seconds 
            modbusData = modbusData[0] * 65536 + modbusData[1]
        else:
            modbusData = modbusData[1]
        if rutData == modbusData:
            return True
        else:
            error.sendError("Read mobile data %s (sim%d)" % (extraArg, (simCard + 1)), modbusData, rutData, main.getRutUptime(dssh), numberOfIterations, numberOfErrors, main.getRutRamUsage(dssh))
            return False
    else:
        main.modbusError("mobile data %s (sim%d)" % (extraArg, (simCard + 1)), dssh, numberOfIterations, numberOfErrors)
        return False 