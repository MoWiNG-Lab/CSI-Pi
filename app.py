import os
import subprocess
from time import time
from flask import Flask, request

data_dir = None
data_file_names = {}
app = Flask(__name__)


@app.before_first_request
def setup_files():
    # Create new directory each time the app is run
    # data_dir = f"storage/data/{time()}
    data_dir = f"storage/data/example/"
    os.makedirs(data_dir, exist_ok=True)

    # Add file for annotations
    data_file_names['annotations'] = open(data_dir + "annotations.csv","w+")
    data_file_names['annotations'].write("type,smartphone_id,timestamp,current_action\n")
    data_file_names['annotations'].flush()

    # Identify all connected devices
    devices = ["app.py", "storage/data/.gitignore"]  # TODO:

    # Start listening for devices and write data to file automatically
    for i,d in enumerate(devices):
        data_file_names[d] = f"{data_dir}{i}.csv"
        subprocess.Popen(f"sh run.sh {d} {data_file_names[d]}".split(" "), stdout=subprocess.PIPE)

@app.route('/')
def index():
    return "Return Stats Here..."


@app.route('/annotation', methods=['POST'])
def new_annotation():
    data_file_names['annotations'].write((",".join([
        'CURRENT_ACTION',
        'fake_uuid',
        str(int(time()*1000)),

        request.values.get('value'),
    ])) + "\n")
    data_file_names['annotations'].flush()
    print(request.values.get('value'))
    print(request.values.get('something'))
    return "OK"

