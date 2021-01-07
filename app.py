import os
import subprocess
from time import time
from flask import Flask, request, send_file
from io import BytesIO
import zipfile

data_dir = f"/home/pi/CSI-Pi/storage/data/{time()}/"
data_file_names = {}
app = Flask(__name__)

print("DATA_DIR:", data_dir)

@app.before_first_request
def setup():
    # Create new directory each time the app is run
    os.makedirs(data_dir, exist_ok=True)

    # Add file for annotations
    data_file_names['annotations'] = open(data_dir + "annotations.csv","w+")
    data_file_names['annotations'].write("type,smartphone_id,timestamp,current_action\n")
    data_file_names['annotations'].flush()

    # Identify all connected devices
    devices = subprocess.Popen("/bin/sh /home/pi/CSI-Pi/get_devices.sh".split(" "), stdout=subprocess.PIPE).communicate()[0].decode('utf-8').split("\n")
    devices = [d for d in devices if d != '']

    # Start listening for devices and write data to file automatically
    print("Start listening for devices")
    for i,d in enumerate(devices):
        # Set baud rate
        subprocess.Popen(f"/bin/stty -F {d} 2000000".split(" "), stdout=subprocess.PIPE)
        
        data_file_names[d] = f"{data_dir}{d.split('/')[-1]}.csv"
        
        # Start listening for data rate
        subprocess.Popen(f"/bin/sh /home/pi/CSI-Pi/record_data_rate.sh {d} {data_file_names[d]}".split(" "), stdout=subprocess.PIPE)

        # Start listening for device and write data to file
        subprocess.Popen(f"/bin/sh /home/pi/CSI-Pi/load_and_save_csi.sh {d} {data_file_names[d]}".split(" "), stdout=subprocess.PIPE)

@app.route('/')
def index():
    output = subprocess.Popen(["timeout", "0.25", "/bin/sh","/home/pi/CSI-Pi/status.sh",data_dir], stdout=subprocess.PIPE).communicate()[0]
    return "<head><meta http-equiv='refresh' content='1'/></head> <body><pre style='white-space: pre-wrap;'>" + output.decode("utf-8") + "</pre><body>"


@app.route('/annotation', methods=['POST'])
def new_annotation():
    data_file_names['annotations'].write((",".join([
        'CURRENT_ACTION',
        'fake_uuid',
        str(int(time()*1000)),
        request.values.get('value'),
    ])) + "\n")
    data_file_names['annotations'].flush()
    return "OK"

@app.route('/data-directory')
def get_data_directory():
    return data_dir

@app.route('/data')
def get_data():
    file_name = 'data.zip'
    memory_file = BytesIO()
    file_path = data_dir
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
          for root, dirs, files in os.walk(file_path):
                    for file in files:
                              zipf.write(os.path.join(root, file))
    memory_file.seek(0)
    return send_file(memory_file,
                     attachment_filename=file_name,
                     as_attachment=True)

app.run(host='0.0.0.0', debug=True, port=8080)

