import h5py


class TrajectoryWriter(object):
    def __init__(self, config):
        self.traj_file = h5py.File(config["trajectory_file"], "w")

    def _create_dataset(self, config, field_size):
        dset_shape = (
            int(config["nsteps"] / config["trajectory_write_interval"]) + 1,
            field_size,
        )
        self.traj_file.traj = self.traj_file.create_dataset(
            "trajectory", shape=dset_shape, dtype="float16"
        )

    def _store_attribute(self, name, content):
        self.traj_file.traj.attrs[name] = content

    def _write_data(self, step, data):
        self.traj_file.traj[step] = data
