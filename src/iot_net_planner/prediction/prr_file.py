
"""
A prr model loaded from a file
"""
from iot_net_planner.prediction.prr_model import PRRModel
import numpy as np

class FileModel(PRRModel):
    def __init__(self, dems, facs, file_path):
        """
        Wraps a PRRModel. Adds a caching layer to avoid regenerating prrs
        Also provides an improve_ub method for incrementally improving upper bounds

        :param model: the PRRModel to wrap a cache around
        """
        self._prrs = np.load(file_path)
        err_msg = f"File shape does not match demands and facilities. File has {self._prrs.shape}, but there were {len(dems)} demand points and {len(facs)} facilities."
        assert self._prrs.shape[0] == len(dems) and self._prrs.shape[1] == len(facs), err_msg
        self._dems = dems
        self._facs = facs
        self._all_dems = np.full(len(dems), True)

    def get_prr(self, fac, dems=None):
        if dems is None:
            dems = self._all_dems
        return self._prrs[fac, dems]

    def get_prr_ub(self, fac, dems=None):       
        return self.get_prr(fac, dems)
    
    def get_prr_lb(self, fac, dems=None):
        return self.get_prr(fac, dems)

    @property
    def dems(self):
        return self._dems

    @property
    def facs(self):
        return self._facs
