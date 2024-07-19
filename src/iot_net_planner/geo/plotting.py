import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import contextily as ctx

def plot_fac_coverage(dems, facs, fac, contributions):
    return plot_facs_coverage(dems, facs, [fac], contributions)
    
def plot_facs_coverage(dems, facs, built, contributions):
    contributions = contributions.clip(0.0, 1.0)
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))

    norm = plt.Normalize(vmin=0.0, vmax=1.0)
    cmap = plt.cm.Reds

    dems.plot(ax=ax, color=cmap(norm(contributions)), alpha=0.3)
    facs.iloc[built].plot(ax=ax, color='magenta', alpha=1.0)
    
    ctx.add_basemap(ax, crs=dems.crs.to_string())
    
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, orientation='vertical')
    cbar.set_label('Contributions')
    
    plt.show()
    

def plot_demands(dems):
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))

    dems.plot(ax=ax, color='magenta', alpha=0.3)
    
    ctx.add_basemap(ax, crs=dems.crs.to_string())

    plt.show()
