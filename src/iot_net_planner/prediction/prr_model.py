"""A module containing an abstract class for predicting packet reception rates.
"""

from abc import ABC, abstractmethod
import numpy as np

class PRRModel(ABC):
    """An abstract class for a PRR model to predict packet 
    reception rate between a gateway and demand point. 
    """
    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @property
    @abstractmethod
    def dems(self):
        """The demand points
        
        :return: the demand points associated with this model
        :rtype: gpd.GeoDataFrame
        """
        pass

    @property
    @abstractmethod
    def facs(self):
        """The gateway points
        
        :return: the gateway points associated with this model
        :rtype: gpd.GeoDataFrame
        """
        pass

    def save_prrs(self, filepath, logging=False):
        """Saves all prrs to a numpy saved file at filepath. The file
        will contain a len(dems) x len(facs) matrix where the entry
        at [i, j] contains the prr from gateway j to demand point i

        :param filepath: the file to save to
        :type filepath: str
        :param logging: whether or not to log progress, defaults to False
        :type logging: bool, optional
        :return: a 2d numpy array with shape (len(dems), len(facs))
            where entry index (i, j) is the prr to the demand point i
            by the facility j
        :rtype: np.ndarray
        """
        A = np.empty((len(self.dems), len(self.facs)))
        for fac in range(A.shape[1]):
            if logging:
                print(f" {fac+1} / {A.shape[1]}", end="\r")
            A[:, fac] = self.get_prr(fac)
        np.save(filepath, A)
        
