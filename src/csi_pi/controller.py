import os
import json
from time import time
import zipfile

from starlette.responses import PlainTextResponse, HTMLResponse, FileResponse

from src.csi_pi.config import Config
from src.csi_pi.helpers import toggle_csi, load_from_file


class Controller:
    def __init__(self, config: Config):
        self.config = config

    async def index(self, request):
        return HTMLResponse(open(self.config.app_dir + '/src/csi_pi/resources/html/index.html').read())

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
            'data': load_from_file(self.config.data_file_names['annotations'].name)
        }))

    async def get_device_list(self, request):
        return PlainTextResponse(json.dumps([d.device_path for d in self.config.devices]))

    async def get_device_metrics(self, request):
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
        filename = '/tmp/data.zip'
        file_path = self.config.data_dir

        with zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for f in os.listdir(file_path):
                if f in ['notes.txt', 'experiment_name.txt']:
                    zipf.write(os.path.join(file_path, f), f)
                elif f != 'annotations.csv':
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

    async def get_experiment_name(self, request):
        experiment_name = load_from_file(self.config.data_file_names['experiment_name'])
        return PlainTextResponse(experiment_name)

    async def get_notes(self, request):
        experiment_name = load_from_file(self.config.data_file_names['notes'])
        return PlainTextResponse(experiment_name)

    async def set_experiment_name(self, request):
        form = await request.json()
        new_experiment_name = form['name'].replace(',', '')

        f = open(self.config.data_file_names['experiment_name'], 'w+')
        f.truncate(0)
        f.write(new_experiment_name)
        f.flush()

        return PlainTextResponse(new_experiment_name)

    async def set_notes(self, request):
        form = await request.json()
        new_note_data = form['note']

        f = open(self.config.data_file_names['notes'], "w+")
        f.truncate(0)
        f.write(new_note_data)
        f.flush()

        return PlainTextResponse(new_note_data)
