import atexit

from starlette.applications import Starlette

from src.csi_pi.config import Config
from src.csi_pi.controller import Controller
from src.csi_pi.helpers import kill_child_processes, setup_app
from src.csi_pi.metrics import Metrics
from src.csi_pi.routes import get_routes

config = Config()
metrics = Metrics(config.data_dir)
controller = Controller(config)

setup_app(config)

app = Starlette(routes=get_routes(controller))
atexit.register(kill_child_processes)
