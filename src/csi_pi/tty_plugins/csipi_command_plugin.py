import requests


def get_object(tty_full_path, tty_save_path, experiment_name_file_path, config):
    return CSIPiCommandTTYPlugin(tty_full_path, tty_save_path, experiment_name_file_path, config)


class CSIPiCommandTTYPlugin:
    """
    This TTY Plugin handles CSI-Pi commands starting with `CSIPI_COMMAND,`

    This allows your TTY microcontroller to automatically control CSI-Pi such as

    `CSIPI_COMMAND,ENABLE_CSI` which enable CSI data collection
    `CSIPI_COMMAND,DISABLE_CSI` which disables CSI data collection

    To "install" this plugin, add `src.csi_pi.tty_plugins.csipi_command_plugin` to the
    `TTY_PLUGINS` variable within your `./env` file.
    """
    def __init__(self, tty_full_path, tty_save_path, experiment_name_file_path, config):
        pass

    def prefix_string(self):
        """
        For each incoming line from our devices we will look for the following prefix-string.
        If the line starts with this string, then we will call `process(line)`.
        :return: str
        """

        return "CSIPI_COMMAND,"

    def process(self, line):
        """
        When we find a string that begins with `prefix_string()`, this function will be called.
        Process the incoming line as you wish.

        :param line: str
        :return: None
        """
        if "ENABLE_CSI" in line:
            requests.post(f'http://localhost:8080/enable_csi')
        elif "DISABLE_CSI" in line:
            requests.post(f'http://localhost:8080/disable_csi')
        else:
            print(f"Unknown CSI_PI_COMMAND: '{line}'")

    def process_every_second(self, current_second):
        pass

