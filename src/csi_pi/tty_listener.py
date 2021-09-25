import os
import sys
import math
import serial
from time import time


# @See: https://github.com/pyserial/pyserial/issues/216#issuecomment-369414522
class ReadLine:
    #
    # Calculate Statistics
    #
    data_rate_stats = {
        'current_second': None,
        'count': 0,
    }

    def __init__(self, s, tty_full_path):
        self.buf = bytearray()
        self.s = s
        self.tty_full_path = tty_full_path

    def readline(self):
        i = self.buf.find(b"\n")
        if i >= 0:
            r = self.buf[:i + 1]
            self.buf = self.buf[i + 1:]
            return f"{str(r)[0:-2]},fake_uuid,{time() * 1000},example_experiment_name"

        while True:
            # LOOP UNTIL there is a PRINTABLE unit (there may be left over data in the buffer though!)
            i = max(1, min(2048, self.s.in_waiting))
            data = self.s.read(i)
            i = data.find(b"\n")
            if i >= 0:
                r = self.buf + data[:i + 1]
                self.buf[0:] = data[i + 1:]

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
                self.data_rate_stats['count'] += 1

                return f"{str(r)[0:-2]},fake_uuid,{curr_time_seconds * 1000},example_experiment_name"
            else:
                self.buf.extend(data)


if __name__ == "__main__":
    tty_full_path = sys.argv[1]
    tty_save_path = sys.argv[2]

    ser = serial.Serial(tty_full_path, 921600)
    f = open(tty_save_path, "a")
    rl = ReadLine(ser, tty_full_path)

    # CLEAR File
    os.makedirs("/tmp/data_rates/dev/", exist_ok=True)
    open(f"/tmp/data_rates{tty_full_path}", "w").close()

    while True:
        # LOOP for each PRINTABLE unit
        csi_line = rl.readline()
        # print(csi_line)
        f.write(csi_line + "\n")
