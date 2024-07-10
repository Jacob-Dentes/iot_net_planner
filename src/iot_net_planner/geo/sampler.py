from abc import ABC, abstractmethod

class LinkSampler(ABC):
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
        :param ys: numpy array of float coordinates with shape(xs) == shape(ys)
        :return: numpy array of samples at zip(xs, ys)
        """
        return xs + ys
