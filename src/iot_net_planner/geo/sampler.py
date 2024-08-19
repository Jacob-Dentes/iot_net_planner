"""Defines an abstract class for a terrain sampler.
"""
from abc import ABC, abstractmethod

class LinkSampler(ABC):
    """An abstract base class for a terrain sampler. Terrain samplers
    support giving the terrain height at certain locations on a texture.
    Implementing classes include geo.dsm_sampler for sampling real geodata
    or geo.simplex_sampler for sampling random terrain
    """
    @abstractmethod
    def sample(self, x, y):
        """Return the raster sample at x, y

        :param x: the x-coordinate in the provided crs
        :type x: float
        :param y: the y-coordinate in the provided crs
        :type y: float
        :returns: the sample at (x, y)
        :rtype: float
        """
        return x + y

    @abstractmethod
    def batched_sample(self, xs, ys):
        """Return a numpy array of the samples at the points defined by xs and ys

        :param xs: the x-coordinates in the provided crs
        :type xs: np.ndarray
        :param ys: the y-coordinates in the provided crs with len(ys) == len(xs)
        :type ys: np.ndarray
        :returns: the samples at the provided points
        :rtype: np.ndarray
        """
        return xs + ys
