# Functional Requirements:
# 1. The system shall be able to detect the location of the user (response time) - DONE
# 2. The system shall be able to detect the number of users at a particular location at the current time (throughput)
# 3. The system shall be able to get alerts of the location which is unpatrolled for a certain period. (response time)
import time
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request, render_template
import pandas as pd
from flask_caching import Cache

app = Flask(__name__)
app.config['CACHE_TYPE'] = 'simple'
cache = Cache(app)
cache.init_app(app)


@app.route('/')
def hello_world():
    global staffLocDict
    global roomList
    for key in roomList:
        roomList[key]['visit'] = 0
    currentTime = int(time.time())
    count = 0
    if bool(staffLocDict) is True:
        for key in staffLocDict:
            roomList[staffLocDict[key][0]['location']]['visit'] += 1
            roomList[staffLocDict[key][0]['location']]['lastvisit'] = staffLocDict[key][0]['timestamp']
            count += 1
    return render_template('dashboard.html', staffLocDict=staffLocDict, roomList=roomList, currentTime=currentTime,
                           time=time, count=count)


@app.route('/extractbeacon', methods=['GET'])
@cache.cached(timeout=10, query_string=True)
def get_beacon_info():
    beaconLocHAWCS = {}  # store latest beacon updates from android upon request from HAWCS server
    if 'start_time' in request.args:
        hawcs_start_time = int(request.args['start_time'])
        hawcs_end_time = int(request.args['end_time'])
        hawcs_staff_id = int(request.args['staff_id'])
        if hawcs_staff_id in staffLocDict:
            for key in staffLocDict[hawcs_staff_id]:
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
#@cache.cached(timeout=5, query_string=True)
def beaconinfo():
    # json_data = flask.request.json
    # timestamp = int(time.time())
    # staff_id = int(json_data["staffId"])
    # rssiInput = int(json_data["rssiInput"])
    # macInput = json_data["macInput"].replace(':', '')
    timestamp = int(time.time())
    staff_id = int(request.form["staffId"])
    rssiInput = int(request.form["rssiInput"])
    macInput = request.form["macInput"].replace(':', '')
    location, level = findLocationByMac(macInput)
    addNewRecord(staff_id, macInput, rssiInput, timestamp, location, level)
    return "200 OK"


# add record into beacon location list
def addNewRecord(staff_id, mac, rssi, timestamp, location, level):
    if staff_id in staffLocDict:
        staffLocDict[staff_id].insert(0,
                                      {'mac': mac, 'rssi': rssi, 'level': level, 'location': location,
                                       'timestamp': timestamp})
    else:
        staffLocDict[staff_id] = [
            {'mac': mac, 'rssi': rssi, 'level': level, 'location': location, 'timestamp': timestamp}]


# find location based on mac address:
def findLocationByMac(mac):
    global df_dict
    try:
        return df_dict[mac]['location'], df_dict[mac]['level']
    except:
        return None, None


# import location based on mac address from text file
def readBeaconLocations():
    readdata = pd.read_csv("beacon_locations.txt", names=["mac", "location", "level"], sep=": ", engine='python')
    df = pd.DataFrame(readdata)  # convert data into pandas dataframe
    df['location'] = df['location'].str.replace('\"', '')
    df['mac'] = df['mac'].str.replace('\"', '')
    df_dict = {}
    for i, row in df.iterrows():
        df_dict[row['mac']] = {'location': row['location'], 'level': row['level']}
    return df_dict, df


# initialise room visits:
def initRoomListVisits():
    global df
    global roomList
    for i, row in df.iterrows():
        if row['location'] in roomList:
            roomList[row['location']]['mac'].append(row['mac'])
        else:
            roomList[row['location']] = {'mac': [row['mac']], 'visit': 0, 'lastvisit': int(time.time())}


def clearStaffLocDictItem():
    for key, value in staffLocDict.items():
        del staffLocDict[key][1:]


# to be removed once done
# def simulatedAndroidData():
#     global simulated_mac
#     global staffLocDict
#     timestamp = int(time.time())
#     staff_id = random.randint(1, 10)
#     rssiInput = random.randint(-100, 0)
#     macInput = random.choice(simulated_mac['mac'])
#     location, level = findLocationByMac(macInput)
#     if rssiInput > -60:
#         if staff_id not in staffLocDict:
#             addNewRecord(staff_id, macInput, rssiInput, timestamp, location, level)
#         elif staffLocDict[staff_id][0]['location'] != location:
#             addNewRecord(staff_id, macInput, rssiInput, timestamp, location, level)


if __name__ == "__main__" or __name__ == "app":
    df_dict, df = readBeaconLocations()
    staffLocDict = {}  # store latest beacon updates from android
    roomList = {}
    initRoomListVisits()

    # to be remove once android part has been updated
    # import random
    #
    # simulated_mac = ["DE69F34B12FB", "ECAC7EDCDF93", "F68644A3A846", "E7F82CE7B318"]
    # readdata = pd.read_csv("beacon_locations.txt", names=["mac", "location", "level"], sep=": ")
    # simulated_mac = pd.DataFrame(readdata)  # convert data into pandas dataframe
    # simulated_mac['location'] = simulated_mac['location'].str.replace('\"', '')
    # simulated_mac['mac'] = simulated_mac['mac'].str.replace('\"', '')
    # sched_0 = BackgroundScheduler(daemon=True)
    # sched_0.add_job(simulatedAndroidData, 'interval', seconds=0.1)
    # sched_0.start()
    sched_1 = BackgroundScheduler(daemon=True)
    sched_1.add_job(clearStaffLocDictItem, 'interval', seconds=20)
    sched_1.start()
    ##################################################
    if __name__ == "__main__":
        app.run(host='0.0.0.0', port=5000)
