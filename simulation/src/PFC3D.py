from src.template import DimensionTemplate
import pyshtools as pysh
import numpy as np
import copy
import math

class PFC3D(DimensionTemplate):
    def __init__(self, sim):
        super().__init__(sim)

    def generate_grid(self):
        lmax = self.config["lmax"]
        ls = np.arange(lmax + 1, dtype=float)
        self.phi_grid = pysh.SHGrid.from_array(np.random.normal(
            loc=self.config["phi0"],
            scale=math.sqrt(self.config["phi_var"]),
            size=(lmax+1, 2*(lmax+1)),
        ), grid="GLQ")
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

    def calc_field_max(self):
        return np.max(self.phi_grid.data)

    def calc_field_min(self):
        return np.min(self.phi_grid.data)

    def flatten_field(self):
        return self.phi_grid.data.ravel()

    def drain(self, dm):
        pass

    def calc_num_grid_points(self):
        return self.phi_grid.nlat * self.phi_grid.nlon

    def log_sim_details(self, log, co, c, eL, eL_inv_m1):
        pass

    def get_grid_shape(self):
        return self.phi_grid.data.shape

    def cube_field(self, field):
        new_field = copy.copy(field)
        new_field.data = new_field.data**3
        return new_field

    def etd1_update(self, eL, field, eL_inv_m1, field_cubed):
        pow_lm = field_cubed.coeffs[0]**2 + field_cubed.coeffs[1]**2
        print("field_cubed max power at m=0:", pow_lm[:, 0].max())
        print("field_cubed max power at m>0:", pow_lm[:, 1:].max())
        lmax = len(eL)-1
        for l in range(lmax + 1):
            field.coeffs[:, l, :l+1] = eL[l] * field.coeffs[:, l, :l+1] + (eL_inv_m1[l] * field_cubed.coeffs[:, l, :l+1])
        return field
