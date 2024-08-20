from make_pypath import pathify
pathify() 
import sys

import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Point

from iot_net_planner.geo.dsm_sampler import DSMSampler

def _process_geojson(dsm_path, facs, out_path):
    if "built" not in facs:
        facs["built"] = np.zeros(len(facs))
    if "altitude" not in facs:
        facs["altitude"] = np.full(len(facs), np.nan)
    nan_mask = facs["altitude"].isna()
    with DSMSampler(facs.crs, dsm_path, 0) as sampler:
        samples = sampler.batched_sample(facs.geometry[nan_mask].x, facs.geometry[nan_mask].y)
        facs.loc[nan_mask, "altitude"] = samples        
    facs.to_file(out_path)

def from_csv(dsm_path, fac_path, out_path):
    df = pd.read_csv(fac_path)
    geometry = [Point(xy) for xy in zip(df["longitude"], df["latitude"])]
    facs = gpd.GeoDataFrame(df, geometry=geometry)

    facs.set_crs(epsg=4326, inplace=True)
    facs = facs.drop(columns=["latitude", "longitude"])
    _process_geojson(dsm_path, facs, out_path)

def from_geojson(dsm_path, fac_path, out_path):
    facs = gpd.read_file(fac_path)
    _process_geojson(dsm_path, facs, out_path)

if __name__ == "__main__":
    args = list(sys.argv[1:])
    
    assert len(args) == 3, "Incorrect arguments. Should be dsm_path gateway_path output_path"

    csv = ".csv"
    if args[1][-len(csv):] == csv:
        from_csv(*args)
    else:
        from_geojson(*args)
       
    
