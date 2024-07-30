"""
Adds a caching layer to a prr model  

Also provides an improve ub method
"""

from iot_net_planner.prediction.prr_model import PRRModel
import numpy as np

class CachedPRRModel(PRRModel):
    def __init__(self, model):
        """
        Wraps a PRRModel. Adds a caching layer to avoid regenerating prrs.
        Also provides an improve_ub method for incrementally improving upper bounds.
        See PRRModel for other method documentation.

        :param model: the PRRModel instance to wrap a cache around
        """
        self._model = model
        self._prrs = np.zeros((len(self.dems), len(self.facs)))
        self._incache = np.full(self._prrs.shape, False)
        self._all_dems = np.full(len(self.dems), True)

    def get_prr(self, fac, dems=None):
        """
        See the corresponding method from PRRModel
        """
        if dems is None:
            dems = self._all_dems
        in_cache = self._incache[:, fac]
        if np.all(in_cache | (~dems)):
            return self._prrs[dems, fac]
        res = self._model.get_prr(fac, dems & (~in_cache))

        prr = np.empty(dems.sum())
        prr[in_cache] = self._prrs[dems & in_cache, fac]
        prr[~in_cache] = res

        self._prrs[dems, fac] = prr
        self._incache[dems, fac] = True

        return prr

    def get_prr_ub(self, fac, dems=None):       
        """
        See the corresponding method from PRRModel
        """
        if dems is None:
            dems = self._all_dems
        in_cache = self._incache[:, fac]
        if np.all(in_cache | (~dems)):
            return self._prrs[dems, fac]

        res = self._model.get_prr_ub(fac, dems & (~in_cache))
       
        ub = np.empty(dems.sum())
        ub[in_cache] = self._prrs[dems & in_cache, fac]
        ub[~in_cache] = res
        
        return ub

    def get_prr_lb(self, fac, dems=None):
        """
        See the corresponding method from PRRModel
        """
        if dems is None:
            dems = self._all_dems
        in_cache = self._incache[:, fac]
        if np.all(in_cache | (~dems)):
            return self._prrs[dems, fac]

        res = self._model.get_prr_lb(fac, dems & (~in_cache))
       
        lb = np.empty(dems.sum())
        lb[in_cache] = self._prrs[dems & in_cache, fac]
        lb[~in_cache] = res
        
        return lb

    @property
    def dems(self):
        """
        See the corresponding method from PRRModel
        """
        return self._model.dems

    @property
    def facs(self):
        """
        See the corresponding method from PRRModel
        """
        return self._model.facs

    def improve_ub(self, fac, quantile):
        """
        Improve the cached upper bound for fac by computing exact prrs
        to the closest quantile of demand points

        :param fac: The facility index to improve ub on
        :param quantile: A float in [0.0, 1.0] representing the proportion
        of demand points to use  

        :returns: None
        """
        in_cache = self._incache[:, fac]
        if np.all(in_cache):
            return

        distances = np.log(self.dems.distance(self.facs.geometry[fac]).to_numpy())

        quant_dist = np.quantile(distances, quantile)
        to_improve = (distances <= quant_dist) & (~in_cache)
        if to_improve.sum() < 1:
            return

        prrs = self._model.get_prr(fac, to_improve)
        self._prrs[to_improve, fac] = prrs
        self._incache[to_improve, fac] = True

        return
