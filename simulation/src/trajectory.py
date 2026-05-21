import json

import h5py


class TrajectoryWriter(object):
    def __init__(self, config, field_size):
        self.traj_file = h5py.File(config["trajectory_file"], "w")
        dset_shape = (
            int(config["nsteps"] / config["trajectory_write_interval"]) + 1,
            field_size,
        )
        self.traj_file.traj = self.traj_file.create_dataset(
            "trajectory", shape=dset_shape, dtype="float16"
        )
        self._store_params(config)

    def _store_params(self, config):
        params_json = json.dumps(config)
        self.traj_file.traj.attrs["parameters"] = params_json

    def _write_data(self, step, data):
        self.traj_file.traj[step] = data
