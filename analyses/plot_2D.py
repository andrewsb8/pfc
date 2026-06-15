# example script that prints final frame from an HDF5
# file containing phase field crystal simulation

import json
import sys

import h5py
import matplotlib.pyplot as plt
import numpy as np
from fipy import (
    CellVariable,
    PeriodicGrid2D,
)

infile = sys.argv[1]
frame = int(sys.argv[2])
data = h5py.File(infile, "r")
center_values = data["trajectory"][frame]
params = json.loads(data["trajectory"].attrs["parameters"])

nx = params["nx"]
ny = params["ny"]
dx = params["dx"]
dy = params["dy"]
mesh = PeriodicGrid2D(dx=dx, dy=dy, nx=nx, ny=ny)
phi = CellVariable(name=r"$\phi$", mesh=mesh)
phi.setValue(center_values)

phi_arr = np.array(phi.value).reshape((ny, nx))

# build coordinates of cell centers for extent
x_centers = np.array(mesh.cellCenters[0]).reshape((ny, nx))
y_centers = np.array(mesh.cellCenters[1]).reshape((ny, nx))

# infer domain bounds from centers and dx, dy
x_min = x_centers.min() - dx / 2.0
x_max = x_centers.max() + dx / 2.0
y_min = y_centers.min() - dy / 2.0
y_max = y_centers.max() + dy / 2.0

fig, ax = plt.subplots(figsize=(12, 8))
im = ax.imshow(
    phi_arr,
    origin="lower",
    extent=(x_min, x_max, y_min, y_max),
    cmap="binary_r",
    aspect="equal",
)
fig.colorbar(im, ax=ax, label=r"$\phi$")
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_title(r"Cell values $\phi$ on Grid2D")
plt.tight_layout()
plt.show()
