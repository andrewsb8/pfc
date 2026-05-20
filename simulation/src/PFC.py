import math

import numpy as np
import yaml
from fipy import (
    CellVariable,
    DiffusionTerm,
    GaussianNoiseVariable,
    Gmsh2DIn3DSpace,
    TransientTerm,
)
from src.logging import Log

# from fipy.tools import dump # may want when generating output time steps


class PFC_Sim(object):
    def __init__(self, config_file):
        self.config = self._parse_config(config_file)
        log_obj = Log()
        self.log = log_obj._create_log(self.config["log_file"])
        log_obj._log_args(self.log, self.config)
        self._generate_mesh()

    def _parse_config(self, config_file):
        with open(config_file, "r") as file:
            return yaml.safe_load(file)

    def _generate_mesh(self):
        c = self.config  # avoid rewriting self.config a ton in equations
        mesh = Gmsh2DIn3DSpace(self.config["mesh_file"]).extrude(
            extrudeFunc=lambda r: 1.1 * r
        )

        # gmsh code for creating meshed sphere is given above
        # set up variables, parameters, and initial condition
        self.phi = CellVariable(name=r"$\phi$", mesh=mesh)
        self.phi.setValue(GaussianNoiseVariable(mesh=mesh, mean=0, variance=0.04))
        self.PHI = self.phi.arithmeticFaceValue

        # define the conserved dynamics equation
        self.sourcey = (
            c["u4"] * 0.5 * self.PHI * self.PHI + c["u3"] * self.PHI + c["tau"]
        ) + c["D"] * c["K"] * c["qn"] ** 4
        self.eq = TransientTerm() == DiffusionTerm(coeff=self.sourcey) + DiffusionTerm(
            coeff=(2 * c["qn"] ** 2, c["D"] * c["K"])
        ) + DiffusionTerm(coeff=(1.0, 1.0, c["D"] * c["K"]))

    def _simulate(self):
        for i in range(self.config["nsteps"]):
            print(self.phi)
            print(len(self.phi))
            self.eq.solve(self.phi, dt=self.config["dt"])
