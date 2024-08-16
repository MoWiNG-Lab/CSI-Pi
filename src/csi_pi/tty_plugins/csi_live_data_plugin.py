import threading
from copy import deepcopy
from time import time

from influxdb import InfluxDBClient
import asyncio


def get_object(tty_full_path, tty_save_path, config):
    return CSILiveDataTTYPlugin(tty_full_path, tty_save_path, config)


class CSILiveDataTTYPlugin:

    # noinspection PyUnusedLocal
    def __init__(self, tty_full_path, tty_save_path, config):
        print(f"CSILiveDataPlugin: class is going to be initialized ...")
        self.log_file = open("/tmp/csi_live.log", "w")
        self.tty_full_path = tty_full_path
        self.config = config
        self.json_points_cache = []
        self.json_points_cache_to_write = []
        self.idb_client = InfluxDBClient(host=self.config.hostname, port=self.config.influxdb_port,
                                         username=self.config.influxdb_user,
                                         password=self.config.influxdb_pwd,
                                         database=self.config.influxdb_dbn)

    # noinspection PyMethodMayBeStatic
    def prefix_string(self):
        """
        For each incoming line from our devices we will look for the following prefix-string.
        If the line starts with this string, then we will call `process(line)`.
        :return: str
        """
        return "CSI_DATA,"

    def process(self, line):
        csi_line = f"{line},fake_uuid,{time() * 1000},default_experiment_name"
        jo = [{
            "measurement": "csi",
            "fields": {
                "source": self.tty_full_path,
                "csi_line": csi_line
            }
        }]
        asyncio.run(self.idb_client.write_points(jo))

        # self.json_points_cache.append(jo)
        # self.log_file.write(f"JSON Points so far = {len(self.json_points_cache)}\n")
        # if len(self.json_points_cache) >= 50:
        #     self.log_file.write(f"Going to write of length = {len(self.json_points_cache)}\n")
        #     self.json_points_cache_to_write = deepcopy(self.json_points_cache)
        #     threading.Thread(target=async_save_to_db, name='async_save_to_db', daemon=True)
        #     self.json_points_cache = []

    # def async_save_to_db(self):
    #     ji = 0
    #     for j in self.json_points_cache_to_write:
    #         try:
    #             # self.log_file.write(f"j: {j}")
    #             r = self.idb_client.write_points([j])
    #             # self.log_file.write(f"{ji}: {r}, ")
    #             ji += 1
    #         except Exception as e:
    #             print(e)
    #             # self.log_file.write(f"Exception: {e}")

    def process_every_millisecond(self, current_millisecond):
        """
        Process and store statistics for the past one second of TTY data.

        :param current_millisecond:
        :return:
        """
        pass
