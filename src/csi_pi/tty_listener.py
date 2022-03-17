import os
import sys
import math
import datetime
import serial
from time import time
from importlib import import_module

sys.path.append(os.path.dirname(__file__) + "/../../")
from src.csi_pi.config import Config
from src.csi_pi.device import Device

tty_plugins = []
current_stats_second = 0


# @See: https://github.com/pyserial/pyserial/issues/216#issuecomment-369414522
class ReadLine:
    debug_log = None

    def __init__(self, ser, tty_full_path):
        self.buf = bytearray()
        self.ser = ser
        self.tty_full_path = tty_full_path
        self.debug_log = open(f"/tmp/debug{self.tty_full_path}", "a+")

    def debug(self, line):
        now = datetime.datetime.today()
        now_str = f"{now.year}-{now.month}-{now.day} {now.hour:02}:{now.minute:02}:{now.second:02}"
        self.debug_log.write(f"{now_str} :: {line}\n")
        self.debug_log.flush()

    def readline(self):
        global current_stats_second

        while True:
            # LOOP UNTIL there is a PRINTABLE unit (there may be left over data in the buffer though!)
            i = max(1, min(2048, self.ser.in_waiting))

            # Process Data Rate Statistics
            now = math.floor(time())
            if current_stats_second != now:
                current_stats_second = now
                for plugin in tty_plugins:
                    try:
                        plugin.process_every_second(current_stats_second)
                    except Exception as e:
                        print(f"ERROR: {plugin}.process_every_second failed with exception: {e}")

            data = self.ser.read(i)
            i = data.find(b"\n")
            if i >= 0:
                r = self.buf + data[:i + 1]
                self.buf[0:] = data[i + 1:]

                r = r.decode('utf-8')

                # Check if this line should be processed by any plugins
                line = r[0:-2]
                for plugin in tty_plugins:
                    prefix = plugin.prefix_string()
                    if prefix in line:
                        ind = line.index(prefix)
                        try:
                            plugin.process(line[ind:])
                        except Exception as e:
                            print(f"ERROR: {plugin}.process failed with exception: {e}")
            else:
                self.buf.extend(data)


if __name__ == "__main__":
    # Parse command arguments
    tty_full_path = sys.argv[1]
    tty_save_path = sys.argv[2]
    experiment_name_file_path = sys.argv[3]

    config = Config()

    tty_plugins = [
        getattr(import_module(s), "get_object")(tty_full_path, tty_save_path, experiment_name_file_path, config)
        for s in config.tty_plugins
    ]

    # Setup Directories for metric files
    os.makedirs("/tmp/debug/dev/", exist_ok=True)

    # Clear metric files from previous sessions
    open(f"/tmp/debug{tty_full_path}", "w").close()

    # If the serial connection fails for any reason, automatically re-try.
    while True:
        # Setup serial connection
        ser = serial.Serial(tty_full_path, Device.get_device_baud_rate(config, tty_full_path), timeout=0.1)

        rl = ReadLine(ser, tty_full_path)

        # Read incoming serial data
        rl.debug(f"Read incoming serial data")
        while True:
            try:
                rl.readline()
            except Exception as e:
                # Exception occurred, reset the serial connection
                rl.debug(f"Exception in tty_listener.py: {e}")
                break

        # Close the serial connection
        ser.close()
