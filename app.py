from flask import Flask

app = Flask(__name__)


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


if __name__ == '__main__':
    app.run()
