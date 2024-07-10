import numpy as np
from pyscipopt import Model, quicksum

from iot_net_planner.optimization.opt_coverage_model import OPTCoverageModel

class SCIPModel(OPTCoverageModel):
    @staticmethod
    def solve_coverage(budget, min_weight, dems, facs, prr, logging=True):
        """
        Solve a CIP with full sampling  
        """
        rlen = lambda l: range(len(l))
        f = facs['cost'].to_numpy()
   
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
