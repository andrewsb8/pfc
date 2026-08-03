from abc import ABC, abstractmethod

class DimensionTemplate(ABC):
    def __init__(self, sim):
        self.config = sim.config   # copy of PFC_Sim config

    @abstractmethod
    def generate_grid(self):
        pass

    @abstractmethod
    def transform_to_real(self, field):
        pass

    @abstractmethod
    def transform_to_spectral(self, field):
        pass

    @abstractmethod
    def calc_field_mean(self):
        pass

    @abstractmethod
    def calc_field_max(self):
        pass

    @abstractmethod
    def calc_field_min(self):
        pass

    @abstractmethod
    def flatten_field(self):
        pass

    @abstractmethod
    def drain(self, dm):
        pass

    @abstractmethod
    def get_grid_shape(self):
        pass

    @abstractmethod
    def cube_field(self, field):
        pass

    @abstractmethod
    def etd1_update(self, eL, field, eL_inv_m1, field_cubed):
        pass
