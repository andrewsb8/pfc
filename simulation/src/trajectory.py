import json

import h5py


class TrajectoryWriter(object):
    def __init__(self, config, time, dset_shape, mesh_content):
        self.traj_file = h5py.File(config["trajectory_file"], "w")
        self._create_dataset(dset_shape)
        self._store_attribute("time", str(time))
        self._store_attribute("parameters", json.dumps(config))
        self._store_attribute("mesh", mesh_content)

    def _create_dataset(self, dset_shape):
        self.traj_file.traj = self.traj_file.create_dataset(
            "trajectory", shape=dset_shape, dtype="float16"
        )

    def _store_attribute(self, name, content):
        self.traj_file.traj.attrs[name] = content

    def _write_data(self, step, data):
        self.traj_file.traj[step] = data
