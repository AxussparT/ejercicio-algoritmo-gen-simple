"""
Motor principal del Algoritmo Genético (Genetic Algorithm Engine).
Controla el ciclo evolutivo, estadísticas generacionales y ejecución asíncrona.
"""
import time
from typing import Callable, Dict, Any, List, Optional, Tuple
import numpy as np

from .individual import Individual
from .population import Population
from .evaluator import SafeEvaluator
from .selection import (
    roulette_wheel_selection,
    linear_ranking_selection,
    non_linear_ranking_selection,
    tournament_selection,
    stochastic_universal_sampling
)
from .crossover import (
    uniform_crossover,
    arithmetic_crossover,
    flat_crossover,
    blx_alpha_crossover,
    pmx_crossover,
    ox_crossover,
    cx_crossover
)
from .mutation import (
    uniform_mutation,
    non_uniform_mutation,
    swap_mutation
)
from .replacement import (
    generational_replacement_with_elitism,
    steady_state_replacement,
    crowding_replacement
)

class GAEngine:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.is_running = False
        self.is_paused = False
        self.stop_requested = False

        # Extraer parámetros básicos
        self.pop_size = int(config.get("pop_size", 40))
        self.max_generations = int(config.get("max_generations", 60))
        self.bounds = config.get("bounds", [(-10.0, 10.0)])
        self.goal = config.get("goal", "minimize")
        self.seed = config.get("seed", None)
        
        # Probabilidades
        self.pc = float(config.get("pc", 0.8))
        self.pm = float(config.get("pm", 0.1))

        # Métodos seleccionados
        self.selection_method = config.get("selection_method", "Torneo")
        self.selection_params = config.get("selection_params", {})

        self.crossover_method = config.get("crossover_method", "BLX-α")
        self.crossover_params = config.get("crossover_params", {})

        self.mutation_method = config.get("mutation_method", "Uniforme")
        self.mutation_params = config.get("mutation_params", {})

        self.replacement_method = config.get("replacement_method", "Generacional con elitismo")
        self.replacement_params = config.get("replacement_params", {})

        # Evaluador de función
        expression = config.get("expression", "x**2")
        self.evaluator = SafeEvaluator(expression)

        # Historial y resultados
        self.history = []
        self.best_global_individual: Optional[Individual] = None
        self.best_global_generation: int = 0
        self.total_evaluations: int = 0
        self.execution_time: float = 0.0

    def _select_parents(self, population: List[Individual], n_needed: int) -> List[Individual]:
        method = self.selection_method
        p = self.selection_params

        if method == "Ruleta proporcional":
            return roulette_wheel_selection(population, n_needed)
        elif method == "Ranking lineal":
            a_max = float(p.get("a_max", 1.6))
            return linear_ranking_selection(population, n_needed, a_max=a_max)
        elif method == "Ranking no lineal":
            q = float(p.get("q", 0.5))
            return non_linear_ranking_selection(population, n_needed, q=q)
        elif method == "Torneo":
            k = int(p.get("k", 2))
            return tournament_selection(population, n_needed, k=k)
        elif method == "Muestreo estocástico universal":
            return stochastic_universal_sampling(population, n_needed)
        else:
            return tournament_selection(population, n_needed, k=2)

    def _crossover_pair(self, p1: Individual, p2: Individual) -> Tuple[Individual, Individual]:
        if np.random.rand() > self.pc:
            return p1.copy(), p2.copy()

        method = self.crossover_method
        p = self.crossover_params

        if method == "Uniforme":
            return uniform_crossover(p1, p2, p_mask=float(p.get("p_mask", 0.5)))
        elif method == "Aritmético":
            return arithmetic_crossover(p1, p2, a=float(p.get("a", 0.25)))
        elif method == "Plano":
            return flat_crossover(p1, p2)
        elif method == "BLX-α":
            return blx_alpha_crossover(p1, p2, alpha=float(p.get("alpha", 0.5)))
        elif method == "PMX":
            return pmx_crossover(p1, p2)
        elif method == "OX":
            return ox_crossover(p1, p2)
        elif method == "CX":
            return cx_crossover(p1, p2)
        else:
            return blx_alpha_crossover(p1, p2, alpha=0.5)

    def _mutate_individual(self, ind: Individual, current_gen: int) -> Individual:
        method = self.mutation_method
        p = self.mutation_params

        if method == "Uniforme":
            return uniform_mutation(ind, p_mut=self.pm)
        elif method == "No uniforme":
            b = float(p.get("b", 1.0))
            return non_uniform_mutation(
                ind, 
                p_mut=self.pm, 
                current_gen=current_gen, 
                max_gen=self.max_generations, 
                b=b
            )
        elif method == "Por intercambio":
            return swap_mutation(ind, p_mut=self.pm)
        else:
            return uniform_mutation(ind, p_mut=self.pm)

    def _apply_replacement(self, current_pop: List[Individual], offspring: List[Individual]) -> List[Individual]:
        method = self.replacement_method
        p = self.replacement_params

        if method == "Steady-state":
            n_replace = int(p.get("n_replace", 2))
            return steady_state_replacement(current_pop, offspring, n_replace=n_replace)
        elif method == "Factor de crowding":
            cf = int(p.get("cf", 3))
            replace_if_better = bool(p.get("replace_if_better", False))
            return crowding_replacement(current_pop, offspring, crowding_factor=cf, replace_if_better=replace_if_better)
        else:
            # Generacional con elitismo
            n_elite = int(p.get("n_elite", 1))
            return generational_replacement_with_elitism(current_pop, offspring, n_elite=n_elite)

    def run(self, callback: Optional[Callable[[int, Dict[str, Any], Individual, List[Individual]], None]] = None) -> Dict[str, Any]:
        """
        Ejecuta el algoritmo genético de forma síncrona o en hilo secundario.
        Invoca callback(generation, stats, best_ind, population) en cada generación.
        """
        self.is_running = True
        self.stop_requested = False
        self.history = []
        start_time = time.time()

        if self.seed is not None:
            np.random.seed(int(self.seed))

        # 1. Crear y evaluar población inicial
        pop = Population(size=self.pop_size, bounds=self.bounds, seed=self.seed)
        self.total_evaluations += pop.evaluate(self.evaluator.evaluate, goal=self.goal)

        best_ind = pop.best_individual(goal=self.goal).copy()
        self.best_global_individual = best_ind.copy()
        self.best_global_generation = 0

        gen_stats = pop.stats(goal=self.goal)
        gen_stats["generation"] = 0
        gen_stats["evaluations"] = self.total_evaluations
        self.history.append(gen_stats)

        if callback:
            callback(0, gen_stats, self.best_global_individual, pop.individuals)

        # 2. Bucle generacional
        for gen in range(1, self.max_generations + 1):
            if self.stop_requested:
                break

            while self.is_paused and not self.stop_requested:
                time.sleep(0.05)

            # Generar descendientes
            offspring: List[Individual] = []
            
            # Si es Steady-State, necesitamos generar exactamente n_replace hijos
            if self.replacement_method == "Steady-state":
                n_children_needed = int(self.replacement_params.get("n_replace", 2))
            else:
                n_children_needed = self.pop_size

            # Seleccionar padres y aplicar cruce en pares
            parents = self._select_parents(pop.individuals, n_children_needed)
            for i in range(0, len(parents), 2):
                p1 = parents[i]
                p2 = parents[i + 1] if i + 1 < len(parents) else parents[0]
                h1, h2 = self._crossover_pair(p1, p2)
                offspring.append(h1)
                if len(offspring) < n_children_needed:
                    offspring.append(h2)

            # Mutación
            mutated_offspring: List[Individual] = []
            for child in offspring:
                m_child = self._mutate_individual(child, current_gen=gen)
                mutated_offspring.append(m_child)

            # Evaluar descendientes
            for child in mutated_offspring:
                val = self.evaluator.evaluate(child.x)
                child.objective_value = val
                self.total_evaluations += 1

            # Calcular fitness provisional para descendientes (necesario para reemplazos)
            dummy_pop = Population(size=len(mutated_offspring), bounds=self.bounds)
            dummy_pop.individuals = mutated_offspring
            dummy_pop.evaluate(self.evaluator.evaluate, goal=self.goal)

            # Sustitución / Reemplazo
            next_generation_inds = self._apply_replacement(pop.individuals, mutated_offspring)
            pop.individuals = next_generation_inds

            # Re-evaluar aptitudes y rangos de la nueva población completa
            pop.evaluate(self.evaluator.evaluate, goal=self.goal)

            # Monitorear mejor global
            curr_best = pop.best_individual(goal=self.goal)
            is_new_best = False
            if self.goal == "minimize":
                if curr_best.objective_value < self.best_global_individual.objective_value:
                    is_new_best = True
            else:
                if curr_best.objective_value > self.best_global_individual.objective_value:
                    is_new_best = True

            if is_new_best:
                self.best_global_individual = curr_best.copy()
                self.best_global_generation = gen

            stats = pop.stats(goal=self.goal)
            stats["generation"] = gen
            stats["evaluations"] = self.total_evaluations
            self.history.append(stats)

            if callback:
                callback(gen, stats, self.best_global_individual, pop.individuals)

        self.execution_time = time.time() - start_time
        self.is_running = False

        return {
            "best_x": self.best_global_individual.x if self.best_global_individual else None,
            "best_fx": self.best_global_individual.objective_value if self.best_global_individual else None,
            "best_fitness": self.best_global_individual.fitness if self.best_global_individual else None,
            "best_generation": self.best_global_generation,
            "total_evaluations": self.total_evaluations,
            "execution_time": self.execution_time,
            "stopped_early": self.stop_requested,
            "history": self.history
        }

    def stop(self):
        self.stop_requested = True
        self.is_paused = False
