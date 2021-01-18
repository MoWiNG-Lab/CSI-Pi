import os
import subprocess
from time import time
from io import BytesIO
import zipfile

from starlette.applications import Starlette
from starlette.responses import PlainTextResponse, HTMLResponse, FileResponse
from starlette.routing import Route

data_dir = f"/home/pi/CSI-Pi/storage/data/{time()}/"
data_file_names = {}

print("DATA_DIR:", data_dir)

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
        subprocess.Popen(f"/bin/stty -F {d} 1500000".split(" "), stdout=subprocess.PIPE)
        
        data_file_names[d] = f"{data_dir}{d.split('/')[-1]}.csv"
        
        # Start listening for data rate
        subprocess.Popen(f"/bin/sh /home/pi/CSI-Pi/record_data_rate.sh {d} {data_file_names[d]}".split(" "), stdout=subprocess.PIPE)

        # Start listening for device and write data to file
        subprocess.Popen(f"/bin/sh /home/pi/CSI-Pi/load_and_save_csi.sh {d} {data_file_names[d]}".split(" "), stdout=subprocess.PIPE)

async def index(request):
    output = subprocess.Popen(["timeout", "0.5", "/bin/sh","/home/pi/CSI-Pi/status.sh",data_dir], stdout=subprocess.PIPE).communicate()[0]
    return HTMLResponse("<head><meta http-equiv='refresh' content='1'/></head> <body><pre style='white-space: pre-wrap;'>" + output.decode("utf-8") + "</pre><body>")


async def new_annotation(request):
    data_file_names['annotations'].write((",".join([
        'CURRENT_ACTION',
        'fake_uuid',
        str(int(time()*1000)),
        request.query_params['value'],
    ])) + "\n")
    data_file_names['annotations'].flush()
    return PlainTextResponse("OK")

async def get_data_directory(request):
    return PlainTextResponse(data_dir)

async def get_data_as_zip(request):
    filename = '/tmp/data.zip'
    file_path = data_dir
    
    with zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for f in os.listdir(file_path):
            if f != 'annotations.csv':
                zipf.write(os.path.join(file_path, f), f"{f}/{f}")
                zipf.write(os.path.join(file_path, 'annotations.csv'), f"{f}/annotations.csv")
            
    return FileResponse(filename, filename='CSI.zip')

setup()

routes = [
    Route("/", index),
    Route("/annotation", new_annotation, methods=['POST']),
    Route("/data-directory", get_data_directory),
    Route("/data", get_data_as_zip),
]

app = Starlette(routes=routes)
