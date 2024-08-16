from make_pypath import pathify
pathify() 
import sys

import numpy as np

from iot_net_planner.geo.dsm_sampler import DSMSampler
from iot_net_planner.prediction.xg_253features import train_xg_253_model, XGModel

def split_array(arr1, arr2, prop):
    if not (0.0 <= prop <= 1.0):
        raise ValueError("The 'prop' parameter must be between 0.0 and 1.0.")
    if not arr1.shape[0] == arr2.shape[0]:
        raise ValueError("The shapes of X and y do not match.")

    shuffled_indices = np.random.permutation(arr1.shape[0])
    split_idx = int(len(shuffled_indices) * prop)

    first_part_indices = shuffled_indices[:split_idx]
    second_part_indices = shuffled_indices[split_idx:]

    return arr1[first_part_indices], arr2[first_part_indices], arr1[second_part_indices], arr2[second_part_indices]

def main(x_path, y_path, sc_out, xg_out, test_prop=0.0):
    X = np.load(x_path)
    y = np.load(y_path)

    X_test, y_test, X, y = split_array(X, y, test_prop)

    train_xg_253_model(X, y, sc_out, xg_out)

    if len(X_test) > 0:
        model = XGModel(xg_out, sc_out)
        prediction = model.forward(X_test)
        brier = (1 / len(X_test)) * np.square(prediction - y_test).sum()
        print(f"Brier score: {brier}")

if __name__ == "__main__":
    args = list(sys.argv[1:])
    
    if len(args) == 5:
        args[4] = float(args[4])
        
    main(*args)
    
