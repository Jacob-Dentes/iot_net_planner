"""
Tools for plotting coverage. This module does not compute coverage, it only displays it
"""

import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import contextily as ctx

def plot_fac_coverage(dems, facs, fac, contributions):
    """
    Creates and shows a matplotlib plot showing the coverage from fac to all of dems

    :param dems: a GeoDataFrame of the demand points to show coverage of

    :param facs: a GeoDataFrame of the facility points to show covverage from

    :param fac: the index into facs representing the facility point to graph

    :param contributions: a numpy array of the contributions to each of the demand points 
    with len(contributions) == len(dems). Look into predictions.prr_model for generating predictions
    """
    return plot_facs_coverage(dems, facs, [fac], contributions)
    
def plot_facs_coverage(dems, facs, built, contributions):
    """
    Creates and shows a matplotlib plot showing the coverage from fac to all of dems

    :param dems: a GeoDataFrame of the demand points to show coverage of

    :param facs: a GeoDataFrame of the facility points to show covverage from

    :param built: a list of the indices into facs representing the facility points to graph

    :param contributions: a numpy array of the contributions to each of the demand points 
    with len(contributions) == len(dems). Look into predictions.prr_model for generating predictions
    """
    contributions = contributions.clip(0.0, 1.0)
    fig, ax = plt.subplots(1, 1, figsize=(8, 8))

    norm = plt.Normalize(vmin=0.0, vmax=1.0)
   
    colors = [(1, 0, 0), (1, 1, 0), (0, 1, 0)]  # Red to Yellow to Green
    cmap = mcolors.LinearSegmentedColormap.from_list('RedYellowGreen', colors)

    dems.plot(ax=ax, color=cmap(norm(contributions)), alpha=0.3)
    facs.iloc[built].plot(ax=ax, color='magenta', alpha=1.0)
    
    ctx.add_basemap(ax, crs=dems.crs.to_string())
    
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, orientation='vertical')
    cbar.set_label('Contributions')
    
    plt.show()
    

def plot_demands(dems):
    """
    Creates and shows a matplotlib plot showing the demand points in dems

    :param dems: a GeoDataFrame of the demand points to show in the plot
    """
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))

    dems.plot(ax=ax, color='magenta', alpha=0.3)
    
    ctx.add_basemap(ax, crs=dems.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)

    plt.show()
