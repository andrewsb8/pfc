import sys

import h5py

infile = sys.argv[1]
frame = sys.argv[2]  # -1 for final frame if don't know count
data = h5py.File(infile, "r")
print(data["trajectory"][-1])
