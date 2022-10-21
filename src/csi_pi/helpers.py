import os
import psutil
import datetime

from src.csi_pi.config import Config


def setup_experiment_filesystem(config: Config):
    """
    When a new experiment begins (i.e. when CSI-Pi restarts), setup the filesystem to store:
    annotations, notes, csi_enabled_or_disabled_flag, etc.

    :param config:
    :return:
    """
    print("DATA_DIR:", config.data_dir)

    # Create new directory each time the app is run
    os.makedirs(config.data_dir, exist_ok=True)

    # Add file for annotations
    config.data_file_names['annotations'] = open(config.data_dir + "annotations.csv", "w+")
    config.data_file_names['annotations'].write("type,smartphone_id,timestamp,current_action\n")
    config.data_file_names['annotations'].flush()

    # Add file for notes
    config.data_file_names['notes'] = config.data_dir + "notes.txt"
    f = open(config.data_file_names['notes'], "w+")
    f.write("Empty Note")
    f.flush()

    # Enabled CSI by default
    toggle_csi(config, "1")


def load_from_file(file_name):
    """
    Load the content of a file as a string

    :param file_name:
    :return:
    """
    output = ""

    if os.path.exists(file_name):
        f = open(file_name, 'r')
        output = f.read()
        f.close()

    return output


def toggle_csi(config: Config, value):
    """
    Toggle CSI on or off (depending on `value).
    Store the toggle state to a file.

    :param config:
    :param value: bool
    :return:
    """
    with open(config.WRITE_CSI_LOCK, 'w') as f:
        f.write(value)


def get_is_csi_enabled(config: Config):
    """
    Get CSI toggle status from file.

    :param config:
    :return:
    """
    with open(config.WRITE_CSI_LOCK, 'r') as f:
        toggle = bool(int(f.read()))

    return toggle


def kill_child_processes():
    """
    When the python process is killed (at exit), clean up all existing child processes

    :return:
    """
    pid = os.getpid()
    for child in psutil.Process(pid).children(recursive=True):
        try:
            child.kill()
        except:
            pass


def format_file_size(file_size):
    if file_size > 1e9:
        file_size = f"{(file_size / 1e9):.1f} GBs"
    elif file_size > 1e6:
        file_size = f"{(file_size / 1e6):.1f} MBs"
    else:
        file_size = f"{(file_size / 1e3):.1f} kBs"

    return file_size


def format_seconds(file_size):
    if file_size >= 60 * 60:
        file_size = f"{(file_size / (60 * 60)):.1f} hours(s)"
    elif file_size >= 60:
        file_size = f"{(file_size / 60):.1f} minute(s)"
    else:
        file_size = f"{file_size} second(s)"

    return file_size
