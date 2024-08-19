"""A tool to load a prr model from a file
"""

from iot_net_planner.prediction.prr_model import PRRModel
import numpy as np

class FileModel(PRRModel):
    """Loads a PRRModel from a file

    :param dems: a GeoDataFrame containing the demand points
    :type dems: gpd.GeoDataFrame
    :param facs: a GeoDataFrame containing the facility points
    :type facs: gpd.GeoDataFrame
    :param file_path: a path to a saved PRRModel
    :type file_path: str
    """
    def __init__(self, dems, facs, file_path):
        """Constructor method
        """
        self._prrs = np.load(file_path)
        err_msg = f"File shape does not match demands and facilities. File has {self._prrs.shape}, but there were {len(dems)} demand points and {len(facs)} facilities."
        assert self._prrs.shape[0] == len(dems) and self._prrs.shape[1] == len(facs), err_msg
        self._dems = dems
        self._facs = facs
        self._all_dems = np.full(len(dems), True)

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
        return self._prrs[dems, fac]

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
        return self.get_prr(fac, dems)
    
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
        return self.get_prr(fac, dems)

    @property
    def dems(self):
        """The demand points
        
        :return: the demand points associated with this model
        :rtype: gpd.GeoDataFrame
        """
        return self._dems

    @property
    def facs(self):
        """The gateway points
        
        :return: the gateway points associated with this model
        :rtype: gpd.GeoDataFrame
        """
        return self._facs
