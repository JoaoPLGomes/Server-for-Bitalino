import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import socket, test
from tornado import gen
import threading
'''
This is a simple Websocket Echo server that uses the Tornado websocket handler.
Please run `pip install tornado` with python of version 2.7.9 or greater to install tornado.
This program will echo back the reverse of whatever it recieves.
Messages are output to the terminal for debuggin purposes. 
''' 
threads = [] #Array with threads
connections = set() #Clients that are connected

class WSHandler(tornado.websocket.WebSocketHandler):
	
	

	def check_origin(self, origin):
		return True

	def open(self):
		connections.add(self)
		print 'New connection was opened'
		
		self.write_message("Conn!")


	
	def on_message(self, message):
		if message == ' receber':
			print  message
			self.write_message("Herro: " + message)

		else :
			try:
				self.write_message('' + str(test.enviar_info()))
			except IOError as e:
				print e
				self.write_message('Connection Error: ' + str(e))
			


	def on_close(self):
		connections.remove(self)
		print 'Conn closed...'




def read_function():
    while True:

    	if len(connections) >= 1:
			
        	data = test.info_loop()
        	print data
        
        	[client.write_message(data) for client in connections]


application = tornado.web.Application([
	(r'/ws', WSHandler),
])
 

if __name__ == "__main__":
	http_server = tornado.httpserver.HTTPServer(application)
	http_server.listen(65)
	t = threading.Thread(target=read_function)
	threads.append(t)
	t.start()
	tornado.ioloop.IOLoop.instance().start()


#[con.write_message('Hi!') for con in self.connections] -- Para enviar mensagens para todos os clientes !