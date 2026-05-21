import json
import sys

import h5py

infile = sys.argv[1]
with h5py.File(infile, "r") as f:
    print(f["trajectory"].attrs["parameters"])
