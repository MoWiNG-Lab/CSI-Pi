import os
import subprocess
import psutil

class Device:
    process = None

    def __init__(self, device_path):
        self.device_path = device_path

    def start_listening(self, config):
        """
        This method is called to when the esp32 device is first discovered (i.e. plugged in).
        :param config:
        :return:
        """
        # Set the baud rate
        subprocess.Popen(f"/bin/stty -F {self.device_path} {config.esp32_baud_rate}".split(" "), stdout=subprocess.PIPE)

        # Start a child process to listen for the serial data.
        p = subprocess.Popen(
            f"/usr/bin/python3 {config.app_dir}/src/csi_pi/tty_listener.py {self.device_path} {config.data_file_names[self.device_path]} {config.data_file_names['experiment_name']}".split(" "),
            env={
                'PYTHONPATH': os.environ.get('PYTHONPATH', '') + f":{config.app_dir},",
            },
            stdout=subprocess.DEVNULL,
            preexec_fn=os.setsid
        )

        # Store the process so that we can kill it later
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
