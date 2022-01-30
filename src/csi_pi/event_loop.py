import asyncio

from src.csi_pi.config import Config
from src.csi_pi.helpers import start_listening


async def check_devices(config: Config):
    print("Start event loop")
    while True:
        start_listening(config)
        await asyncio.sleep(1)


def startup_event_loop(config):
    async def start_event_loop_lambda():
        loop = asyncio.get_event_loop()
        loop.create_task(check_devices(config))
    return start_event_loop_lambda