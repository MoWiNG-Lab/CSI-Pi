import json
import os
import shutil
import socket
import zipfile
from time import time

from starlette.responses import PlainTextResponse, HTMLResponse, FileResponse, JSONResponse

from src.csi_pi.config import Config
from src.csi_pi.helpers import get_is_csi_enabled, toggle_csi, load_from_file


class Controller:
    def __init__(self, config: Config):
        self.config = config

    async def index(self, request):
        """
        Returns the main web-page of CSI-Pi

        :param request:
        :return:
        """
        return HTMLResponse(open(self.config.app_dir + '/src/csi_pi/resources/html/index.html').read())

    async def annotate_index(self, request):
        """
        Returns the main web-page of CSI-Pi

        :param request:
        :return:
        """
        return HTMLResponse(open(self.config.app_dir + '/src/csi_pi/resources/html/annotate.html').read())

    async def new_annotation(self, request):
        """
        Create a new annotation based on the value in `request.query_params['value']`.

        :param request:
        :return:
        """
        self.config.data_file_names['annotations'].write((",".join([
            'CURRENT_ACTION',
            'fake_uuid',
            str(int(time() * 1000)),
            request.query_params['value'],
        ])) + "\n")
        self.config.data_file_names['annotations'].flush()
        return PlainTextResponse("OK")

    async def get_server_stats(self, request):
        """
        Returns some stats and information about the server

        :param request:
        :return:
        """
        return PlainTextResponse(json.dumps({
            'data_directory': self.config.data_dir,
            'notes': load_from_file(self.config.data_file_names['notes']),
            'is_csi_enabled': get_is_csi_enabled(self.config),
            'tty_plugins': self.config.tty_plugins,
            'storage': {
                'used': shutil.disk_usage("/").used,
                'total': shutil.disk_usage("/").total,
            },
            'devices': [d.device_path for d in self.config.devices],
            'hostname': socket.gethostname(),
        }))

    async def get_annotation_metrics(self, request):
        """
        Returns a JSON object containing the content of the `annotations.csv` file.
        This is not returned from `get_server_stats` because the content of `annotations.csv` can get quite large.

        :param request:
        :return:
        """
        return PlainTextResponse(json.dumps({
            'data': load_from_file(self.config.data_file_names['annotations'].name)
        }))

    async def get_device_metrics(self, request):
        """
        Returns a JSON object containing metrics about the given device.
        This is not returned from `get_server_stats` because the JSON object can get quite large.

        :param request:
        :return:
        """
        device_name = request.query_params['device_name']

        if device_name not in [d.device_path for d in self.config.devices]:
            return PlainTextResponse(json.dumps({
                'status': 'DEVICE_DISCONNECTED'
            }))

        return PlainTextResponse(json.dumps({
            'status': 'OK',
            'device_name': device_name,
            'file': self.config.data_file_names[device_name],
            'application': load_from_file(f'/tmp/application/{device_name}'),
            'wifi_channel': load_from_file(f'/tmp/wifi_channel/{device_name}'),
            'data_rate': os.popen(f'tail -n 60 /tmp/data_rates/{device_name}').read(),
            'files_size': os.path.getsize(self.config.data_file_names[device_name]),
            'most_recent_csi': {
                'samples': os.popen(f'tail -n 3 {self.config.data_file_names[device_name]}').read(),
            }
        }))

    async def get_data_as_zip(self, request):
        """
        Stores the collected experiment data as a ZIP file and returns the ZIP file to the user.
        This process can take a long time.

        :param request:
        :return:
        """
        filename = '/tmp/data.zip'
        file_path = self.config.data_dir

        with zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for f in os.listdir(file_path):
                if f in ['notes.txt']:
                    zipf.write(os.path.join(file_path, f), f)
                elif f != 'annotations.csv':
                    d = f.replace(".csv", "")
                    zipf.write(os.path.join(file_path, f), f"{d}/{f}")
                    zipf.write(os.path.join(file_path, 'annotations.csv'), f"{d}/annotations.csv")
                elif f.endswith(".mkv") or f.endswith(".avi") or f.endswith(".mp4"):
                    zipf.write(os.path.join(file_path, f), f"{d}/{f}")

        return FileResponse(filename, filename='CSI.zip')

    async def enable_csi(self, request):
        """
        Enabling CSI means that CSI-Pi will write incoming CSI data to disk.

        If we are recording CSI for a very long time, we might end up with a lot of data.
        Enabling/Disabling CSI programatically can greatly reduce the amount of data stored on disk.

        :param request:
        :return:
        """
        toggle_csi(self.config, "1")
        return PlainTextResponse("OK")

    async def disable_csi(self, request):
        """
        Disabling CSI means that CSI-Pi will NOT write incoming CSI data to disk.

        If we are recording CSI for a very long time, we might end up with a lot of data.
        Enabling/Disabling CSI programatically can greatly reduce the amount of data stored on disk.

        :param request:
        :return:
        """
        toggle_csi(self.config, "0")
        return PlainTextResponse("OK")

    async def set_notes(self, request):
        """
        Update the notes for the current experiment

        :param request:
        :return:
        """
        form = await request.json()
        new_note_data = form['note']

        f = open(self.config.data_file_names['notes'], "w+")
        f.truncate(0)
        f.write(new_note_data)
        f.flush()

        return PlainTextResponse(new_note_data)

    async def get_camera_list(self, request):
        """
        List all the connected active cameras.
        :param request:
        :return:
        """
        cams = []
        for cam in self.config.cameras:
            cams.append(cam.device_path)
        return JSONResponse(json.dumps(cams))

    async def start_cam(self, request):
        """
        If any camera is attached to the system, then start recording video feeds from the camera and
        save it inside the data directory of the current session.

        :param request:
        :return: "OK" if the camera is attached & video recording is started, otherwise the specific error-message.
        """
        cam_number = int(request.query_params["camera_number"] if "camera_number" in request.query_params else 0)
        return PlainTextResponse(self.config.cameras[cam_number].start_recording())

    async def end_cam(self, request):
        """
        If any camera is attached to the system, then start recording video feeds from the camera and
        save it inside the data directory of the current session.

        :param request:
        :return: "OK" if the video recording is properly completed & processed, otherwise the specific error-message.
        """
        cam_number = int(request.query_params["camera_number"] if "camera_number" in request.query_params else 0)
        return PlainTextResponse(self.config.cameras[cam_number].end_recording())
