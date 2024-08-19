"""A tool for sampling simulated random terrain
"""

from iot_net_planner.geo.sampler import LinkSampler
from opensimplex import seed, noise2
from numpy import array

class SimplexSampler(LinkSampler):
    """A sampler that samples from a random texture to simulate a random terrain

    :param random_seed: the seed for the random texture
    :type random_seed: int
    :param scale: a float greater than 0 controlling the size of the noise.
        A smaller number means the terrain will be generally more uniform, defaults to 1.0.
    :type scale: float, optional
    """
    def __init__(self, random_seed, scale=1.0):
        """Constructor method
        """
        self.scale = scale
        seed(random_seed)

    def sample(self, x, y):
        """Return the raster sample at x, y

        :param x: the x-coordinate in the provided crs
        :type x: float
        :param y: the y-coordinate in the provided crs
        :type y: float
        :returns: the sample at (x, y)
        :rtype: float
        """
        value = noise2(self.scale * x, self.scale * y)
        return value

    def batched_sample(self, xs, ys):
        """Return a numpy array of the samples at the points defined by xs and ys

        :param xs: the x-coordinates in the provided crs
        :type xs: np.ndarray
        :param ys: the y-coordinates in the provided crs with len(ys) == len(xs)
        :type ys: np.ndarray
        :returns: the samples at the provided points
        :rtype: np.ndarray
        """
        return array([self.sample(x, y) for x, y in zip(xs, ys)])
