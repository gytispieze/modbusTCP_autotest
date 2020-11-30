from pyModbusTCP.client import ModbusClient
import json
import error
import config

def openJson():
    try:
        with open("addresses.json", "r") as read_file:
            jsonFile = json.load(read_file)
        return jsonFile
    except FileNotFoundError:
        print("Addresses file not found.")
        exit()
    except json.decoder.JSONDecodeError:
        print("Addresses file error. Check addresses.json")
        exit()
    

def findRutModel(rutIP, modbusConnection):
    if config.getRutModel():
        rutModel = config.getRutModel()
    else:
        data = openJson()
        connection = modbusConnection
        connected = False
        while connected == False: 
            if connection.open():
                print("Retrieving router's model from modbus...")
                connected = True
            else:
                print("Modbus connection error.")
                exit()

        readRutModelFromModbus = connection.read_holding_registers(71, 16)
        rutModel = ""
        while True:
            try:
                for each in readRutModelFromModbus:
                    if each != 0:
                        line = str(hex(each)) ##convert each decimal line to hex
                        line = bytearray.fromhex(line[2:6]).decode() ##then convert the hex value to ASCII
                        rutModel += line
                
                break
            except:
                print("Failed to retrieve router's model.")
                rutModels = []
                for each in data: ##find every rut model in JSON and put it in a list
                    rutModels.append(each)
                while True:
                    rutModel = input("Please insert your router's model > ")
                    if rutModel not in rutModels: ##check if inserted model exists in the model list
                        print("Unidentified model. ")
                    else:
                        print("Model identified.")
                        break
                break

    return rutModel

    

