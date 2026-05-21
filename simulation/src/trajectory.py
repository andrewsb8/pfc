import json

import h5py


class TrajectoryWriter(object):
    def __init__(self, config):
        self.traj = h5py.File(config["trajectory_file"], "w")
        self.traj.create_dataset("trajectory", shape=(1, 1))
        self._store_params(config)

    def _store_params(self, config):
        params_json = json.dumps(config)
        self.traj["trajectory"].attrs["parameters"] = params_json
        self.traj.close()

    def _write_data(self, data):
        pass
