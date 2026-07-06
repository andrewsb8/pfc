from copy import deepcopy

import numpy as np


class ContourGroups(object):
    def __init__(self, contours, params):
        self.contours = contours
        self.num_contours = len(contours)
        self.contour_ends = np.array(
            [
                [self.contours[i][0], self.contours[i][-1]]
                for i in range(self.num_contours)
            ]
        )
        self.params = params
        self.contour_indices_grouped = []

    def calc_centroids(self):
        # shift contours to make smooth curve (can shift to max dims like voronoi calc does)
        # calc centroid
        # return centroid coords modulo dimensions
        pass

    def calc_centroid(self, group):
        pass

    def is_closed(self, group):
        # determined if group of contours forms closed shape
        pass

    def is_in_group(self, index):
        return index in [x for row in self.contour_indices_grouped for x in row]


def get_axis_shift(point, params):
    if point[0] == 0:
        return 0, params["ny"] - 1
    elif point[0] == params["ny"] - 1:
        return 0, -(params["ny"] - 1)
    elif point[1] == 0:
        return 1, params["nx"] - 1
    elif point[1] == params["nx"] - 1:
        return 1, -(params["nx"] - 1)
    else:
        raise ValueError("Point without a zero")


def stitch_contour(contour_groups, i, params):
    contour_ends = contour_groups.contour_ends
    active = deepcopy(contour_ends[i][0])
    axis, shift = get_axis_shift(active, params)
    active[axis] += shift
    group = [i]
    for j in range(contour_groups.num_contours):
        if not contour_groups.is_in_group(j):
            if np.allclose(active, contour_ends[j, 0], rtol=1e-1, atol=1e-1):
                if j == i and len(group) > 1:
                    break
                else:
                    active = deepcopy(contour_ends[j, 1])
                    axis, shift = get_axis_shift(active, params)
                    active[axis] += shift
                    group.append(j)
                    j = 0
            elif np.allclose(active, contour_ends[j, 1], rtol=1e-1, atol=1e-1):
                if j == i and len(group) > 1:
                    break
                else:
                    active = deepcopy(contour_ends[j, 0])
                    axis, shift = get_axis_shift(active, params)
                    active[axis] += shift
                    group.append(j)
                    j = 0
    return group


def stitch_contours(contours, params):
    contour_groups = ContourGroups(contours, params)
    for i in range(contour_groups.num_contours):
        # each contour can only be part of 1 group
        if contour_groups.is_in_group(i):
            continue
        # add closed group individually
        if np.allclose(
            contour_groups.contour_ends[i][0], contour_groups.contour_ends[i][1]
        ):
            contour_groups.contour_indices_grouped.append([i])
        else:
            contour_groups.contour_indices_grouped.append(
                stitch_contour(contour_groups, i, params)
            )
    print(len(contour_groups.contour_indices_grouped))
    print(contour_groups.contour_indices_grouped)
    return contour_groups
