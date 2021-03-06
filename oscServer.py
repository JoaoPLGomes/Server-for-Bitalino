import OSC, threading, json,bitalino, numpy

macAddress = ""
acqChannels = []
samplingRate = 0
nSamples = 0
digitalOutput = []
device = ""
nStop = 0
#receive_address = ('192.168.1.5', 12035) 
send_address = '192.168.1.5', 8888
#send_address = '127.0.0.1', 8888
threads = [] #Array with threads
contador =  0

def getJsonInfo():

  global macAddress
  global acqChannels
  global samplingRate
  global nSamples
  global digitalOutput
  global nStop

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
    nStop = data[macAddress]["nStop"]



# simple send function for multiple arguments
def send_osc(addr, *stuff):
    msg = OSC.OSCMessage()
    msg.setAddress(addr)
    for item in stuff:
        msg.append(item)
    c.send(msg)


def stopDevice():
  global device 
  if type(device) == bitalino.BITalino :
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
  global device
  global contador
  global nStop
  zeros = [float(0.0)] * 21
  
  while True:
    

    if not type(device) == bitalino.BITalino :
        
      try :
        print "Chega aqui 1 "
        device = bitalino.BITalino(macAddress)
        print "Chega aqui 2 "
        contador = 0
      except Exception as e:
        print e 
        device = ""
        contador +=1
        if contador == nStop : 
          stopDevice()
          return;
          
        
    else :
      try:
        if not device.started :
          print "here 1 "

          device.start(samplingRate,acqChannels)
          print "here 2"
            
        
            #data = json.dumps(device.read(nSamples).tolist())
        data = device.read(nSamples)

        for i in range(0,nSamples,5):
          send_osc("/0/raw", zeros)
          send_osc("/0/bitalino",data[i,:].astype('float'))

      except Exception as e:

        print e
        device = ""
        contador +=1
        if contador == nStop : 
          stopDevice()
          return;




if __name__ == "__main__":
  getJsonInfo()
  # Initialize the OSC client.

  c = OSC.OSCClient()
  c.connect(send_address)
  t = threading.Thread(target=read_function)
  threads.append(t)
  t.start()
  print "SERVER ON"