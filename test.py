import bitalino, time




def enviar_info() :
	info = ''
	# This example will collect data for 5 sec.
	macAddress = "20:15:05:29:21:00"
	'''running_time = 5
    
	batteryThreshold = 30
	acqChannels = [0, 1, 2, 3, 4, 5]
	samplingRate = 1000
	nSamples = 10
	digitalOutput = [1,1]'''

	# Connect to BITalino
	device = bitalino.BITalino(macAddress)

	# Set battery threshold
	#print device.battery(batteryThreshold)

	# Read BITalino version
	device.version()
	

	info = device.state()

# Stop acquisition
	device.stop()
    
# Close connection
	device.close()
	return info
	'''

	# Start Acquisition
	device.start(samplingRate, acqChannels)

	start = time.time()
	end = time.time()
	


	while (end - start) < running_time:
		# Read samples
		print device.read(nSamples)
		end = time.time()
	'''
