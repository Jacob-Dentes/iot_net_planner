import numpy as np
import rasterio as rio
import geopandas as gpd
from shapely.geometry import Point

from iot_net_planner.geo.sampler import LinkSampler

class DSMSampler(LinkSampler):
    def __init__(self, dems, facs, raster_path):
        self._raster = rio.open(raster_path)
        self._crs = dems.crs
        if dems.crs != facs.crs:
            print(f"Warning. Demand point CRS: {self._dems.crs}. Facility CRS: {facs.crs}.")
    
    def sample(self, x, y):
        return self.batched_sample(np.array(x), np.array(y))[0]

    def batched_sample(self, xs, ys):
        geo_points = gpd.GeoSeries([Point(x, y) for x, y in zip(xs, ys)], crs=self._crs).to_crs(self._raster.crs)
        xs = geo_points.geometry.x
        ys = geo_points.geometry.y
        return np.fromiter(self._raster.sample(zip(xs, ys)), xs.dtype, count=len(xs))

    def clean_up(self):
        self._raster.close()
