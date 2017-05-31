import json


class Connection:
	
	def __init__(self, conection):
		self.sizeScreen = 2750
		self.connection = conection
		self.macAddress = 0
		self.nSamples = 0
		with open('variables.json') as data_file:    
			data = json.load(data_file)
			for a in data :
				self.macAddress = a
				break
			self.nSamples = data[self.macAddress]["nSamples"]

	def get_sizeScreen(self):
		return self.sizeScreen

	def set_sizeScreen(self,sizeScreen):
		self.sizeScreen = int(sizeScreen)

	def get_connection(self):
		return self.connection

	def get_divider(self):
		if self.nSamples <= self.get_sizeScreen():
			return -1
		else:
			return self.nSamples // self.get_sizeScreen()
