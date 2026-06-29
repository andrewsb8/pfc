import json
import sys

import h5py
import matplotlib.pyplot as plt
import numpy as np
from skimage import measure

infile = sys.argv[1]
frame = int(sys.argv[2])
plot = True
data = h5py.File(infile, "r")
center_values = data["trajectory"][frame]

params = json.loads(data["trajectory"].attrs["parameters"])
nx = params["nx"]
ny = params["ny"]
dx = params["dx"]
dy = params["dy"]
total_area = nx * dx * ny * dy
if params["drain"]:
    level = params["phif"]
else:
    level = params["phi0"]

phi_arr = np.array(center_values).reshape((ny, nx))
contours = measure.find_contours(phi_arr, level=level)
bubble_count = len(contours)

polygon_vertex_counts = []
for contour in contours:
    poly = measure.approximate_polygon(contour, tolerance=1.5)
    if len(poly) > 1 and np.allclose(poly[0], poly[-1]):
        poly = poly[:-1]
    # print(poly)
    polygon_vertex_counts.append(len(poly))
print(polygon_vertex_counts)
bins = np.arange(1, max(polygon_vertex_counts) + 1, 1)
hist, edges = np.histogram(polygon_vertex_counts, bins=bins)
print(hist)

plt.bar(edges[:-1], hist, edgecolor="black", align="center")
plt.xlabel("Vertex Count", fontsize=16)
plt.ylabel("Count", fontsize=16)
plt.tick_params("both", labelsize=14)
plt.show()
