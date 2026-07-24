import datetime
import math

import numpy as np
from src.fileIO import FileIO
from src.logging import Log
from src.trajectory import TrajectoryWriter
from src.PFC2D import PFC2D
from src.PFC3D import PFC3D

class PFC_Sim(FileIO):
    def __init__(self, config_file):
        time = datetime.datetime.now()
        self.config = self._parse_yaml(config_file)
        log_obj = Log()
        self.log = log_obj._create_log(self.config["log_file"], time)
        log_obj._log_args(self.log, self.config)
        self.dim_specific = self._set_dimension()

        self.log.debug("------ Grid ------")
        self.dim_specific.generate_grid()
        num_grid_points = self.dim_specific.calc_num_grid_points()
        grid_shape = self.dim_specific.get_grid_shape()
        self.log.debug(f"Number of cells: {num_grid_points}")
        self.log.debug(f"Grid shape: {grid_shape}")
        self.log.debug(
            f"Completed generating grid in {self.config['dim']} dimensions.\n"
        )

        dset_shape = (
            int(self.config["nsteps"] / self.config["trajectory_write_interval"]) + 1,
            num_grid_points,
        )
        self.traj_writer = TrajectoryWriter(self.config, time, dset_shape, grid_shape)

        self.log.debug("------ Simulation details ------")
        self.log.debug(f"Number of expected output frames: {dset_shape[0]}")
        if self.config["drain"]:
            self.drain_magnitude = (self.config["phif"] - self.config["phi0"]) / (
                self.config["drain_stop"] - self.config["drain_start"]
            )
            self.log.debug(
                f"Draining field from step {self.config['drain_start']} to {self.config['drain_stop']}."
            )

        self._generate_eq_motion()
        self.log.debug("")

    def _set_dimension(self):
        if self.config["dim"] == 2:
            return PFC2D(self)
        elif self.config["dim"] == 3:
            return PFC3D(self)
        raise ValueError(f"Unsupported dimension: {self.config['dim']}")

    def _generate_eq_motion(self):
        co = self.config  # avoid rewriting self.config a ton in equations
        K2 = self.dim_specific.K2
        print("K2: ", K2)
        k0 = math.sqrt(3.0 / (2 + math.sqrt(1 - (3 * co["b"]))))
        invk0sq = 1 / (k0**2)
        # linear operator in k space
        c = (
            -co["D"]
            * K2
            * (
                (
                    K2 * invk0sq * (co["q0"] - (K2 * invk0sq)) ** 2
                    + (co["b"] * K2 * invk0sq)
                )
                - co["alpha"]
            )
        )

        # Pre-compute ETD coefficients
        self.eL = np.exp(c * co["dt"])
        # Stable computation of (e^x - 1)/x via expm1 to avoid cancellation near x≈0
        # Include other coefficients of nonlinear term
        with np.errstate(divide="ignore", invalid="ignore"):
            self.eL_inv_m1 = np.where(
                np.abs(c * co["dt"]) < 1e-10,
                (-K2) * co["D"] * co["alpha"] * co["dt"],  # limit as L_hat → 0
                (-K2) * co["D"] * co["alpha"] * (np.expm1(c * co["dt"])) / c,
            )

        self.dim_specific.log_sim_details(self.log, self.config, c, self.eL, self.eL_inv_m1)

    def etd1(self, phi, eL, eL_inv_m1):
        phi3 = self.dim_specific.cube_field(phi)
        phi_hat = self.dim_specific.transform_to_spectral(phi)
        F = self.dim_specific.transform_to_spectral(phi3)
        phi_hat_new = self.dim_specific.etd1_update(eL, phi_hat, eL_inv_m1, F)
        return self.dim_specific.transform_to_real(phi_hat_new)

    def _simulate(self):
        self.log.debug("------ Simulation Progress ------")
        self.log.info("# step, avg phi, max phi, min phi, max phi")
        self.log.info(
            f"0, {self.dim_specific.calc_field_mean()}, {self.dim_specific.calc_field_max()}, {self.dim_specific.calc_field_min()}"
        )
        with self.traj_writer.traj_file:
            self.traj_writer._write_data(0, self.dim_specific.flatten_field())
            for i in range(1, self.config["nsteps"] + 1):
                self.dim_specific.phi_grid = self.etd1(
                    self.dim_specific.phi_grid, self.eL, self.eL_inv_m1
                )
                if i % self.config["trajectory_write_interval"] == 0:
                    self.traj_writer._write_data(
                        int(i / self.config["trajectory_write_interval"]),
                        self.dim_specific.flatten_field(),
                    )
                    self.log.info(
                        f"{i}, {self.dim_specific.calc_field_mean()}, {self.dim_specific.calc_field_max()}, {self.dim_specific.calc_field_min()}"
                    )
                if (
                    self.config["drain"]
                    and i >= self.config["drain_start"]
                    and i <= self.config["drain_stop"]
                ):
                    self.dim_specific.phi_grid = self.dim_specific.drain(self.drain_magnitude)
