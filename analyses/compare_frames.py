import sys

import h5py
import numpy as np

infile = sys.argv[1]
frame1 = int(sys.argv[2])  # -1 for final frame if don't know count
frame2 = int(sys.argv[3])
data = h5py.File(infile, "r")
print(np.allclose(data["trajectory"][frame1], data["trajectory"][frame2]))
