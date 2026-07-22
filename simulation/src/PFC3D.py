from src.template import DimensionTemplate
import pyshtools as pysh
import numpy as np

class PFC3D(DimensionTemplate):
    def __init__(self, sim):
        super().__init__(sim)

    def generate_grid(self):
        ls = np.arange(self.config["lmax"] + 1, dtype=float)
        power = np.zeros_like(ls)
        power[1:] = ls[1:] ** -2  # e.g. power-law spectrum

        coeffs = pysh.SHCoeffs.from_random(power)
        # Set the mean through l=0, m=0
        coeffs.set_coeffs(self.config["phi0"], 0, 0)

        self.phi_grid = coeffs.expand(grid='GLQ')
        self.K2 = -ls * (ls + 1)

    def transform_to_real(self, field):
        return field.expand(grid='GLQ')

    def transform_to_spectral(self, field):
        return field.expand()

    def calc_field_mean(self):
        lon_mean = np.mean(self.phi_grid.data, axis=1)
        mean_val = np.sum(self.phi_grid.weights * lon_mean) / np.sum(self.phi_grid.weights)

        # logic for field variance
        """lon_mean_sq = np.mean(self.phi_grid**2, axis=1)
        mean_sq = np.sum(self.phi_grid.weights * lon_mean_sq) / np.sum(self.phi_grid.weights)
        var_val = mean_sq - mean_val**2
        print("area-weighted var:", var_val)"""

        return mean_val

    def flatten_field(self):
        pass

    def drain(self, dm):
        pass

    def calc_num_grid_points(self):
        return self.phi_grid.nlat * self.phi_grid.nlon

    def log_sim_details(self, log, co, c, eL, eL_inv_m1):
        pass

    def get_grid_shape(self):
        return self.phi_grid.data.shape
