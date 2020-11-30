# Running the test
Before starting the test, you must configure the `config.ini` file according to your router. You should see:
```[modbusTCP]
rutIP = 192.168.1.1
rutModel = RUT955
modbusPort = 502
rutPass = Admin123
testGPS = 0
testSIM = 2
```
* rutIP - your router's LAN IP address
* rutModel - model of your router (eg. RUT950; RUTX11)
* modbusPort - modbusTCP port of your router (default on factory boot - 502)
* rutPass - admin password of your router 
* testGPS - change to **1** to test GPS modbus addresses, otherwise **0**.
* testSIM - change to **1** to test only SIM1 slot, **2** for both SIM slots, otherwise **0**.

**IF TESTING BOTH SIMS** - make sure your active SIM is SIM1 before starting the test.

Once done configuring, you can start the test from the terminal by executing `main.py`.

# Modifying the modbus addresses
If any changes are made to modbusTCP addresses, you can configure the test accordingly in the `addresses.json` file. Here are some examples:

```
"address":1, 
"registers":2,
"type":"global",
"testMethod":"testGlobalMethods.testUptime"
```
* address - register's address
* registers - number of registers to read
* type - type of the parameter (used in the code to filter through which addresses are needed according to config.ini)
  * global - used for global parameters (like uptime, wan ip, hostname, etc.)
  * sim - used for global sim parameters (like modem temp, active sim slot, etc.)
  * sim1 - used for sim1 only parameters (data received/sent for sim1)
  * sim2 - used for sim2 only parameters (data received/sent for sim2)
  * gps - used for gps parameters (longitude, sat count, etc.)
  * io - used for input/output parameters (DIN/DOUT)
* testMethod - `testGlobalMethods`(.py) - coressponding file which contains required method; `testUptime` - coressponding method to call within that file

--  

Some instances in the json will have an `extraArg` value, for example:
```
"extraArg":"sent last month"
```
```
"extraArg":"received this week"
```
Used with SIM data testing methods, required for the program to know which value is being returned by modbus. 
```
"extraArg":"DOUT1"
```
Used with input/output methods.

--

You may notice some seemingly duplicate instances in the json, like:
```
  "address":325,
  "registers":1,
  "type":"io",
  "testMethod":"testIOMethods.testReadIO",
  "extraArg":"DOUT3"
},
{
  "address":325,
  "registers":1,
  "type":"io",
  "testMethod":"testIOMethods.testWriteIO",
  "extraArg":"DOUT3"
```
Some addresses can also be written to, notice that the first one is `testReadIO` and the second one is `testWriteIO`. 
