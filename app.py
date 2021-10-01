# Functional Requirements:
# 1. The system shall be able to detect the location of the user (response time) - DONE
# 2. The system shall be able to detect the number of users at a particular location at the current time (throughput)
# 3. The system shall be able to get alerts of the location which is unpatrolled for a certain period. (response time)
import time

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template
import flask_profiler
from flask import Flask, request
import pandas as pd

app = Flask(__name__)
# app.config["flask_profiler"] = {
#     "enabled": True,
#     "storage": {
#     "engine": "mongodb"
#   },
#   "basicAuth":{
#     "enabled": True,
#     "username": "admin",
#     "password": "admin"
#   },
#   "ignore": [
#     "^/static/.*"
#   ]
# }
# flask_profiler.init_app(app)


@app.route('/')
def hello_world():
    global staffLocDict
    global roomList

    # conn.close()
    currentTime = int(time.time())
    return render_template('dashboard.html', staffLocDict=staffLocDict, roomList=roomList, currentTime=currentTime,
                           time=time)


@app.route('/extractbeacon', methods=['GET'])
# @flask_profiler.profile()
def get_beacon_info():
    beaconLocHAWCS = {}  # store latest beacon updates from android upon request from HAWCS server
    if 'start_time' in request.args:
        hawcs_start_time = int(request.args['start_time'])
        hawcs_end_time = int(request.args['end_time'])
        hawcs_staff_id = int(request.args['staff_id'])
        if hawcs_staff_id in staffLocDict:
            for key in staffLocDict[hawcs_staff_id]:
                print(key)
                if hawcs_start_time < key['timestamp'] < hawcs_end_time:
                    if 'location' in beaconLocHAWCS:
                        beaconLocHAWCS["location"].insert(0,
                                                          {'level': key['level'], 'location': key['location'],
                                                           'timestamp': key['timestamp']})
                    else:
                        beaconLocHAWCS["location"] = [
                            {'level': key['level'], 'location': key['location'], 'timestamp': key['timestamp']}]
    return beaconLocHAWCS


# retrieve beacon information from android phone (staff id, rssi and mac address)
@app.route("/beaconinfo", methods=["POST"])
# @flask_profiler.profile()
def beaconinfo():
    global staffLocDict
    timestamp = int(time.time())
    staff_id = int(request.form["staffId"])
    rssiInput = int(request.form["rssiInput"])
    macInput = request.form["macInput"].replace(':', '')
    location, level = findLocationByMac(macInput)
    if staff_id not in staffLocDict:
        addNewRecord(staff_id, macInput, rssiInput, timestamp, location, level)
    elif staffLocDict[staff_id][0]['location'] != location:
        addNewRecord(staff_id, macInput, rssiInput, timestamp, location, level)
    return "200 OK"


# add record into beacon location list
def addNewRecord(staff_id, mac, rssi, timestamp, location, level):
    global staffLocDict
    if staff_id in staffLocDict:
        staffLocDict[staff_id].insert(0,
                                      {'mac': mac, 'rssi': rssi, 'level': level, 'location': location,
                                       'timestamp': timestamp})
        updateRoomVisits(staff_id, location, timestamp)
    else:
        staffLocDict[staff_id] = [
            {'mac': mac, 'rssi': rssi, 'level': level, 'location': location, 'timestamp': timestamp}]
        updateRoomVisits(staff_id, location, timestamp)


# find location based on mac address:
def findLocationByMac(mac):
    for i, row in df.iterrows():
        if row['mac'] == mac:
            return row['location'], row['level']
    print(mac)
    return None, None


# import location based on mac address from text file
def readBeaconLocations():
    readdata = pd.read_csv("beacon_locations.txt", names=["mac", "location", "level"], sep=": ")
    df = pd.DataFrame(readdata)  # convert data into pandas dataframe
    df['location'] = df['location'].str.replace('\"', '')
    df['mac'] = df['mac'].str.replace('\"', '')
    # for i, row in df.iterrows():
    #     print(row['mac'], row['location'], row['level'])
    return df


# initialise room visits:
def initRoomListVisits():
    global df
    global roomList
    for i, row in df.iterrows():
        if row['location'] in roomList:
            roomList[row['location']]['mac'].append(row['mac'])
        else:
            roomList[row['location']] = {'mac': [row['mac']], 'visit': 0, 'lastvisit': int(time.time())}


# update room visits:
def updateRoomVisits(staff_id, location, timestamp):
    global staffLocDict
    global roomList
    # update number of staff
    if len(staffLocDict[staff_id]) > 1:
        # update number of staff in a room
        roomList[location]['visit'] += 1
        roomList[location]['lastvisit'] = timestamp

        # previous staff location
        room = staffLocDict[staff_id][1]['location']
        # minus visit
        roomList[room]['visit'] -= 1
    else:
        roomList[location]['visit'] += 1
        roomList[location]['lastvisit'] = timestamp
    # print(staffLocDict)


def clearstaffLocDictItem():
    global staffLocDict
    for key, value in staffLocDict.items():
        del staffLocDict[key][1:]


# to be removed once done
# def simulatedAndroidData():
#     global simulated_mac
#     global staffLocDict
#     timestamp = int(time.time())
#     staff_id = random.randint(1, 5)
#     rssiInput = random.randint(-100, 0)
#     macInput = random.choice(simulated_mac['mac'])
#     location, level = findLocationByMac(macInput)
#     if rssiInput > -60:
#         if staff_id not in staffLocDict:
#             addNewRecord(staff_id, macInput, rssiInput, timestamp, location, level)
#         elif staffLocDict[staff_id][0]['location'] != location:
#             addNewRecord(staff_id, macInput, rssiInput, timestamp, location, level)


if __name__ == "__main__" or __name__ == "app":
    df = readBeaconLocations()
    staffLocDict = {}  # store latest beacon updates from android
    roomList = {}
    initRoomListVisits()

    # to be remove once android part has been updated
    # import random
    # simulated_mac = ["DE69F34B12FB", "ECAC7EDCDF93", "F68644A3A846", "E7F82CE7B318"]
    # readdata = pd.read_csv("beacon_locations.txt", names=["mac", "location", "level"], sep=": ")
    # simulated_mac = pd.DataFrame(readdata)  # convert data into pandas dataframe
    # simulated_mac['location'] = simulated_mac['location'].str.replace('\"', '')
    # simulated_mac['mac'] = simulated_mac['mac'].str.replace('\"', '')
    # sched_0 = BackgroundScheduler(daemon=True)
    # sched_0.add_job(simulatedAndroidData, 'interval', seconds=0.5)
    # sched_0.start()
    sched_1 = BackgroundScheduler(daemon=True)
    sched_1.add_job(clearstaffLocDictItem, 'interval', seconds=20)
    sched_1.start()
    ##################################################
    if __name__ == "__main__":
        app.run(threaded=True, host='0.0.0.0', port=5000)
