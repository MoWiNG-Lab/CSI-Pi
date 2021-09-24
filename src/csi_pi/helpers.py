import os
import subprocess
import psutil

from src.csi_pi.config import Config


def start_listening(config: Config):
    if config.is_listening:
        return False

    print("Start Listening")
    config.is_listening = True

    # Identify all connected devices
    devices = sorted(["/dev/" + d for d in os.listdir("/dev") if "ttyUSB" in d])
    print("Got devices", devices)

    # Start listening for devices and write data to file automatically
    print("Start listening for devices")
    for i, d in enumerate(devices):
        # Set baud rate
        subprocess.Popen(f"/bin/stty -F {d} 921600".split(" "), stdout=subprocess.PIPE)

        config.data_file_names[d] = f"{config.data_dir}{d.split('/')[-1]}.csv"

        # Start listening for device, write data to file, and record data rate
        subprocess.Popen(f"/usr/bin/python3 {config.app_dir}/src/csi_pi/tty_listener.py {d} {config.data_file_names[d]}".split(" "),
                         stdout=subprocess.PIPE, preexec_fn=os.setsid)


def stop_listening(config: Config):
    if not config.is_listening:
        return False

    print("Stop Listening")
    config.is_listening = False

    kill_child_processes()


def setup_app(config: Config):
    print("DATA_DIR:", config.data_dir)

    # Create new directory each time the app is run
    os.makedirs(config.data_dir, exist_ok=True)

    # Add file for annotations
    config.data_file_names['annotations'] = open(config.data_dir + "annotations.csv", "w+")
    config.data_file_names['annotations'].write("type,smartphone_id,timestamp,current_action\n")
    config.data_file_names['annotations'].flush()

    start_listening(config)

    toggle_csi(config, "1")


def toggle_csi(config: Config, value):
    with open(config.WRITE_CSI_LOCK, 'w') as f:
        f.write(value)


def kill_child_processes():
    # When the python process is killed (at exit), clean up all existing child processes)
    pid = os.getpid()
    for child in psutil.Process(pid).children(recursive=True):
        try:
            child.kill()
        except:
            pass
