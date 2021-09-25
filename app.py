from flask import Flask, render_template
from flask import request
from flask_ngrok import run_with_ngrok
from flask import Flask, request, Response
import pandas as pd

app = Flask(__name__)
run_with_ngrok(app)


@app.route('/')
def hello_world():
    return render_template('dashboard.html')


@app.route('/extractbeacon', methods=['GET'])
def get_beacon_info():
    # Possible parameters passed via URL
    # staff_id = 0
    # start_time = 1632192072
    # end_time = 1632192082
    # Change below logic/variables as needed. Currently matches 'template' in project brief
    # rssiInput, macInput = beaconinfo()
    if 'start_time' in request.args:
        start_time = int(request.args['start_time'])
        end_time = int(request.args['end_time'])
        staff_id = int(request.args['staff_id'])
        print("start time: " + str(start_time))
        print("end time: " + str(end_time))
        print("staff id: " + str(staff_id))
        payload_dict = {
            "location": [
                {
                    "level": 3,
                    "location": "ROOM 4",
                    "timestamp": start_time + 1
                },
                {
                    "level": 7,
                    "location": "SR7D",
                    "timestamp": start_time + 2
                },
                {
                    "level": 7,
                    "location": "ROOM 4",
                    "timestamp": start_time + 3
                }
            ]
        }
        return payload_dict


# retrieve beacon information from android phone (staff id, rssi and mac address)
@app.route("/beaconinfo", methods=["POST"])
def beaconinfo():
    staff_id = request.form["staffId"]
    rssiInput = request.form["rssiInput"]
    macInput = request.form["macInput"]
    addNewRecord(staff_id, rssiInput, macInput)
    print(beaconLocList)


# add record into beacon location list
def addNewRecord(staff_id, mac, rssi):
    beaconLocList.append({'staff_id': staff_id, 'mac': mac, 'rssi': rssi})


# import location based on mac address from text file
def readBeaconLocations():
    readdata = pd.read_csv("beacon_locations.txt", names=["mac", "location"], sep=":")
    df = pd.DataFrame(readdata)  # convert data into pandas dataframe
    # for i, row in df.iterrows():
    #    print(row['mac'], row['location'])
    return df


if __name__ == "__main__":
    df = readBeaconLocations()
    beaconLocList = []  # store latest beacon updates from android
    # beaconLocList.append({'staff_id': 1, 'mac': 'abcde1234', 'rssi': -55})
    app.run()
