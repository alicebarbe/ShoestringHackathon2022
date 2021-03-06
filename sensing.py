import time
import json
import board
import busio
import adafruit_ina260
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui
from pymongo import MongoClient
import numpy as np
import pandas as pd
import twilio_notif 

plotting = True

with open('sensor_config.json', 'r') as f:
    sensor_config = json.load(f)
uid = sensor_config["uid"]
#uid = 'currentSensor1'

# initialize graph things
if plotting:
    app = QtGui.QApplication([])
    win = pg.GraphicsWindow(title="Current")  # creates a window
    p = win.addPlot(title="Realtime plot")  # creates empty space for the plot in the window
    curve = p.plot()
    windowWidth = 500  # width of the window displaying the curve
    x = np.linspace(0, 0, windowWidth)  # create array that will contain the relevant time series
    ptr = -windowWidth  # set first x position

def update(value):
    """Update live QT plot with new value"""
    global curve, ptr, x
    ptr += 1  # update x position for displaying the curve
    x[:-1] = x[1:]  # shift data in the temporal mean 1 sample left
    try:
        x[-1] = float(value)  # vector containing the instantaneous values
    except:
        x[-1] = 0
    curve.setData(x)  # set the curve with this data
    curve.setPos(ptr, 0)  # set x position in the graph to 0

    QtGui.QApplication.processEvents()  # you MUST process the plot now

    
with open('credentials.json', 'r') as f:
    creds = json.load(f)
mongostr = creds["mongostr"]
client = MongoClient(mongostr)
db = client["shoestring"]
collection = db["rawdata"]

# find machine limits
machinelimits = pd.DataFrame(list(db["machinelimits"].find({"uid": uid})))
max_under_limit = int(machinelimits["maxunderlimit"])
max_over_limit = int(machinelimits["maxoverlimit"])
max_current = float(machinelimits["maxcurrent"])
min_current = float(machinelimits["mincurrent"])

i2c = busio.I2C(board.SCL, board.SDA)
ina260=adafruit_ina260.INA260(i2c)

old_time = time.time()

moving_values = np.zeros(20)
current_values = []
current_payload_list = []

notif_flag = True # to avoid spamming users repeatedly with texts

current_time = time.time()
new_time = time.time()
while True:
    #print("Current:", ina260.current)
    current_val = ina260.current
    current_values.append(current_val)
    moving_values = np.append(moving_values,current_val)
    moving_values = np.delete(moving_values,0)
    if plotting:
        #update(np.mean(moving_values))
        update(current_val)
    
    new_time = time.time()
    if new_time - current_time >= 60:
        current_payload_list.append(np.mean(current_values))
        payload = {"timestamp": new_time,
                   "current": np.mean(current_values),
                   "uid": uid}
        print(payload)
        result=collection.insert_one(payload)
        
        under_limit_flag = all(np.array(current_payload_list)[-max_under_limit:] < min_current)
        over_limit_flag = all(np.array(current_payload_list)[-max_over_limit:] > max_current)
        if under_limit_flag and notif_flag:
            twilio_notif.send_sms_to_all(f"{uid} is detecting downtime (under {min_current}mA for more than {max_under_limit}min).")
            notif_flag = False
        elif over_limit_flag and notif_flag:
                twilio_notif.send_sms_to_all(f"{uid} is detecting excess consumption (over {max_current}mA for more than {max_over_limit}min).")
                notif_flag = False
        elif not under_limit_flag and not over_limit_flag:
            notif_flag = True
                
        current_values = []
        current_time = time.time()
        
    time.sleep(0.05)