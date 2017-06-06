import OSC, threading, json,bitalino

macAddress = ""
acqChannels = []
samplingRate = 0
nSamples = 0
digitalOutput = []
device = ""
#receive_address = ('192.168.1.5', 12035) 
send_address = '192.168.1.5', 8000
threads = [] #Array with threads

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



# simple send function for multiple arguments
def send_osc(addr, *stuff):
    msg = OSC.OSCMessage()
    msg.setAddress(addr)
    for item in stuff:
        msg.append(item)
    c.send(msg)


def read_function():
  global device

  
  while True:
    

    if not type(device) == bitalino.BITalino :
        
      try :
        print "Chega aqui 1 "
        device = bitalino.BITalino(macAddress)
        print "Chega aqui 2 "
      except Exception as e:
        print e
        device = ""
          
        
    else :
      try:
        if not device.started :
          print "here 1 "

          device.start(samplingRate,acqChannels)
          print "here 2"
            
        
            #data = json.dumps(device.read(nSamples).tolist())
        data = device.read(nSamples).tolist()

        for i in range(0,nSamples,5):
          send_osc("/0/raw", [0] * 11)
          send_osc("/0/bitalino",data[i])

      except Exception as e:

        print e
        device = ""




if __name__ == "__main__":
  getJsonInfo()
  # Initialize the OSC client.

  c = OSC.OSCClient()
  c.connect(send_address)
  t = threading.Thread(target=read_function)
  threads.append(t)
  t.start()
  print "SERVER ON"