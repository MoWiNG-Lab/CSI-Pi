import os
import subprocess
from time import time
import zipfile

from starlette.responses import PlainTextResponse, HTMLResponse, FileResponse

from src.csi_pi.config import Config
from src.csi_pi.helpers import toggle_csi


class Controller:
    def __init__(self, config: Config):
        self.config = config

    async def index(self, request):
        output = subprocess.Popen(
            ["timeout", "0.9", "/bin/sh", f"{self.config.shell_dir}/status.sh", self.config.data_dir, self.config.app_dir],
            stdout=subprocess.PIPE
        ).communicate()[0]

        return HTMLResponse(
            "<head><meta http-equiv='refresh' content='1'/></head> <body><pre style='white-space: pre-wrap;'>" + output.decode(
                "utf-8") + "</pre><body>")

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

