# ref: https://github.com/asjaradja/PollenPhaseTransitionPaper/blob/master/PhaseDiagramCalculations/ConservedDynamics/FiPyConservedDynamics.ipynb

import math

import matplotlib.pyplot as plt
import numpy as np
from fipy import *
from fipy.tools import dump

mesh = Gmsh2DIn3DSpace(
    """
     radius = 15.0;
     cellSize = 0.4;

     // create inner 1/8 shell
     Point(1) = {0, 0, 0, cellSize};
     Point(2) = {-radius, 0, 0, cellSize};
     Point(3) = {0, radius, 0, cellSize};
     Point(4) = {0, 0, radius, cellSize};
     Circle(1) = {2, 1, 3};
     Circle(2) = {4, 1, 2};
     Circle(3) = {4, 1, 3};
     Line Loop(1) = {1, -3, 2} ;
     Ruled Surface(1) = {1};

     // create remaining 7/8 inner shells
     t1[] = Rotate {{0,0,1},{0,0,0},Pi/2} {Duplicata{Surface{1};}};
     t2[] = Rotate {{0,0,1},{0,0,0},Pi} {Duplicata{Surface{1};}};
     t3[] = Rotate {{0,0,1},{0,0,0},Pi*3/2} {Duplicata{Surface{1};}};
     t4[] = Rotate {{0,1,0},{0,0,0},-Pi/2} {Duplicata{Surface{1};}};
     t5[] = Rotate {{0,0,1},{0,0,0},Pi/2} {Duplicata{Surface{t4[0]};}};
     t6[] = Rotate {{0,0,1},{0,0,0},Pi} {Duplicata{Surface{t4[0]};}};
     t7[] = Rotate {{0,0,1},{0,0,0},Pi*3/2} {Duplicata{Surface{t4[0]};}};

     // create entire inner and outer shell
     Surface Loop(100)={1,t1[0],t2[0],t3[0],t7[0],t4[0],t5[0],t6[0]};
"""
).extrude(extrudeFunc=lambda r: 1.1 * r)

# gmsh code for creating meshed sphere is given above
# set up variables, parameters, and initial condition
phi = CellVariable(name=r"$\phi$", mesh=mesh)
phi.setValue(GaussianNoiseVariable(mesh=mesh, mean=0, variance=0.04))
PHI = phi.arithmeticFaceValue
a = epsilon = 1.0
qn = 1.5
D = 1.0
K = 1.0
u4 = 120.0
u3 = -40.0
tau = 20.0
dexp = -7
elapsed = 0

# define the conserved dynamics equation
sourcey = (u4 * 0.5 * PHI * PHI + u3 * PHI + tau) + D * K * qn**4
eq = TransientTerm() == DiffusionTerm(coeff=sourcey) + DiffusionTerm(
    coeff=(2 * qn**2, D * K)
) + DiffusionTerm(coeff=(1.0, 1.0, D * K))
# set the total integration time "duration" and evolve the dynamics
duration = 0.002
while elapsed < duration:
    print(elapsed)
    print(phi)
    print(len(phi))
    dt = min(0.005, math.exp(dexp))
    elapsed += dt
    dexp += 0.005
    eq.solve(phi, dt=dt)
# view the result
# view = Viewer(vars=phi)
# extrapolate the solution onto points on sphere
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
