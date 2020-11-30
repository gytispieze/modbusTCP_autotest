import json
import rutModel

def findAddresses(rutIP, modbusConnection, testGPS, testSIM):
    modbusConn = modbusConnection
    model = rutModel.findRutModel(rutIP, modbusConn)
    data = rutModel.openJson()

    addresses = {}
    testMethods = {}
    i = 0
    for eachModel in data.keys(): ## loop through each model name in the json file
        if model == eachModel: ## find if model in config file matches any of the models in json
            for each in data[model]: ## loop through each address under the found model
                if each['type'] == 'global':
                    addresses[i] = each
                elif each['type'] == 'gps' and testGPS == 1:
                    addresses[i] = each
                elif each['type'] == 'sim' and testSIM in (1, 2):
                    addresses[i] = each
                elif each['type'] == 'sim1' and testSIM in (1, 2):
                    addresses[i] = each
                elif each['type'] == 'sim2' and testSIM == 2:
                    addresses[i] = each    
                elif each['type'] == 'io':
                    addresses[i] = each   
                i += 1
            modelFound = True
            break
        else:
            modelFound = False
    
    if modelFound == False:
        print("Rut model not found in addresses.json. Check your config.ini.")
        exit()
    else:
        return addresses