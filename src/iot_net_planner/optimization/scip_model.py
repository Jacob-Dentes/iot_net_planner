import numpy as np
from pyscipopt import Model, quicksum

from iot_net_planner.optimization.opt_coverage_model import OPTCoverageModel

class SCIPModel(OPTCoverageModel):
    @staticmethod
    def solve_coverage(budget, min_weight, dems, facs, prr, blob_size=10, logging=True):
        """Solves a CIP for coverage

        :param budget: The maximum allowable amount to spend
        :type budget: float
        :param min_weight: The objective is min_weight * worst coverage + (1 - min_weight) * average coverage
        :type min_weight: float
        :param dems: a GeoDataFrame of the demand points
        :type dems: gpd.GeoDataFrame
        :param facs: a GeoDataFrame for the potential gateways. It should have a 'cost'
            field representing how much each gateway costs (pricing is relative)
        :type facs: gpd.GeoDataFrame
        :param prr: A CachedPRRModel initialized with dems and facs
        :type prr: `iot_net_planner.prediction.prr_cache.CachedPRRModel`
        :param blob_size: the number of points in an indexact blob, defaults to 10
        :type blob_size: int, optional
        :param logging: whether to log, defaults to True
        :type logging: bool, optional
        :return: a set of indices of facs to build
        :rtype: set
        """
        rlen = lambda l: range(len(l))
        f = facs['cost'].to_numpy()

        prr = OPTCoverageModel._blobify(facs, prr, blob_size)
   
        # Get a matrix with contributions
        A = np.empty((len(dems), len(facs)))

        for i in rlen(facs):
            if logging:
                print(f" {i+1} / {len(dems)}", end="\r")
            A[:, i] = prr.get_prr(i)
        prrs = A
        A = -1 * np.log(1 - A)
    
        m = Model("CIP")
        m.hideOutput(not logging)
        x = {i: m.addVar(vtype='B', lb=facs['built'][i]) for i in rlen(facs)}

        m.addCons(quicksum(f[i] * x[i] for i in x) <= budget) # Stay under budget

        min_cov = m.addVar(lb=None) # The coverage at the least covered point

        total_coverage_terms = []
        for i in rlen(dems):
            m.addCons(quicksum(A[i, j] * x[j] for j in x) >= min_cov)
            total_coverage_terms += [A[i, j] * x[j] for j in x]

        scalar = (2 * m.feastol()) / np.median(np.abs(prrs)[np.abs(prrs) > 0])
    
        avg_term = scalar * ((1 - min_weight) / len(dems)) * quicksum(total_coverage_terms)
        min_term = scalar * min_weight * min_cov
        m.setObjective(avg_term + min_term, "maximize")

        m.optimize()

        sol = {i for i in x if m.getVal(x[i]) > 0.9}
        if logging:
            print(sol)

        return sol
