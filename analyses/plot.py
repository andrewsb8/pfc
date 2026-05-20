import matplotlib.pyplot as plt
import numpy as np

# NEED TO LOAD THE MESH AND FIELD VALUES TO USE THIS

x3d, y3d, z3d = mesh.faceCenters
valc = np.array(phi.arithmeticFaceValue)

rr = -1.0
r3d = (x3d**2 + y3d**2) ** 0.5
theta3d = np.zeros(len(z3d))
pp3d = np.zeros(len(z3d))
x3dn = np.zeros(len(z3d))
y3dn = np.zeros(len(z3d))
z3dn = np.zeros(len(z3d))


for i in range(0, len(z3d)):
    pp3d[i] = np.arctan2(y3d[i], x3d[i])
    rad = (x3d[i] ** 2 + y3d[i] ** 2 + z3d[i] ** 2) ** 0.5
    theta3d[i] = np.arccos(z3d[i] / rad)
    x3dn[i] = (rad + rr * valc[i]) * np.cos(pp3d[i]) * np.sin(theta3d[i])
    y3dn[i] = (rad + rr * valc[i]) * np.sin(pp3d[i]) * np.sin(theta3d[i])
    z3dn[i] = (rad + rr * valc[i]) * np.cos(theta3d[i])

valc = (valc - valc.min()) / (valc.max() - valc.min())

fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection="3d")

# equivalent to mlab.points3d with colormap "YlOrBr"
sc = ax.scatter3D(
    x3dn,
    y3dn,
    z3dn,
    c=valc,
    s=20,  # roughly matches scale_factor=0.5 spheres; tune s as needed
    cmap="YlOrBr",
    alpha=0.8,
)

ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")

# add a colorbar for the scalar values
plt.colorbar(sc, ax=ax, label="valc")

# set black background and axes color
fig.patch.set_facecolor("black")
ax.set_facecolor("black")
ax.xaxis.label.set_color("white")
ax.yaxis.label.set_color("white")
ax.zaxis.label.set_color("white")
ax.tick_params(colors="white")

plt.show()
