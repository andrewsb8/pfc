from abc import ABC, abstractmethod

class DimensionStrategy(ABC):
    def __init__(self, sim):
        self.config = sim.config   # copy of PFC_Sim config

    @abstractmethod
    def generate_mesh(self):
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
    def flatten_field(self):
        pass

    @abstractmethod
    def drain(self, dm):
        pass

    @abstractmethod
    def calc_num_grid_points(self):
        pass
