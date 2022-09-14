import os
import threading
import time
import traceback

from src.csi_pi.camera.plugins.photo_burst import PhotoBurst
from src.csi_pi.camera.plugins.video_recorder import VideoRecorder
from src.csi_pi.config import Config


# noinspection PyBroadException
class Camera:

    def __init__(self, config: Config, device_path):
        self.picam2 = None
        self.recording_thread = None
        self.config = config

        self.video_recorder = VideoRecorder(config=config)
        self.photo_burst = PhotoBurst(config=config)
        self.device_path = device_path

    @staticmethod
    def get_connected_cameras():
        devices = []
        for d in os.listdir("/dev"):
            if "video" in d and len(d) < 7:
                devices.append("/dev/" + d)
        return sorted(devices)

    def start_recording(self):
        # def threaded_recording():
        #     self.picam2 = Picamera2()
        #     video_config = self.picam2.video_configuration()
        #     self.picam2.configure(video_config)
        #     encoder = H264Encoder(10000000)
        #     os.makedirs(self.config.data_dir, exist_ok=True)
        #     self.picam2.start_recording(encoder, f"{self.config.data_dir}csi_session_{time.time()}.h264")
        #
        # if self.picam2 is not None:
        #     return "ERROR: Already recording using this camera! Please call '.../cam/end' API first."
        # try:
        #     self.recording_thread = threading.Thread(target=threaded_recording, name="Picamera2 Recording")
        #     self.recording_thread.start()
        #     return "OK"
        # except:
        #     return f"ERROR: {traceback.format_exc()}"
        return self.video_recorder.start_recording()

    def end_recording(self):
        # try:
        #     if self.recording_thread and self.recording_thread.isAlive():
        #         if self.picam2 is not None:
        #             self.picam2.stop_recording()
        #             ret = "OK"
        #         else:
        #             ret = "ERROR: No recording is on-going."
        #         self.recording_thread.finish()
        #         self.recording_thread = None
        #         return ret
        # except:
        #     return f"ERROR: {traceback.format_exc()}"
        return self.video_recorder.end_recording()

    def start_photo_burst(self, interval):
        return self.photo_burst.start_burst(interval)

    def end_photo_burst(self):
        return self.photo_burst.end_burst()


if __name__ == '__main__':
    cam = Camera(Config(), "/dev/video0")
    cam.start_recording()
    time.sleep(10)
    cam.end_recording()
