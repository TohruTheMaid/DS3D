import tkinter as tk
import json, threading, signal, sys, variables, os, time
from tkinter import *
from pypresence import Presence

from ctypes import *                             # stuff needed to get the hp
from time import sleep


def makeNewEmptyJSON():
    try:
        with open(variables.sendToDir + "/DS3C/path.json") as a:     # reads json that directs to rest of data
            path = json.load(a)
    except:
        with open(variables.sendToDir + "/DS3C/path.json", "w+") as a:     # if it doesnt exist, make it and make path for savepath same as exe
            path = "./"
            json.dump(path, a)

    variables.fileName = "DS3C_Savedata"
    variables.actualData = 0
    variables.colourCodeFont = "white"
    variables.colourCodeBack = "green"
    variables.txtFont = "Comic Sans MS"
    variables.jsonData['deaths'] = variables.actualData               # creates a dict with data we need to save
    variables.jsonData['font colour'] = variables.colourCodeFont
    variables.jsonData['background colour'] = variables.colourCodeBack
    variables.jsonData['font'] = variables.txtFont
    variables.JSON.writeToJSONFile(path, variables.fileName, variables.jsonData)

try:
    with open(variables.sendToDir + "/DS3C/ftb.json") as a:     # first time boot
        ftb = json.load(a)
except:
    if not os.path.exists(variables.sendToDir + "/DS3C"):
        os.makedirs(variables.sendToDir + "/DS3C")
        with open(variables.sendToDir + "/DS3C/ftb.json", "w+") as a:
            ftb = json.dump("This is a dummy file. Only its presence is checked and not its content :). Thanks for poking around in the files though.", a)
            variables.info.infoBox(event=None)
    else:
        with open(variables.sendToDir + "/DS3C/ftb.json", "w+") as a:
            ftb = json.dump("This is a dummy file. Only its presence is checked and not its content :). Thanks for poking around in the files though.", a)
            variables.info.infoBox(event=None)

try:
    with open(variables.sendToDir + "/DS3C/path.json") as a:     # 'sendToDir' holds path to savedata json (sendToDir is in %appdata%)
        variables.path = json.load(a)
    with open(variables.path  + "/" "DS3C_Savedata.json") as f:     # opens savedata json with the rest of the save data
        readData = json.load(f)
except:
    makeNewEmptyJSON()
    with open(variables.path + "/DS3C_Savedata.json") as f:     # makes default json and then reads it
        readData = json.load(f)    
    
    whoopsRoot = Tk()
    whoopsRoot.title("Oops")                                    
    whoopsRoot.iconbitmap(variables.resource_path("iconds3.ico"))
    WhoopsCanvas = tk.Canvas(whoopsRoot, width = 340, height = 100)  # window to say data has been reset to default.
    WhoopsCanvas.pack()  
    labelWhoops = tk.Label(whoopsRoot, text= "Sorry. Your data couldn't be loaded, \n so it has been reset to default.", font=("Courier", 10))   
    WhoopsCanvas.create_window(170, 50, window=labelWhoops)
    whoopsRoot.mainloop()                                 

if(len(readData) < 1):
    makeNewEmptyJSON()          # if the json is present in file directory but empty, make new default one.
else:
    variables.actualData = readData['deaths']
    variables.colourCodeFont = readData['font colour']                    # otherwise, assign json values to data.
    variables.colourCodeBack = readData['background colour']
    variables.txtFont = readData['font']

client_id = '921746813529256009'  # client id
RPC = Presence(client_id,pipe=0)  # Initialize the client class
RPC.connect() # Start the handshake loop
start_time=time.time()

def incrementDeaths():
            variables.actualData += 1                                         
            sleep(0.01)           # sleep to make sure it doesnt increment more than once

def HP():
    loopOnce = True
    while True:
        try:
            # this code and the process_interface class belong to a man called 'Random Davis' on YT (~650 subs) and randomdavis on github. Super thanks sir for making this - ily :).
            base_address = 0x140000000                   # getting hp from ds3 (multi level pointers)
            step8_pointer_address = 0x004768E78
            step8_static_address = c_uint64(base_address + step8_pointer_address)
            step8_base_pointer_val = c_uint64.from_buffer(variables.process.read_memory(step8_static_address, buffer_size =8)).value                
            step8_pointer_val_1 = c_uint64.from_buffer(variables.process.read_memory(c_uint64(step8_base_pointer_val + 0x80), buffer_size=8)).value
            step8_pointer_val_2 = c_uint64.from_buffer(variables.process.read_memory(c_uint64(step8_pointer_val_1 + 0x1f90), buffer_size=8)).value
            step8_pointer_val_3 = c_uint64.from_buffer(variables.process.read_memory(c_uint64(step8_pointer_val_2 + 0x18), buffer_size=8)).value
            step8_final_val = c_uint32.from_buffer(variables.process.read_memory(c_uint64(step8_pointer_val_3 + 0xD8), buffer_size=8)).value
            while(loopOnce and variables.connectedToGame):
                originalHealth = step8_final_val                    # grabs the initial health value
                loopOnce = False 
            if (abs(originalHealth - step8_final_val) >= 7 and originalHealth > step8_final_val):
                incrementDeaths()                               # if health decreases by more than 7, increment 'deaths' (too lazy to change variable name to hits)
                originalHealth = step8_final_val
            originalHealth = step8_final_val
            sleep(0.01)
        except:             
            sleep(0.01)                      # so the program doesnt throttle

def gameReconnect():
    while True:    # function to reconnect program after it disconnects (every 10 seconds)
        while(not variables.connectedToGame and variables.lookForGame): 
            variables.process.open(name = 'DarkSoulsIII')
            sleep(10)         
        sleep(0.01)      # stop throttling please

def updatePresence():
    while True:  # The presence will stay on as long as the program is running
        RPC.update(large_image="large-image", large_text="DARK SOULS III", start = start_time, details="Hits: " + str(variables.actualData))
        time.sleep(1) # Can only update rich presence every second

def signalHandler(signum, frame):
    sys.exit                                 # make sure threads are all closed
signal.signal(signal.SIGINT, signalHandler)

t1 = threading.Thread(target=HP)
t1.daemon = True                  # created it in a new thread because I said so.
t1.start()

t2 = threading.Thread(target=gameReconnect)
t2.daemon = True          # shutup I'll create a new thread if I want
t2.start()

t3 = threading.Thread(target=updatePresence)
t3.daemon = True          # another thread, another day. I do what I want.
t3.start()

class App():

    
    def __init__(self):

        self.root = tk.Tk()
        self.root.title("ds3 hit count")                                # setup
        self.root.geometry("750x200")       
        self.root.iconbitmap(variables.resource_path("iconds3.ico"))

        self.label = tk.Label(text= "hits: " + str(variables.actualData), font=(variables.txtFont, 100))
        self.label.config(bg=variables.colourCodeBack, fg=variables.colourCodeFont)       
        self.label.pack(pady=21)                                          # thanks imani
        self.root.bind("<y>", variables.options.optionsMenu)
        self.root.bind("<Y>", variables.options.optionsMenu)  # press y to open a window > look at OptionsMenu.py
        self.root.bind("<i>", variables.info.infoBox)  
        self.root.bind("<I>", variables.info.infoBox)  # info box (i)
        self.root.config(bg="green")
        self.update_clock()                                             # function to update stuff
        self.root.mainloop()

    def update_clock(self):

        self.label.configure(text= "hits: " + str(variables.actualData), font=(variables.txtFont, 100))
        variables.jsonData['deaths'] = variables.actualData
        variables.jsonData['font colour'] = variables.colourCodeFont
        variables.jsonData['background colour'] = variables.colourCodeBack   # json data continously checked for changes
        variables.jsonData['font'] = variables.txtFont
        self.label.config(bg=variables.colourCodeBack, fg=variables.colourCodeFont) # also checked continously for changes
        self.root.config(bg=variables.colourCodeBack)
        variables.JSON.writeToJSONFile(variables.path, variables.fileName, variables.jsonData)       # always updates json
        self.root.after(100, self.update_clock)

app=App()
