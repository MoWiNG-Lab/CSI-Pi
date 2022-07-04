import os

from src.csi_pi.camera.plugins.video_recorder import VideoRecorder
from src.csi_pi.config import Config


class Camera:

    def __init__(self, config: Config, device_path):
        self.video_recorder = VideoRecorder(config=config)
        self.device_path = device_path

    @staticmethod
    def get_connected_cameras():
        devices = []
        for d in os.listdir("/dev"):
            if "video" in d and len(d) < 7:
                devices.append("/dev/" + d)
        return sorted(devices)

    def start_recording(self, expt_name="", params=""):
        return self.video_recorder.start_recording(expt_name, params)

    def end_recording(self):
        return self.video_recorder.end_recording()

