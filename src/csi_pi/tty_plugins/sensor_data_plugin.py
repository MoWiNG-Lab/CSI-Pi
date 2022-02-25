import requests


def get_object(tty_full_path, tty_save_path, experiment_name_file_path):
    return SensorDataTTYPlugin(tty_full_path, tty_save_path, experiment_name_file_path)


class SensorDataTTYPlugin:
    """
    This TTY Plugin shows how we can capture lines starting with `SENSOR_DATA,` and then
    automatically store the data as an annotation.

    Furthermore, this script shows a simplified interface for creating a custom tty-plugin.

    To "install" this plugin, add `src.csi_pi.tty_plugins.sensor_data_plugin` to the
    `TTY_PLUGINS` variable within your `./env` file.
    """
    def __init__(self, tty_full_path, tty_save_path, experiment_name_file_path):
        self.num_sensor_readings = 0

    def prefix_string(self):
        """
        For each incoming line from our devices we will look for the following prefix-string.
        If the line starts with this string, then we will call `process(line)`.
        :return: str
        """

        return "SENSOR_DATA,"

    def process(self, line):
        """
        When we find a string that begins with `prefix_string()`, this function will be called.
        Process the incoming line as you wish.

        :param line: str
        :return: None
        """
        self.num_sensor_readings += 1

        line = line.replace("SENSOR_DATA,", "")

        requests.post(f'http://localhost:8080/annotation?value={line}')

    def process_every_second(self, current_second):
        """
        Process and store statistics for the past one second of TTY data.

        :param current_second:
        :return:
        """
        print(f"We captured {self.num_sensor_readings} sensor readings in the past 1 second.")
        self.num_sensor_readings = 0

