"""An abstract class for an optimization model that solves for minimum cost
"""
from abc import ABC, abstractmethod

from sklearn.neighbors import NearestNeighbors
import numpy as np

class OPTBudgetModel(ABC):
    @staticmethod
    @abstractmethod
    def solve_budget(coverage, dems, facs, prr, blob_size=10, logging=True):
        """Solves a CIP for budget. Note that this may be infeasible, 
        in which case all facs will be returned

        :param coverage: a numpy array with the same length as dems
            denoting the required prr at each demand point
        :type coverage: np.ndarray
        :param dems: a GeoDataFrame of the demand points
        :type dems: gpd.GeoDataFrame
        :param facs: a GeoDataFrame of the potential gateways
        :type facs: gpd.GeoDataFrame
        :param prr: a CachedPRRModel initialized with dems and facs
        :type prr: class: `iot_net_planner.prediction.prr_cache.CachedPRRModel`
        :return: a set of indices of facs to build
        :rtype: set
        """ 
        pass
        
