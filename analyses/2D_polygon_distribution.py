import json
import sys

import freud
import h5py
import matplotlib.pyplot as plt
import numpy as np
from periodic_contours import ContourStitcher

infile = sys.argv[1]
frame = int(sys.argv[2])
# number of points in contour used as threshold for inclusion in voronoi.
# Typical value of 75 works but recommend sensitivity analysis.
# -1 includes all bubbles in analysis
threshold = 50
plot = True
data = h5py.File(infile, "r")
center_values = data["trajectory"][frame]

params = json.loads(data["trajectory"].attrs["parameters"])
nx = params["nx"]
ny = params["ny"]
dx = params["dx"]
dy = params["dy"]
total_area = nx * dx * ny * dy

phi_arr = np.array(center_values).reshape((ny, nx))
level = np.mean(phi_arr)
c_obj = ContourStitcher(phi_arr, level, params)
fig, ax = plt.subplots(1, 1, figsize=(8, 8))
# Plot the original field
# ax.imshow(phi_arr, cmap="binary_r", origin="lower")
for contour in c_obj.stitched_contours:
    ax.plot(contour[:, 1], contour[:, 0], linewidth=1, color="red")

bubble_count = len(c_obj.stitched_contours)
centroids = c_obj.calc_centroids(threshold=threshold)
#plt.scatter(centroids[:, 0], centroids[:, 1])
#plt.show()

# voronoi
# We must add a z=0 component to this array for freud
points = np.hstack((centroids, np.zeros((centroids.shape[0], 1))))
# box should be square otherwise input to Voronoi won't work correctly
# not sure if below will work with stereographic projection
box = freud.box.Box(nx, ny, is2D=True)
voro = freud.locality.Voronoi()
cells = voro.compute((box, points)).polytopes
polys = [cell[:, :2] for cell in cells if len(cell) > 0]
from matplotlib.collections import PolyCollection
pc = PolyCollection(
    polys,
    facecolors="none",      # empty fill
    edgecolors="blue",     # outline only
    linewidths=1,
)
ax.add_collection(pc)
ax.set_aspect("equal")
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
