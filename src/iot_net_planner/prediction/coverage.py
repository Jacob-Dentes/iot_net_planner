"""
Tools for predicting how much coverage a solution provides
"""

import numpy as np

def get_coverage(sol, prr, min_weight=0.0):
    """
    Returns the coverage for building indices `sol` as preddicted by `prr`

    :param sol: an iterable of indices into prr indicating what to build

    :param prr: a prr model initialized with demand points and facilities indexed in the same way as sol

    :param min_weight: returns (average coverage) * (1 - min_weight) + (worst coverage) * (min_weight).
    The default is 0.0, meaning only the predicted average is returned

    :returns: The predicted coverage 
    """
    if len(sol) == 0:
        return 0.0

    coverages = [prr.get_prr(i) for i in sol]

    # Compute the coverage at each demand point
    dem_coverage = np.ones(len(coverages[0]))
    for cov in coverages:
        # The chance of failure is 1 - prr, so we multiply chances
        # of failure to get chance they all fail
        dem_coverage = dem_coverage * (1 - cov)
    # The chance if success is 1 - chance of failure
    dem_coverage = 1 - dem_coverage

    return (1 - min_weight) * np.mean(dem_coverage) + (min_weight) * np.min(dem_coverage)
