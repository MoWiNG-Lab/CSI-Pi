import os
import subprocess
import psutil


class Device:
    process = None

    def __init__(self, device_path):
        self.device_path = device_path

    @staticmethod
    def get_currently_connected_devices():
        devices = []
        for d in os.listdir("/dev"):
            for type in ['ttyUSB', 'ttyACM']:
                if type in d:
                    devices.append("/dev/" + d)
        return sorted(devices)

    @staticmethod
    def get_device_baud_rate(config, device_path):
        baud_rates = {
            'ttyUSB': config.esp32_baud_rate,
            'ttyACM': config.acm_baud_rate,
        }
        baud_rate = None
        for k in baud_rates.keys():
            if k in device_path:
                baud_rate = baud_rates[k]
        if baud_rate is None:
            raise Exception(f"Baud-rate cannot be determined for {device_path}.")

        return baud_rate

    def start_listening(self, config):
        """
        This method is called to when the esp32 device is first discovered (i.e. plugged in).

        :param config:
        :return:
        """
        # Set the baud rate
        baud_rate = self.get_device_baud_rate(config, self.device_path)
        subprocess.Popen(f"/bin/stty -F {self.device_path} {baud_rate}".split(" "), stdout=subprocess.PIPE)

        # Start a child process to listen for the serial data.
        p = subprocess.Popen(
            f"/usr/bin/python3 {config.app_dir}/src/csi_pi/tty_listener.py {self.device_path} {config.data_file_names[self.device_path]}".split(" "),
            env={'PYTHONPATH': os.environ.get('PYTHONPATH', '') + f":{config.app_dir},"},
            stdout=subprocess.DEVNULL,
            preexec_fn=os.setsid
        )

        # Store the process so that we can kill it when the device becomes disconnected
        self.process = p

    def stop_listening(self, config):
        """
        This method is called when the esp32 is no longer available (i.e. unplugged).

        :param config:
        :return:
        """
        if self.process and self.process.pid:
            # Kill the process
            psutil.Process(self.process.pid).kill()
