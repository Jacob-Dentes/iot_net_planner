"""
An abstract class for a PRR model 
"""
from abc import ABC, abstractmethod
import numpy as np

class PRRModel(ABC):
    @abstractmethod
    def get_prr(self, fac, dems=None):
        """
        Get the exact prrs between fac and the self.dems[dems]  

        :param fac: the facility to generate prrs from
        :param dems: a boolean numpy array with length equal to the
        number of demand points, dems[i] == True means to generate 
        the prrs to demand point i

        :returns: a numpy array with length dems.sum() of the prrs to
        each of the demand points where dems[i]
        """
        pass

    @abstractmethod
    def get_prr_ub(self, fac, dems=None):
        """
        Get an upper bound on prrs between fac and the self.dems[dems]  

        :param fac: the facility to generate prrs from
        :param dems: a boolean numpy array with length equal to the
        number of demand points, dems[i] == True means to generate 
        an upper bound on prrs to demand point i

        :returns: a numpy array with length dems.sum() of the prr
        upper bounds to each of the demand points where dems[i]
        """
        pass

    @abstractmethod
    def get_prr_lb(self, fac, dems=None):
        """
        Get a lower bound on prrs between fac and the self.dems[dems]  

        :param fac: the facility to generate prrs from
        :param dems: a boolean numpy array with length equal to the
        number of demand points, dems[i] == True means to generate 
        a lower bound on prrs to demand point i

        :returns: a numpy array with length dems.sum() of the prr
        lower bounds to each of the demand points where dems[i]
        """
        pass

    @property
    @abstractmethod
    def dems(self):
        """
        :returns: the demand points associated with this model
        """
        pass

    @property
    @abstractmethod
    def facs(self):
        """
        :returns: the facilities associated with this model
        """
        pass

    def save_prrs(self, filepath):
        """
        Saves all prrs to a numpy saved file at filepath. The file
        will contain a len(dems) x len(facs) matrix where the 

        :param filepath: the file to save to

        :returns: a 2d numpy array with shape (len(dems), len(facs))
        where entry index (i, j) is the prr to the demand point i
        by the facility j
        """
        A = np.empty((len(self.dems), len(self.facs)))
        for fac in range(A.shape[1]):
            A[:, fac] = self.get_prr(fac)
        np.save(filepath, A)
        
