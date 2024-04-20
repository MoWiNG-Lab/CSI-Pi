import asyncio

from src.csi_pi.config import Config
from src.csi_pi.device import Device


def check_devices(config: Config):
    """
    Handle newly connected and newly disconnected devices.
    This method should be called in the event-loop.

    :param config:
    :return:
    """
    # Identify all connected devices
    currently_connected_devices = Device.get_currently_connected_devices()

    # Remove newly disconnected devices
    for d in config.devices:
        if d.device_path not in currently_connected_devices:
            print("Device no longer detected:", d.device_path)
            print("Removing device from list.")
            del config.data_file_names[d.device_path]
            d.stop_listening(config)
            config.devices.remove(d)

    # Add newly discovered devices
    for i, device_path in enumerate(currently_connected_devices):
        if device_path not in [d.device_path for d in config.devices]:
            print("New device detected:", device_path)
            device = Device(device_path=device_path)
            config.data_file_names[device_path] = f"{config.data_dir}{device_path.split('/')[-1]}.csv"
            device.start_listening(config)
            config.devices.append(device)


async def watch_devices(config: Config):
    print("Start event loop. Watching for devices to connect or disconnected.")
    while True:
        check_devices(config)
        await asyncio.sleep(1)


def startup_event_loop(config):
    async def start_event_loop_lambda():
        loop = asyncio.get_event_loop()
        loop.create_task(watch_devices(config))
    return start_event_loop_lambda
