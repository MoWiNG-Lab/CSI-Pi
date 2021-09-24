class Metrics:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.most_recent_annotation = None

    def get_data_dir(self):
        return self.data_dir

    def get_is_powered_down(self):
        raise Exception("Not Implemented")

    def set_most_recent_annotation(self, most_recent_annotation):
        self.most_recent_annotation = most_recent_annotation

    def get_most_recent_annotation(self):
        return self.most_recent_annotation

    def get_wifi_channel(self, dev):
        raise Exception("Not Yet Implemented")

    def get_data_rate(self, dev):
        raise Exception("Not Yet Implemented")

    def get_file_size(self, dev):
        raise Exception("Not Yet Implemented")

    def get_most_recent_N_rows(self, dev, n):
        raise Exception("Not Yet Implemented")

    def get_most_recent_csi_datetime(self, dev):
        raise Exception("Not Yet Implemented")

    def get_samples_collected_in_past(self, dev, n_hours):
        raise Exception("Not Yet Implemented")
