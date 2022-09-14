import json
import os
import subprocess as sp
import time
import traceback
from threading import Timer

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from src.csi_pi.config import Config


class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        # self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False


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
        self.to_capture = False
        self.recorder_process = None
        self.GDRIVE_PHOTO_FOLDER = config.GDRIVE_PHOTO_FOLDER
        self.google_drive = GAuth(env_path=f"{config.app_dir}/environment")

    def capture(self, folder_path, interval_secs):
        if not self.to_capture:
            return json.dumps({'status': 'OK', 'message': f"ERROR: Session is already completed."})

        # TODO: Schedule next capture using RepeatedTimer object in every `interval_secs` seconds

        file_name = f"{folder_path}/{time.time() * 1000}.jpg"
        # noinspection PyBroadException
        try:
            cmd = f"gst-launch-1.0 libcamerasrc ! videoconvert ! jpegenc snapshot=true ! " \
                  f"filesink location='{file_name}'"  #
            print(f"Capturing image using CMD: '{cmd}'")
            self.recorder_process = sp.Popen([cmd], shell=True)
            self.google_drive.upload(file_name, self.GDRIVE_PHOTO_FOLDER)
            return json.dumps({'status': 'OK', 'file': file_name})
        except:
            return json.dumps({'status': 'OK', 'message': f"ERROR: {traceback.format_exc()}"})

    def start_burst(self, interval_secs=5, debug=False):
        f"""
        Save camera-feed image every `interval_secs` seconds.
        :param: interval_secs Interval in seconds between two successive captures.
        :return: JSON-object with the proper first image's file-path if the camera is attached & photo-bursting is started, 
        otherwise containing the specific error-message.
        """
        folder_path = f"{self.config.data_dir}/photos_{time.time() * 1000}"
        os.makedirs(folder_path, exist_ok=True)
        self.to_capture = True
        return self.capture(folder_path, interval_secs)

    def end_burst(self):
        f"""
        Call to end a currently active photo-burst.
        """
        self.to_capture = False
        return json.dumps({'status': 'OK', 'message': "Stopped capturing photos."})


if __name__ == '__main__':
    pb = PhotoBurst(Config())
    pb.google_drive.upload(
        "/home/pi/CSI-Pi/storage/data/1663179399.8994606/photos_1663179835910.1692/1663179835913.842.jpg",
        pb.GDRIVE_PHOTO_FOLDER)
    # pb.start_burst()
    # print("I've started 30 Seconds of photo-bursting. Put an eye in the specified GDrive ...")
    # time.sleep(30)
    # pb.end_burst()
    # print("30 Seconds of photo-bursting has just ended.")
