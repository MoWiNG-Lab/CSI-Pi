import os
import subprocess
import signal
from time import time, sleep
from io import BytesIO
import zipfile
import atexit
import psutil

from starlette.applications import Starlette
from starlette.responses import PlainTextResponse, HTMLResponse, FileResponse
from starlette.routing import Route

data_dir = f"/home/pi/CSI-Pi/storage/data/{time()}/"
data_file_names = {}

print("DATA_DIR:", data_dir)

processes = []
is_listening = False

def start_listening():
    global is_listening, processes
    if is_listening:
        return False

    print("Start Listening")
    is_listening = True

    # Identify all connected devices
    devices = subprocess.Popen("/bin/sh /home/pi/CSI-Pi/get_devices.sh".split(" "), stdout=subprocess.PIPE).communicate()[0].decode('utf-8').split("\n")
    devices = [d for d in devices if d != '']

    print("Got devices", devices)

    # Start listening for devices and write data to file automatically
    print("Start listening for devices")
    for i,d in enumerate(devices):
        # Set baud rate
        subprocess.Popen(f"/bin/stty -F {d} 1500000".split(" "), stdout=subprocess.PIPE)
        
        data_file_names[d] = f"{data_dir}{d.split('/')[-1]}.csv"
        
        # Start listening for data rate
        p = subprocess.Popen(f"/bin/sh /home/pi/CSI-Pi/record_data_rate.sh {d} {data_file_names[d]}".split(" "), stdout=subprocess.PIPE, preexec_fn=os.setsid)
        processes.append(p)

        # Start listening for device and write data to file
        p = subprocess.Popen(f"/bin/sh /home/pi/CSI-Pi/load_and_save_csi.sh {d} {data_file_names[d]}".split(" "), stdout=subprocess.PIPE, preexec_fn=os.setsid)
        processes.append(p)

def stop_listening():
    global is_listening, processes
    if not is_listening:
        return False

    print("Stop Listening")
    is_listening = False

    kill_child_processes()

def setup():
    # Create new directory each time the app is run
    os.makedirs(data_dir, exist_ok=True)

    # Add file for annotations
    data_file_names['annotations'] = open(data_dir + "annotations.csv","w+")
    data_file_names['annotations'].write("type,smartphone_id,timestamp,current_action\n")
    data_file_names['annotations'].flush()

    start_listening()

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
                d = f.replace(".csv", "")
                zipf.write(os.path.join(file_path, f), f"{d}/{f}")
                zipf.write(os.path.join(file_path, 'annotations.csv'), f"{d}/annotations.csv")
            
    return FileResponse(filename, filename='CSI.zip')

async def power_up(request):
    start_listening()
    return PlainTextResponse("OK")

async def power_down(request):
    stop_listening()
    return PlainTextResponse("OK")

def kill_child_processes():
    global processes

    pid = os.getpid()
    print(pid, psutil.Process(pid).children(recursive=True))


    for child in psutil.Process(pid).children(recursive=True):
            child.kill()

    processes = []


# When the python process is killed (at exit), clean up all existing child processes)
atexit.register(kill_child_processes)

setup()

routes = [
    Route("/", index),
    Route("/annotation", new_annotation, methods=['POST']),
    Route("/data-directory", get_data_directory),
    Route("/data", get_data_as_zip),
    Route("/power_up", power_up, methods=['POST']),
    Route("/power_down", power_down, methods=['POST']),
]

app = Starlette(routes=routes)
