"""
A tool for filling holes in a DSM using interpolation
"""

import rasterio
import numpy as np
from rasterio.fill import fillnodata

def fill_file(input_file, output_file, band, threshold=-9000):
    """
    Interpolate a DSM file to fill in holes

    :param input_file: a path to the DSM

    :param output_file: the path to save the modified DSM

    :param band: the 1-indexed band number to modify from the DSM

    :param threshold: values below this threshold will be interpolated
    """
    with rasterio.open(input_file) as src:
        file_band = src.read(band)
    
        mask = file_band >= threshold   
        filled_band = fillnodata(file_band, mask=mask, max_search_distance=10_000.0, smoothing_iterations=0)
    
        profile = src.profile
        profile.update(count=1)
        with rasterio.open(output_file, 'w', **profile) as dst:
            dst.write(filled_band, 1)


