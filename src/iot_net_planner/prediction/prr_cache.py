"""Adds a caching layer to a prr model. Also provides an improve ub method
"""

from iot_net_planner.prediction.prr_model import PRRModel
import numpy as np

class CachedPRRModel(PRRModel):
    def __init__(self, model):
        """Wraps a PRRModel. Adds a caching layer to avoid regenerating prrs.
        Also provides an improve_ub method for incrementally improving upper bounds.

        :param model: the PRRModel instance to wrap a cache around
        :type model: class: `iot_net_planner.prediction.prr_model.PRRModel`
        """
        self._model = model
        self._prrs = np.zeros((len(self.dems), len(self.facs)))
        self._incache = np.full(self._prrs.shape, False)
        self._all_dems = np.full(len(self.dems), True)

    def get_prr(self, fac, dems=None):
        """Get the exact prrs between fac and the self.dems[dems]  

        :param fac: the facility to generate prrs from
        :type fac: int
        :param dems: a boolean numpy array with length equal to the
            number of demand points, dems[i] == True means to generate 
            the prrs to demand point i. If None, will generate to all
            demand points, defaults to None
        :type dems: np.ndarray, optional
        :return: a numpy array with length dems.sum() of the prrs to
            each of the demand points where dems[i]
        :rtype: np.ndarray
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
        """Get an upper bound on prrs between fac and the self.dems[dems]  

        :param fac: the facility to generate prrs from
        :type fac: int
        :param dems: a boolean numpy array with length equal to the
            number of demand points, dems[i] == True means to generate 
            an upper bound on the prrs to demand point i. If None,
            will generate to all demand points, defaults to None
        :type dems: np.ndarray, optional
        :return: a numpy array with length dems.sum() of the prr upper
            bounds to each of the demand points where dems[i]. This means
            that self.get_prr_ub(fac) >= self.get_prr(fac)
        :rtype: np.ndarray
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
        """Get a lower bound on prrs between fac and the self.dems[dems]  

        :param fac: the facility to generate prrs from
        :type fac: int
        :param dems: a boolean numpy array with length equal to the
            number of demand points, dems[i] == True means to generate 
            a lower bound on the prrs to demand point i. If None,
            will generate to all demand points, defaults to None
        :type dems: np.ndarray, optional
        :return: a numpy array with length dems.sum() of the prr upper
            bounds to each of the demand points where dems[i]. This means
            that self.get_prr_ub(fac) <= self.get_prr(fac)
        :rtype: np.ndarray
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
        """The demand points
        
        :return: the demand points associated with this model
        :rtype: gpd.GeoDataFrame
        """
        return self._model.dems

    @property
    def facs(self):
        """The gateway points
        
        :return: the gateway points associated with this model
        :rtype: gpd.GeoDataFrame
        """
        return self._model.facs

    def improve_ub(self, fac, quantile):
        """Improve the cached upper bound for fac by computing exact prrs
        to the closest quantile of demand points

        :param fac: The facility index to improve ub on
        :type fac: int
        :param quantile: A float in [0.0, 1.0] representing the proportion
            of demand points to use  
        :type quantile: float
        :return: None
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
