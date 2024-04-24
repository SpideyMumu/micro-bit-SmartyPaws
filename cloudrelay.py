import time
import sqlite3
import requests
import json



try:
	conn = sqlite3.connect('smartypaws.db')
	
	put_pet_data_uri = 'http://192.168.42.78:8000/pet_data'
	headers = {'content-type': 'application/json'}
	
	
	
	while True:
	
		time.sleep(10)
		
		print('Relaying data to cloud server...')
				
		c = conn.cursor()
		c.execute('SELECT id, collarName, temp, steps, heart_rate, timestamp FROM collar_data_local WHERE tocloud = 0')
		results = c.fetchall()
		c = conn.cursor()
				
		for result in results:
					
			print('Relaying id={}; collarName={}; temp={}; steps={}; heart_rate={}; timestamp={}'.format(result[0], result[1], result[2], result[3], result[4], result[5]))
			
			gtemp = {
				'devicename':result[1],
				'temp':result[2],
				'steps':result[3],
				'heart_rate':result[4],
				'timestamp':result[5]
			}
			req = requests.put(put_pet_data_uri, headers = headers, data = json.dumps(gtemp))
			
			c.execute('UPDATE collar_data_local SET tocloud = 1 WHERE id = ' + str(result[0]))
		
		conn.commit()



except KeyboardInterrupt:
	
	print('********** END')
	
except Error as err:

	print('********** ERROR: {}'.format(err))

finally:

	conn.close()
