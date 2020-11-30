import csv
import datetime

def sendError(parameter, modbusValue, rutValue, uptime, iteration, numOfErrors, ramUsage):
    with open('errors.csv', mode='a') as error_file:
        error_writer = csv.writer(error_file, delimiter=',')
        if numOfErrors == 1:
            error_writer.writerow(['Parameter', 'Modbus Value', 'Router\'s value', 'System uptime', 'Number of iteration', 'Number of errors', 'RAM Usage', 'Computer\'s time'])
            error_writer.writerow(['On test start', '', '', str(datetime.timedelta(seconds=int(uptime))), '', '', ramUsage, datetime.datetime.now().time()])
        else:
            pass
        error_writer.writerow([parameter, modbusValue, rutValue, str(datetime.timedelta(seconds=int(uptime))), iteration, numOfErrors, ramUsage, datetime.datetime.now().time()])
        
  