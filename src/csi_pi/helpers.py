import os
import subprocess
import psutil
import datetime

from src.csi_pi.config import Config

class Device:
    process = None

    def __init__(self, device_path):
        self.device_path = device_path

    def start_listening(self, config):
        subprocess.Popen(f"/bin/stty -F {self.device_path} 921600".split(" "), stdout=subprocess.PIPE)
        p = subprocess.Popen(
            f"/usr/bin/python3 {config.app_dir}/src/csi_pi/tty_listener.py {self.device_path} {config.data_file_names[self.device_path]} {config.data_file_names['experiment_name']}".split(" "),
            env={
                'PYTHONPATH': os.environ.get('PYTHONPATH', '') + f":{config.app_dir},",
            },
            stdout=subprocess.PIPE, preexec_fn=os.setsid)
        self.process = p

    def stop_listening(self, config):
        if self.process and self.process.pid:
            psutil.Process(self.process.pid).kill()



def start_listening(config: Config):
    config.is_listening = True

    # Identify all connected devices
    currently_connected_devices = sorted(["/dev/" + d for d in os.listdir("/dev") if "ttyUSB" in d])

    # Remove newly disconnected devices
    for d in config.devices:
        if d.device_path not in currently_connected_devices:
            print("Device no longer detected:", d.device_path)
            print("Removing device from list.")
            del config.data_file_names[d.device_path]
            d.stop_listening(config)
            config.devices.remove(d)

    # Add newly discovered devices
    for i, device_path in enumerate(currently_connected_devices):
        if device_path not in [d.device_path for d in config.devices]:
            print("New device detected:", device_path)
            device = Device(device_path=device_path)
            config.data_file_names[device_path] = f"{config.data_dir}{device_path.split('/')[-1]}.csv"
            device.start_listening(config)
            config.devices.append(device)


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

    # Add file for experiment_name
    now = datetime.datetime.today()
    now_str = f"{now.year}_{now.month}_{now.day}__{now.hour:02}_{now.minute:02}_{now.second:02}"
    config.data_file_names['experiment_name'] = config.data_dir + "experiment_name.txt"
    f = open(config.data_file_names['experiment_name'], "w+")
    f.write(f"default_experiment_name__{now_str}")
    f.flush()

    # Add file for notes
    config.data_file_names['notes'] = config.data_dir + "notes.txt"
    f = open(config.data_file_names['notes'], "w+")
    f.write("Empty Note")
    f.flush()

    toggle_csi(config, "1")


def load_from_file(file_name):
    output = ""

    if os.path.exists(file_name):
        f = open(file_name, 'r')
        output = f.read()
        f.close()

    return output


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
