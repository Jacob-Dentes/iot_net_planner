"""
An abstract class for an optimization model that solves for maximum coverage
"""
from abc import ABC, abstractmethod

class OPTCoverageModel(ABC):
    @staticmethod
    @abstractmethod
    def solve_coverage(budget, min_weight, dems, facs, prr, logging=True):
        pass
