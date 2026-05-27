import datetime
import json
import os

from fipy import (
    CellVariable,
    DiffusionTerm,
    GaussianNoiseVariable,
    Gmsh2DIn3DSpace,
    TransientTerm,
    solvers,
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
        mesh_content = self._return_file_contents_as_string(self.config["mesh_file"])
        self.log.debug(mesh_content)
        self._generate_mesh()

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
        if os.environ.get("FIPY_SOLVERS") == "pyamgx":
            from fipy.solvers.pyamgx.linearGMRESSolver import LinearGMRESSolver

            """cfg_dict = {
                "config_version": 2,
                "determinism_flag": 1,
                "exception_handling": 1,
                "solver": {
                    "print_grid_stats": 1,
                    "store_res_history": 1,
                    "solver": "GMRES",
                    "print_solve_stats": 1,
                    "obtain_timings": 1,
                    "preconditioner": {
                        "interpolator": "D2",
                        "print_grid_stats": 1,
                        "solver": "AMG",
                        "smoother": "JACOBI_L1",
                        "presweeps": 2,
                        "selector": "PMIS",
                        "coarsest_sweeps": 2,
                        "coarse_solver": "NOSOLVER",
                        "max_iters": 1,
                        "interp_max_elements": 4,
                        "min_coarse_rows": 2,
                        "scope": "amg_solver",
                        "max_levels": 24,
                        "cycle": "V",
                        "postsweeps": 2,
                    },
                    "max_iters": 100,
                    "monitor_residual": 1,
                    "gmres_n_restart": 10,
                    "convergence": "RELATIVE_INI_CORE",
                    "tolerance": 1e-06,
                    "norm": "L2",
                },
            }"""

            self.solver = LinearGMRESSolver()
            self.log.debug(f"Solver: {self.solver}")
        else:
            self.solver = None
            self.log.debug(f"Solver: {solvers.DefaultSolver}")

    def _generate_mesh(self):
        mesh = Gmsh2DIn3DSpace(self.config["mesh_file"]).extrude(
            extrudeFunc=lambda r: 1.1 * r
        )
        self.phi = CellVariable(name=r"$\phi$", mesh=mesh)
        self.phi.setValue(GaussianNoiseVariable(mesh=mesh, mean=0, variance=0.04))

    def _generate_eq_motion(self):
        c = self.config  # avoid rewriting self.config a ton in equations
        PHI = self.phi.arithmeticFaceValue
        # define the conserved dynamics equation
        self.sourcey = (c["u4"] * 0.5 * PHI * PHI + c["u3"] * PHI + c["tau"]) + c[
            "D"
        ] * c["K"] * c["qn"] ** 4
        self.eq = TransientTerm() == DiffusionTerm(coeff=self.sourcey) + DiffusionTerm(
            coeff=(2 * c["qn"] ** 2, c["D"] * c["K"])
        ) + DiffusionTerm(coeff=(1.0, 1.0, c["D"] * c["K"]))

    def _simulate(self):
        self.log.debug("------ Simulation Progress ------")
        self.traj_writer._write_data(0, self.phi)
        for i in range(1, self.config["nsteps"] + 1):
            self.eq.solve(self.phi, dt=self.config["dt"], solver=self.solver)
            if i % self.config["trajectory_write_interval"] == 0:
                self.traj_writer._write_data(i, self.phi)
            self.log.info(f"Step {i} complete.")
        self.traj_writer.traj_file.close()
