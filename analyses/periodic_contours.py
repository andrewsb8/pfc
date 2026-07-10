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
        centroids = []
        for group in self.contour_indices_grouped:
            if len(group) == 1:
                index = group[0]
                centroids.append(self.calc_centroid(self.contours[index]))
                print(group, self.contours[index][0], self.contours[index][1])
            else:
                aligned_contour = self.align_contours(group)
                cent = self.calc_centroid(aligned_contour)
                cent[0] = cent[0] % self.params["nx"]
                cent[1] = cent[1] % self.params["ny"]
                centroids.append(cent)
        return np.array(centroids)

    def calc_centroid(self, contour):
        # y and x seem flipped because coords based on typical 2D array with ij indexing
        y_avg = np.mean(contour[:, 0])
        x_avg = np.mean(contour[:, 1])
        return [x_avg, y_avg]

    def align_contours(self, group):
        # align arbitrarily on top right corner of grid to avoid negative numbers
        c = []
        for g in group:
            contour = deepcopy(self.contours[g])
            if np.max(contour[:, 0] < self.params["ny"] / 2):
                contour[:, 0] += self.params["ny"] - 1
            if np.max(contour[:, 1] < self.params["nx"] / 2):
                contour[:, 1] += self.params["nx"] - 1
            c.append(contour)
        return np.vstack(c)

    def is_closed_group(self, group):
        # determined if group of contours forms closed shape
        pass

    def is_in_group(self, index):
        # simple `index in object` does not work for nested lists...
        return index in [x for row in self.contour_indices_grouped for x in row]

    def is_closed_index(self, index):
        return np.allclose(
            self.contour_ends[index][0],
            self.contour_ends[index][1],
            rtol=1e-3,
            atol=1e-8,
        )


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
    j = 0
    while j < contour_groups.num_contours:
        if j not in group and not contour_groups.is_in_group(j) and not contour_groups.is_closed_index(j):
            # explicitly stop from identifying closed contours
            # from entering path
            if np.allclose(active, contour_ends[j, 0], rtol=5e-2, atol=1e-8):
                if j == i and len(group) > 1:
                    break
                else:
                    active = deepcopy(contour_ends[j, 1])
                    axis, shift = get_axis_shift(active, params)
                    active[axis] += shift
                    group.append(j)
                    j = 0
                    continue
            elif np.allclose(active, contour_ends[j, 1], rtol=5e-2, atol=1e-8):
                if j == i and len(group) > 1:
                    break
                else:
                    active = deepcopy(contour_ends[j, 0])
                    axis, shift = get_axis_shift(active, params)
                    active[axis] += shift
                    group.append(j)
                    j = 0
                    continue
        j += 1
    return group


def stitch_contours(contours, params):
    contour_groups = ContourGroups(contours, params)
    # identify closed groups first so the stitching is more efficient
    for i in range(contour_groups.num_contours):
        # add closed group individually
        if contour_groups.is_closed_index(i):
            contour_groups.contour_indices_grouped.append([i])

    for j in range(contour_groups.num_contours):
        # each contour can only be part of 1 group
        if contour_groups.is_in_group(j):
            continue
        else:
            contour_groups.contour_indices_grouped.append(
                stitch_contour(contour_groups, j, params)
            )
    return contour_groups
