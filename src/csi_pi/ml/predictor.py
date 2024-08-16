import pickle

from src.csi_pi.config import Config


class Predictor:

    def __init__(self, config, model_file, voting_window=1000, device_name=None, duration_secs=60):
        super().__init__()
        self.config = config
        self.model_file = model_file
        self.voting_window_size = voting_window
        self.duration_seconds = duration_secs

        self.device_name = None
        for d in self.config.devices:
            if device_name == d:
                self.device_name = d
                break
        if self.device_name is None or device_name is None:
            self.device_name = "all"

    def predict(self):
        # 1. load pkl file
        with open(self.model_file, 'rb') as f:
            model = pickle.load(f)
        # 2. query last few frames from Influx-DB / CSI-file
        
        # 3. run pca & other preprocessing steps
        # 4. make CSI input shape
        # 5. feed into the pkl file
        # 6. get & save predictions into InfluxDB / file
        model.predict()
        # 7. implement majority voting using the last few predictions


if __name__ == '__main__':
    predictor = Predictor(Config(),
                          model_file=self.config.app_dir + "/storage/models/model_h2class_95acc.pkl",
                          voting_window=1000,
                          device_name=None,
                          duration_secs=60)
    print(predictor.predict())
