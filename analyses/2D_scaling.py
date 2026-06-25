import json
import math
import sys

import h5py
import matplotlib.pyplot as plt
import numpy as np
from skimage import measure

infile = sys.argv[1]
starting_frame = int(sys.argv[2])
plot = True
data = h5py.File(infile, "r")

params = json.loads(data["trajectory"].attrs["parameters"])
nx = params["nx"]
ny = params["ny"]
dx = params["dx"]
dy = params["dy"]
total_area = nx * dx * ny * dy

if plot:
    time = []
    total_bubble_areas = []
    num_bubbles = []
    avg_rs = []

for i in range(starting_frame, len(data["trajectory"])):
    t = i * params["dt"] * params["trajectory_write_interval"]
    center_values = data["trajectory"][i]
    total_bubble_area = sum(
        [
            dx * dy
            for i in range(len(center_values))
            if center_values[i] > params["phi0"]
        ]
    )
    phi_arr = np.array(center_values).reshape((ny, nx))
    contours = measure.find_contours(phi_arr, level=params["phi0"])
    bubble_count = len(contours)
    avg_A = total_bubble_area / len(contours)
    avg_r = math.sqrt(avg_A / (4 * np.pi))
    print(
        t,
        total_area,
        total_bubble_area,
        bubble_count,
        avg_A,
        avg_r,
    )
    if plot:
        time.append(t)
        total_bubble_areas.append(total_bubble_area)
        num_bubbles.append(bubble_count)
        avg_rs.append(avg_r)

if plot:
    if params["drain"]:
        lab = r"t$^{1/2}$"
        scale = np.array(time) ** (1 / 2)
    else:
        lab = r"t$^{1/3}$"
        scale = np.array(time) ** (1 / 3)
    fig, ax = plt.subplots(1, 1, figsize=(8, 8))
    ax.loglog(time, avg_rs, label="<r>")
    ax.loglog(time, scale, label=lab, linestyle="--")
    ax.set_xlabel("t", fontsize=16)
    ax.set_ylabel("<r>", fontsize=16)
    ax.tick_params("both", labelsize=14)
    ax.legend(fontsize=14)
    plt.show()
