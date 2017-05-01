import bitalino, time



def info_loop() :
	info = []
	# This example will collect data for 5 sec.
	macAddress = "20:15:05:29:21:00"
	running_time = 1
    
	batteryThreshold = 30
	acqChannels = [0, 1, 2, 3, 4, 5]
	samplingRate = 1000
	nSamples = 250
	digitalOutput = [1,1]

	# Connect to BITalino
	device = bitalino.BITalino(macAddress)

	# Start Acquisition
	device.start(samplingRate, acqChannels)

	start = time.time()
	end = time.time()
	info = device.read(nSamples)	

	
	# Stop acquisition
	device.stop()
    
	# Close connection
	device.close()
	
	return info





'''
	while  (end - start) < running_time:
		# Read samples
		info.append(device.read(nSamples))
		
		end = time.time()
'''