import serial


import time
import sys
import os

def process_data(data):
	print(data)
	
    
def on_start():
      
	try:
		comPort = 'COM11' # edit port number accordingly	
		ser = serial.Serial(port=comPort, baudrate=115200)
		print('Receiving data.... Press CTRL+C to exit \nData: ')		
		while True:			
			# Read newline terminated data
			msg = ser.readline()
			smsg = msg.decode('utf-8').strip()
			process_data(smsg)	
	except serial.SerialException as err:
		print('SerialException: {}'.format(err))
	except KeyboardInterrupt:
		print('Program Ended!')




if __name__ == "__main__":
    on_start()
