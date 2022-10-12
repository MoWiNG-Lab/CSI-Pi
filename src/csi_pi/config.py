import os
from time import time
from dotenv import load_dotenv
load_dotenv()


class Config:
    expt_name = os.environ['NAME']
    app_dir = os.environ['APP_DIR']
    shell_dir = f"{app_dir}/src/shell"
    data_dir = f"{app_dir}/storage/data/{time()}/"

    use_legacy_cam = (int(os.environ['USE_LEGACY_CAM']) == 1)

    is_to_start_photo_burst_at_startup = (int(os.environ['BEGIN_PHOTO_BURST_AT_STARTUP']) == 1)
    photo_burst_interval = int(os.environ['PHOTO_BURST_INTERVAL'])
    gdrive_photo_folder = os.environ['GDRIVE_PHOTO_FOLDER']

    is_to_start_video_at_startup_and_continue = (int(os.environ['BEGIN_VIDEO_AT_STARTUP_AND_CONTINUE']) == 1)
    video_chunk_length = int(os.environ['VIDEO_CHUNK_LENGTH_SEC'])
    video_start_time = int(os.environ['VIDEO_START_TIME'])
    video_end_time = int(os.environ['VIDEO_END_TIME'])

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
