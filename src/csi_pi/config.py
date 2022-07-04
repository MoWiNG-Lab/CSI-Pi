import os
from time import time
from dotenv import load_dotenv
load_dotenv()


class Config:
    expt_name = os.environ['NAME']
    app_dir = os.environ['APP_DIR']
    shell_dir = f"{app_dir}/src/shell"
    data_dir = f"{app_dir}/storage/data/{time()}/"
    WRITE_CSI_LOCK = '/tmp/lock.write_csi.txt'

    # Baud Rate
    esp32_baud_rate = int(os.environ.get('ESP32_BAUD_RATE', 921600))
    acm_baud_rate = int(os.environ.get('ACM_BAUD_RATE', 115200))

    # Device Variables
    data_file_names = {}
    devices = []
    cameras = []

    # TTY-Plugins
    default_tty_plugins = """
    src.csi_pi.tty_plugins.csi_data_plugin
    src.csi_pi.tty_plugins.csipi_command_plugin
    """
    tty_plugins = [
        plugin.strip() for plugin in
        os.environ.get('TTY_PLUGINS', default_tty_plugins).strip().split("\n")
        if plugin[0] != "#" # any lines starting with `#` are comments and should be ignored
    ]

    # TODO : Camera Plugins -- not fully integrated, will do after video recording format is well tested.
    default_cam_plugins = """
    src.csi_pi.camera.plugins.video_recorder
    """
    cam_plugins = [
        plugin.strip() for plugin in os.environ.get('CAM_PLUGINS', default_tty_plugins).strip().split("\n")
        if plugin[0] != "#"  # any lines starting with `#` are comments and should be ignored
    ]
