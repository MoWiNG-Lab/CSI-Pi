import asyncio
from datetime import datetime as dt

from src.csi_pi.camera.camera import Camera
from src.csi_pi.camera.plugins.photo_burst import CaptureStatus
from src.csi_pi.config import Config
from src.csi_pi.device import Device


def check_devices(config: Config):
    """
    Handle newly connected and newly disconnected devices.
    This method should be called in the event-loop.

    :param config:
    :return:
    """
    check_cameras(config)
    check_esp32_devices(config)


def check_cameras(config: Config):
    active_cams = Camera.get_connected_cameras()
    # Remove newly disconnected devices
    for cam in config.cameras:
        if cam.device_path not in active_cams:
            print("Camera no longer detected:", cam.device_path)
            print("Removing device from list.")
            del config.data_file_names[cam.device_path]
            cam.stop_recording(config)
            config.cameras.remove(cam)

    # Add newly discovered devices
    for i, device_path in enumerate(active_cams):
        if device_path not in [cam.device_path for cam in config.cameras]:
            print("New camera detected:", device_path)
            camera = Camera(config=config, device_path=device_path)
            # TODO Handle multi-camera recording: Separate record file per camera/device name
            # config.data_file_names[device_path] = f"{config.data_dir}{device_path.split('/')[-1]}.csv"
            # camera.start_listening(config)
            config.cameras.append(camera)


def check_esp32_devices(config: Config):
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


async def check_photo_burst(config: Config):
    while True:
        # print(f"event_loop.py:: config.is_to_start_photo_burst_at_startup={config.is_to_start_photo_burst_at_startup}")
        await asyncio.sleep(1)
        # print(f"event_loop.py:: len(config.cameras)={len(config.cameras)}")

        # if there is at least one-camera and ENV file indicates to start photo-bursting at the startup of the server,
        # then start photo-bursting with the first camera.
        if len(config.cameras) > 0 and config.cam_mode == config.CAM_MODE_PHOTO_BURST:
            # and not config.cameras[0].photo_burst.is_capturing:
            if CaptureStatus.STANDBY == config.cameras[0].photo_burst.capture_status:  # not capturing & not stopped
                config.cameras[0].start_photo_burst(int(config.photo_burst_interval))
            # The following call is self-sufficient to capture based on the conditions of capturing the photo.
            config.cameras[0].photo_burst.perform_burst()
            # config.is_to_start_photo_burst_at_startup = False


async def check_video_startup(config: Config):
    while True:
        await asyncio.sleep(10)
        now = dt.now()
        curr = now.hour * 100 + now.minute
        print(f"curr={curr}, start={config.video_start_time}, end={config.video_end_time}")
        if config.video_start_time <= curr < config.video_end_time:
            config.cameras[0].start_recording()
        else:
            config.cameras[0].end_recording()


async def watch_devices(config: Config):
    print("Start event loop. Watching for devices to connect or disconnect.")
    while True:
        check_devices(config)
        await asyncio.sleep(1)


async def start_and_continue_video_recording(config):
    await asyncio.sleep(5)
    config.cameras[0].start_recording()


def startup_event_loop(config: Config):
    async def start_event_loop_lambda():
        loop = asyncio.get_event_loop()
        loop.create_task(watch_devices(config))
        if config.cam_mode == config.CAM_MODE_PHOTO_BURST:
            loop.create_task(check_photo_burst(config))
        elif config.cam_mode == config.CAM_MODE_VIDEO_CONTINUALLY:
            loop.create_task(start_and_continue_video_recording(config))
        elif config.cam_mode == config.CAM_MODE_VIDEO_SCHEDULED:
            loop.create_task(check_video_startup(config))

    return start_event_loop_lambda
