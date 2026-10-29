"""
Módulo de representación de individuos para el algoritmo genético.
Soporta dimensiones arbitrarias (1D hasta n-D).
"""
from typing import List, Tuple, Any, Union
import numpy as np

class Individual:
    """
    Representa un individuo de la población evolutiva.
    En funciones de n dimensiones, 'genes' es un vector de longitud n.
    """
    def __init__(self, genes: Union[np.ndarray, list], bounds: List[Tuple[float, float]] = None):
        self.genes = np.array(genes, dtype=float)
        if bounds is not None:
            self.bounds = list(bounds)
        else:
            self.bounds = [(-10.0, 10.0)] * len(self.genes)

        self.objective_value: float = float('nan') # f(x) real
        self.fitness: float = 0.0                  # Aptitud positiva para selección
        self.rank: int = 1                         # Rango (1 = mejor)
        self.selection_prob: float = 0.0           # Probabilidad asignada por métodos de selección

    @property
    def x(self) -> Any:
        """
        Retorna el fenotipo. Si la dimensión es 1, retorna float.
        Si la dimensión es > 1, retorna el array de genes.
        """
        if len(self.genes) == 1:
            return float(self.genes[0])
        return self.genes

    @property
    def x_list(self) -> List[float]:
        """Retorna las coordenadas como lista de flotantes serializables."""
        return [float(g) for g in self.genes]

    @property
    def x_formatted(self) -> str:
        """Representación en cadena legible para la interfaz gráfica."""
        if len(self.genes) == 1:
            return f"{float(self.genes[0]):.6f}"
        elif len(self.genes) <= 4:
            vals = ", ".join(f"{g:.4f}" for g in self.genes)
            return f"[{vals}]"
        else:
            first_two = ", ".join(f"{g:.3f}" for g in self.genes[:2])
            last_one = f"{self.genes[-1]:.3f}"
            return f"[{first_two}, ..., {last_one}] (dim {len(self.genes)})"

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
        return f"Individual(x={self.x_formatted}, f(x)={self.objective_value:.5f}, fitness={self.fitness:.5f})"
