import datetime
import math

import healpy as hp
import numpy as np
from src.fileIO import FileIO
from src.logging import Log
from src.trajectory import TrajectoryWriter


class PFC_Sim(FileIO):
    def __init__(self, config_file):
        time = datetime.datetime.now()
        self.config = self._parse_yaml(config_file)
        log_obj = Log()
        self.log = log_obj._create_log(self.config["log_file"], time)
        log_obj._log_args(self.log, self.config)

        self.log.debug("------ Mesh ------")
        if self.config["dim"] == 2:
            self._generate_mesh_2D()
        elif self.config["dim"] == 3:
            self._generate_mesh_3D()
        else:
            raise ValueError("Invalid dimension choice. Options: 2, 3")
        self.log.debug(
            f"Completed generating mesh in {self.config['dim']} dimensions.\n"
        )

        num_grid_points = len(self.phi_grid.ravel())
        dset_shape = (
            int(self.config["nsteps"] / self.config["trajectory_write_interval"]) + 1,
            num_grid_points,
        )
        self.traj_writer = TrajectoryWriter(self.config, time, dset_shape)

        self.log.debug("------ Simulation details ------")
        self.log.debug(f"Number of expected output frames: {dset_shape[0]}")
        self.log.debug(f"Number of cells: {num_grid_points}")
        if self.config["drain"]:
            self.drain_magnitude = (self.config["phif"] - self.config["phi0"]) / (
                self.config["drain_stop"] - self.config["drain_start"]
            )
            self.log.debug(f"Draining field for first {self.drain_magnitude} steps.")

        self._generate_eq_motion()

    def _generate_mesh_2D(self):
        # just abbreviate to reduce verbosity
        dx = self.config["dx"]
        dy = self.config["dy"]
        nx = self.config["nx"]
        ny = self.config["ny"]

        # generate k-space field
        self.phi_grid = np.random.normal(
            loc=self.config["phi0"],
            scale=math.sqrt(self.config["phi_var"]),
            size=(ny, nx),
        )

        # generate k space wavevectors
        kx = 2 * np.pi * np.fft.fftfreq(nx, d=dx)  # shape (Nx,)
        ky = 2 * np.pi * np.fft.fftfreq(ny, d=dy)  # shape (Ny,)
        self.KX, self.KY = np.meshgrid(kx, ky, indexing="ij")  # shape (Nx, Ny)
        self.K2 = self.KX**2 + self.KY**2

    def _generate_mesh_3D(self):
        nside = self.config["nside"]
        npix = hp.nside2npix(nside)

        self.phi_grid = np.random.normal(
            loc=self.config["phi0"], scale=math.sqrt(self.config["phi_var"]), size=npix
        )

        phi_hat = hp.map2alm(self.phi_grid)
        self.lmax = hp.Alm.getlmax(len(phi_hat))
        ells, ems = hp.Alm.getlm(self.lmax)
        self.K2 = -ells * (ells + 1)

    def _generate_eq_motion(self):
        co = self.config  # avoid rewriting self.config a ton in equations
        K2 = self.K2
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
        self.log.debug(f"Max calculated wavevector from dx (pi/dx): {np.pi / co['dx']}")
        self.log.debug(f"Max 2D plane wavevector magnitude: {np.max(K2)}")
        self.log.debug(f"Max value of linear operator: {np.max(c)}")
        self.log.debug(
            f"Max of exponentiation of linear operator * dt: {np.max(self.eL)}"
        )
        hat_max = np.unravel_index(self.eL.argmax(), self.eL.shape)
        self.log.debug(
            f"Wavevector at max of exponential of linear operator * dt: {K2[hat_max]}"
        )

    def _ifft_phi_hat(self, phi_hat, conf):
        # inverse FFT to real space in 2D or 3D and recollapse
        if conf["dim"] == 2:
            return np.real(np.fft.ifft2(phi_hat))
        if conf["dim"] == 3:
            return hp.alm2map(phi_hat, nside=conf["nside"])
        else:
            raise NotImplementedError()

    def _fft_phi(self, phi, conf):
        # FFT to real space in 2D or 3D and recollapse
        if conf["dim"] == 2:
            return np.fft.fft2(phi)
        if conf["dim"] == 3:
            return hp.map2alm(phi, lmax=self.lmax)
        else:
            raise NotImplementedError()

    def etd1(self, phi, eL, eL_inv_m1, conf):
        phi_hat = self._fft_phi(phi, conf)
        F = self._fft_phi(phi**3, conf)
        phi_hat_new = (eL * phi_hat) + (eL_inv_m1 * F)
        return self._ifft_phi_hat(phi_hat_new, conf)

    def _simulate(self):
        self.log.debug("------ Simulation Progress ------")
        self.log.info("# step, avg phi, max phi, min phi, max phi hat")
        self.log.info(
            f"0, {np.mean(self.phi_grid)}, {np.max(self.phi_grid)}, {np.min(self.phi_grid)}"
        )
        with self.traj_writer.traj_file:
            self.traj_writer._write_data(0, self.phi_grid.ravel())
            for i in range(1, self.config["nsteps"] + 1):
                self.phi_grid = self.etd1(
                    self.phi_grid, self.eL, self.eL_inv_m1, self.config
                )
                if i % self.config["trajectory_write_interval"] == 0:
                    if self.config["dim"] == 2:
                        field = self.phi_grid.ravel()
                    else:
                        # 3D case is handled as 1D array so no need to change
                        field = self.phi_grid
                    self.traj_writer._write_data(
                        int(i / self.config["trajectory_write_interval"]),
                        field,
                    )
                    self.log.info(
                        f"{i}, {np.mean(self.phi_grid)}, {np.max(self.phi_grid)}, {np.min(self.phi_grid)}"
                    )
                if (
                    self.config["drain"]
                    and i >= self.config["drain_start"]
                    and i <= self.config["drain_stop"]
                ):
                    self.phi_grid = np.add(self.phi_grid, self.drain_magnitude)
