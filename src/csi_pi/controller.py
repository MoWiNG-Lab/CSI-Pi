import os
import json
from time import time
import zipfile

from starlette.responses import PlainTextResponse, HTMLResponse, FileResponse

from src.csi_pi.config import Config
from src.csi_pi.helpers import toggle_csi


class Controller:
    def __init__(self, config: Config):
        self.config = config

    @staticmethod
    def load_from_file(file_name):
        output = ""

        if os.path.exists(file_name):
            f = open(file_name, 'r')
            output = f.read()
            f.close()

        return output

    async def index(self, request):
        return HTMLResponse(open(self.config.app_dir + '/src/csi_pi/html/index.html').read())

    async def new_annotation(self, request):
        self.config.data_file_names['annotations'].write((",".join([
            'CURRENT_ACTION',
            'fake_uuid',
            str(int(time() * 1000)),
            request.query_params['value'],
        ])) + "\n")
        self.config.data_file_names['annotations'].flush()
        return PlainTextResponse("OK")

    async def get_data_directory(self, request):
        return PlainTextResponse(self.config.data_dir)

    async def get_annotation_metrics(self, request):
        return PlainTextResponse(json.dumps({
            'data': self.load_from_file(self.config.data_file_names['annotations'].name)
        }))

    async def get_device_list(self, request):
        return PlainTextResponse(json.dumps(self.config.devices))

    async def get_device_metrics(self, request):
        device_name = request.query_params['device_name']
        return PlainTextResponse(json.dumps({
            'device_name': device_name,
            'file': self.config.data_file_names[device_name],
            'application': self.load_from_file(f'/tmp/application/{device_name}'),
            'wifi_channel': self.load_from_file(f'/tmp/wifi_channel/{device_name}'),
            'data_rate': self.load_from_file(f'/tmp/data_rates/{device_name}'),
            'files_size': os.path.getsize(self.config.data_file_names[device_name]),
            'most_recent_csi': {
                'samples': os.popen(f'tail -n 3 {self.config.data_file_names[device_name]}').read(),
            }
        }))

    async def get_data_as_zip(self, request):
        filename = '/tmp/data.zip'
        file_path = self.config.data_dir

        with zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for f in os.listdir(file_path):
                if f != 'annotations.csv':
                    d = f.replace(".csv", "")
                    zipf.write(os.path.join(file_path, f), f"{d}/{f}")
                    zipf.write(os.path.join(file_path, 'annotations.csv'), f"{d}/annotations.csv")

        return FileResponse(filename, filename='CSI.zip')

    async def power_up(self, request):
        toggle_csi(self.config, "1")
        return PlainTextResponse("OK")

    async def power_down(self, request):
        toggle_csi(self.config, "0")
        return PlainTextResponse("OK")
