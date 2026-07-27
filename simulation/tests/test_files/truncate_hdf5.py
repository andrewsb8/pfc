import json
import sys

import h5py

infile = sys.argv[1]
data = h5py.File(infile, "r+")
dataset_len = len(data["trajectory"][-1])
new_data = [0 for i in range(dataset_len)]

data["trajectory"].attrs["steps_written"] = 3
data["trajectory"][-1] = new_data
data["trajectory"][-2] = new_data

data.close()
