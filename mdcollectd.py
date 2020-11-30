import sqlite3
import datetime

def iterate(data, period, direction):
    rutData = 0
    for i in range(period):
        try:
            rutData += (data[i])[direction]
        except KeyError:
            pass
    return rutData


mdcollectd = sqlite3.connect('mdcollectd.db')
data = {}
direction = "received"
typeOfPeriod = "this"
period = "month"

now = datetime.datetime.now()
datetill = int(datetime.datetime.timestamp(now))

if typeOfPeriod == "last":
    if period == "week":
        datefrom = now - datetime.timedelta(7)
    elif period == "month:":
        datefrom = now - datetime.timedelta(30)
else:
    if period == "week":
        datefrom = now - datetime.timedelta(days=datetime.datetime.today().weekday() % 7)
    elif period == "month":
        datefrom = now.replace(day=1)
    datefrom = datefrom.replace(hour=0, minute=0, second=0)

datefrom = int(datetime.datetime.timestamp(datefrom))

print(datefrom)
print(datetill)
i = 0
for row in mdcollectd.execute('SELECT rx, tx FROM days WHERE sim = 1 AND time >= %r AND time <= %r' % (datefrom, datetill)):
    data[i] = row
    i += 1
print(data)


rutData = 0


if bool(data) != False:
    print("test")
else:
    print("not")
if direction == "received":
    if typeOfPeriod == "last": ##last 24h, last week, last month
        if period == "24h":
            rutData = (data[1])[0]
        elif period == "week":
            rutData = iterate(data, 7, 0)
        elif period == "month":
            rutData = iterate(data, 30, 0)     
    else: ## today, this week, this month
        if period == "24h":
            rutData = (data[1])[0]
        elif period == "week":
            rutData = iterate(data, 7, 0)
        elif period == "month":
            rutData = iterate(data, 30, 0)
else: ##if sent
    if typeOfPeriod == "last":
        if period == "24h":
            rutData = (data[1])[1]
        elif period == "week":
            rutData = iterate(data, 7, 1)
        elif period == "month":
            rutData = iterate(data, 30, 1)    
    else:
        if period == "24h":
            rutData = (data[1])[0]
        elif period == "week":
            rutData = iterate(data, 7, 1)
        elif period == "month":
            rutData = iterate(data, 30, 1)    

print(rutData)
modbusData = 26001644
##if rutData == modbusData:
    ##print("success")
    ##return True
##else:
    ##pass
    ##error
    ##return False
    