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
threshold = -1
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
bubble_count = len(c_obj.stitched_contours)
centroids = c_obj.calc_centroids(threshold=threshold)

fig, ax = plt.subplots(1, 1, figsize=(8, 8))

# Plot the original field and contours
# ax.imshow(phi_arr, cmap="binary_r", origin="lower")
#for contour in c_obj.stitched_contours:
#    ax.plot(contour[:, 1], contour[:, 0], linewidth=1, color="red")

# voronoi
if centroids.shape[0] > 0:
    # We must add a z=0 component to this array for freud
    points = np.hstack((centroids, np.zeros((centroids.shape[0], 1))))
else:
    # no contours so no centroids, report and exit
    print(f"{infile},{params['trajectory_write_interval']},{frame},0,0,0")
    exit()
# box should be square otherwise input to Voronoi won't work correctly
# not sure if below will work with stereographic projection
box = freud.box.Box(nx, ny, is2D=True)
voro = freud.locality.Voronoi()
cells = voro.compute((box, points)).polytopes
polys = [cell[:, :2] for cell in cells if len(cell) > 0]
all_polys = np.concatenate(polys)
xmin, ymin = all_polys.min(axis=0)
xmax, ymax = all_polys.max(axis=0)
from matplotlib.collections import PolyCollection
pc = PolyCollection(
    polys,
    facecolors="none",      # empty fill
    edgecolors="blue",     # outline only
    linewidths=1,
)
ax.add_collection(pc)
ax.set_aspect("equal")
from matplotlib.patches import Rectangle
rect = Rectangle(
    (0, 0),          # lower-left corner
    width=nx,             # horizontal side length
    height=ny,            # vertical side length
    fill=False,        # no interior fill
    edgecolor="crimson",
    linewidth=1.0,
    linestyle="dashed",
    zorder=10,
    alpha=0.5,
)
ax.add_patch(rect)
# determine if x/y limits need to be set by box or
# by voronoi polyhedra extending through the box
xmin, ymin = all_polys.min(axis=0)
if xmin > 0:
    xmin = 0
if ymin > 0:
    ymin = 0
xmax, ymax = all_polys.max(axis=0)
if xmax < nx:
    xmax = nx
if ymax < ny:
    ymax = ny
ax.set_xlim(xmin, xmax)
ax.set_ylim(ymin, ymax)
ax.set_axis_off()
#plt.savefig(f"{infile}_{frame}_voro.png")

# calculate and plot vertex historgram
fig, ax = plt.subplots(1, 1, figsize=(8, 8))
polygon_vertex_counts = [len(cell) for cell in cells]
bins = np.arange(min(polygon_vertex_counts) - 1, max(polygon_vertex_counts) + 3, 1) # + 3 to avoid truncation and extend data to plot 1 bin past max
hist, edges = np.histogram(polygon_vertex_counts, bins=bins)
if np.max(edges) <= 6 or np.min(edges) > 6:
    num_hex = 0
else:
    num_hex = hist[np.where(edges == 6)][0]
num_poly = np.sum(hist)
frac_hex = num_hex/num_poly
print(f"{infile},{params['trajectory_write_interval']},{frame},{num_hex},{num_poly},{frac_hex}")
plt.bar(edges[:-1], hist, edgecolor="black", align="center")
plt.xlabel("Vertex Count", fontsize=16)
plt.ylabel("Count", fontsize=16)
plt.tick_params("both", labelsize=14)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.set_xlim()
#plt.savefig(f"{infile}_{frame}_hist.png")

# delauney triangulation
fig, ax = plt.subplots(1, 1, figsize=(8, 8))
nlist = voro.nlist
line_data = np.asarray(
    [[points[i], points[i] + box.wrap(points[j] - points[i])] for i, j in nlist]
)[:, :, :2]
from matplotlib.collections import LineCollection
line_collection = LineCollection(line_data, alpha=0.75)
ax = plt.gca()
ax.add_collection(line_collection)
ax.set_xlim(0, nx)
ax.set_ylim(0, ny)
#plt.savefig(f"{infile}_{frame}_delauney.png")
plt.show()
