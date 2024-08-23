from make_pypath import pathify
pathify() 
import sys
import os

import numpy as np

from iot_net_planner.prediction.xg_253features import train_xg_253_model

def main(folder_path, cities, xg_out):
    X_files = []
    y_files = []
    for city in cities:
        X_files.append(os.path.join(folder_path, city + "_X.npy"))
        y_files.append(os.path.join(folder_path, city + "_y.npy"))

    def create_memory_mapped_array(file_paths, output_file):
        total_rows = 0
        shape = None
        dtype = None

        for file in file_paths:
            arr = np.load(file)
            if shape is None:
                shape = arr.shape[1:]
            total_rows += arr.shape[0]
            dtype = arr.dtype

        large_array = np.memmap(output_file, dtype=dtype, mode='w+', shape=(total_rows, *shape))

        current_row = 0

        for file in file_paths:
            arr = np.load(file)
            num_rows = arr.shape[0]
            large_array[current_row:current_row + num_rows] = arr
            current_row += num_rows

        large_array.flush()
        return large_array

    X_file_path = os.path.join(folder_path, "_".join(cities) + "_temp_Xs.npy")
    y_file_path = os.path.join(folder_path, "_".join(cities) + "_temp_ys.npy")

    X = create_memory_mapped_array(X_files, X_file_path)
    y = create_memory_mapped_array(y_files, y_file_path)
    
    train_xg_253_model(X, y, ".onnx", xg_out)

    os.remove(X_file_path)
    os.remove(y_file_path)

if __name__ == "__main__":
    args = list(sys.argv[1:])

    args[1] = list(args[1].split(","))
           
    main(*args)
    
