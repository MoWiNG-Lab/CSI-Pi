import sys
import os
import math
import requests
import shutil
import json
from time import time

sys.path.append(sys.path[0] + "/../../")
from src.csi_pi.helpers import format_file_size, format_seconds

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
for i, c in enumerate(server_stats['cameras']):
    print(f"Camera #{i}: {c['photo_burst']['count']} photos, {format_file_size(c['photo_burst']['size'])}")
    print(f"Camera #{i}: {c['video_recorder_legacy_count']['count']} videos ({format_seconds(c['video_recorder_legacy_count']['video_length'])} each), {format_file_size(c['video_recorder_legacy_count']['size'])}")

storage_used = format_file_size(shutil.disk_usage("/").used)
storage_available = format_file_size(shutil.disk_usage("/").total)
print(f"Total Storage Used: {storage_used}, Available: {storage_available}.")
