from make_pypath import pathify
pathify() 
import sys
import json

import geopandas as gpd
import pandas as pd
import numpy as np

from iot_net_planner.prediction.prr_file import FileModel
from iot_net_planner.optimization.scip_model import SCIPModel

def main(dem_file, fac_file, prr_file, out_file, coverage=None, inexact_k=10):
    dems = gpd.read_file(dem_file).to_crs(epsg=4326)
    facs = gpd.read_file(fac_file).to_crs(dems.crs)

    new_geom = gpd.GeoSeries(pd.concat([dems.geometry, facs.geometry], ignore_index=True), crs=dems.crs)
    utm = new_geom.estimate_utm_crs()

    dems = dems.to_crs(utm)
    facs = facs.to_crs(utm)

    dems.reset_index(inplace=True)
    facs.reset_index(inplace=True)

    if 'cost' not in facs:
        facs['cost'] = np.ones(len(facs))
    if 'built' not in facs:
        facs['built'] = np.zeros(len(facs))
    if coverage is None:
        coverage = dems['coverage'].to_numpy()

    prr = FileModel(dems, facs, prr_file)

    sol = SCIPModel.solve_budget(coverage, dems, facs, prr, blob_size=inexact_k, logging=False)

    sol_object = {'coverage': list(coverage),  'sol': list(sol)}

    # From https://stackoverflow.com/questions/12309269/how-do-i-write-json-data-to-a-file#12309296
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(sol_object, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    args = list(sys.argv[1:])

    if len(args) == 5:
        args[5] = float(args[5])
    
    main(*args)
    
