from iot_net_planner.prediction.ml_253_input import ML253FeaturesInput

import numpy as np
from sklearn.preprocessing import StandardScaler
from skl2onnx import to_onnx
    
def estimate_sc_253features(dems, facs, sampler, sc_out, per_fac=10, logging=True):
    """
    Create a StandardScaler estimation for given demands and facilities.
    This is intended to make a StandardScaler for cities without traindata

    :param dems: a GeoDataFrame of the demand points to use

    :param facs: a GeoDataFrame of the facilities to use

    :param sampler: a sampler initialized that works with dems and facs

    :param sc_out: a path to the file to output to. Should have a '.onnx'
    file extension, this will be appended if not present

    :param per_fac: the number of demand points to use per facilitiy to
    estimate. Should be between 1 and len(dems). Larger inputs are more
    accurate but slower.
    """
    def ends_in(s, ending):
        return s[-1*len(ending):] == ending

    sc_out += (not ends_in(sc_out, ".onnx")) * ".onnx"

    input_gen = ML253FeaturesInput(dems, facs, sampler)
    per_fac = max(1, min(len(dems), per_fac))

    X = np.empty((len(facs)*per_fac, 253))
    for fac in range(len(facs)):
        if logging:
            print(f"{fac + 1} / {len(facs)}", end="\r")
        dem_choice = np.full(len(dems), False)
        dem_choice[np.random.choice(np.arange(0, len(dems)), per_fac, False)] = True
        X[fac*per_fac:(fac+1)*per_fac] = input_gen.get_input(fac, dem_choice)

    finite_mask = np.isfinite(X)
    finite_rows = np.all(finite_mask, axis=1)
    X_train = X[finite_rows]

    sc = StandardScaler()
    X_train = sc.fit_transform(X_train)
    onx = to_onnx(sc, X_train[:1].astype(np.double))
    with open(sc_out, "wb") as f:
        f.write(onx.SerializeToString())
      
