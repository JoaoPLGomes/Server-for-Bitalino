import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import socket, test
from tornado import gen
import threading
from random import randint
import bitalino


macAddress = "20:15:05:29:21:00"
acqChannels = [0, 1, 2, 3, 4, 5]
samplingRate = 1000
nSamples = 250
digitalOutput = [1,1]

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

		try:
			self.write_message(message)
		except IOError as e:
			print e
			self.write_message('Connection Error: ' + str(e))
			


	def on_close(self):
		connections.remove(self)
		print 'Conn closed...'
		
		if len(connections) == 0 and type(device) == bitalino.BITalino:
			
			global toStop 
			toStop = True
			
			


def read_function():
	global toStop
	global device
	
	while True:
		
		if toStop :
			
			device.stop()
			toStop = False

		elif len(connections) >= 1:

			if not type(device) == bitalino.BITalino :
				
				try :
					device = bitalino.BITalino(macAddress)
				except Exception as e:
					[client.write_message(str(e)) for client in connections]
			 				
				
			else :
				try:
					if not device.started :

						device.start(samplingRate,acqChannels)
					
					data = device.read(nSamples)

					[client.write_message(str(data)) for client in connections]
        			
				except Exception as e:
					[client.write_message(str(e)) for client in connections]
    			
        	


application = tornado.web.Application([
	(r'/ws', WSHandler),
])
 

if __name__ == "__main__":
	http_server = tornado.httpserver.HTTPServer(application)
	http_server.listen(65)

	t = threading.Thread(target=read_function)
	threads.append(t)
	t.start()
	print "Server On"
	tornado.ioloop.IOLoop.instance().start()

        

