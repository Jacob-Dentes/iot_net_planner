"""
A tool to load a prr model from a file
"""

from iot_net_planner.prediction.prr_model import PRRModel
import numpy as np

class FileModel(PRRModel):
    def __init__(self, dems, facs, file_path):
        """
        Loads a PRRModel from a file. See the PRRModel documentation for information

        :param dems: a GeoDataFrame containing the demand points

        :param facs: a GeoDataFrame containing the facility points

        :param file_path: a path to a saved PRRModel
        """
        self._prrs = np.load(file_path)
        err_msg = f"File shape does not match demands and facilities. File has {self._prrs.shape}, but there were {len(dems)} demand points and {len(facs)} facilities."
        assert self._prrs.shape[0] == len(dems) and self._prrs.shape[1] == len(facs), err_msg
        self._dems = dems
        self._facs = facs
        self._all_dems = np.full(len(dems), True)

    def get_prr(self, fac, dems=None):
        """
        See the corresponding PRRModel documentation
        """
        if dems is None:
            dems = self._all_dems
        return self._prrs[dems, fac]

    def get_prr_ub(self, fac, dems=None):       
        """
        See the corresponding PRRModel documentation
        """
        return self.get_prr(fac, dems)
    
    def get_prr_lb(self, fac, dems=None):
        """
        See the corresponding PRRModel documentation
        """
        return self.get_prr(fac, dems)

    @property
    def dems(self):
        """
        See the corresponding PRRModel documentation
        """
        return self._dems

    @property
    def facs(self):
        """
        See the corresponding PRRModel documentation
        """
        return self._facs
