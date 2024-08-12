from make_pypath import pathify
pathify() 
import sys

import geopandas as gpd
import pandas as pd
import numpy as np

def main(corner_file, manual_file, output_path, mode=None):
    if mode is not None and mode.lower() not in ["all_exact", "no_exact"]:
        mode = None
    elif mode is not None:
        mode = mode.lower()
    
    corner_gdf = gpd.read_file(corner_file)
    manual_gdf = gpd.read_file(manual_file)

    assert "altitude" in corner_gdf, "Corner gateway file missing altitude"
    assert "altitude" in manual_gdf, "Manual gateway file missing altitude"

    if "built" not in corner_gdf:
        corner_gdf["built"] = np.zeros(len(corner_gdf))

    if "built" not in manual_gdf:
        manual_gdf["built"] = np.zeros(len(manual_gdf))

    corner_gdf["exact"] = np.full(len(corner_gdf), False if mode != "all_exact" else True)
    manual_gdf["exact"] = np.full(len(manual_gdf), True if mode != "no_exact" else False)

    corner_gdf = corner_gdf.to_crs(epsg=4326)
    manual_gdf = manual_gdf.to_crs(epsg=4326)

    combined_gdf = pd.concat([corner_gdf, manual_gdf], ignore_index=True)
    combined_gdf.reset_index(drop=True, inplace=True)

    try:
        crs = combined_gdf.estimate_utm_crs()
    except:
        crs = combined_gdf.crs

    combined_gdf = combined_gdf.to_crs(crs)
    combined_gdf.to_file(output_path)

if __name__ == "__main__":
    args = list(sys.argv[1:])

    if len(args) < 4:
        args.append(None)
    
    main(*args)
