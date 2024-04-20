import json
import os
import subprocess as sp
import time
from datetime import datetime
from threading import Thread

# noinspection PyPackageRequirements
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder

from src.csi_pi.config import Config


class VideoRecorder2:

    def __init__(self, config: Config):
        self.video_chunk_length_seconds = config.video_chunk_length
        self.fps = 15.0
        print(config.data_dir)
        self.video_folder = f"{config.data_dir}videos_{time.time() * 1000}"

        self.picam2 = Picamera2()
        self.picam2.video_configuration.controls.FrameRate = self.fps
        video_config = self.picam2.create_video_configuration(
            main={"size": [dim // 2 for dim in self.picam2.sensor_resolution]},
            # controls={"FrameDurationLimits": (40000, 40000)}, # fps=1000000/FDL
            lores={"size": (840, 480)}, encode="lores")
        self.picam2.configure(video_config)
        self.encoder = H264Encoder(10000000)

        self.current_video_file = None
        self.latest_video_file = None
        # TO-DO: need to use camera.device_path to identify each camera's last-mp4-file-path-holder file
        self.latest_mp4_filename_holder_file = "/tmp/csi_pi_processed_latest_mp4file_path.txt"
        self.is_to_record = False
        self.video_postprocess = None
        self.num_videos_captured = 0
        os.mkdir(self.video_folder)

    def process_video_file(self):
        # 1. `ffmpeg` encode (e.g.: ffmpeg -r 15 -i video.h264 foo.mp4)
        mp4file = f"{self.latest_video_file}"[0:f"{self.latest_video_file}".rindex(".")] + ".mp4"
        cmd = (f"nohup ffmpeg -i {self.latest_video_file} " +
               "-vf \"drawtext=text='%{pts\:hms}': x=(w-text_w)/2: y=10: fontsize=24: fontcolor=white: box=1: boxcolor=black@0.65: boxborderw=10\" " +
               f"{mp4file} -loglevel quiet && " +
               f"rm {self.latest_video_file} && " +
               f"echo '{mp4file}' > {self.latest_mp4_filename_holder_file} &")
        print(f"process_video_file_in_bg: ffmpeg-cmd = {cmd}\n\n")
        self.video_postprocess = sp.Popen([cmd], shell=True)
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
            # self.set_time_annotation(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
            self.current_video_file = f"{self.video_folder}/{int((time.time() * 1000))}.h264"
            print(f"\n\ndo_record: Started new record -> {self.current_video_file}")

            # self.picam2.start_and_record_video(output=self.current_video_file, encoder=self.encoder,
            #           show_preview=False, duration=self.video_chunk_length_seconds, audio=False)
            try:
                self.picam2.start_recording(self.encoder, self.current_video_file)
                while self.is_to_record and ((datetime.now() - start).seconds < self.video_chunk_length_seconds):
                    # self.set_time_annotation(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
                    time.sleep(self.video_chunk_length_seconds + 0.01)
                print("do_record: Ended recording this chunk")
            finally:
                self.picam2.stop_recording()

            self.latest_video_file = self.current_video_file
            self.num_videos_captured += 1
            Thread(target=self.process_video_file, daemon=True, name='VideoProcessorNonDaemon').start()
        print("do_record: Ended Recording Video\n")

    # def set_time_annotation(self, time_str):
    #     colour = (0, 255, 0, 255)
    #     origin = (0, 30)
    #     font = cv2.FONT_HERSHEY_SIMPLEX
    #     fontScale = 1
    #     thickness = 2
    #     overlay = np.zeros((640, 480, 4), dtype=np.uint8)
    #     cv2.putText(overlay, time_str, origin, font, fontScale, colour, thickness)
    #     self.picam2.set_overlay(overlay)  # Giving picam2._preview=None exception inside the set_overlay() call

    def end_recording(self):
        if self.is_to_record:
            self.is_to_record = False
        print(f"end_recording: self.is_to_record = {self.is_to_record}\n")
        return json.dumps({'status': 'OK', 'file': self.latest_mp4_filename_holder_file})


def local_test():
    vr2 = VideoRecorder2(Config())
    # vr2.video_chunk_length_seconds = 5
    print("-----------------Starting to record & then a 7s sleep ...-----------------")
    print(f"Return from start_recording: {vr2.start_recording()}")
    time.sleep(vr2.video_chunk_length_seconds * 2 + 10)
    print("-----------------7s Timer is Up-----------------")
    vr2.end_recording()
    time.sleep(1)


if __name__ == '__main__':
    local_test()
