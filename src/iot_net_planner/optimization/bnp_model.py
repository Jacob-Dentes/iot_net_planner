"""Uses branch and bound to solve an optimization input
"""

import numpy as np
from pyscipopt import Model, quicksum, Pricer, SCIP_RESULT, SCIP_PARAMSETTING

from iot_net_planner.optimization.opt_coverage_model import OPTCoverageModel

class ColPricer(Pricer):
    def pricerredcost(self):
        qinc = self.data['qinc']
        logify = lambda arr: -1 * np.log(1 - arr)

        def add_var(contributions, fac):
            # add variable
            var = self.model.addVar(vtype='B', obj = self.data['obj_weight'] * contributions.sum(), pricedVar=True)
            # add budget constraint
            self.model.addConsCoeff(self.data['budget_con'], var, -1 * self.data['f'][fac])
            # add coverage constraints
            for i, c in enumerate(self.data['min_coverage_cons']):
                self.model.addConsCoeff(c, var, -1 * contributions[i])
            return var

        def remove_var(var):
            self.model.fixVar(var, 0.0)

        def check_ub(fac, q=0.0):
            # Check if we already have a variable with this accuracy
            if q <= self.data['quantiles'][fac] + 1e-12 and fac in self.data['q_vars']:
                return self.model.getVarRedcost(self.data['q_vars'][fac])

            # Improve ub to quantile q
            self.data['prr'].improve_ub(fac, q)

            # Add variable, get its reduced cost
            contributions = logify(self.data['prr'].get_prr_ub(fac))
            var = add_var(contributions, fac)
            redcost = self.model.getVarRedcost(var)

            # Cache variable
            self.data['q_vars'][fac] = var
            self.data['quantiles'][fac] = q

            # Remove variable
            remove_var(var)
            return redcost

        # Find best reduced cost for each facility
        ubs = []
        for fac in self.data['frontier']:
            redcost = check_ub(fac)
            ubs.append((fac, redcost))
        ubs.sort(key=lambda v: v[1])

        # Look for exact prr with reduced cost
        for fac, ub in [(fac, ub) for fac, ub in ubs if self.model.isLT(ub, 0)]:
            # Improve bound to exact (TODO: incrementally improve bounds)
            set_to_check = set(np.arange(self.data['quantiles'][fac] + qinc, 1.0, qinc))
            set_to_check.add(1.0)
            for q in sorted(list(set_to_check)):
                redcost = check_ub(fac, q)
                if self.data['log']:
                    print(f"Improving {fac} bound to quantile {q} yielded {redcost}")
                if self.model.isGT(redcost, 0.0):
                    break
            else:
                exacts = logify(self.data['prr'].get_prr(fac))
                # exacts = logify(self.data['prr'].exact_prrs(fac))
                var = add_var(exacts, fac)
                self.data['frontier'] = self.data['frontier'][self.data['frontier'] != fac]
                self.data['x'][fac] = var
                redcost = self.model.getVarRedcost(var)
                if self.data['log']:
                    print(f'Found fac {fac} with red-cost {redcost}')
                break
        return {'result': SCIP_RESULT.SUCCESS}        

    def pricerinit(self):
        self.data['budget_con'] = self.model.getTransformedCons(self.data['budget_con'])
        for i, c in enumerate(self.data['min_coverage_cons']):
            self.data['min_coverage_cons'][i] = self.model.getTransformedCons(c)
         
class BNPModel(OPTCoverageModel):
    @staticmethod
    def solve_coverage(budget, min_weight, dems, facs, prr, qinc=1.0, logging=True):
        """Solves a CIP for coverage with branch and price

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
        :return: a set of indices of facs to build
        :rtype: set
        """
        rlen = lambda l: range(len(l))
        f = facs['cost'].to_numpy() 
   
        # Get a matrix with lower bounded contributions
        A = np.empty((len(dems), len(facs)))

        for i in rlen(facs):
            A[:, i] = prr.get_prr_lb(i)
        prrs = A
        A = -1 * np.log(1 - A)

        # Solve the initial IP with lower bounds to ensure feasibility
        m = Model("Initial CIP")
        m.hideOutput(True)
        x = [m.addVar(vtype='B', lb=facs['built'][i]) for i in rlen(facs)]

        m.addCons(quicksum(-1 * f[i] * x[i] for i in rlen(facs)) >= -1 * budget) # Stay under budget

        min_cov = m.addVar(lb=None) # The coverage at the least covered point

        total_coverage_terms = []
        for i in rlen(dems):
            m.addCons(quicksum(A[i, j] * x[j] for j in rlen(facs)) >= min_cov)
            total_coverage_terms += [A[i, j] * x[j] for j in rlen(facs)]

        scalar = (2 * m.feastol()) / np.median(np.abs(prrs)[np.abs(prrs) > 0])
    
        avg_term = scalar * ((1 - min_weight) / len(dems)) * quicksum(total_coverage_terms)
        min_term = scalar * min_weight * min_cov
        m.setObjective(avg_term + min_term, "maximize")

        m.optimize()
        if logging:
            print("Found a lower bound primal. Computing exact prrs...")
        primal = np.array([round(m.getVal(var)) for var in x]) # Solution to the lower-bounded problem

        # Get exact contributions for the basic variables
        A = np.empty((len(dems), primal.sum()))
        basics = [i for i in rlen(facs) if primal[i] > 0.9]
        nonbasics = [i for i in rlen(facs) if primal[i] <= 0.9]
        for i, basic in enumerate(basics):
            if logging:
                print(f" {i+1} / {len(basics)}", end="\r")
            A[:, i] = prr.get_prr(basic)
        A = -1 * np.log(1 - A)

        if logging:
            print(f"Computed exact prrs. Beginning branch and price...")

        m = Model("BnP CIP")
        m.hideOutput(not logging)
        m.setPresolve(0)
        m.setIntParam("propagating/rootredcost/freq", -1)

        pricer = ColPricer()
        m.includePricer(pricer, "CIPPricer", "Pricer to identify new gateway locations.")

        x = {basics[i]: m.addVar(f'Fac: {basics[i]}', vtype='B', lb=facs['built'][i]) for i in range(A.shape[1])}
        budget_cons = m.addCons(quicksum(-1 * f[i] * x[i] for i in x) >= -1 * budget, modifiable=True, separate=False)

        min_cov = m.addVar('MinCov', lb=None)

        total_coverage_terms = []
        min_coverage_cons = []
        for i in rlen(dems):
            min_coverage_cons.append(m.addCons(quicksum(A[i, k] * x[j] for k, j in enumerate(x)) >= min_cov, modifiable=True, separate=False))
            total_coverage_terms += [A[i, k] * x[j] for k, j in enumerate(x)]

        avg_obj_weights = -1 * scalar * ((1 - min_weight) / len(dems))
        min_obj_weight = -1 * scalar * min_weight

        avg_term = avg_obj_weights * quicksum(total_coverage_terms)
        min_term = min_obj_weight * min_cov
        m.setObjective(avg_term + min_term, "minimize")

        pricer.data = {}
        pricer.data['frontier'] = np.array(nonbasics)
        pricer.data['quantiles'] = {i: 0.0 for i in nonbasics}
        pricer.data['budget_con'] = budget_cons
        pricer.data['min_coverage_cons'] = min_coverage_cons
        pricer.data['obj_weight'] = avg_obj_weights
        pricer.data['min_obj_weight'] = min_obj_weight
        pricer.data['f'] = f
        pricer.data['x'] = x
        pricer.data['prr'] = prr
        pricer.data['log'] = logging
        pricer.data['qinc'] = qinc
        pricer.data['q_vars'] = {}

        m.optimize()

        sol = {i for i in pricer.data['x'] if m.getVal(pricer.data['x'][i]) > 0.9}
        if logging:
            print(f"Found optimum")
            print(sol)

        return sol
