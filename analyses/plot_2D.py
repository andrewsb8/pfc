# example script that prints final frame from an HDF5
# file containing phase field crystal simulation

import json
import sys

import h5py
import matplotlib.pyplot as plt
import numpy as np

infile = sys.argv[1]
frame = int(sys.argv[2])
data = h5py.File(infile, "r")
center_values = data["trajectory"][frame]
params = json.loads(data["trajectory"].attrs["parameters"])

nx = params["nx"]
ny = params["ny"]
dx = params["dx"]
dy = params["dy"]

phi_arr = np.array(center_values).reshape((ny, nx))

# infer domain bounds from centers and dx, dy
x_min = 0 - dx / 2.0
x_max = nx + dx / 2.0
y_min = 0 - dy / 2.0
y_max = ny + dy / 2.0

fig, ax = plt.subplots(figsize=(12, 8))
im = ax.imshow(
    phi_arr,
    origin="lower",
    extent=(x_min, x_max, y_min, y_max),
    cmap="binary_r",
    aspect="equal",
)
cbar = fig.colorbar(im, ax=ax)
cbar.set_label(r"$\phi$", fontsize=16)
cbar.ax.tick_params(labelsize=14)
ax.set_xlabel("x", fontsize=16)
ax.set_ylabel("y", fontsize=16)
ax.tick_params("both", labelsize=14)
plt.tight_layout()
plt.show()
