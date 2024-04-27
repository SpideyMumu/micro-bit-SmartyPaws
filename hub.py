import time
from bluetooth import ble

import sqlite3

import util
from bleuartlib import BleUartDevice



def bleUartReceiveCallback(data):
	dataParts = data.split('=')
	collar_data.append({'devicename':dataParts[0], 'temp':dataParts[1], 'steps':dataParts[2]})	
	
	print('Received data: Device Name = {};Temperature = {}; Steps = {}'.format(dataParts[0], dataParts[1], dataParts[2]))



def addBleUartDevice(address, name):
	
	bleUartDevice = BleUartDevice(address)
	bleUartDevice.connect()
	bleUartDevice.enable_uart_receive(bleUartReceiveCallback)
	
	bleUartDevices.append({'device':bleUartDevice, 'name':name})



def sendCommandToAllBleUartDevices(command):
	
	for bled in bleUartDevices:		
		
		bled['device'].send(command)



def disconnectFromAllBleUartDevices():
	
	for bled in bleUartDevices:
		
		bled['device'].disconnect()
		bled['device'] = None



def saveData():
	
	c = conn.cursor()
	
	for data in collar_data:
		
		devicename = '' + data['devicename']
		devicename = devicename.strip('\x00')
		temp = '' + data['temp']
		temp = temp.strip('\x00')
		steps = '' + data['steps']
		steps = steps.strip('\x00')
		
		sql = "INSERT INTO collar_data_local (devicename, temp, steps, timestamp) VALUES('" + devicename + "', " + temp + ", " + steps + ", datetime('now', 'localtime'))"				
		c.execute(sql)
	
	conn.commit()
	
	collar_data.clear()


try:
	conn = sqlite3.connect('smartypaws.db')

	bleUartDevices = []
	collar_data = []

	service = ble.DiscoveryService()
	devices = service.discover(2)

	print('********** Initiating device discovery......')

	for address,name in devices.items():

		if address == 'CA:47:7D:AF:80:C4':
			print('Found BBC micro:bit [vegav]: {}'.format(address))
			addBleUartDevice(address, 'vegav')
			
			print('Added micro:bit device...')
		
        # Add future new devices here:
			
		# elif address == 'C8:06:B1:B4:66:53':

		# 	print('Found BBC micro:bit [tipov]: {}'.format(address))
		# 	addBleUartDevice(address, 'tipov')
			
		# 	print('Added micro:bit device...')
        
		# elif address == 'DF:60:7F:9B:61:F6':

		# 	print('Found BBC micro:bit [popap]: {}'.format(address))
		# 	addBleUartDevice(address, 'popap')
			
		# 	print('Added micro:bit device...')
  
		# elif address == 'CA:47:7D:AF:80:C4':
		# 	print('Found BBC micro:bit []: {}'.format(address))
		# 	addBleUartDevice(address, 'vegav')
			
		# 	print('Added micro:bit device...')
	
	if len(bleUartDevices) > 0:	
		
		while True:
		
			time.sleep(5)
			print('Sending command to all micro:bit devices...')
			sendCommandToAllBleUartDevices('sensor=temp')
			print('Finished sending command to all micro:bit devices...')
			saveData()
	
    # For simulation: use serial to receive data from micro:bit
	


except KeyboardInterrupt:
	
	print('********** END')
	
except:

	print('********** UNKNOWN ERROR')

finally:

	conn.close()
	disconnectFromAllBleUartDevices()
	print('Disconnected from micro:bit devices')
