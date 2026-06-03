import datetime
import json
import math
import os

from fipy import (
    CellVariable,
    DiffusionTerm,
    GaussianNoiseVariable,
    TransientTerm,
)
from src.fileIO import FileIO
from src.logging import Log
from src.trajectory import TrajectoryWriter

# from fipy.tools import dump # may want when generating output time steps


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
        self._configure_solver()
        self.log.debug(f"Number of expected output frames: {dset_shape[0]}")
        self.log.debug(f"Number of cells: {len(self.phi)}")
        self.log.debug("")

        self._generate_eq_motion()

    def _configure_solver(self):
        env_var = os.environ.get("FIPY_SOLVERS")
        if env_var == "pyamgx":
            from fipy.solvers.pyamgx import LinearGMRESSolver

            self.solver = LinearGMRESSolver(iterations=self.config["iterations"])
        else:
            from fipy.solvers.scipy import LinearGMRESSolver

            self.solver = LinearGMRESSolver(iterations=self.config["iterations"])
        self.log.debug(f"FIPY_SOLVERS={env_var}")
        self.log.debug(f"Solver: {self.solver}")

    def _generate_mesh_2D(self):
        from fipy import PeriodicGrid2D

        mesh = PeriodicGrid2D(
            dx=0.5, dy=0.5, nx=self.config["nx"], ny=self.config["ny"]
        )
        self._initialize_field_values(mesh)
        return f"PeriodicGrid2D(dx=0.5, dy=0.5, nx={self.config['nx']}, ny={self.config['ny']})\n"

    def _generate_mesh_3D(self):
        from fipy import Gmsh2DIn3DSpace

        mesh_content = self._return_file_contents_as_string(self.config["mesh_file"])
        mesh = Gmsh2DIn3DSpace(self.config["mesh_file"]).extrude(
            extrudeFunc=lambda r: 1.1 * r
        )
        self._initialize_field_values(mesh)
        return mesh_content

    def _initialize_field_values(self, mesh):
        self.phi = CellVariable(name=r"$\phi$", mesh=mesh, hasOld=True)
        self.phi.setValue(
            GaussianNoiseVariable(
                mesh=mesh, mean=self.config["phi0"], variance=self.config["phi_var"]
            )
        )

    def _generate_eq_motion(self):
        c = self.config  # avoid rewriting self.config a ton in equations
        PHI = self.phi.arithmeticFaceValue
        k = math.sqrt(3.0 / (2 + math.sqrt(1 - (3 * c["b"]))))
        invksq = 1 / (k**2)
        # define the conserved dynamics equation
        self.eq = TransientTerm() == DiffusionTerm(
            coeff=3 * c["alpha"] * PHI * PHI - c["alpha"]
        ) + DiffusionTerm(coeff=(1.0, invksq)) + DiffusionTerm(
            coeff=(-1.0, c["b"] * invksq)
        ) + DiffusionTerm(coeff=(1.0, invksq, 2 * invksq)) + DiffusionTerm(
            coeff=(1.0, invksq, invksq, invksq)
        )

    def _simulate(self):
        self.log.debug("------ Simulation Progress ------")
        self.log.info("# step, residual")
        with self.solver, self.traj_writer.traj_file:
            self.traj_writer._write_data(0, self.phi)
            for i in range(1, self.config["nsteps"] + 1):
                self.phi.updateOld()
                residual = self.eq.sweep(
                    var=self.phi, dt=self.config["dt"], solver=self.solver
                )
                if i % self.config["trajectory_write_interval"] == 0:
                    self.traj_writer._write_data(i, self.phi)
                self.log.info(f"{i}, {residual}")
