from iot_net_planner.geo.sampler import LinkSampler
from opensimplex import seed, noise2
from numpy import array

class SimplexSampler(LinkSampler):
    def __init__(self, random_seed, scale=1.0):
        self.scale = scale
        seed(random_seed)

    def sample(self, x, y):
        value = noise2(self.scale * x, self.scale * y)
        return value

    def batched_sample(self, xs, ys):
        return array([self.sample(x, y) for x, y in zip(xs, ys)])
