
import os
from flask import Flask, render_template, abort, url_for, json, jsonify
import json

app = Flask(__name__)

# read file

@app.route("/")
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
