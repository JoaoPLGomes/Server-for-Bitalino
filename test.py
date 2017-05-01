import bitalino, time




def info_loop() :
	info = ''
	# This example will collect data for 5 sec.
	macAddress = "20:15:05:29:21:00"
	running_time = 0.5
    
	batteryThreshold = 30
	acqChannels = [0, 1, 2, 3, 4, 5]
	samplingRate = 1000
	nSamples = 15
	digitalOutput = [1,1]

	# Connect to BITalino
	device = bitalino.BITalino(macAddress)

	# Set battery threshold
	#print device.battery(batteryThreshold)


	


	

	# Start Acquisition
	device.start(samplingRate, acqChannels)

	start = time.time()
	end = time.time()
	


	while  (end - start) < running_time:
		# Read samples
		info += str(device.read(nSamples))
		
		end = time.time()
	
	# Stop acquisition
	device.stop()
    
	# Close connection
	device.close()
	
	return info


