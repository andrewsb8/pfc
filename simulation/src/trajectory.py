import h5py


class TrajectoryWriter(object):
    def __init__(self, config):
        self.traj_file = h5py.File(config["trajectory_file"], "w")

    def _create_dataset(self, dset_shape):
        self.traj_file.traj = self.traj_file.create_dataset(
            "trajectory", shape=dset_shape, dtype="float16"
        )

    def _store_attribute(self, name, content):
        self.traj_file.traj.attrs[name] = content

    def _write_data(self, step, data):
        self.traj_file.traj[step] = data
