"""
An implementation for an xgboost ML model with 253 inputs
"""
from iot_net_planner.prediction.prr_model import PRRModel
from iot_net_planner.prediction.ml_253_input import ML253FeaturesInput

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
        self._input_gen = ML253FeaturesInput(dems, facs, sampler, ncols)
        self._dems = dems
        self._facs = facs
        self._sampler = sampler
        self._ncols = ncols
        self._model = XGModel(model_path, standard_scalar)
        self._all_dems = np.full(len(dems), True)

    @property
    def dems(self):
        return self._dems

    @property
    def facs(self):
        return self._facs

    def get_prr(self, fac, dems=None):
        return self._model.forward(self._input_gen.get_input(fac, dems))

    def get_prr_ub(self, fac, dems=None):
        return self.get_prr(fac, dems)
            
    def get_prr_lb(self, fac, dems=None):
        return self.get_prr(fac, dems)
