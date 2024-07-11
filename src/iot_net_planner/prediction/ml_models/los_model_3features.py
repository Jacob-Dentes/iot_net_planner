"""
A prr implementation for the log(distance), los, log(distance) * los model
"""
from iot_net_planner.prediction.prr_model import PRRModel

import numpy as np
import torch
import torch.nn as nn

class LogisticRegression(nn.Module):
    def __init__(self, n_inputs, n_outputs):
        super(LogisticRegression, self).__init__()
        self.linear = nn.Linear(n_inputs, n_outputs)

    def forward(self, x):
        x = torch.from_numpy(x)
        y_predicted = torch.sigmoid(self.linear(x))
        return y_predicted

class LogisticModel():
    def __init__(self, path, sc, n_inputs=3, n_outputs=1):
        self.model = LogisticRegression(n_inputs, n_outputs).double()
        self.model.load_state_dict(torch.load(path))
        self._sc = sc

    def forward(self, log_distance, los):
        x = np.zeros((len(log_distance), 3))
        x[:, 0] = log_distance
        x[:, 1] = los
        x[:, 2] = log_distance * los
        
        x = self._sc.run(None, {"X": x})[0]
        
        return self.model.forward(x).detach().numpy().flatten()

class LOS3Features(PRRModel):
    def __init__(self, dems, facs, sampler, model_path, standard_scalar, ncols=150):
        self._dems = dems
        self._facs = facs
        self._sampler = sampler
        self._ncols = ncols
        self._model = LogisticModel(model_path, standard_scalar)
        self._all_dems = np.full(len(dems), True)

    def _generate_sample_points(self, fac, dems=None):
        if dems is None:
            dems = np.full(len(self._dems), True)
        
        segments = np.empty((dems.sum(), 2, 2))
        segments[:, 0, 0] = self._facs.geometry[fac].x
        segments[:, 0, 1] = self._facs.geometry[fac].y
        segments[:, 1, 0] = self._dems.geometry.x[dems]
        segments[:, 1, 1] = self._dems.geometry.y[dems]

        altitudes = np.empty((dems.sum(), 2))
        altitudes[:, 0] = self._facs['altitude'][fac]
        altitudes[:, 1] = self._dems['altitude'][dems]
        
        segments = np.linspace(segments[:, 0, :], segments[:, 1, :], self._ncols, axis=1)
        altitudes = np.linspace(altitudes[:, 0], altitudes[:, 1], self._ncols, axis=1)

        seg_shape = segments.shape
        return (segments.reshape((seg_shape[0] * seg_shape[1], seg_shape[2])), [seg_shape, altitudes])

    def _reshape_samples(self, arr, seg_shape, altitudes):
        arr = arr.reshape(seg_shape[:2])
        return (altitudes >= arr).mean(axis=1)

    @property
    def dems(self):
        return self._dems

    @property
    def facs(self):
        return self._facs

    def get_prr(self, fac, dems=None):
        if dems is None:
            dems = self._all_dems
        distances = np.log(self._dems[dems].distance(self._facs.geometry[fac]).to_numpy())

        samples, args = self._generate_sample_points(fac, dems)
        samples = self._sampler.batched_sample(samples[:, 0], samples[:, 1])
        los = self._reshape_samples(samples, *args)
        
        return self._model.forward(distances, los)

    def get_prr_ub(self, fac, dems=None):
        if dems is None:
            dems = self._all_dems
        distances = np.log(self._dems[dems].distance(self._facs.geometry[fac]).to_numpy())
        los = np.ones(len(distances))

        return self._model.forward(distances, los)
        
    
    def get_prr_lb(self, fac, dems=None):
        if dems is None:
            dems = self._all_dems
        distances = np.log(self._dems[dems].distance(self._facs.geometry[fac]).to_numpy())
        los = np.zeros(len(distances))

        return self._model.forward(distances, los)
