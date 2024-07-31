"""
An implementation for a logistic regression ML model with 253 inputs
"""
from iot_net_planner.prediction.prr_model import PRRModel
from iot_net_planner.prediction.ml_253_input import ML253FeaturesInput

import numpy as np
from statsmodels.iolib.smpickle import load_pickle as load_model
import statsmodels.api as sm

class LRModel():
    def __init__(self, path, sc):
        self.model = load_model(path)
        self._sc = sc

    def forward(self, X):
        X = self._sc.run(None, {"X": X})[0]
        return self.model.predict(X)

class LR253Features(PRRModel):
    def __init__(self, dems, facs, sampler, model_path, standard_scalar, ncols=250):
        self._input_gen = ML253FeaturesInput(dems, facs, sampler, ncols)
        self._dems = dems
        self._facs = facs
        self._sampler = sampler
        self._ncols = ncols
        self._model = LRModel(model_path, standard_scalar)
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

def train_xg_253_model(X_train, y_train, sc_out, lr_out, logging=False):
    """
    Train a logistic regression model on data X and y. 
    Generates a standard scaler (sc) model and a logistic
    regression model. Both of these models need to be used 
    to construct a full model

    :param X_train: a numpy array of the training inputs. 
    See ml_253_input for generating the input data

    :param y_train: a numpy array of the training outputs

    :param sc_out: the file path to write the sc output to.
    The file extension should be '.onnx', and this will be
    appended if it is not present

    :param lr_out: the file path to write the logistic regression
    output to. The file extension should be '.pkl', and this
    will be appended if it is not present

    :param logging: when True, prints statistics about the model.
    Defaults to False
    """
    def ends_in(s, ending):
        return s[-1*len(ending):] == ending

    sc_out += (not ends_in(sc_out, ".onnx")) * ".onnx"
    lr_out += (not ends_in(lr_out, ".pkl")) * ".pkl"

    sc = StandardScaler()
    X_train = sc.fit_transform(X_train)
    onx = to_onnx(sc, X_train[:1].astype(np.double))
    with open(sc_out, "wb") as f:
        f.write(onx.SerializeToString())

    weights = [
        len(y_train) / (len(np.unique(y_train))*np.where(y_train == 0)[0].size),
        len(y_train) / (len(np.unique(y_train))*np.where(y_train == 1)[0].size)
    ]

    freq_weights = []
    for i in y_train:
        if i == 0:
            freq_weights.append(weights[0])
        else:
            freq_weights.append(weights[1])

    log_reg = sm.GLM(y_train, X_train, freq_weights=freq_weights).fit()
    if logging:
        print(log_reg.summary())

    log_reg.save(lr_out)
