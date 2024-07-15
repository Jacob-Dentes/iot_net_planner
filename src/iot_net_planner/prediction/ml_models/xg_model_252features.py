"""
A prr implementation for the log(distance), los, log(distance) * los model
"""
from iot_net_planner.prediction.prr_model import PRRModel

import numpy as np
from xgboost import Booster, DMatrix

class XGModel():
    def __init__(self, path, sc, n_inputs=252):
        self.model = Booster()
        self.model.load_model(path)
        self._sc = sc

    def forward(self, X):
        X = self._sc.run(None, {"X": X})[0]
        dmat = DMatrix(X)
        return self.model.predict(dmat)

class XG252Features(PRRModel):
    def __init__(self, dems, facs, sampler, model_path, standard_scalar, ncols=250):
        self._dems = dems
        self._facs = facs
        self._sampler = sampler
        self._ncols = ncols
        self._model = XGModel(model_path, standard_scalar)
        self._all_dems = np.full(len(dems), True)

    def _generate_sample_points(self, fac, dems=None):
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
        arr = arr.reshape(seg_shape[:2])
        return (altitudes - arr)

    @property
    def dems(self):
        return self._dems

    @property
    def facs(self):
        return self._facs

    def get_input(self, fac, dems=None):
        if dems is None:
            dems = self._all_dems
        distances = np.log(self._dems[dems].distance(self._facs.geometry[fac]).to_numpy())
        heights = np.log(np.absolute(self._dems['altitude'][dems] - self._facs['altitude'][fac]))

        samples, args = self._generate_sample_points(fac, dems)
        samples = self._sampler.batched_sample(samples[:, 0], samples[:, 1])
        los = self._reshape_samples(samples, *args)

        X = np.empty((los.shape[0], los.shape[1] + 2))
        X[:, :-2] = los
        X[:, -2] = distances
        X[:, -1] = heights

        return X
        
      
    def get_prr(self, fac, dems=None):
        return self._model.forward(self.get_input(fac, dems))
        # if dems is None:
        #     dems = self._all_dems
        # distances = np.log(self._dems[dems].distance(self._facs.geometry[fac]).to_numpy())
        # heights = np.log(np.absolute(self._dems['altitude'][dems] - self._facs['altitude'][fac]))

        # samples, args = self._generate_sample_points(fac, dems)
        # samples = self._sampler.batched_sample(samples[:, 0], samples[:, 1])
        # los = self._reshape_samples(samples, *args)

        # X = np.empty((los.shape[0], los.shape[1] + 2))
        # X[:, :-2] = los
        # X[:, -2] = distances
        # X[:, -1] = heights
        
        # return self._model.forward(X)

    def get_prr_ub(self, fac, dems=None):
        return self.get_prr(fac, dems)
            
    def get_prr_lb(self, fac, dems=None):
        return self.get_prr(fac, dems)
