import os
import math
import requests
import shutil
import json
from time import time


def format_file_size(file_size):
    if file_size > 1e9:
        file_size = f"{(file_size / 1e9):.1f} GBs"
    elif file_size > 1e6:
        file_size = f"{(file_size / 1e6):.1f} MBs"
    else:
        file_size = f"{(file_size / 1e3):.1f} kBs"

    return file_size

curr_time_seconds = math.floor(time())
server_stats = json.loads(requests.get(url="http://localhost:8080/server-stats").text)

# For each ESP32
for tty_full_path in server_stats['devices']:
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
                line_time = float(l.split(",")[0])
                line_samples_count = int(l.split(",")[1])

                stats['overall'] += line_samples_count
                if curr_time_seconds - (60 * 10) < line_time:
                    stats['10_min'] += line_samples_count
                if curr_time_seconds - (60 * 60) < line_time:
                    stats['60_min'] += line_samples_count
                if curr_time_seconds - (60 * 60 * 24) < line_time:
                    stats['24_hour'] += line_samples_count

            # Get File Size
            data_directory = server_stats['data_directory']
            file_size = format_file_size(os.path.getsize(f"{data_directory}{tty_full_path.split('/')[-1]}.csv"))

            # Print Results
            print(f"{tty_full_path}, Channel: {channel}, {stats['10_min']} collected [10 minutes], {stats['60_min']} collected [1 hour], {stats['24_hour']} [24 hours], {stats['overall']} [overall], {file_size}")
    except Exception as e:
        print(f"{tty_full_path}, Exception while calculating stats: ", e)

# For each camera
for i, camera_photo_burst_path in enumerate(server_stats['cameras']):
    print(f"Camera #{i}: {len(os.listdir(camera_photo_burst_path))} photos")

storage_used = format_file_size(shutil.disk_usage("/").used)
storage_available = format_file_size(shutil.disk_usage("/").total)
print(f"Total Storage Used: {storage_used}, Available: {storage_available}.")
