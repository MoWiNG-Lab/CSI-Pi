import os
from time import time
from src.csi_pi.helpers import get_is_csi_enabled, load_from_file


def get_object(tty_full_path, tty_save_path, experiment_name_file_path, config):
    return CSIDataTTYPlugin(tty_full_path, tty_save_path, experiment_name_file_path, config)


class CSIDataTTYPlugin:
    #
    # Calculate Statistics
    #
    data_rate_stats = {
        'current_second': None,
        'count': 0,
    }

    experiment_name_set_at = 0
    experiment_name = ""
    wifi_channel = None
    application = None
    output_file = None

    def __init__(self, tty_full_path, tty_save_path, experiment_name_file_path, config):
        self.tty_full_path = tty_full_path
        self.tty_save_path = tty_save_path
        self.experiment_name_file_path = experiment_name_file_path
        self.config = config

        os.makedirs("/tmp/data_rates/dev/", exist_ok=True)
        os.makedirs("/tmp/wifi_channel/dev/", exist_ok=True)
        os.makedirs("/tmp/application/dev/", exist_ok=True)

        # Clear metric files from previous sessions
        open(f"/tmp/data_rates{tty_full_path}", "w").close()

        self.output_file = open(tty_save_path, "a")

    def prefix_string(self):
        """
        For each incoming line from our devices we will look for the following prefix-string.
        If the line starts with this string, then we will call `process(line)`.
        :return: str
        """

        return "CSI_DATA,"

    def process(self, line):
        """
        When we find a string that begins with `prefix_string()`, this function will be called.
        Process the incoming line as you wish.

        :param line: str
        :return: None
        """

        # Get Application Name
        application = line.split(",")[1]
        if self.application != application:
            f = open(f"/tmp/application{self.tty_full_path}", "w")
            f.write(str(application))
            f.close()

            self.application = application

        # Get WiFi Channel
        wifi_channel = line.split(",")[16]
        if wifi_channel.isdigit() and self.wifi_channel != wifi_channel:
            f = open(f"/tmp/wifi_channel{self.tty_full_path}", "w")
            f.write(str(wifi_channel))
            f.close()

            self.wifi_channel = wifi_channel

        # Update Data Rate
        self.data_rate_stats['count'] += 1

        if get_is_csi_enabled(self.config):
            curr_time_seconds = time()
            csi_line = f"{line},fake_uuid,{curr_time_seconds * 1000},{self.get_experiment_name()}"
            self.output_file.write(f"{csi_line}\n")

    def process_every_second(self, current_second):
        """
        Process and store statistics for the past one second of TTY data.

        :param current_second:
        :return:
        """
        self.data_rate_stats['current_second'] = current_second
        print("Got rate of", self.data_rate_stats['count'], "Hz")

        with open(f"/tmp/data_rates{self.tty_full_path}", "a") as data_rate_stats_file:
            data_rate_stats_file.write(f"{current_second},{self.data_rate_stats['count']}\n")
        self.data_rate_stats['count'] = 0

    def get_experiment_name(self):
        os.path.getmtime(self.experiment_name_file_path)
        if self.experiment_name_set_at < os.path.getmtime(self.experiment_name_file_path):
            self.experiment_name = load_from_file(self.experiment_name_file_path)
            self.experiment_name_set_at = os.path.getmtime(self.experiment_name_file_path)

        return self.experiment_name

