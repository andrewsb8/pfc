This directory contains scripts to read or perform analyses on PFC simulations stored in the HDF5 format. Here is a list of what they all do:

- `read_hdf5.py`: Reads metadata from trajectory file
- `print_frame.py`: Prints the field grid for a user-defined frame from a trajectory
- `plot_xD.py`: Plot the field for a user-defined time step
- `compare_frames.py`: Check if two user-defined frames from a single trajectory are equivalent.
- `2D_scaling.py`: Estimation of bubble radius as a function of time. 2D wet and dry foams scale as $t^{1/3}$ and $t^{1/2}$, respectively. Produces a log-log plot and reference curve.
- `2D_polygon_distribution.py`: Identify bubble contours, perform voronoi tesselation based on bubble geometric centroids, and create a histogram of the polygon edge #s
- `2D_polygon_distribution_time.py`: Do the above as a function of time
- `periodic_contours.py`: The scaling and polygon analyses require bubble identification in a periodic 2D space but image analysis tools are rarely periodic. This file includes a class which matches bubble contours which cross the periodic boundary.
