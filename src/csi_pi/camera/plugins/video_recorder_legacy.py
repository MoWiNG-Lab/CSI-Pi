import json
import os
import subprocess as sp
import threading
import time
from datetime import datetime
from threading import Thread

# noinspection PyUnresolvedReferences,PyPackageRequirements
from picamera import PiCamera

from src.csi_pi.config import Config


class VideoRecorderLegacy:

    def __init__(self, config: Config):
        self.config = config
        self.video_chunk_length_seconds = config.video_chunk_length
        self.fps = 15

        self.camera = PiCamera()
        self.camera.resolution = (840, 480)
        self.camera.framerate = self.fps
        self.camera.hflip = False
        self.camera.annotate_text_size = 12
        self.video_folder = f"{self.config.data_dir}videos_{time.time() * 1000}"
        self.current_video_file = None
        self.last_video_file = None
        self.last_mp4_file = None
        self.is_to_record = False
        self.video_postprocess = None

    def process_video_file(self):
        # 1. `ffmpeg` encode (e.g.: ffmpeg -r 15 -i video.h264 foo.mp4)
        mp4file = f"{self.last_video_file}"[0:f"{self.last_video_file}".rindex(".")] + ".mp4"
        cmd = f"nohup ffmpeg -r {self.fps} -i {self.last_video_file} {mp4file} -loglevel quiet && rm {self.last_video_file} &"
        print(f"process_video_file_in_bg: ffmpeg-cmd = {cmd}\n\n")
        self.video_postprocess = sp.Popen([cmd], shell=True)
        self.last_mp4_file = mp4file
        # 2. Upload to Google-Drive / Server (needed or not?)

    def start_recording(self):
        """Record for a specific duration into a file named by starting epoch, then record into another file
        while `ffmpeg` processing & uploading the previous file"""
        os.makedirs(self.video_folder, exist_ok=True)
        if not self.is_to_record:
            Thread(target=self.do_record, daemon=True, name='VideoRecordingDaemon').start()
        return json.dumps({'status': 'OK', 'folder': self.video_folder})

    def do_record(self):
        self.is_to_record = True
        while self.is_to_record:
            start = datetime.now()
            self.camera.annotate_text = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            self.current_video_file = f"{self.video_folder}/{int((time.time() * 1000))}.h264"
            print(f"\n\ndo_record: Started new record -> {self.current_video_file}")
            self.camera.start_recording(self.current_video_file)
            while self.is_to_record and (
                    (datetime.now() - start).seconds < self.video_chunk_length_seconds):
                self.camera.annotate_text = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                self.camera.wait_recording(0.2)
            print("do_record: Ended recording this chunk")
            self.camera.stop_recording()
            self.last_video_file = self.current_video_file
            Thread(target=self.process_video_file, daemon=True, name='VideoProcessorNonDaemon').start()
        print("do_record: Ended Recording Video\n")

    def end_recording(self):
        if self.is_to_record:
            self.is_to_record = False
        print(f"end_recording: self.is_to_record = {self.is_to_record}\n")
        return json.dumps({'status': 'OK', 'file': self.last_mp4_file})


if __name__ == '__main__':
    vrl = VideoRecorderLegacy(Config())
    vrl.video_chunk_length_seconds = 5
    print("-----------------Starting to record & then a 45s sleep ...-----------------")
    print(f"Return from start_recording: {vrl.start_recording()}")
    time.sleep(13)
    print("-----------------45s Timer is Up-----------------")
    vrl.end_recording()
    time.sleep(1)
