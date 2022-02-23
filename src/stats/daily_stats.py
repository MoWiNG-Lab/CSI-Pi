import os
import math
import requests
import shutil
from time import time

from src.csi_pi.device import Device


def format_file_size(file_size):
    if file_size > 1e9:
        file_size = f"{(file_size / 1e9):.1f} GBs"
    elif file_size > 1e6:
        file_size = f"{(file_size / 1e6):.1f} MBs"
    else:
        file_size = f"{(file_size / 1e3):.1f} kBs"

    return file_size

curr_time_seconds = math.floor(time())
currently_connected_devices = Device.get_currently_connected_devices()
for tty_full_path in currently_connected_devices:
    try:
        with open(f"/tmp/data_rates{tty_full_path}", "r") as f:
            # Get WiFi Channel
            with open(f"/tmp/wifi_channel{tty_full_path}", "r") as channel_f:
                channel = channel_f.read()

            # Get Data Rate Stats
            stats = {
                '10_min': 0,
                '60_min': 0,
                '24_hour': 0,
                'overall': 0,
            }
            for l in f.readlines():
                line_time = int(l.split(",")[0])
                line_samples_count = int(l.split(",")[1])

                stats['overall'] += line_samples_count
                if curr_time_seconds - (60 * 10) < line_time:
                    stats['10_min'] += line_samples_count
                if curr_time_seconds - (60 * 60) < line_time:
                    stats['60_min'] += line_samples_count
                if curr_time_seconds - (60 * 60 * 24) < line_time:
                    stats['24_hour'] += line_samples_count

            # Get File Size
            raw_data_directory = requests.get(url="http://localhost:8080/data-directory").text
            file_size = format_file_size(os.path.getsize(f"{raw_data_directory}{tty_full_path.split('/')[-1]}.csv"))

            # Print Results
            print(f"{tty_full_path}, Channel: {channel}, {stats['10_min']} collected [10 minutes], {stats['60_min']} collected [1 hour], {stats['24_hour']} [24 hours], {stats['overall']} [overall], {file_size}")
    except Exception as e:
        print(f"{tty_full_path}, Exception while calculating stats: ", e)

storage_used = format_file_size(shutil.disk_usage("/").used)
storage_available = format_file_size(shutil.disk_usage("/").total)
print(f"Total Storage Used: {storage_used}, Available: {storage_available}).")
