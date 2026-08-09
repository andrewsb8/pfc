import json
import sys

import freud
import h5py
import matplotlib.pyplot as plt
import numpy as np
from periodic_contours import ContourStitcher

infile = sys.argv[1]
starting_frame = int(sys.argv[2])
threshold = 50
plot = True
data = h5py.File(infile, "r")

params = json.loads(data["trajectory"].attrs["parameters"])
nx = params["nx"]
ny = params["ny"]
dx = params["dx"]
dy = params["dy"]
total_area = nx * dx * ny * dy

times = []
polygon_dist_values = [] # need to deal with the fact that each time step will produce different ranges
distribution = [] # 2D list with counts of polygon vertices
hex_fracs = []

trajlen = len(data["trajectory"])
for i in range(starting_frame, trajlen):
    print(f"Step {i} of {trajlen}")
    times.append(i * params["dt"] * params["trajectory_write_interval"])
    phi_arr = np.array(data["trajectory"][i]).reshape((ny, nx))
    level = np.mean(phi_arr)
    c_obj = ContourStitcher(phi_arr, level, params)
    bubble_count = len(c_obj.stitched_contours)
    centroids = c_obj.calc_centroids(threshold=threshold)

    # voronoi
    # We must add a z=0 component to this array for freud
    points = np.hstack((centroids, np.zeros((centroids.shape[0], 1))))
    # box should be square otherwise input to Voronoi won't work correctly
    # not sure if below will work with stereographic projection
    box = freud.box.Box(nx, ny, is2D=True)
    voro = freud.locality.Voronoi()
    cells = voro.compute((box, points)).polytopes

    # calculate vertex historgram
    polygon_vertex_counts = [len(cell) for cell in cells]
    bins = np.arange(min(polygon_vertex_counts)-1, max(polygon_vertex_counts) + 2, 1)
    hist, edges = np.histogram(polygon_vertex_counts, bins=bins, density=True)
    num_hex = hist[np.where(edges == 6)][0]
    num_poly = np.sum(hist)
    hex_fracs.append(num_hex/num_poly)
    polygon_dist_values.append(edges[:-1])
    distribution.append(hist)


# need to deal with the fact that the len of arrays at each time step is not the same
def pad_to_reference(all_var_lists, all_density_lists):
    """
    all_var_lists: list of 1D arrays/lists (independent variable values), possibly ragged
    all_density_lists: list of 1D arrays/lists (probability densities), same ragged shape as all_var_lists

    Returns:
        ref_vars: the longest independent-variable array (used as common y-axis)
        padded_densities: list of arrays, each same length as ref_vars, zero-padded
    """
    # Find the longest independent variable array
    lengths = [len(v) for v in all_var_lists]
    ref_idx = np.argmax(lengths)
    ref_vars = np.asarray(all_var_lists[ref_idx])

    padded_densities = []
    for var_arr, dens_arr in zip(all_var_lists, all_density_lists):
        var_arr = np.asarray(var_arr)
        dens_arr = np.asarray(dens_arr)

        if len(var_arr) == len(ref_vars) and np.array_equal(var_arr, ref_vars):
            # already matches reference, no padding needed
            padded_densities.append(dens_arr)
            continue

        # Build a zero array the size of the reference grid
        padded = np.zeros_like(ref_vars, dtype=float)

        # Find where each value in var_arr lands in ref_vars, place density there
        # (assumes var_arr values are a subset of ref_vars; use np.isin + searchsorted)
        idx_in_ref = np.searchsorted(ref_vars, var_arr)

        # Safety check: make sure the matched positions actually correspond to equal values
        valid = (idx_in_ref < len(ref_vars)) & (ref_vars[np.clip(idx_in_ref, 0, len(ref_vars)-1)] == var_arr)
        if not np.all(valid):
            raise ValueError("Some values in this var_arr do not exist in the reference grid — "
                              "check that all independent variable arrays share a common value spacing.")

        padded[idx_in_ref[valid]] = dens_arr[valid]
        padded_densities.append(padded)

    return ref_vars, padded_densities

polygon_dist_axis, distribution = pad_to_reference(polygon_dist_values, distribution)

# plot heat map showing time evolution of polygon distribution
times = np.asarray(times)
polygon_dist_axis = np.asarray(polygon_dist_axis)
distribution = np.asarray(distribution)  # shape (T, N)
# pcolormesh expects distribution with shape (len(y), len(x)), so transpose
distribution = distribution.T

fig, ax = plt.subplots(figsize=(10, 6))
mesh = ax.pcolormesh(
    times, polygon_dist_axis, distribution,
    cmap='bone_r'
)

cbar = fig.colorbar(mesh, ax=ax)
cbar.set_label('Probability Density', fontsize=16)
cbar.ax.tick_params(labelsize=14)

ax.set_xlabel('Time', fontsize=16)
ax.set_ylabel('# Polygon Edges', fontsize=16)
ax.tick_params("both", labelsize=14)

plt.tight_layout()
#plt.savefig('prob_dist_heatmap.png', dpi=150)
plt.show()

# hexagon fraction vs time
fig, ax = plt.subplots(1, 1, figsize=(8, 8))
ax.plot(times, hex_fracs, label="<r>")
ax.set_xlabel('Time', fontsize=16)
ax.set_ylabel('% Hexagons', fontsize=16)
ax.tick_params("both", labelsize=14)
plt.show()
