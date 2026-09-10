import numpy as np
from skimage import measure

class ContourStitcher(object):
    def __init__(self, field, level, params):
        self.contours = measure.find_contours(field, level=level)
        self.num_contours = len(self.contours)
        self.params = params
        self.stitched_contours = self.find_periodic_contours(field, level, params)

    def calc_centroids(self, threshold=-1):
        return np.array([[np.mean(sc[:, 1]) % self.params['nx'], np.mean(sc[:, 0]) % self.params['ny']] for sc in self.stitched_contours if len(sc) > threshold])

    def is_closed(self, contour):
        return np.allclose(
            contour[0],
            contour[-1],
            rtol=1e-3,
            atol=1e-8,
        )

    def find_periodic_contours(self, field, level, params):
        tiled_field = np.tile(field, (2,2))
        reduced_contours = measure.find_contours(tiled_field, level=level)
        kept = []
        for c in reduced_contours:
            x_max = np.max(c[:,1])
            x_min = np.min(c[:,1])
            y_max = np.max(c[:,0])
            y_min = np.min(c[:,0])
            # if inside original field and closed, keep it
            if x_min >= 0 and x_max <= params['nx'] and y_min >= 0 and y_max <= params['ny'] and self.is_closed(c):
                kept.append(c)
            # gets the corner
            elif ((x_min < params['nx'] and x_max > params['nx']) and (y_min < params['ny'] and y_max > params['ny'])) and self.is_closed(c):
                kept.append(c)
            # only crosses horizontal
            elif ((x_min < params['nx'] and x_max > params['nx']) and (y_min >= 0 and y_max < params['ny'])) and self.is_closed(c):
                kept.append(c)
            # only crosses vertical
            elif ((x_min > 0 and x_max < params['nx']) and (y_min < params['ny'] and y_max > params['ny'])) and self.is_closed(c):
                kept.append(c)
        return kept
