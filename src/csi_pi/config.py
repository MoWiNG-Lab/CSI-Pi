import os
from time import time
from dotenv import load_dotenv
load_dotenv()

class Config:
    app_dir = os.environ['APP_DIR']
    shell_dir = f"{app_dir}/src/shell"

    esp32_baud_rate = int(os.environ.get('ESP32_BAUD_RATE', 921600))
    acm_baud_rate = int(os.environ.get('ACM_BAUD_RATE', 115200))

    tty_plugins = os.environ.get('TTY_PLUGINS', "src.csi_pi.tty_plugins.csi_data_plugin").strip().split("\n")

    WRITE_CSI_LOCK = '/tmp/lock.write_csi.txt'
    data_dir = f"{app_dir}/storage/data/{time()}/"
    data_file_names = {}
    devices = []
    is_listening = False
