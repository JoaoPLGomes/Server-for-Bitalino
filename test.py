
def info_loop(device,nSamples) :
	info = []
	# This example will collect data for 5 sec.
	
	# Start Acquisition
	
	try:

		info = device.read(nSamples)
		
	except Exception as e:
		
		raise e
		
	
	
	return info





'''
	while  (end - start) < running_time:
		# Read samples
		info.append(device.read(nSamples))
		
		end = time.time()
'''

