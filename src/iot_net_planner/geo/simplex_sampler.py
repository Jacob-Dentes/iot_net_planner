from iot_net_planner.geo.sampler import LinkSampler
from opensimplex import seed, noise2
from numpy import array

class SimplexSampler(LinkSampler):
    def __init__(self, random_seed):
        seed(random_seed)

    def sample(self, x, y):
        value = noise2(x, y)
        return value

    def batched_sample(self, xs, ys):
        return array([self.sample(x, y) for x, y in zip(xs, ys)])
