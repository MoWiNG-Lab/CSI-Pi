import atexit

from starlette.applications import Starlette

from src.csi_pi.config import Config
from src.csi_pi.controller import Controller
from src.csi_pi.event_loop import startup_event_loop
from src.csi_pi.helpers import kill_child_processes, setup_experiment_filesystem
from src.csi_pi.routes import get_routes

# Global application variables
config = Config()
controller = Controller(config)

# Setup filesystem before app begins
setup_experiment_filesystem(config)

# Register the Starlette HTTP server application
app = Starlette(
    routes=get_routes(controller),
    on_startup=[startup_event_loop(config)],
)

# When CSI-Pi stops, we must kill the child processes programatically.
# Otherwise we will have zombie processes still listening to `/dev/ttyUSB*`
atexit.register(kill_child_processes)
