import json
import os
import subprocess as sp
import time
import traceback
from enum import Enum

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from src.csi_pi.config import Config


class CaptureStatus(Enum):
    STANDBY = 1
    CAPTURING = 2
    STOP = 3


class GAuth:

    def __init__(self, env_path):
        google_auth = GoogleAuth()
        google_auth.settings["client_config_backend"] = "file"
        google_auth.settings["client_config_file"] = env_path + "/pydrive.client_secrets.json"
        google_auth.settings["save_credentials"] = True
        google_auth.settings["save_credentials_backend"] = "file"
        google_auth.settings["save_credentials_file"] = env_path + "/pydrive.credentials.json"
        google_auth.settings["get_refresh_token"] = True
        # google_auth.LocalWebserverAuth()  ## Enable this line to authenticate a new setup with a new Google-Account
        self.gdrive = GoogleDrive(google_auth)

    def get_remote_directory(self, directory_name, parent_directory_id=None):
        q = f"title = '{directory_name}'"
        file_list = self.gdrive.ListFile({'q': q}).GetList()
        if parent_directory_id is not None:
            file_list = [f for f in file_list if len(f['parents']) and f['parents'][0]['id'] == parent_directory_id]
        if len(file_list) > 1:
            raise Exception(f"More than one directory returned for query: ({q}).")
        if len(file_list) == 0:
            raise Exception(f"No directory '{directory_name}' found.")
        return file_list[0]['id']

    def get_dir_id(self, directory_path):
        parent_directories = directory_path.split("/")
        directory_id = None
        for d in parent_directories:
            directory_id = self.get_remote_directory(d, parent_directory_id=directory_id)
        return directory_id

    def upload(self, file_name, gdrive_folder):
        f"""
        Use PyDrive Library to upload the provided `file` to the specified Google-Drive folder.
        """
        f = self.gdrive.CreateFile({'title': file_name.split('/')[-1],
                                    'parents': [{'id': self.get_dir_id(gdrive_folder)}]})
        f.SetContentFile(file_name)
        f.Upload()
        # noinspection PyUnusedLocal
        f = None  # Needed to prevent memory leak due to keeping the file open in memory by pydrive lib


class PhotoBurst:

    def __init__(self, config: Config):
        self.config = config
        self.interval_seconds = int(config.photo_burst_interval)
        self.curr_capture_interval = 0
        self.capture_status = CaptureStatus.STANDBY
        self.folder_path = None
        self.most_recent_file = None
        self.gst_process = None
        self.GDRIVE_PHOTO_FOLDER = config.gdrive_photo_folder
        self.google_drive = GAuth(env_path=f"{config.app_dir}/environment")
        self.rep_timer = None
        self.num_images_captured = 0

    def capture(self, folder_path):
        if self.capture_status != CaptureStatus.CAPTURING:
            return json.dumps({'status': 'OK', 'message': f"ERROR: Session is already completed."})

        file_name = f"{folder_path}/{time.time() * 1000}.jpg"
        # noinspection PyBroadException
        try:
            cmd = f"gst-launch-1.0 libcamerasrc ! videoconvert ! " \
                  f"clockoverlay time-format=\"%d-%b-%Y, %H:%M:%S\" ! " \
                  f"jpegenc snapshot=true ! " \
                  f"filesink location='{file_name}'"  #
            print(f"Capturing image using CMD: '{cmd}'")
            self.gst_process = sp.Popen([cmd], shell=True)
            self.gst_process.wait()
            self.most_recent_file = file_name
            self.num_images_captured += 1
            # self.google_drive.upload(file_name, self.GDRIVE_PHOTO_FOLDER)
            return json.dumps({'status': 'OK', 'file': file_name})
        except:
            return json.dumps({'status': 'OK', 'message': f"ERROR: {traceback.format_exc()}"})

    def start_burst(self, interval_secs=5):
        f"""
        Save camera-feed image every `interval_secs` seconds.
        :param: interval_secs Interval in seconds between two successive captures.
        :return: JSON-object with the proper first image's file-path if the camera is attached & photo-bursting is started, 
        otherwise containing the specific error-message.
        """
        if self.capture_status == CaptureStatus.CAPTURING:
            return json.dumps({'status': 'OK', 'message': f"ERROR: Already bursting photos using this camera."})

        self.interval_seconds = int(interval_secs)
        self.curr_capture_interval = 1
        self.folder_path = f"{self.config.data_dir}/photos_{time.time() * 1000}"
        os.makedirs(self.folder_path, exist_ok=True)
        self.capture_status = CaptureStatus.CAPTURING
        return self.capture(self.folder_path)

    def perform_burst(self):
        f"""
        This function is supposed to be called per second to check whether we're to capture the camera-frame based 
        on the capture-interval and capture-status. 
        """
        if self.capture_status == CaptureStatus.CAPTURING \
                and self.curr_capture_interval != 0 \
                and self.curr_capture_interval % self.interval_seconds == 0:
            self.capture(folder_path=self.folder_path)
            self.curr_capture_interval = 1
        self.curr_capture_interval += 1

    def end_burst(self):
        f"""
        This function ends a currently active photo-burst, irrespective of the photo-burst been started by the 
        server startup event or an individual API-call.
        """
        self.capture_status = CaptureStatus.STOP
        self.curr_capture_interval = 0

        # For photo-captures, `self.gst_process` should not exist at this point,
        # but just ensuring below that it is out of the way by now.
        if self.gst_process:
            # If the process exists, then terminate it.
            pid = self.gst_process.pid
            print(f"\n\t\tPID={pid}\n")
            self.gst_process.terminate()
            sp.Popen([f"kill {pid}"], shell=True)

        return json.dumps({'status': 'OK', 'message': "Stopped capturing photos."})


if __name__ == '__main__':
    pb = PhotoBurst(Config())
    # DONE: pb.google_drive.upload(
    #     "/absolute/path/of/the/image/file",
    #     pb.GDRIVE_PHOTO_FOLDER)
    pb.start_burst(10)
    print("I've started 30 Seconds of photo-bursting. Put an eye in the specified GDrive ...")
    for i in range(1, 30):
        pb.perform_burst()
        time.sleep(1)
    pb.end_burst()
    print("30 Seconds of photo-bursting has just ended.")
