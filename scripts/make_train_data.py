from make_pypath import pathify
pathify() 
import sys

import geopandas as gpd
import numpy as np
from shapely.geometry import Point

from iot_net_planner.prediction.ml_253_input import ML253FeaturesInput
from iot_net_planner.geo.dsm_sampler import DSMSampler

first_pt = lambda line: Point(line.coords[0])
second_pt = lambda line: Point(line.coords[1])

def main(dsm_file, link_file, X_out, y_out, progress_save=None):
    links = gpd.read_file(link_file)
    if links.crs is None:
        print("Link data does not have a CRS. Assuming EPSG:4326.")
        links = links.set_crs(epsg=4326)
    utm = links.estimate_utm_crs()
    links = links.to_crs(utm)

    dems = gpd.GeoDataFrame(geometry=gpd.GeoSeries([first_pt(i) for i in links.geometry]), crs=utm)
    dems['altitude'] = links['ele_tr']
    facs = gpd.GeoDataFrame(geometry=gpd.GeoSeries([second_pt(i) for i in links.geometry]), crs=utm)
    facs['altitude'] = links['ele_gw']

    X = np.zeros((len(links), 253))
    y = np.array([int(i) for i in links['success']])   

    with DSMSampler(utm, dsm_file, 0) as sampler:
        input_gen = ML253FeaturesInput(dems, facs, sampler)
        
        for i in range(len(links)):
            if i % 512 == 0:
                print(f"{i+1} / {len(links)}", end="\r")
            if (progress_save is not None) and (i % progress_save == 0):
                np.save(X_out, X)
            dem_choice = np.full(len(dems), False)
            dem_choice[i] = True
            X[i] = input_gen.get_input(i, dem_choice)[0]

    finite_rows = np.all(np.isfinite(X), axis=1)
    real_samples = np.all(X > -9998, axis=1)
    if np.any(~real_samples):
        print(f"Some ({(~real_samples).sum()}) links were not fully contained in the DSM." + \
              " Ensure the files have correct CRS's and the DSM includes all LineStrings." + \
              " Links outside the DSM have been ignored.")
    X = X[finite_rows & real_samples]
    y = y[finite_rows & real_samples]

    np.save(X_out, X)
    np.save(y_out, y)     

if __name__ == "__main__":
    args = list(sys.argv[1:])
    
    if len(args) == 5:
        args[4] = int(args[4])

    main(*args)
    
