import datetime
import math
from copy import deepcopy

import numpy as np
from fipy import (
    CellVariable,
    GaussianNoiseVariable,
)
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
            mesh_content = self._generate_mesh_2D()
        elif self.config["dim"] == 3:
            mesh_content = self._generate_mesh_3D()
        else:
            raise ValueError("Invalid dimension choice. Options: 2, 3")
        self.log.debug(mesh_content)

        dset_shape = (
            int(self.config["nsteps"] / self.config["trajectory_write_interval"]) + 1,
            len(self.phi),
        )
        self.traj_writer = TrajectoryWriter(self.config, time, dset_shape, mesh_content)

        self.log.debug("------ Simulation details ------")
        self.log.debug(f"Number of expected output frames: {dset_shape[0]}")
        self.log.debug(f"Number of cells: {len(self.phi)}")

        self._generate_eq_motion()

    def _generate_mesh_2D(self):
        from fipy import PeriodicGrid2D

        # just abbreviate to reduce verbosity
        dx = self.config["dx"]
        dy = self.config["dy"]
        nx = self.config["nx"]
        ny = self.config["ny"]

        mesh = PeriodicGrid2D(
            dx=dx,
            dy=dy,
            nx=nx,
            ny=ny,
        )
        self.phi = self._initialize_field_values(mesh)

        # generate k-space field
        phi_2D = np.reshape(
            self.phi.value, shape=((self.config["nx"], self.config["ny"]))
        )
        self.phi_hat = self._fft_phi(phi_2D, self.config)

        # generate k space wavevectors
        kx = 2 * np.pi * np.fft.fftfreq(nx, d=dx)  # shape (Nx,)
        ky = 2 * np.pi * np.fft.fftfreq(ny, d=dy)  # shape (Ny,)
        self.KX, self.KY = np.meshgrid(kx, ky, indexing="ij")  # shape (Nx, Ny)
        self.K2 = self.KX**2 + self.KY**2
        # self.dealias_mask = self.K2 < (1 / 2) * np.max(self.K2)

        return f"PeriodicGrid2D(dx={self.config['dx']}, dy={self.config['dy']}, nx={self.config['nx']}, ny={self.config['ny']})\n"

    def _generate_mesh_3D(self):
        raise NotImplementedError()
        from fipy import Gmsh2DIn3DSpace

        mesh_content = self._return_file_contents_as_string(self.config["mesh_file"])
        mesh = Gmsh2DIn3DSpace(self.config["mesh_file"]).extrude(
            extrudeFunc=lambda r: 1.1 * r
        )
        self.phi = self._initialize_field_values(mesh)
        return mesh_content

    def _initialize_field_values(self, mesh):
        phi = CellVariable(name=r"$\phi$", mesh=mesh)
        phi.setValue(
            GaussianNoiseVariable(
                mesh=mesh, mean=self.config["phi0"], variance=self.config["phi_var"]
            )
        )
        return phi

    def _generate_eq_motion(self):
        co = self.config  # avoid rewriting self.config a ton in equations
        K2 = self.K2
        k0 = math.sqrt(3.0 / (2 + math.sqrt(1 - (3 * co["b"]))))
        invk0sq = 1 / (k0**2)
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
        with np.errstate(divide="ignore", invalid="ignore"):
            self.eL_inv_m1 = np.where(
                np.abs(c * co["dt"]) < 1e-10,
                co["dt"],  # limit as L_hat → 0
                (np.expm1(c * co["dt"])) / c,
            )
        with np.errstate(divide="ignore", invalid="ignore"):
            self.eL_inv_m1_so = np.where(
                np.abs(c * co["dt"]) < 1e-10,
                co["dt"],  # limit as L_hat → 0
                (np.expm1(c * co["dt"]) - (c * co["dt"])) / (co["dt"] * c**2),
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
        else:
            raise NotImplementedError()

    def _fft_phi(self, phi, conf):
        # FFT to real space in 2D or 3D and recollapse
        if conf["dim"] == 2:
            return np.fft.fft2(phi)
        else:
            raise NotImplementedError()

    def etd2rk(self, phi_hat, eL, eL_inv_m1, K2, conf):
        # get nonlinear term
        phi = self._ifft_phi_hat(phi_hat, conf)
        phi3 = phi**3
        F = (-K2) * conf["D"] * conf["alpha"] * self._fft_phi(phi3, conf)
        an = (eL * phi_hat) + (eL_inv_m1 * F)  # etd1
        an_r = self._ifft_phi_hat(an, conf)
        Fnh = (-K2) * conf["D"] * conf["alpha"] * self._fft_phi(an_r**3, conf)
        # return result of first order exponential time diff
        return an + (self.eL_inv_m1_so * (Fnh - F))

    def _simulate(self):
        self.log.debug("------ Simulation Progress ------")
        self.log.info("# step, avg phi, max phi, min phi, max phi hat")
        self.log.info(
            f"0, {np.mean(self.phi.value)}, {np.max(self.phi.value)}, {np.min(self.phi.value)}, {np.max(self.phi_hat)}"
        )
        with self.traj_writer.traj_file:
            self.traj_writer._write_data(0, self.phi)
            for i in range(1, self.config["nsteps"] + 1):
                self.phi_hat = self.etd2rk(
                    self.phi_hat, self.eL, self.eL_inv_m1, self.K2, self.config
                )
                if i % self.config["trajectory_write_interval"] == 0:
                    phi = self._ifft_phi_hat(self.phi_hat, self.config).ravel()
                    self.phi.setValue(phi)
                    self.traj_writer._write_data(
                        int(i / self.config["trajectory_write_interval"]), self.phi
                    )
                    hat_max = np.unravel_index(
                        self.phi_hat.argmax(), self.phi_hat.shape
                    )
                    self.log.info(
                        f"{i}, {np.mean(self.phi.value)}, {np.max(self.phi.value)}, {np.min(self.phi.value)}, {np.max(self.phi_hat)}, {self.K2[hat_max]}, {self.eL[hat_max]}"
                    )
