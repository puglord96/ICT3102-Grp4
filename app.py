from flask import Flask
from flask import request
from flask_ngrok import run_with_ngrok
from flask import Flask, request, Response

app = Flask(__name__)
run_with_ngrok(app)



@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/extractbeacon', methods=['GET'])
def get_beacon_info():
    # Possible parameters passed via URL
    # staff_id = 0
    # start_time = 1632192072
    # end_time = 1632192082

    # Change below logic/variables as needed. Currently matches 'template' in project brief
    if 'start_time' in request.args:
        start_time = int(request.args['start_time'])
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

@app.route("/debug", methods=["POST"])
def debug():
    rssiInput = request.form["rssiInput"]
    macInput = request.form["macInput"]
    print("rssi: ",rssiInput)
    print("mac: ",macInput)
    return "received"



app.run()
