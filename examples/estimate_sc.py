from make_pypath import pathify
pathify() 
import sys

import geopandas as gpd
import pandas as pd

from iot_net_planner.geo.dsm_sampler import DSMSampler
from iot_net_planner.prediction.sc_estimation import estimate_sc_253features

def main(dsm_file, dem_file, fac_file, sc_out, per_fac):
    dems = gpd.read_file(dem_file).to_crs(epsg=4326)
    facs = gpd.read_file(fac_file).to_crs(dems.crs)

    new_geom = gpd.GeoSeries(pd.concat([dems.geometry, facs.geometry], ignore_index=True), crs=dems.crs)
    utm = new_geom.estimate_utm_crs()

    dems = dems.to_crs(utm)
    facs = facs.to_crs(utm)

    with DSMSampler(utm, dsm_file, 0) as sampler:
        estimate_sc_253features(dems, facs, sampler, sc_out, per_fac)

if __name__ == "__main__":
    args = list(sys.argv[1:])
    
    if len(args) == 5:
        args[4] = int(args[4])
    
    main(*args)
    
