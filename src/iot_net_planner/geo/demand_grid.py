import geopandas as gpd
from shapely.geometry import Point
import pandas as pd
import numpy as np
from fiona.drvsupport import supported_drivers
import fiona
supported_drivers['LIBKML'] = 'r'
supported_drivers['KML'] = 'r'

def _load_file(area_file, utm=None):
    # Load the KML file
    layers = list(fiona.listlayers(area_file))
    gdfs = [gpd.read_file(area_file, driver='KML', layer=layer) for layer in layers]
    area_frame = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True))

    if utm is not None:
        area_frame = area_frame.to_crs(utm)

    return area_frame

def _make_grid(area_frame, granularity):
    # Generate points
    minx, miny, maxx, maxy = area_frame.total_bounds
    x_coords = np.arange(minx, maxx, granularity)
    y_coords = np.arange(miny, maxy, granularity)
    points = [Point(x, y) for x in x_coords for y in y_coords]

    # Get intersection points
    dems = gpd.GeoDataFrame(geometry=points, crs=area_frame.crs)
    return dems[dems.geometry.apply(lambda point: any(area_frame.contains(point)))]

def add_alts(dems, sampler):
    """
    Add altitudes to a demand GeoDataFrame

    :param dems: the GeoDataFrame to add altitudes to, may be modified in place

    :param sampler: the sampler to use to determine the altitudes

    :returns: the modified GeoDataFrame
    """
    samples = sampler.batched_sample(dems.geometry.x, dems.geometry.y)
    dems['altitude'] = np.array(samples)

    return dems

def generate_grid(area_file, granularity, sampler=None, utm=None):
    """
    Generates a grid of demand points in the area defined by area_file
    with the number of points defined by granularity

    :param area_file: a string path to a kml file representing the area to
    put demand points

    :param granularity: a float, one point will be placed every granularity
    meters

    :param sampler: a geo sampler to use to fill the altitude column.
    If left None there will be no altitude column

    :param utm: a crs for the area. If none is provided then the area_file's
    crs is used, which may mean that granularity will no longer be meters

    :returns: a GeoDataFrame of the demand points
    """
    area_frame = _load_file(area_file, utm)

    dems = _make_grid(area_frame, granularity)

    dems = add_alts(dems, sampler)

    return dems

def generate_grid_with_points(area_file, target_points, sampler=None, utm=None):
    """
    Tries to generate a grid of demand points with roughly target_points demand points
    the answer may not be exact

    :param area_file: a string path to a kml file representing the area to put demand points

    :param target_points: the target number of demand points, may not be exact

    :param sampler: a geo sampler to use to fill the altitude column.
    If left None there will be no altitude column

    :param utm: a crs for the area. If none is provided then the area_file's
    crs is used, which may mean that granularity will no longer be meters

    
    :returns: a GeoDataFrame of the demand points
    """
    tolerance = 5
    area_frame = _load_file(area_file, utm)

    # Generate points
    minx, miny, maxx, maxy = area_frame.total_bounds
    hi_granularity = 0.25 * min(maxx - minx, maxy - miny)
    hi_dems = _make_grid(area_frame, hi_granularity)
    if len(hi_dems) >= target_points:
        return add_alts(hi_dems, sampler)

    lo_granularity = 0.5 * hi_granularity
    lo_dems = _make_grid(area_frame, lo_granularity)
    while len(lo_dems) <= target_points:
        lo_granularity *= 0.5
        lo_dems = _make_grid(area_frame, lo_granularity)

    while len(hi_dems) + tolerance <= len(lo_dems):
        mid_granularity = (lo_granularity + hi_granularity) / 2
        mid_dems = _make_grid(area_frame, mid_granularity)

        if len(mid_dems) == target_points:
            break
        elif len(mid_dems) < target_points:
            hi_granularity = mid_granularity
            hi_dems = _make_grid(area_frame, hi_granularity)
        else:
            lo_granularity = mid_granularity
            lo_dems = _make_grid(area_frame, lo_granularity)

    mid_granularity = (lo_granularity + hi_granularity) / 2
    mid_dems = _make_grid(area_frame, mid_granularity)
    
    return add_alts(mid_dems, sampler)
