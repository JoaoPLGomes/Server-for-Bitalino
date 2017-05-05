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
connections = set() #Clients that are connected
device = ""
toStop = False


class WSHandler(tornado.websocket.WebSocketHandler):
	
	

	def check_origin(self, origin):
		return True

	def open(self):
		connections.add(self)
		print 'New connection was opened'
		
		self.write_message("Conn!")


	
	def on_message(self, message):

		
		self.write_message(message)
		
			


	def on_close(self):
		connections.remove(self)
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
		except Exception as e:
			close()
			device = ""
	else:	
		device.close()
		device = ""

def read_function():
	global toStop
	global device

	
	while True:
		
		if toStop :
			
			stopDevice()
			toStop = False

		elif len(connections) >= 1:

			if not type(device) == bitalino.BITalino :
				
				try :
					print "Chega aqui 1 "
					device = bitalino.BITalino(macAddress)
					print "Chega aqui 2 "
				except Exception as e:
					
					[client.write_message("Could not connect to Bitalino !") for client in connections]

				
			else :
				try:
					if not device.started :
						print "here 1 "
						print samplingRate
						print acqChannels
						device.start(samplingRate,acqChannels)
						print "here 2"
					data = device.read(nSamples)
					print "here3"
					[client.write_message(str(data)) for client in connections]

				except Exception as e:
					print "ERRO"
					toStop = True
					[client.write_message(str(e)) for client in connections]


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