# example script that prints final frame from an HDF5
# file containing phase field crystal simulation

import sys

import h5py
import matplotlib.pyplot as plt
import numpy as np
import pyshtools as pysh

infile = sys.argv[1]
frame = int(sys.argv[2])
data = h5py.File(infile, "r")
field = np.array(data["trajectory"][frame])
array_shape = (int(data["trajectory"].attrs["grid_shape_ax0"]), int(data["trajectory"].attrs["grid_shape_ax1"]))
grid = pysh.SHGrid.from_array(field.reshape(array_shape), grid="GLQ")
fig, ax = grid.plot()
plt.show()
