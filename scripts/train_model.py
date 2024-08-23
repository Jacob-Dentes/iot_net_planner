from make_pypath import pathify
pathify() 
import sys
import os

import numpy as np

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

def main(x_path, y_path, sc_out, xg_out, test_prop=0.0, folder_path=None, cities=[]):
    X = np.load(x_path)
    y = np.load(y_path)

    X_test, y_test, X, y = split_array(X, y, test_prop)
    
    X_files = [X]
    y_files = [y]
    for city in cities:
        X_files.append(os.path.join(folder_path, city + "_X.npy"))
        y_files.append(os.path.join(folder_path, city + "_y.npy"))

    def create_memory_mapped_array(file_paths, output_file):
        total_rows = 0
        shape = None
        dtype = None

        for file in file_paths:
            if isinstance(file, str):
                arr = np.load(file)
            else:
                arr = file
            if shape is None:
                shape = arr.shape[1:]
            total_rows += arr.shape[0]
            dtype = arr.dtype

        large_array = np.memmap(output_file, dtype=dtype, mode='w+', shape=(total_rows, *shape))

        current_row = 0

        for file in file_paths:
            if isinstance(file, str):
                arr = np.load(file)
            else:
                arr = file
            num_rows = arr.shape[0]
            large_array[current_row:current_row + num_rows] = arr
            current_row += num_rows

        large_array.flush()
        return large_array

    if folder_path is not None:
        X_file_path = os.path.join(folder_path, "_".join(cities) + "_temp_Xs.npy")
        y_file_path = os.path.join(folder_path, "_".join(cities) + "_temp_ys.npy")
        
        X = create_memory_mapped_array(X_files, X_file_path)
        y = create_memory_mapped_array(y_files, y_file_path)
    
    train_xg_253_model(X, y, sc_out, xg_out)

    if len(X_test) > 0:
        model = XGModel(xg_out, sc_out)
        prediction = model.forward(X_test)
        brier = (1 / len(X_test)) * np.square(prediction - y_test).sum()
        print(f"Brier score: {brier}")

    if folder_path is not None:
        os.remove(X_file_path)
        os.remove(y_file_path)

if __name__ == "__main__":
    args = list(sys.argv[1:])
    
    if len(args) >= 5:
        args[4] = float(args[4])

    if len(args) == 7:
        args[6] = list(args[6].split(","))
        
    main(*args)
    
