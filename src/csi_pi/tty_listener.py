import os
import sys
import math
import datetime
import serial
from time import time
from src.csi_pi.helpers import load_from_file


# @See: https://github.com/pyserial/pyserial/issues/216#issuecomment-369414522
class ReadLine:
    #
    # Calculate Statistics
    #
    data_rate_stats = {
        'current_second': None,
        'count': 0,
    }

    wifi_channel = None
    application = None
    experiment_name_set_at = 0
    debug_log = None

    def __init__(self, s, tty_full_path, experiment_name_file_path):
        self.buf = bytearray()
        self.s = s
        self.tty_full_path = tty_full_path
        self.experiment_name_file_path = experiment_name_file_path
        self.experiment_name = self.get_experiment_name()
        self.debug_log = open(f"/tmp/debug{self.tty_full_path}", "a+")

    def debug(self, line):
        now = datetime.datetime.today()
        now_str = f"{now.year}-{now.month}-{now.day} {now.hour:02}:{now.minute:02}:{now.second:02}"
        self.debug_log.write(f"{now_str} :: {line}\n")
        self.debug_log.flush()

    def get_experiment_name(self):
        if self.experiment_name_set_at < os.path.getmtime(self.experiment_name_file_path):
            self.experiment_name = load_from_file(self.experiment_name_file_path)
        return self.experiment_name

    def readline(self):
        i = self.buf.find(b"\n")
        if i >= 0:
            r = self.buf[:i + 1]
            self.buf = self.buf[i + 1:]
            return f"{str(r)[0:-2]},fake_uuid,{time() * 1000},{self.get_experiment_name()}"

        while True:
            # LOOP UNTIL there is a PRINTABLE unit (there may be left over data in the buffer though!)
            i = max(1, min(2048, self.s.in_waiting))

            # Process Data Rate Statistics
            curr_time_seconds = time()
            curr_time_seconds_floor = math.floor(curr_time_seconds)
            if (self.data_rate_stats['current_second'] is None) or \
                    (self.data_rate_stats['current_second'] != curr_time_seconds_floor):
                self.data_rate_stats['current_second'] = curr_time_seconds_floor
                print("Got rate of", self.data_rate_stats['count'], "Hz")

                self.data_rate_stats_file = open(f"/tmp/data_rates{self.tty_full_path}", "a")
                self.data_rate_stats_file.write(f"{curr_time_seconds_floor},{self.data_rate_stats['count']}\n")
                self.data_rate_stats['count'] = 0

            data = self.s.read(i)
            i = data.find(b"\n")
            if i >= 0:
                r = self.buf + data[:i + 1]
                self.buf[0:] = data[i + 1:]

                r = r.decode('utf-8')

                # Determine if this row of data is actually CSI_DATA
                if r[0:-2].split(",")[0] != "CSI_DATA":
                    continue

                # Get Application Name
                application = r[0:-2].split(",")[1]
                if self.application != application:
                    f = open(f"/tmp/application{self.tty_full_path}", "w")
                    f.write(str(application))
                    f.close()

                    self.application = application

                # Get WiFi Channel
                wifi_channel = r[0:-2].split(",")[16]
                if wifi_channel.isdigit() and self.wifi_channel != wifi_channel:
                    f = open(f"/tmp/wifi_channel{self.tty_full_path}", "w")
                    f.write(str(wifi_channel))
                    f.close()

                    self.wifi_channel = wifi_channel

                # Update Data Rate
                self.data_rate_stats['count'] += 1

                return f"{r[0:-2]},fake_uuid,{curr_time_seconds * 1000},{self.get_experiment_name()}"
            else:
                self.buf.extend(data)


if __name__ == "__main__":
    # Parse command arguments
    tty_full_path = sys.argv[1]
    tty_save_path = sys.argv[2]
    experiment_name_file_path = sys.argv[3]

    # Setup Directories for metric files
    os.makedirs("/tmp/debug/dev/", exist_ok=True)
    os.makedirs("/tmp/data_rates/dev/", exist_ok=True)
    os.makedirs("/tmp/wifi_channel/dev/", exist_ok=True)
    os.makedirs("/tmp/application/dev/", exist_ok=True)

    # Clear metric files from previous sessions
    open(f"/tmp/data_rates{tty_full_path}", "w").close()
    open(f"/tmp/debug{tty_full_path}", "w").close()

    while True:
        # Setup serial connection
        ser = serial.Serial(tty_full_path, 921600, timeout=0.1)
        f = open(tty_save_path, "a")
        rl = ReadLine(ser, tty_full_path, experiment_name_file_path)

        # Read incoming serial data
        rl.debug(f"Read incoming serial data")
        while True:
            try:
                csi_line = rl.readline()
                f.write(f"{csi_line}\n")
            except Exception as e:
                # Exception occurred, reset the serial connection
                rl.debug(f"Exception in tty_listener.py: {e}")
                break

        # Close the serial connection
        ser.close()
