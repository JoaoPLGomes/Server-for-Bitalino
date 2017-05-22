import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import socket, test
from tornado import gen
import threading
from random import randint
import bitalino
import json
import connectionClass



macAddress = ""
acqChannels = []
samplingRate = 0
nSamples = 0
digitalOutput = []

'''
This is a simple Websocket Echo server that uses the Tornado websocket handler.
Please run `pip install tornado` with python of version 2.7.9 or greater to install tornado.
This program will echo back the reverse of whatever it recieves.
Messages are output to the terminal for debuggin purposes.
''' 
threads = [] #Array with threads

device = ""
toStop = False
connections = [] #Clients that are connected

class WSHandler(tornado.websocket.WebSocketHandler):
	
	

	def check_origin(self, origin):
		return True

	def open(self):
		
		
		connections.append(connectionClass.Connection(self))
		print connections
		print 'New connection was opened'
		
		#self.write_message("Conn!")


	
	def on_message(self, message):
		if type(message) == unicode:
			print type(message)
			print message
			for val in connections:
				
				val.set_sizeScreen(message)
				
		self.write_message(message)
		
			


	def on_close(self):
		for val in connections:
			if val.get_connection():

				connections.remove(val)
		print 'Conn closed...'
		
		if len(connections) == 0:
			
			global toStop 
			toStop = True

		
def getJsonInfo():

	global macAddress
	global acqChannels
	global samplingRate
	global nSamples
	global digitalOutput


	with open('variables.json') as data_file:    
		data = json.load(data_file)
		for a in data :
			macAddress = a
			break

		
		

		for i in data[macAddress]["acqChannels"] :
			acqChannels.append(i-1)

		samplingRate =data[macAddress]["samplingRate"]
		nSamples = data[macAddress]["nSamples"]
		for i in data[macAddress]["digitalOutput"] :
			digitalOutput.append(int(i))


def stopDevice():
	global device 
	if device.started :
		try:
			device.stop()
			device.close()
			device = ""
		except Exception as e:
			print e
	else:	
		device.close()
		device = ""

def read_function():
	global toStop
	global device

	
	while True:
		
		if toStop :
			if type(device) == bitalino.BITalino :
				stopDevice()
			toStop = False

		elif len(connections) >= 1:

			if not type(device) == bitalino.BITalino :
				
				try :
					print "Chega aqui 1 "
					device = bitalino.BITalino(macAddress)
					print "Chega aqui 2 "
				except Exception as e:
					print e
					[client.get_connection().write_message("Could not connect to Bitalino !") for client in connections]
					
				
			else :
				try:
					if not device.started :
						print "here 1 "

						device.start(samplingRate,acqChannels)
						print "here 2"
						
					
					#data = json.dumps(device.read(nSamples).tolist())
					data = device.read(nSamples).tolist()
					
					
					#[client.get_connection().write_message(data[::client.get_divider()]) for client in connections]
					for client in connections :

						dataToSend = data[::client.get_divider()]

						dataToSend = json.dumps(dataToSend)

						client.get_connection().write_message(dataToSend)


				except Exception as e:
					
					
					[client.get_connection().write_message("Erro de coneccao") for client in connections]
					toStop = True


application = tornado.web.Application([
	(r'/ws', WSHandler),
])
 

if __name__ == "__main__":
	getJsonInfo()
	
	http_server = tornado.httpserver.HTTPServer(application)
	http_server.listen(65)
	t = threading.Thread(target=read_function)
	threads.append(t)
	t.start()
	print "Server On"
	tornado.ioloop.IOLoop.instance().start()