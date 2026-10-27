"""
Gestión y evaluación de la población.
Conversión de f(x) a aptitud positiva (fitness) para Minimización y Maximización.
"""
from typing import List, Tuple, Callable
import numpy as np
from .individual import Individual

class Population:
    def __init__(self, size: int, bounds: List[Tuple[float, float]], seed: int = None):
        self.size = size
        self.bounds = bounds
        if seed is not None:
            np.random.seed(seed)
        self.individuals: List[Individual] = []
        self._initialize()

    def _initialize(self):
        """Inicializa los individuos uniformemente dentro de los límites de búsqueda."""
        self.individuals = []
        for _ in range(self.size):
            genes = []
            for lb, ub in self.bounds:
                genes.append(np.random.uniform(lb, ub))
            ind = Individual(np.array(genes), self.bounds)
            self.individuals.append(ind)

    def evaluate(self, eval_func: Callable[[float], float], goal: str = "minimize") -> int:
        """
        Evalúa f(x) para cada individuo y calcula su fitness positivo y rango.
        Retorna el número de evaluaciones realizadas.
        """
        n_evals = 0
        obj_values = []
        for ind in self.individuals:
            val = eval_func(ind.x)
            ind.objective_value = val
            obj_values.append(val)
            n_evals += 1

        obj_arr = np.array(obj_values, dtype=float)
        
        # Asignar rangos (1 = mejor)
        if goal == "minimize":
            sorted_indices = np.argsort(obj_arr) # Menor f(x) es mejor
        else:
            sorted_indices = np.argsort(-obj_arr) # Mayor f(x) es mejor

        for rank, idx in enumerate(sorted_indices, start=1):
            self.individuals[idx].rank = rank

        # Calcular fitness positivo para ruleta y operadores proporcionales
        min_v = np.min(obj_arr)
        max_v = np.max(obj_arr)
        span = max_v - min_v

        eps = 1e-6
        for ind in self.individuals:
            if goal == "minimize":
                # A menor f(x), mayor fitness
                if span > 1e-12:
                    ind.fitness = float(max_v - ind.objective_value + (span * 0.05))
                else:
                    ind.fitness = 1.0
            else:
                # A mayor f(x), mayor fitness
                if span > 1e-12:
                    ind.fitness = float(ind.objective_value - min_v + (span * 0.05))
                else:
                    ind.fitness = 1.0

            if ind.fitness <= 0 or np.isnan(ind.fitness):
                ind.fitness = eps

        return n_evals

    def best_individual(self, goal: str = "minimize") -> Individual:
        """Retorna el mejor individuo de la población según el objetivo."""
        if goal == "minimize":
            return min(self.individuals, key=lambda ind: ind.objective_value)
        else:
            return max(self.individuals, key=lambda ind: ind.objective_value)

    def stats(self, goal: str = "minimize") -> dict:
        """Calcula estadísticas numéricas de la población actual."""
        obj_vals = np.array([ind.objective_value for ind in self.individuals])
        fits = np.array([ind.fitness for ind in self.individuals])
        best_ind = self.best_individual(goal)

        return {
            "best_x": float(best_ind.x),
            "best_fx": float(best_ind.objective_value),
            "best_fitness": float(best_ind.fitness),
            "mean_fx": float(np.mean(obj_vals)),
            "std_fx": float(np.std(obj_vals)),
            "mean_fitness": float(np.mean(fits)),
            "min_fx": float(np.min(obj_vals)),
            "max_fx": float(np.max(obj_vals))
        }
