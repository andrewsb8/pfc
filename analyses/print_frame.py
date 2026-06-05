import sys

import h5py

infile = sys.argv[1]
frame = int(sys.argv[2])  # -1 for final frame if don't know count
data = h5py.File(infile, "r")
print(data["trajectory"][frame])
