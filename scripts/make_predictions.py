from make_pypath import pathify
pathify() 
import sys

import geopandas as gpd
import pandas as pd

from iot_net_planner.geo.dsm_sampler import DSMSampler

from iot_net_planner.prediction.prr_cache import CachedPRRModel
from iot_net_planner.prediction.xg_253features import XG253Features

def main(dsm_file, dem_file, fac_file, sc_path, xg_path, prr_out):
    dems = gpd.read_file(dem_file).to_crs(epsg=4326)
    facs = gpd.read_file(fac_file).to_crs(dems.crs)

    new_geom = gpd.GeoSeries(pd.concat([dems.geometry, facs.geometry], ignore_index=True), crs=dems.crs)
    utm = new_geom.estimate_utm_crs()

    dems = dems.to_crs(utm)
    facs = facs.to_crs(utm)

    with DSMSampler(utm, dsm_file, 0) as sampler:
        model = CachedPRRModel(XG253Features(dems, facs, sampler, xg_path, sc_path))

        model.save_prrs(prr_out, logging=True)


if __name__ == "__main__":
    args = list(sys.argv[1:])
    
    main(*args)
    
