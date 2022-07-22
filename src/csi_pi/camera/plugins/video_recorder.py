import json
import os
import subprocess as sp
import time
import traceback

from src.csi_pi.config import Config


# noinspection PyUnusedLocal
def get_object(config: Config):
    return VideoRecorder(config)


class VideoRecorder:

    def __init__(self, config: Config):
        self.config = config
        self.recorder_process = None
        self.FPS = 30
        self.VIDEO_FILE_NAME = f"{self.config.data_dir}_{time.time() * 1000}.avi"

    def start_recording(self, debug=False):
        f"""
        Starts to record the camera feed in AVI format using GStreamer & `libcamera` library bundled with Bullseye+ OS.
        :return: JSON-object with the proper video-file-path if the camera is attached & video recording is started, 
        otherwise containing the specific error-message.
        """
        if debug:
            self.VIDEO_FILE_NAME = f"{int((time.time() * 1000).__floor__())}.avi"
        else:
            os.makedirs(self.config.data_dir, exist_ok=True)
            self.VIDEO_FILE_NAME = f"{self.config.data_dir}_{time.time() * 1000}.avi"
        # noinspection PyBroadException
        try:
            cmd = f"gst-launch-1.0 -e -v libcamerasrc ! " \
                  f"'video/x-raw,format=(string)I420,width=320,height=240,framerate={self.FPS}/1' ! " \
                  f"clockoverlay time-format=\"%d-%b-%Y, %H:%M:%S\" ! " \
                  f"avimux ! " \
                  f"filesink location='{self.VIDEO_FILE_NAME}'"  #
            print(f"Recording video using CMD: '{cmd}'")
            self.recorder_process = sp.Popen([cmd], shell=True)
            return json.dumps({'status': 'OK', 'file': self.VIDEO_FILE_NAME})
        except:
            return json.dumps({'status': 'OK', 'message': f"ERROR: {traceback.format_exc()}"})

    def end_recording(self):
        """
        :return: "OK" if the video recording is properly completed & processed, otherwise the specific error-message.
        """
        # noinspection PyBroadException
        try:
            if self.recorder_process:
                # If the process exists, then terminate it.
                pid = self.recorder_process.pid
                print(f"\n\t\tPID={pid}\n")
                self.recorder_process.terminate()
                sp.Popen([f"kill {pid}"], shell=True)
                # sp.Popen([f"kill {pid+1}"], shell=True)

                while True:
                    try:
                        pid = int(sp.check_output(["pidof", "gst-launch-1.0"]).strip())
                        print("\n\t\tNew PID:", pid, "\n")
                        if not pid or pid < 1:
                            break
                        sp.Popen([f"kill {pid}"], shell=True)
                    except sp.CalledProcessError as cpe:
                        print(cpe)
                        break

            return json.dumps({'status': 'OK', 'file': self.VIDEO_FILE_NAME})
        except:
            return json.dumps({'status': 'OK', 'message': f"ERROR: {traceback.format_exc()}"})


if __name__ == '__main__':
    v = VideoRecorder(Config())
    v.start_recording(debug=True)
    time.sleep(10)
    v.end_recording()
