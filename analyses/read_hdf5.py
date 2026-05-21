import json
import sys

import h5py

infile = sys.argv[1]
with h5py.File(infile, "r") as f:
    print(f"Time: {f['trajectory'].attrs['time']}\n")
    print(f"Parameters: {f['trajectory'].attrs['parameters']}\n")
    print(f"Mesh:\n{f['trajectory'].attrs['mesh']}\n")
    print(f"Data Object: {f['trajectory']}\n")
