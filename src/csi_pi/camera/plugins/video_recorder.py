import os
import subprocess as sp
import traceback

from src.csi_pi.config import Config


# noinspection PyUnusedLocal
def get_object(config: Config, expt_name, params):
    return VideoRecorder(expt_name, params)


class VideoRecorder:

    def __init__(self, config: Config, expt_name="", params=""):
        self.config = config
        self.recorder_process = None
        self.params = params
        self.FPS = 15
        self.TMP_FILE = "/tmp/csi_session.h264"
        self.TMP_FILE_TIMES = "/tmp/csi_session.txt"
        self.VIDEO_FILE_NAME = f"{config.data_dir}csi_session_{expt_name}.mkv"

    def start_recording(self, expt_name="", params=""):
        if expt_name != "":
            self.VIDEO_FILE_NAME = f"{self.config.data_dir}csi_session_{expt_name}.mkv"
        if params != "":
            self.params = params
        f"""
        Starts to record camera feed into the {self.TMP_FILE} using the provided params
        :return: "OK" if the camera is attached & video recording is started, otherwise the specific error-message.
        """
        # noinspection PyBroadException
        try:
            p = self.params.lower()
            if self.params != "" and ("-o " in p or "-t " in p or "--save-pts " in p):
                raise ValueError("Cannot accept reserved parameters of duration & output files.")
            if self.params != "" and "--framerate" not in p:
                self.params += f" --framerate {self.FPS}"
            self.recorder_process = sp.Popen([f"libcamera-vid -t 0 -o {self.TMP_FILE}"
                                                      f" --save-pts {self.TMP_FILE_TIMES}"
                                                      f" {self.params}"], shell=True)
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
                self.recorder_process.terminate()

                # Afterwards, process the recorded file into an MKV file & delete the temporary files.
                sp.Popen(
                    [f"mkvmerge -o {self.VIDEO_FILE_NAME} --timecodes 0:{self.TMP_FILE_TIMES} {self.TMP_FILE}"],
                    shell=True)
                os.remove(self.TMP_FILE)
                os.remove(self.TMP_FILE_TIMES)
            return "OK"
        except:
            return f"ERROR: {traceback.format_exc()}"


# if __name__ == '__main__':
#     v = VideoRecorder(Config(), "Cam Integration Test").start_recording()
#     time.sleep(10)
#     v.end_recording()
