# Functional Requirements:
# 1. The system shall be able to detect the location of the user (response time) - DONE
# 2. The system shall be able to detect the number of users at a particular location at the current time (throughput)
# 3. The system shall be able to get alerts of the location which is unpatrolled for a certain period. (response time)
import time

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template
from flask import request
from flask_ngrok import run_with_ngrok
from flask import Flask, request, Response
import pandas as pd

app = Flask(__name__)
run_with_ngrok(app)


@app.route('/')
def hello_world():
    # cleanList()
    global beaconLocDict
    return render_template('dashboard.html', beaconLocDict=beaconLocDict)


def cleanList():
    global beaconLocDict
    for key in beaconLocDict:
        beaconLocDict[key] = sorted(beaconLocDict[key], key=lambda i: (i['timestamp']), reverse=True)


@app.route('/extractbeacon', methods=['GET'])
def get_beacon_info():
    beaconLocHAWCS = {}  # store latest beacon updates from android upon request from HAWCS server
    if 'start_time' in request.args:
        hawcs_start_time = int(request.args['start_time'])
        hawcs_end_time = int(request.args['end_time'])
        hawcs_staff_id = int(request.args['staff_id'])
        if hawcs_staff_id in beaconLocDict:
            for key in beaconLocDict[hawcs_staff_id]:
                print (key)
                if hawcs_start_time <key['timestamp'] < hawcs_end_time:
                    if 'location' in beaconLocHAWCS:
                        beaconLocHAWCS["location"].append(
                            {'level': key['level'], 'location': key['location'], 'timestamp': key['timestamp']})
                    else:
                        beaconLocHAWCS["location"] = [{'level': key['level'], 'location': key['location'], 'timestamp': key['timestamp']}]
    return beaconLocHAWCS


# retrieve beacon information from android phone (staff id, rssi and mac address)
@app.route("/beaconinfo", methods=["POST"])
def beaconinfo():
    timestamp = int(time.time())
    staff_id = request.form["staffId"]
    rssiInput = request.form["rssiInput"]
    macInput = request.form["macInput"]
    if rssiInput > -60:
        addNewRecord(staff_id, macInput, rssiInput, timestamp)
    print(beaconLocDict)


# add record into beacon location list
def addNewRecord(staff_id, mac, rssi, timestamp):
    global hawcs_staffLocReq
    global hawcs_staff_id
    global hawcs_start_time
    global hawcs_end_time
    global beaconLocDict
    # print(beaconLocDict)
    location, level = findLocationByMac(mac)
    if staff_id in beaconLocDict:
        beaconLocDict[staff_id].append(
            {'mac': mac, 'rssi': rssi, 'level': level, 'location': location, 'timestamp': timestamp})
        cleanList()  # sort by latest timestamp
    else:
        beaconLocDict[staff_id] = [
            {'mac': mac, 'rssi': rssi, 'level': level, 'location': location, 'timestamp': timestamp}]
        cleanList()  # sort by latest timestamp


# find location based on mac address:
def findLocationByMac(mac):
    for i, row in df.iterrows():
        if row['mac'] == mac:
            return row['location'], row['level']
    return None, None


# import location based on mac address from text file
def readBeaconLocations():
    readdata = pd.read_csv("beacon_locations.txt", names=["mac", "location", "level"], sep=":")
    df = pd.DataFrame(readdata)  # convert data into pandas dataframe
    # for i, row in df.iterrows():
    #     print(row['mac'], row['location'], row['level'])
    return df



# to be removed once done 
def simulatedAndroidData():
    global simulated_mac
    timestamp = int(time.time())
    staff_id = random.randint(0, 2)
    rssiInput = random.randint(-100, 0)
    macInput = random.choice(simulated_mac)
    if rssiInput > -60:
        addNewRecord(staff_id, macInput, rssiInput, timestamp)


if __name__ == "__main__":
    df = readBeaconLocations()
    beaconLocDict = {}  # store latest beacon updates from android
    roomList = {} # store
    import random
    simulated_mac = ["DE69F34B12FB", "ECAC7EDCDF93", "F68644A3A846"]
    sched_0 = BackgroundScheduler(daemon=True)
    sched_0.add_job(simulatedAndroidData, 'interval', seconds=1)
    sched_0.start()
    app.run()

# payload_dict = {
#     "location": [
#         {
#             "level": 3,
#             "location": "ROOM 4",
#             "timestamp": start_time + 1
#         },
#         {
#             "level": 7,
#             "location": "SR7D",
#             "timestamp": start_time + 2
#         },
#         {
#             "level": 7,
#             "location": "ROOM 4",
#             "timestamp": start_time + 3
#         }
#     ]
# }
