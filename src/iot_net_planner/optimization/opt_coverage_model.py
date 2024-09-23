"""An abstract class for an optimization model that solves for maximum coverage
"""
from abc import ABC, abstractmethod

from sklearn.neighbors import NearestNeighbors
import numpy as np

class OPTCoverageModel(ABC):
    @staticmethod
    # Modify prrs for blobs of size k
    def _blobify(facs, prrs, k):
        if "exact" not in facs:
            return prrs
        
        k = min(k, (~facs['exact']).sum())
        
        prrs = prrs.copy()
        false_mask = facs['exact'] == False
        false_indices = facs.index[false_mask].tolist()
        false_coords = np.array(list(zip(facs.geometry.x[false_mask], facs.geometry.y[false_mask])))

        nbrs = NearestNeighbors(n_neighbors=k)
        nbrs.fit(false_coords)

        index_map = {i: original_idx for i, original_idx in enumerate(false_indices)}

        for i in false_indices:
            distances, indices = nbrs.kneighbors([false_coords[i]], n_neighbors=k)

            nearest_false_indices = [index_map[idx] for idx in indices[0]]
            min_value = np.min(prrs[nearest_false_indices, :], axis=0)

            prrs[i, :] = min_value

        return prrs           
                
    @staticmethod
    @abstractmethod
    def solve_coverage(budget, min_weight, dems, facs, prr, blob_size=10, logging=True):
        """Solves a CIP for coverage

        :param budget: the maximum allowable amount to spend
        :type budget: float
        :param min_weight: The objective is min_weight * worst coverage + (1 - min_weight) * average coverage
        :type min_weight: float
        :param dems: a GeoDataFrame of the demand points
        :type dems: gpd.GeoDataFrame
        :param facs: a GeoDataFrame for the potential gateways. It should have a 'cost'
            field representing how much each gateway costs (pricing is relative)
        :type facs: gpd.GeoDataFrame
        :param prr: A CachedPRRModel initialized with dems and facs
        :type prr: class: `iot_net_planner.prediction.prr_cache.CachedPRRModel`
        :return: a set of indices of facs to build
        :rtype: set
        """
        pass
