"""
A driver for creating an ml input for a 253 feature prr model.
The input is 250 line segment samples, the log-distance,
the log of the absolute altitude difference, and a constant
"""
import numpy as np
import statsmodels.api as sm

class ML253FeaturesInput():
    """
    A class for generating ml model inputs using the 253 feature model.
    The input contains 250 line of sight samples, the log-distance, 
    the log of the absolute altitude difference, and a constant
    """
    def __init__(self, dems, facs, sampler, ncols=250):
        """
        Create a new input generator

        :param dems: a GeoDataFrame of the demand points to compute inputs to

        :param facs: a GeoDataFrame of the facility points to compute inputs from

        :param sampler: an instance of geo.sampler instantiated with dems and facs
        """
        self._dems = dems
        self._facs = facs
        self._sampler = sampler
        self._ncols = ncols
        self._all_dems = np.full(len(dems), True)

    def _generate_sample_points(self, fac, dems=None):
        # Returns the locations to sample, the shape to reshape to after sampling, and altitudes
        if dems is None:
            dems = self._all_dems

        fac_start = False # When true the line segment originates from the facility, usually false
        if fac_start:
            fs, ds = (0, 1)
        else:
            fs, ds = (1, 0)
        
        segments = np.empty((dems.sum(), 2, 2))
        segments[:, fs, 0] = self._facs.geometry[fac].x
        segments[:, fs, 1] = self._facs.geometry[fac].y
        segments[:, ds, 0] = self._dems.geometry.x[dems]
        segments[:, ds, 1] = self._dems.geometry.y[dems]

        altitudes = np.empty((dems.sum(), 2))
        altitudes[:, fs] = self._facs['altitude'][fac]
        altitudes[:, ds] = self._dems['altitude'][dems]
        
        segments = np.linspace(segments[:, 0, :], segments[:, 1, :], self._ncols, axis=1)
        altitudes = np.linspace(altitudes[:, 0], altitudes[:, 1], self._ncols, axis=1)

        seg_shape = segments.shape
        return (segments.reshape((seg_shape[0] * seg_shape[1], seg_shape[2])), [seg_shape, altitudes])
    
    def _reshape_samples(self, arr, seg_shape, altitudes):
        # Reshape the samples back after sampling
        arr = arr.reshape(seg_shape[:2])
        return (altitudes - arr)

    def get_input(self, fac, dems=None):
        """
        Get the input from fac to dems, includes the constant

        :param fac: the facility to get input from

        :param dems: a boolean numpy array of the demand points to get. 
        Will get the inputs to each demand point where dems[i] is True.
        If None is passed in then it will get the input to all demand points

        :returns: A dems.sum() x 253 numpy array of inputs if demands is not None 
        """
        if dems is None:
            dems = self._all_dems
        distances = np.log(0.01 + self._dems[dems].distance(self._facs.geometry[fac]).to_numpy())
        heights = np.log(0.01 + np.absolute(self._dems['altitude'][dems] - self._facs['altitude'][fac]))

        samples, args = self._generate_sample_points(fac, dems)
        samples = self._sampler.batched_sample(samples[:, 0], samples[:, 1])
        los = self._reshape_samples(samples, *args)

        X = np.empty((los.shape[0], los.shape[1] + 2))
        X[:, :-2] = los
        X[:, -2] = distances
        X[:, -1] = heights

        return sm.add_constant(X, has_constant='add')
