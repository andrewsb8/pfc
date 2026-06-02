import sys

import h5py

infile = sys.argv[1]
data = h5py.File(infile, "r")
print(data["trajectory"][-1])
