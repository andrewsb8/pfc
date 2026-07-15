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
