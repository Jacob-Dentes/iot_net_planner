"""
An implementation for an xgboost ML model with 253 inputs
"""
from iot_net_planner.prediction.prr_model import PRRModel
from iot_net_planner.prediction.ml_253_input import ML253FeaturesInput

from sklearn.preprocessing import StandardScaler
from skl2onnx import to_onnx
import numpy as np
import xgboost as xgb

class XGModel():
    def __init__(self, path, sc, n_inputs=252):
        self.model = xgb.Booster()
        self.model.load_model(path)
        self._sc = sc

    def forward(self, X):
        X = self._sc.run(None, {"X": X})[0]
        dmat = xgb.DMatrix(X)
        return self.model.predict(dmat)

class XG253Features(PRRModel):
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

def train_xg_253_model(X_train, y_train, sc_out, xg_out, num_round=1000):
    """
    Train an xg_boost model on data X and y. Generates
    a standard scaler (sc) model and an xg boost model.
    Both of these models need to be used to construct
    a full model

    :param X_train: a numpy array of the training inputs. 
    See ml_253_input for generating the input data

    :param y_train: a numpy array of the training outputs

    :param sc_out: the file path to write the sc output to.
    The file extension should be '.onnx', and this will be
    appended if it is not present

    :param xg_out: the file path to write the xg boost
    output to. The file extension should be '.json', and this
    will be appended if it is not present

    :param num_round: int for how many training rounds to perform.
    Defaults to 1000
    """
    def ends_in(s, ending):
        return s[-1*len(ending):] == ending

    sc_out += (not ends_in(sc_out, ".onnx")) * ".onnx"
    xg_out += (not ends_in(xg_out, ".json")) * ".json"

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

    X_train = xgb.DMatrix(X_train, label=y_train, weight=freq_weights)

    params = {
        'objective': 'binary:logistic',
        'eval_metric': 'logloss',
        'max_depth': 10,
        'eta': 0.3,
        'seed': 10
    }

    model = xgb.train(params, X_train, num_round)

    model.save_model(xg_out)
