import os
from time import time
from dotenv import load_dotenv
load_dotenv()

class Config:
    app_dir = os.environ['APP_DIR']
    shell_dir = f"{app_dir}/src/shell"

    WRITE_CSI_LOCK = '/tmp/lock.write_csi.txt'
    data_dir = f"{app_dir}/storage/data/{time()}/"
    data_file_names = {}
    devices = None
    is_listening = False