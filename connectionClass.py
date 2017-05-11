class Connection:
	
	def __init__(self, conection):
		self.sizeScreen = 2750
		self.connection = conection

	def get_sizeScreen(self):
		return self.sizeScreen

	def set_sizeScreen(self,sizeScreen):
		self.sizeScreen = int(sizeScreen)

	def get_connection(self):
		return self.connection

	def get_divider(self):
		return 2750 // self.get_sizeScreen()