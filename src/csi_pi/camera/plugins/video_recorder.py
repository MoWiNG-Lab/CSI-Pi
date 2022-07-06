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
        # self.params = params
        self.FPS = 15
        self.TMP_FILE = "/tmp/csi_session.h264"
        self.TMP_FILE_TIMES = "/tmp/csi_session.txt"
        self.VIDEO_FILE_NAME = f"{self.config.data_dir}_{time.time()}.avi"

    def start_recording(self):
        os.makedirs(self.config.data_dir, exist_ok=True)
        self.VIDEO_FILE_NAME = f"{self.config.data_dir}_{time.time()}.avi"
        f"""
        Starts to record camera feed into the {self.TMP_FILE} using the provided params
        :return: "OK" if the camera is attached & video recording is started, otherwise the specific error-message.
        """
        # noinspection PyBroadException
        try:
            cmd = f"gst-launch-1.0 -e libcamerasrc ! video/x-raw, width=640, height=480, " \
                  f"framerate=15/1 ! clockoverlay time-format=\"%d-%b-%Y, %H:%M:%S\" ! avimux ! " \
                  f"filesink location='{self.VIDEO_FILE_NAME}'"  #
            print(f"Recording video using CMD: '{cmd}'")
            self.recorder_process = sp.Popen([cmd], shell=True)
            return "OK"
        except:
            return f"ERROR: {traceback.format_exc()}"

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
                    pid = int(sp.check_output(["pidof", "gst-launch-1.0"]).strip())
                    print("\n\t\tNew PID:", pid, "\n")
                    if not pid or pid < 1:
                        break
                    sp.Popen([f"kill {pid}"], shell=True)

                # Afterwards, process the recorded file into an MKV file & delete the temporary files.
                # sp.Popen(
                #     [f"mkvmerge -o {self.VIDEO_FILE_NAME} --timecodes 0:{self.TMP_FILE_TIMES} {self.TMP_FILE}"],
                #     shell=True)
                # os.remove(self.TMP_FILE)
                # os.remove(self.TMP_FILE_TIMES)
            return "OK"
        except:
            return f"ERROR: {traceback.format_exc()}"


if __name__ == '__main__':
    v = VideoRecorder(Config())
    v.start_recording()
    time.sleep(10)
    v.end_recording()
