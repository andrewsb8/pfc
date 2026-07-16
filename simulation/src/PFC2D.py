from src.strategy import DimensionStrategy
import math
import numpy as np

class PFC2D(DimensionStrategy):
    def __init__(self, sim):
        super().__init__(sim)

    def generate_mesh(self):
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

    def transform_to_real(self, field):
        return np.real(np.fft.ifft2(field))

    def transform_to_spectral(self, field):
        return np.fft.fft2(field)

    def drain(self, dm):
        return np.add(self.phi_grid, dm)

    def calc_field_mean(self):
        return np.mean(self.phi_grid)

    def flatten_field(self):
        return self.phi_grid.ravel()

    def calc_num_grid_points(self):
        return len(self.phi_grid.ravel())

    def log_sim_details(self, log, co, c, eL, eL_inv_m1):
        K2 = self.K2
        log.debug(f"Max calculated wavevector from dx (pi/dx): {np.pi / co['dx']}")
        log.debug(f"Max 2D plane wavevector magnitude: {np.max(K2)}")
        log.debug(f"Max value of linear operator: {np.max(c)}")
        log.debug(
            f"Max of exponentiation of linear operator * dt: {np.max(eL)}"
        )
        hat_max = np.unravel_index(eL.argmax(), eL.shape)
        log.debug(
            f"Wavevector at max of exponential of linear operator * dt: {K2[hat_max]}"
        )
