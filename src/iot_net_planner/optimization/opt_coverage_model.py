"""An abstract class for an optimization model that solves for maximum coverage
"""
from abc import ABC, abstractmethod

class OPTCoverageModel(ABC):
    @staticmethod
    @abstractmethod
    def solve_coverage(budget, min_weight, dems, facs, prr, logging=True):
        """Solves a CIP for coverage

        :param budget: The maximum allowable amount to spend
        :type budget: float
        :param min_weight: The objective is min_weight * worst coverage + (1 - min_weight) * average coverage
        :type min_weight: float
        :param dems: a GeoDataFrame of the demand points
        :type dems: gpd.GeoDataFrame
        :param facs: a GeoDataFrame for the potential gateways. It should have a 'cost'
            field representing how much each gateway costs (pricing is relative)
        :type facs: gpd.GeoDataFrame
        :param prr: A CachedPRRModel initialized with dems and facs
        :type prr: `iot_net_planner.prediction.prr_cache.CachedPRRModel`
        :return: a set of indices of facs to build
        :rtype: set
        """
        pass
