import os
from time import time
from dotenv import load_dotenv
load_dotenv()


class Config:
    expt_name = os.environ['NAME']
    app_dir = os.environ['APP_DIR']
    hostname = os.environ['HOSTNAME']
    shell_dir = f"{app_dir}/src/shell"
    data_dir = f"{app_dir}/storage/data/{time()}/"

    use_legacy_cam = (int(os.environ['USE_LEGACY_CAM']) == 1)
    cam_mode = str(os.environ['CAM_MODE'])
    CAM_MODE_PHOTO_BURST = "photo_burst"
    CAM_MODE_VIDEO_CONTINUALLY = "continuous_video"
    CAM_MODE_VIDEO_SCHEDULED = "scheduled_video"

    photo_burst_interval = int(os.environ['PHOTO_BURST_INTERVAL'])
    gdrive_photo_folder = os.environ['GDRIVE_PHOTO_FOLDER']

    video_chunk_length = int(os.environ['VIDEO_CHUNK_LENGTH_SEC'])
    video_start_time = int(os.environ['VIDEO_START_TIME'])
    video_end_time = int(os.environ['VIDEO_END_TIME'])

    WRITE_CSI_LOCK = '/tmp/lock.write_csi.txt'

    navigation = {
        x.split(',')[0]: x.split(',')[1]
        for x in os.environ.get('NAVIGATION', '').replace("HOSTNAME", hostname).strip().split("\n")
    }

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
        if plugin[0] != "#"  # any lines starting with `#` are comments and should be ignored
    ]

    # TODO : Camera Plugins -- not fully integrated, will do after video recording format is well tested.
    default_cam_plugins = """
    src.csi_pi.camera.plugins.video_recorder
    """
    cam_plugins = [
        plugin.strip() for plugin in os.environ.get('CAM_PLUGINS', default_tty_plugins).strip().split("\n")
        if plugin[0] != "#"  # any lines starting with `#` are comments and should be ignored
    ]
