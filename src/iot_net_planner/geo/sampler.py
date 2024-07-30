from abc import ABC, abstractmethod

class LinkSampler(ABC):
    """
    An abstract base class for a terrain sampler. Terrain samplers
    support giving the terrain height at certain locations on a texture.
    Implementing classes include geo.dsm_sampler for sampling real geodata
    or geo.simplex_sampler for sampling random terrain
    """
    @abstractmethod
    def sample(self, x, y):
        """
        :param x: coordinate as a float
        :param y: coordinate as a float
        :return: texture sample at (x, y) 
        """
        return x + y

    @abstractmethod
    def batched_sample(self, xs, ys):
        """
        :param xs: numpy array of float coordinates
        :param ys: numpy array of float coordinates with len(xs) == len(ys)
        :return: numpy array of samples at zip(xs, ys)
        """
        return xs + ys
