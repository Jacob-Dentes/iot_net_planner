from make_pypath import pathify
pathify() 
import sys

import geopandas as gpd
import pandas as pd
import json

from iot_net_planner.geo.plotting import plot_facs_coverage
from iot_net_planner.prediction.coverage import get_coverages
from iot_net_planner.prediction.prr_file import FileModel

def main(dem_file, fac_file, prr_file, sol_file):
    dems = gpd.read_file(dem_file).to_crs(epsg=4326)
    facs = gpd.read_file(fac_file).to_crs(dems.crs)

    new_geom = gpd.GeoSeries(pd.concat([dems.geometry, facs.geometry], ignore_index=True), crs=dems.crs)
    utm = new_geom.estimate_utm_crs()

    dems = dems.to_crs(utm)
    facs = facs.to_crs(utm)

    with open(sol_file, 'rb') as f:
        sol_obj = json.load(f)      
        sol = sol_obj['sol']

    prr = FileModel(dems, facs, model_file)
    coverages = get_coverages(sol, prr)
    plot_facs_coverage(dems, facs, sol)    

if __name__ == "__main__":
    args = list(sys.argv[1:])
       
    main(*args)
    
