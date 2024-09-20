"""Tools for plotting coverage. This module does not compute coverage, it only displays it
"""

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import contextily as ctx
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from shapely.geometry import Polygon, Point

def plot_fac_coverage(dems, facs, fac, contributions, save_to=None):
    """Creates and shows a matplotlib plot showing the coverage from fac to all of dems

    :param dems: a GeoDataFrame of the demand points to show coverage of
    :type dems: gpd.GeoDataFrame
    :param facs: a GeoDataFrame of the facility points to show covverage from
    :type facs: gpd.GeoDataFrame
    :param fac: the index into facs representing the facility point to graph
    :type fac: int
    :param contributions: a numpy array of the contributions to each of the demand points 
        with len(contributions) == len(dems). Look into predictions.prr_model for generating predictions
    :type contributions: np.ndarray
    :param save_to: is None will show the plot, otherwise it is the path to save the file to,
        defaults to None
    :type save_to: str, optional
    """
    return plot_facs_coverage(dems, facs, [fac], contributions, save_to)
    
def plot_facs_coverage(dems, facs, built, contributions, save_to=None):
    """Creates and shows a matplotlib plot showing the coverage from fac to all of dems

    :param dems: a GeoDataFrame of the demand points to show coverage of
    :type dems: gpd.GeoDataFrame
    :param facs: a GeoDataFrame of the facility points to show covverage from
    :type facs: gpd.GeoDataFrame
    :param built: a list of the indices into facs representing the facility points to graph
    :type built: list
    :param contributions: a numpy array of the contributions to each of the demand points 
        with len(contributions) == len(dems). Look into predictions.prr_model for generating predictions
    :type contributions: np.ndarray
    :param save_to: is None will show the plot, otherwise it is the path to save the file to,
        defaults to None
    :type save_to: str, optional
    """
    dems = dems.to_crs(epsg=3857)
    facs = facs.to_crs(epsg=3857)
    contributions = contributions.clip(0.0, 1.0)
    fig, ax = plt.subplots(1, 1, figsize=(8, 8))

    def get_color(contribution):
        if contribution < 0.5:
            return (1.0, contribution * 2.0, 0.0)
        else:
            return ((1.0 - contribution) * 2, 1.0, 0.0)

    colors = [get_color(c) for c in contributions]
   
    dems.plot(ax=ax, color=colors, alpha=0.3, markersize=5.0)
    facs.iloc[built].plot(ax=ax, color='magenta', alpha=1.0)
    
    ctx.add_basemap(ax, crs=dems.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)
    
    norm = Normalize(vmin=0.0, vmax=1.0)
    sm = ScalarMappable(cmap='RdYlGn', norm=norm)
    sm.set_array([])

    cbar = plt.colorbar(sm, ax=ax, orientation='vertical')
    cbar.set_label('Contributions', rotation=270, labelpad=15)
    cbar.set_ticks([0.0, 0.5, 1.0])
    cbar.set_ticklabels(['0.0', '0.5', '1.0'])    

    if save_to is None:
        plt.show()
    else:
        plt.savefig(save_to)
    

def plot_demands(dems, save_to=None):
    """Creates and shows a matplotlib plot showing the demand points in dems

    :param dems: a GeoDataFrame of the demand points to show in the plot
    :type dems: gpd.GeoDataFrame
    :param save_to: is None will show the plot, otherwise it is the path to save the file to,
        defaults to None
    :type save_to: str, optional
    """
    dems = dems.to_crs(epsg=3857)
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))

    dems.plot(ax=ax, color='magenta', alpha=0.3)
    
    ctx.add_basemap(ax, crs=dems.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)

    if save_to is None:
        plt.show()
    else:
        plt.savefig(save_to)

def plot_facs(facs, save_to=None):
    """Creates and shows a matplotlib plot showing the facility points in facs

    :param facs: a GeoDataFrame of the facility points to show in the plot
    :type facs: gpd.GeoDataFrame
    :param save_to: is None will show the plot, otherwise it is the path to save the file to,
        defaults to None
    :type save_to: str, optional
    """
    plot_demands(facs, save_to)

def plot_facs_coverage_hex(dems, facs, built, contributions, grid_granularity=300/0.3048):
    dems = dems.to_crs(dems.estimate_utm_crs())
    facs = facs.to_crs(epsg=3857)
    
    fig, ax = plt.subplots(figsize=(9, 9))

    def get_color(contribution):
        if contribution < 0.5:
            return (1.0, contribution * 2.0, 0.0)
        else:
            return ((1.0 - contribution) * 2, 1.0, 0.0)

    dems = dems.copy()
    dems['colors'] = contributions

    ## make grid
    xmin, ymin, xmax, ymax = dems.total_bounds
    length, wide = [grid_granularity] * 2

    cols = list(np.arange(xmin, xmax + wide, 3/4 * wide))
    rows = list(np.arange(ymin, ymax + length, length))

    def hex_coords(center, vert_offset=0.0):
        coords = []
        angle = np.deg2rad(np.arange(0.0, 301.0, 60.0))
        cos_angle = np.cos(angle)
        sin_angle = np.sin(angle)
        x_coords = np.repeat(center[0], 6) + (wide / 2) * cos_angle
        y_coords = np.repeat(center[1], 6) + (length / np.sqrt(3.0)) * sin_angle
        y_coords = y_coords + vert_offset
        return [(x_coords[i], y_coords[i]) for i in range(6)]

    polygons = []
    for col_idx, x in enumerate(cols[:-1]):
        for y in rows[:-1]:
            vert_offset = 0.0 if col_idx % 2 == 0 else wide / 2
            polygons.append(Polygon(hex_coords((x,y), vert_offset)))

    grid = gpd.GeoDataFrame({'geometry':polygons}, crs=dems.crs)
    # grid.plot(ax=ax)

    joined = dems.sjoin(grid, how="inner", predicate="within")
    grouped = joined.groupby("index_right")["colors"].mean().reset_index()

    result = grid.merge(grouped, left_index=True, right_on="index_right", how="left")
    result = result.rename(columns={"colors": "average_color"}).drop("index_right", axis=1)

    result = result[result["average_color"].notna()]
    color = np.array([get_color(c) for c in result['average_color']])

    dems = dems.to_crs(epsg=3857)
    result = result.to_crs(epsg=3857)
    dems.plot(ax=ax, alpha=0.0)
    ctx.add_basemap(ax, crs=dems.crs, source=ctx.providers.OpenStreetMap.Mapnik)
    
    norm = Normalize(vmin=0.0, vmax=1.0)
    sm = ScalarMappable(cmap='RdYlGn', norm=norm)
    sm.set_array([])

    cbar = plt.colorbar(sm, ax=ax, orientation='vertical')
    cbar.set_label('Contributions', rotation=270, labelpad=15)
    cbar.set_ticks([0.0, 0.5, 1.0])
    cbar.set_ticklabels(['0.0', '0.5', '1.0'])    

    # ax.figure.colorbar(sm, ax=ax)
    result.plot(ax=ax, alpha=0.3, color=color)#, edgecolor="black")
    facs.iloc[built].plot(ax=ax, markersize=10, c='magenta')
    plt.show()
