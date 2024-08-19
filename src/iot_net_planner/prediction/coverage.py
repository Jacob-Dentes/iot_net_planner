"""Tools for predicting how much coverage a solution provides
"""

import numpy as np

def get_coverages(sol, prr):
    """Returns the coverage for building indices sol as predicted by prr

    :param sol: an iterable of indices into prr indicating what to build
    :type sol: list
    :param prr: a prr model initialized with demand points and facilities
        indexed in the same way as sol
    :type prr: class: `iot_net_planner.prediction.prr_model.PRRModel`
    :return: a numpy array of the coverage for each demand point
    :rtype: np.ndarray
    """
    coverages = [prr.get_prr(i) for i in sol]

    # Compute the coverage at each demand point
    dem_coverage = np.ones(len(coverages[0]))
    for cov in coverages:
        # The chance of failure is 1 - prr, so we multiply chances
        # of failure to get chance they all fail
        dem_coverage = dem_coverage * (1 - cov)
    # The chance if success is 1 - chance of failure
    dem_coverage = 1 - dem_coverage

    return dem_coverage
    

def get_coverage_scalar(sol, prr, min_weight=0.0):
    """Returns the coverage for building indices sol as predicted by prr

    :param sol: an iterable of indices into prr indicating what to build
    :type sol: list
    :param prr: a prr model initialized with demand points and facilities
        indexed in the same way as sol
    :type prr: class: `iot_net_planner.prediction.prr_model.PRRModel`
    :param min_weight: returns (average coverage) * (1 - min_weight) + (worst coverage) * (min_weight).
        For example, 0.0 means only average coverage is returned, defaults to 0.0.
    :type min_weight: float
    :return: the predicted coverage 
    :rtype: float
    """
    if len(sol) == 0:
        return 0.0

    dem_coverage = get_coverages(sol, prr)

    return (1 - min_weight) * np.mean(dem_coverage) + (min_weight) * np.min(dem_coverage)
