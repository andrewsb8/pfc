import json
import sys

import freud
import h5py
import matplotlib.pyplot as plt
import numpy as np
from periodic_contours import stitch_contours
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
contour_groups = stitch_contours(contours, params)
bubble_count = len(contours)

fig, ax = plt.subplots(1, 1, figsize=(8, 8))
# Plot the original field
ax.imshow(phi_arr, cmap="binary_r", origin="lower")
centroids = []
open_count = 0
for contour in contours:
    if not np.allclose(contour[0], contour[-1]):
        open_count += 1
    ax.plot(contour[:, 1], contour[:, 0], linewidth=2, color="red")
    # y and x seem flipped because coords based on typical 2D array with ij indexing
    y_avg = np.mean(contour[:, 0])
    x_avg = np.mean(contour[:, 1])
    centroids.append([x_avg, y_avg])
centroids = np.array(centroids)
print(len(contours), open_count, len(centroids))
plt.scatter(centroids[:, 0], centroids[:, 1])
plt.show()

# voronoi
# We must add a z=0 component to this array for freud
points = np.hstack((centroids, np.zeros((centroids.shape[0], 1))))
# box should be square otherwise input to Voronoi won't work correctly
# not sure if below will work with stereographic projection
box = freud.box.Box(nx, ny, is2D=True)
voro = freud.locality.Voronoi()
cells = voro.compute((box, points)).polytopes
ax = plt.gca()
voro.plot(ax=ax)
plt.show()

# calculate and plot vertex historgram
polygon_vertex_counts = [len(cell) for cell in cells]
bins = np.arange(1, max(polygon_vertex_counts) + 1, 1)
hist, edges = np.histogram(polygon_vertex_counts, bins=bins)
plt.bar(edges[:-1], hist, edgecolor="black", align="center")
plt.xlabel("Vertex Count", fontsize=16)
plt.ylabel("Count", fontsize=16)
plt.tick_params("both", labelsize=14)
plt.show()
