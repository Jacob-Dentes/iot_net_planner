"""
A tool for sampling simulated random terrain
"""

from iot_net_planner.geo.sampler import LinkSampler
from opensimplex import seed, noise2
from numpy import array

class SimplexSampler(LinkSampler):
    """
    A sampler that samples from a random texture to simulate a random terrain
    """
    def __init__(self, random_seed, scale=1.0):
        """
        Creates a random sampler from a random seed

        :param random_seed: the seed for the random texture

        :param scale: a float greater than 0 controlling the size of the noise.
        A smaller number means the terrain will be generally more uniform
        """
        self.scale = scale
        seed(random_seed)

    def sample(self, x, y):
        """
        Return the raster sample at x, y

        :param x: a float representing the x-coordinate

        :param y: a float representing the y-coordinate

        :returns: a float representing the sample
        """
        value = noise2(self.scale * x, self.scale * y)
        return value

    def batched_sample(self, xs, ys):
        """
        Return a numpy array of the samples at the points defined by xs and ys

        :param xs: a numpy array of the x-coordinates

        :param ys: a numpy array of the y-coordinates with len(ys) == len(xs)

        :returns: a numpy array of the samples at the provided points
        """
        return array([self.sample(x, y) for x, y in zip(xs, ys)])
