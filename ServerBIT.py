from tornado import websocket, web, ioloop
import threading
import json
import signal
import sys
import numpy
import time
import sys, traceback, os
import bitalino
from os.path import expanduser
import OSC
import pystray
import datetime
from PIL import Image, ImageDraw
import logging
logging.basicConfig()



stateOSC = False
stateWS = False
stateOpenSignals = False
done = False
digitalIO = []
connection = False
exit_flag = threading.Event()
protocol = ""

# Generate an image
def create_image():
    # Generate an image and draw a pattern
    image = Image.open("logo.ico")
    return image

def on_clicked_OSC(icon, item):
    global stateWS
    global stateOSC
    global stateOpenSignals
    global done
    
    if stateOpenSignals :
        stateOpenSignals = False
        done = False
    else : 
        done = True
        if stateWS :
            print "WTF"
            stateWS = False
            done = False

        else : 
            done = True
    
    while not done : 
        print stateWS
       # print "Waiting for other protocols to close!"
    stateOSC = not item.checked
    if stateOSC :
        done = False
        home = expanduser("~") + '/desktop/serverBit'
        print home
        try:
            with open(home+'/config.json') as data_file:
                config = json.load(data_file)
        except Exception:
            with open('config.json') as data_file:
                config = json.load(data_file)
            os.mkdir(home)
            with open(home+'/config.json', 'w') as outfile:
                json.dump(config, outfile)
        signal.signal(signal.SIGINT, signal_handler)
        print "Using OSC protocol!"
        send_address = config['IP'] ,config['port']
        print send_address

        t=threading.Thread(target=read_function,args =('OSC',config['device'],config['nSamples'],config['sampling_rate'], config['channels'],config['retry_attemps'],config['labels'],send_address))
        t.start()
    else : 
        done = True
# Update the state in `on_clicked` and return the new state in
# a `checked` callable

def on_clicked_OPS(icon, item):
    global stateWS
    global stateOSC
    global stateOpenSignals
    global done
    
    if stateOSC :
        stateOSC = False
        done = False
    else : 
        done = True
        if stateWS :
            stateWS = False
            done = False
        else : 
            done = True
    
    while not done : 
        
        print "Waiting for other protocols to close!"

    stateOpenSignals = not item.checked
    if stateOpenSignals :
        done = False
        home = expanduser("~") + '/desktop/serverBit'
        print home
        try:
            with open(home+'/config.json') as data_file:
                config = json.load(data_file)
        except Exception:
            with open('config.json') as data_file:
                config = json.load(data_file)
            os.mkdir(home)
            with open(home+'/config.json', 'w') as outfile:
                json.dump(config, outfile)
        signal.signal(signal.SIGINT, signal_handler)
        print "Using OSC protocol with Opensignals!"
        send_address = config['IP'] ,config['port']
        print send_address

        t=threading.Thread(target=read_function,args =('OPENSIGNALS',config['device'],config['nSamples'],config['sampling_rate'], config['channels'],config['retry_attemps'],config['labels'],send_address))
        t.start()
    else : 
        done = True

def on_clicked_Websockets(icon, item):
    global stateWS
    global stateOSC
    global stateOpenSignals
    global done
    stateWS = not item.checked

    if stateOSC :
        stateOSC = False
        done = False
    else : 
        done = True
        if stateOpenSignals :
            stateOpenSignals = False
            done = False
        else : 
            done = True

    while not done : 
        
        print "Waiting for other protocols to close!"

        
    if stateWS :
        
        done = False
        home = expanduser("~") + '/desktop/serverBit'
        print home
        try:
            with open(home+'/config.json') as data_file:
                config = json.load(data_file)
        except Exception:
            with open('config.json') as data_file:
                config = json.load(data_file)
            os.mkdir(home)
            with open(home+'/config.json', 'w') as outfile:
                json.dump(config, outfile)
            for file in ['ClientBIT.html', 'jquery.flot.js', 'jquery.js']:
                with open(home+'/'+file, 'w') as outfile:
                    outfile.write(open(file).read())
        signal.signal(signal.SIGINT, signal_handler)
        
        print('Using Websockets')
        t=threading.Thread(target=BITalino_handler, args =(config['device'],config['channels'],config['sampling_rate'], config['labels']))
        t.start()
        Loopt=threading.Thread(target=startIOLoop)
        Loopt.start()
    else : 
        done = True
# Update the state in `on_clicked` and return the new state in
# a `checked` callable

def startIOLoop():
    ioloop.IOLoop.instance().start()

def stopIOLoop():
    loop = ioloop.IOLoop.instance()
    loop.add_callback(loop.stop)
    print "Asked Tornado to exit"

def on_clicked_exit(icon, item):
    os._exit(0)

def setup(icon):
    icon.visible = True


cl = []

def tostring(data):
    """
    :param data: object to be converted into a JSON-compatible `str`
    :type data: any
    :return: JSON-compatible `str` version of `data`
    
    Converts `data` from its native data type to a JSON-compatible `str`.
    """
    dtype=type(data).__name__
    if dtype=='ndarray':
        if numpy.shape(data)!=(): data=data.tolist() # data=list(data)
        else: data='"'+data.tostring()+'"'
    elif dtype=='dict' or dtype=='tuple':
        try: data=json.dumps(data)
        except: pass
    elif dtype=='NoneType':
        data=''
    elif dtype=='str' or dtype=='unicode':
        data=json.dumps(data)
    
    return str(data)


class SocketHandler(websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        if self not in cl:
            cl.append(self)
        print("CONNECTED")

    def on_message(self, message):
        self.write_message(u"You said: " + message)

    def on_close(self):
        if self in cl:
            cl.remove(self)
        print("DISCONNECTED")

def signal_handler(signal, frame):
    print('TERMINATED')
    sys.exit(0)

def BITalino_handler(mac_addr, ch_mask, srate, labels):
    #labels = ["'nSeq'", "'I1'", "'I2'", "'O1'", "'O2'", "'A1'", "'A2'", "'A3'", "'A4'", "'A5'", "'A6'"]
    ch_mask = numpy.array(ch_mask)-1
    global connection
    global stateWS 
    try:
        print(mac_addr)
        device=bitalino.BITalino(mac_addr)
        print(ch_mask)
        print(srate)
        device.start(srate, ch_mask)
        cols = numpy.arange(len(ch_mask)+5)
        print cols
        while stateWS:
            print "GFGFGFGFG"
            data=device.read(250)
            res = "{"
            for i in cols:
                idx = i
                if (i>4): idx=ch_mask[i-5]+5
                res += '"'+labels[idx]+'":'+tostring(data[:,i])+','
            res = res[:-1]+"}"
            if connection : 
                if len(cl)>0 : 
                    [con.write_message(res) for con in cl] 
                    print "SSS"
            else : [con.write_message(res) for con in cl]
        print "ASSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS"
        stopDevice(device)
        stateWS = False
        done = True
        stopIOLoop()
    except KeyboardInterrupt:
        print "Closing Program"
        os._exit(0)
    except Exception:
        traceback.print_exc()
        os._exit(0)


#Simple send function for multiple arguments
def send_osc(c,addr, *stuff):
    msg = OSC.OSCMessage()
    msg.setAddress(addr)
    for item in stuff:
        msg.append(item)
    c.send(msg)

#Stops the device if called
def stopDevice(device):
  
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


#Starts the device, receives the information from the device and sends that information to the address in the variable.json file
def read_function(protocolType,macAddress,nSamples,samplingRate,acqChannels,nStop,labels,send_address):
    global stateOSC
    global stateOpenSignals
    if protocolType == "OSC" or protocolType == "OPENSIGNALS":
            c = OSC.OSCClient()
            c.connect(send_address)
    if protocolType == "OSC":
        addr = "/" + macAddress + "/"
    zeros = [float(0.0)] * 21
    counter = 0
    device = ""
    global done
    print macAddress
    while stateOSC or stateOpenSignals:
        if done :
            print "Closing OSC protocol!"
            stopDevice(device)
            return;
        if not type(device) == bitalino.BITalino :
            try :
                device = bitalino.BITalino(macAddress)
                print "Connected to a device with the macAddress : " + str(macAddress)
            except Exception as e:
                print "Try number "+ str(counter +1) + " : " + str(e)
                counter +=1
                if counter == nStop : 
                    print "Number of tries reached, something went wrong!"
                    stopDevice(device)
                    return;
        else :
            try:
                if not device.started :
                    print type(samplingRate)
                    acqChannels[:] = [x-1 for x in acqChannels]
                    print type(acqChannels)
                    device.start(samplingRate,acqChannels)
                    textFile = createTextFile()
                data = device.read(nSamples)
                numpy.savetxt(textFile,data,fmt='%d',delimiter='    ',newline='\n')
                
                if sum(digitalIO)!=0: 
                    idx = numpy.ones(len(digitalIO))*-1

                    for i in numpy.arange(len(digitalIO)):
                        if (digitalIO[i]==1):
                            aux = numpy.where(data[:,i+1]==0)
                            print aux
                            if len(aux[0]) > 0 : idx[i] = aux[0]
                            if idx[i]>=0: digitalIO[i]-=1

                    print idx
                    idx.sort()
                    
                    if idx[-1] >=0: data=data[idx[-1]:,:]

                    if sum(digitalIO)!=0: continue
                
                
                if protocolType == "OPENSIGNALS":
                    for i in range(0,nSamples,5):
                        send_osc(c,"/0/raw", zeros)
                        send_osc(c,"/0/bitalino",data[i,:].astype('float'))
                elif protocolType == "OSC":

                    cols = numpy.arange(len(acqChannels)+5)
                    for i in cols:
                        #idx = i
                        #if (i>4): idx=acqChannels[i-5]+5
                        idx=(acqChannels[i-5]+5 if (i>4) else i)
                        send_osc(c,addr + labels[idx],data[:,i])

            except Exception as e:
                print "Try number "+ str(counter +1) + " : " + str(e)
                counter +=1
                if counter == nStop : 
                    stopDevice(device)
                    stateOSC = False
                    stateOpenSignals = False
                    textFile.close()
                    done = True
                    print "Number of tries reached, something went wrong!"
                    return;
    stopDevice(device)
    done = True
    print "OSC Closed"

def startServer():
    global digitalIO
    global protocol
    home = expanduser("~") + '/desktop/serverBit'
    print home
    try:
        with open(home+'/config.json') as data_file:
            config = json.load(data_file)
    except Exception:
        with open('config.json') as data_file:
            config = json.load(data_file)
        os.mkdir(home)
        with open(home+'/config.json', 'w') as outfile:
            json.dump(config, outfile)
    if type(config['acquisition_mode'])== list : 
        digitalIO.append(config['acquisition_mode'][0])
        digitalIO.append(config['acquisition_mode'][1])
    elif config['acquisition_mode'] == "connection_driven" : 
        digitalIO = [0,0]
        connection = True
    elif config['acquisition_mode'] == "startup" : 
        digitalIO = [0,0]
    else :
        print "Wrong acquisition mode, please check the configuration file !"
        os._exit(0)

    app = web.Application([(r'/', SocketHandler)])
    app.listen(config['port'])
    print digitalIO
    print config['acquisition_mode']
    
    if config['protocol'] == "OSC":
        protocol = "OSC"
    elif config['protocol'] == "OPS" : 
        protocol = "OPS"
    elif config['protocol'] == "WS":
        protocol = "WS"
    else : 
        print "Wrong protocol, please check the configuration file !"
        os._exit(0)
    print protocol

def createTextFile():
    home = expanduser("~") + '/desktop/serverBit'
    file = open(str(datetime.datetime.now()).replace(":","-")+ ".txt","w")
    file.write("# OpenSignals Text File Format\n")
    json_data = open(home+'/textHeader.json').read()
    print json_data
    file.write(json_data+"\n")
    file.write("# EndOfHeader\n")
    return file

def createJsonFile():
    home = expanduser("~") + '/desktop/serverBit'
    print home
    try:
        with open(home+'/config.json') as data_file:
            config = json.load(data_file)
    except Exception:
        with open('config.json') as data_file:
            config = json.load(data_file)
        os.mkdir(home)
        with open(home+'/config.json') as outfile:
            json.dump(config, outfile)

    data = {str(config['device']) : {
    "sensor": len(config['channels']) * ["RAW"],
    "device name" : str(config['device']), 
    "column":config['labels'],
    "sync interval": 2,
    "time": str(datetime.datetime.now().time()),
    "comments":"",
    "device connection": str(config['device']),
    "channels": config['channels'],
    "date" : str(datetime.datetime.today().date()),
    "mode": 0,
    "digital IO": config['labels'][0:len(config['labels'])-len(config['channels'])],
    "firmware version": "5.2",
    "device" : "bitalino_rev",
    "position" : 0,
    "sampling rate" : config['sampling_rate'],
    "label" : config['labels'][len(config['labels'])-len(config['channels']):],
    "resolution" : [4,1,1,1,1,10,10,10,10,6,6][:11 - (6 - len(config['channels']))],
    "special" : [{}] * len(config['channels'])
        }
    }
    
    with open(home+'/textHeader.json',"w") as outfile:
        json.dump(data, outfile)

if __name__ == '__main__':
    createJsonFile()
    startServer()
    if sys.platform == "win32":
        pystray.Icon('ServerBit', create_image(), menu=pystray.Menu(
        pystray.MenuItem(
            'OSC',
            on_clicked_OSC,
            checked=lambda item: stateOSC),
        pystray.MenuItem(
            'OpenSignals',
            on_clicked_OPS,
            checked=lambda item: stateOpenSignals),
        pystray.MenuItem(
            'WebSockets',
            on_clicked_Websockets,
            checked=lambda item: stateWS),
        pystray.MenuItem(
            'Exit',
            on_clicked_exit))).run()
    elif sys.platform == "linux" or sys.platform == "linux2":
        if protocol == "OSC" : 
            home = expanduser("~") + '/desktop/serverBit'
            print home
            try:
                with open(home+'/config.json') as data_file:
                    config = json.load(data_file)
            except Exception:
                with open('config.json') as data_file:
                    config = json.load(data_file)
                os.mkdir(home)
                with open(home+'/config.json', 'w') as outfile:
                    json.dump(config, outfile)
            signal.signal(signal.SIGINT, signal_handler)
            print "Using OSC protocol!"
            send_address = config['IP'] ,config['port']
            print send_address

            read_function('OSC',config['device'],config['nSamples'],config['sampling_rate'], config['channels'],config['retry_attemps'],config['labels'],send_address)
        elif protocol == "OPS":
            home = expanduser("~") + '/desktop/serverBit'
            print home
            try:
                with open(home+'/config.json') as data_file:
                    config = json.load(data_file)
            except Exception:
                with open('config.json') as data_file:
                    config = json.load(data_file)
                os.mkdir(home)
                with open(home+'/config.json', 'w') as outfile:
                    json.dump(config, outfile)
            signal.signal(signal.SIGINT, signal_handler)
            send_address = config['IP'] ,config['port']
            print send_address

            read_function('OPENSIGNALS',config['device'],config['nSamples'],config['sampling_rate'], config['channels'],config['retry_attemps'],config['labels'],send_address)
        elif protocol == "WS" : 
            home = expanduser("~") + '/desktop/serverBit'
            print home
            try:
                with open(home+'/config.json') as data_file:
                    config = json.load(data_file)
            except Exception:
                with open('config.json') as data_file:
                    config = json.load(data_file)
                os.mkdir(home)
                with open(home+'/config.json', 'w') as outfile:
                    json.dump(config, outfile)
            signal.signal(signal.SIGINT, signal_handler)

            BITalino_handler(config['device'],config['channels'],config['sampling_rate'],config['labels'])