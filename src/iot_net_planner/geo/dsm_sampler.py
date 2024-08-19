import numpy as np
import rasterio as rio
import geopandas as gpd
from shapely.geometry import Point

from iot_net_planner.geo.sampler import LinkSampler

class DSMSampler(LinkSampler):
    """A link sampler that samples from a DSM. All DSM samplers should be cleaned up after use
    using self.clean_up(). Conversely, you can use the ```with open DSMSampler(crs, path) as sampler```
    syntax.

    :param crs: the crs of the input points, should match the demand and facility crs.
    :type crs: str
    :param raster_path: a path to the raster file to use.
    :type raster_path: str
    :param band: the 0-indexed DSM band to use, can be None if only one band is present,
        defaults to None.
    :type band: int, optional
    """
    def __init__(self, crs, raster_path, band=None):
        """Constructor method       
        """
        self._band = band
        self._raster = rio.open(raster_path)
        self._crs = crs
    
    def sample(self, x, y):
        """Return the raster sample at x, y

        :param x: the x-coordinate in the provided crs
        :type x: float
        :param y: the y-coordinate in the provided crs
        :type y: float
        :returns: the sample at (x, y)
        :rtype: float
        """
        return self.batched_sample(np.array(x), np.array(y))[0]

    def batched_sample(self, xs, ys):
        """Return a numpy array of the samples at the points defined by xs and ys

        :param xs: the x-coordinates in the provided crs
        :type xs: np.ndarray
        :param ys: the y-coordinates in the provided crs with len(ys) == len(xs)
        :type ys: np.ndarray
        :returns: the samples at the provided points
        :rtype: np.ndarray
        """
        geo_points = gpd.GeoSeries([Point(x, y) for x, y in zip(xs, ys)], crs=self._crs).to_crs(self._raster.crs)
        xs = geo_points.geometry.x
        ys = geo_points.geometry.y
        if self._band is None:
            return np.fromiter(self._raster.sample(zip(xs, ys)), xs.dtype, count=len(xs))
        return np.fromiter((i[self._band] for i in self._raster.sample(zip(xs, ys))), xs.dtype, count=len(xs))

    def clean_up(self):
        """Closes the raster file, should always be called after the sampler is no longer in use
        """
        self._raster.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.clean_up()
