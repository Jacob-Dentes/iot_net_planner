"""Tools for plotting coverage. This module does not compute coverage, it only displays it
"""

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import contextily as ctx
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable

def plot_fac_coverage(dems, facs, fac, contributions):
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
    """
    return plot_facs_coverage(dems, facs, [fac], contributions)
    
def plot_facs_coverage(dems, facs, built, contributions):
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
   
    dems.plot(ax=ax, color=colors, alpha=0.3)
    facs.iloc[built].plot(ax=ax, color='magenta', alpha=1.0)
    
    ctx.add_basemap(ax, crs=dems.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)
    
    norm = Normalize(vmin=0.0, vmax=1.0)
    sm = ScalarMappable(cmap='RdYlGn', norm=norm)
    sm.set_array([])

    cbar = plt.colorbar(sm, ax=ax, orientation='vertical')
    cbar.set_label('Contributions', rotation=270, labelpad=15)
    cbar.set_ticks([0.0, 0.5, 1.0])
    cbar.set_ticklabels(['0.0', '0.5', '1.0'])    

    plt.show()
    

def plot_demands(dems):
    """Creates and shows a matplotlib plot showing the demand points in dems

    :param dems: a GeoDataFrame of the demand points to show in the plot
    :type dems: gpd.GeoDataFrame
    """
    dems = dems.to_crs(epsg=3857)
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))

    dems.plot(ax=ax, color='magenta', alpha=0.3)
    
    ctx.add_basemap(ax, crs=dems.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)

    plt.show()

def plot_facs(facs):
    """Creates and shows a matplotlib plot showing the facility points in facs

    :param facs: a GeoDataFrame of the facility points to show in the plot
    :type facs: gpd.GeoDataFrame
    """
    plot_demands(facs)
