"""An implementation for an xgboost ML model with 253 inputs. Credit to Alfredo Rodriguez.
"""
from iot_net_planner.prediction.prr_model import PRRModel
from iot_net_planner.prediction.ml_253_input import ML253FeaturesInput

from sklearn.preprocessing import StandardScaler
from skl2onnx import to_onnx
from onnxruntime import InferenceSession
import numpy as np
import xgboost as xgb

class XGModel():
    """A prediction model using XG boost

    :param path: a path to the model's .json file
    :type path: str
    :param sc_file: a path to the model's standard
        scaler .onnx file
    :type sc_file: str
    """
    def __init__(self, path, sc_file, n_inputs=252):
        """Constructor method
        """
        self.model = xgb.Booster()
        self.model.load_model(path)
        with open(sc_file, "rb") as f:
            onx = f.read()
        standard_scalar = InferenceSession(onx)
        self._sc = standard_scalar

    def forward(self, X):
        """Run the model on input X

        :param X: an n by 253 numpy array of inputs
        :type: np.ndarray
        :return: an n dimensional numpy array of predictions
        :rtype: np.ndarray
        """
        X = self._sc.run(None, {"X": X})[0]
        dmat = xgb.DMatrix(X)
        return self.model.predict(dmat)

class XG253Features(PRRModel):
    """A PRRModel API wrapper around XGModel

    :param dems: the demand points to use
    :type dems: gpd.GeoDataFrame
    :param facs: the gateways to use
    :type facs: gpd.GeoDataFrame
    :param sampler: the sampler to use
    :type sampler: class: `iot_net_planner.geo.sampler.LinkSampler`
    :param model_path: a path to the model's .json file
    :type model_path: str
    :param sc_path: a path to the model's standard scaler .onnx file
    :type sc_path: str
    :param ncols: the number of samples to use. The total number of
        inputs will be ncols + 3, defaults to 250
    :type ncols: int, optional
    """
    def __init__(self, dems, facs, sampler, model_path, sc_path, ncols=250):
        self._input_gen = ML253FeaturesInput(dems, facs, sampler, ncols)
        self._dems = dems
        self._facs = facs
        self._sampler = sampler
        self._ncols = ncols
        self._model = XGModel(model_path, sc_path)
        self._all_dems = np.full(len(dems), True)

    @property
    def dems(self):
        """The demand points
        
        :return: the demand points associated with this model
        :rtype: gpd.GeoDataFrame
        """
        return self._dems

    @property
    def facs(self):
        """The gateway points
        
        :return: the gateway points associated with this model
        :rtype: gpd.GeoDataFrame
        """
        return self._facs

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
        return self._model.forward(self._input_gen.get_input(fac, dems))

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
        return self.get_prr(fac, dems)
            
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
        return self.get_prr(fac, dems)

def train_xg_253_model(X_train, y_train, sc_out, xg_out, num_round=1000):
    """Train an xg_boost model on data X and y. Generates
    a standard scaler (sc) model and an xg boost model.
    Both of these models need to be used to construct
    a full model

    :param X_train: a numpy array of the training inputs. 
        See ml_253_input for generating the input data
    :type X_train: np.ndarray
    :param y_train: a numpy array of the training outputs
    :type y_train: np.ndarray
    :param sc_out: the file path to write the sc output to.
        The file extension should be '.onnx', and this will be
        appended if it is not present
    :type sc_out: str
    :param xg_out: the file path to write the xg boost
        output to. The file extension should be '.json', and this
        will be appended if it is not present
    :type xg_out: str
    :param num_round: int for how many training rounds to perform,
        defaults to 1000
    :type num_round: int, optional
    """
    def ends_in(s, ending):
        return s[-1*len(ending):] == ending

    sc_out += (not ends_in(sc_out, ".onnx")) * ".onnx"
    xg_out += (not ends_in(xg_out, ".json")) * ".json"

    sc = StandardScaler()
    X_train = sc.fit_transform(X_train)
    onx = to_onnx(sc, X_train[:1].astype(np.double))
    if sc_out != ".onnx":
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
