"""
Módulo de representación de individuos para el algoritmo genético.
"""
from typing import List, Tuple, Any
import numpy as np

class Individual:
    """
    Representa un individuo de la población evolutiva.
    En funciones univariadas, el fenotipo 'x' corresponde a genes[0].
    """
    def __init__(self, genes: np.ndarray, bounds: List[Tuple[float, float]] = None):
        self.genes = np.array(genes, dtype=float)
        self.bounds = bounds if bounds is not None else [(-10.0, 10.0)]
        self.objective_value: float = float('nan') # f(x) real
        self.fitness: float = 0.0                  # Aptitud positiva para selección
        self.rank: int = 1                         # Rango (1 = mejor)
        self.selection_prob: float = 0.0           # Probabilidad asignada por métodos de selección

    @property
    def x(self) -> float:
        """Fenotipo correspondiente a la primera variable independiente."""
        return float(self.genes[0])

    def clamp_bounds(self):
        """Asegura que todos los genes se encuentren dentro de sus límites [LB, UB]."""
        for i, (lb, ub) in enumerate(self.bounds):
            if i < len(self.genes):
                self.genes[i] = np.clip(self.genes[i], lb, ub)

    def copy(self) -> 'Individual':
        ind = Individual(self.genes.copy(), self.bounds.copy() if self.bounds else None)
        ind.objective_value = self.objective_value
        ind.fitness = self.fitness
        ind.rank = self.rank
        ind.selection_prob = self.selection_prob
        return ind

    def __repr__(self) -> str:
        return f"Individual(x={self.x:.5f}, f(x)={self.objective_value:.5f}, fitness={self.fitness:.5f})"
