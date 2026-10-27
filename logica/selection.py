"""
Operadores de selección según '05_hiperparametros':
- Ruleta proporcional
- Ranking lineal
- Ranking no lineal
- Torneo
- Muestreo estocástico universal (SUS)
"""
from typing import List
import numpy as np
from .individual import Individual

def roulette_wheel_selection(population: List[Individual], n_parents: int) -> List[Individual]:
    """
    Selección proporcional (Ruleta).
    p_i = f_i / sum(f_j).
    """
    m = len(population)
    fitnesses = np.array([ind.fitness for ind in population], dtype=float)
    total_fit = np.sum(fitnesses)
    
    if total_fit <= 0 or np.isnan(total_fit):
        probs = np.ones(m) / m
    else:
        probs = fitnesses / total_fit

    cum_probs = np.cumsum(probs)
    selected = []
    for _ in range(n_parents):
        r = np.random.rand()
        idx = int(np.searchsorted(cum_probs, r))
        idx = min(idx, m - 1)
        selected.append(population[idx].copy())
    return selected

def linear_ranking_selection(population: List[Individual], n_parents: int, a_max: float = 1.6) -> List[Individual]:
    """
    Ranking lineal.
    Ordena del mejor al peor (rank_c = 1 ... m).
    1 <= a_max <= 2, a_min = 2 - a_max.
    p(r) = [a_max - (a_max - a_min) * (rank_c - 1) / (m - 1)] / m
    """
    m = len(population)
    if m == 1:
        return [population[0].copy() for _ in range(n_parents)]

    # Asegurar orden del mejor (rank 1) al peor (rank m)
    # Mayor fitness = mejor individuo = rank 1
    sorted_pop = sorted(population, key=lambda ind: ind.fitness, reverse=True)
    
    a_max = np.clip(a_max, 1.0, 2.0)
    a_min = 2.0 - a_max
    
    ranks = np.arange(1, m + 1)
    probs = (a_max - (a_max - a_min) * (ranks - 1.0) / (m - 1.0)) / m
    probs = np.maximum(probs, 0.0)
    probs /= np.sum(probs)

    cum_probs = np.cumsum(probs)
    selected = []
    for _ in range(n_parents):
        r = np.random.rand()
        idx = int(np.searchsorted(cum_probs, r))
        idx = min(idx, m - 1)
        selected.append(sorted_pop[idx].copy())
    return selected

def non_linear_ranking_selection(population: List[Individual], n_parents: int, q: float = 0.5) -> List[Individual]:
    """
    Ranking no lineal (geométrico).
    w(r) = q * (1 - q)^(rank_c - 1)
    p'(r) = w(r) / sum(w)
    """
    m = len(population)
    if m == 1:
        return [population[0].copy() for _ in range(n_parents)]

    sorted_pop = sorted(population, key=lambda ind: ind.fitness, reverse=True)
    q = np.clip(q, 0.001, 0.999)
    
    ranks = np.arange(1, m + 1)
    weights = q * np.power(1.0 - q, ranks - 1.0)
    total_w = np.sum(weights)
    probs = weights / total_w

    cum_probs = np.cumsum(probs)
    selected = []
    for _ in range(n_parents):
        r = np.random.rand()
        idx = int(np.searchsorted(cum_probs, r))
        idx = min(idx, m - 1)
        selected.append(sorted_pop[idx].copy())
    return selected

def tournament_selection(population: List[Individual], n_parents: int, k: int = 2) -> List[Individual]:
    """
    Selección por torneo determinista de tamaño k.
    Elige k participantes al azar y gana el de mayor aptitud.
    """
    m = len(population)
    k = max(1, min(k, m))
    selected = []
    for _ in range(n_parents):
        indices = np.random.choice(m, size=k, replace=False)
        best_cand = max((population[i] for i in indices), key=lambda ind: ind.fitness)
        selected.append(best_cand.copy())
    return selected

def stochastic_universal_sampling(population: List[Individual], n_parents: int) -> List[Individual]:
    """
    Muestreo Estocástico Universal (SUS).
    Distribución acumulada con punteros equidistantes y desplazamiento inicial u in [0, 1/n_parents).
    """
    m = len(population)
    fitnesses = np.array([ind.fitness for ind in population], dtype=float)
    total_fit = np.sum(fitnesses)
    
    if total_fit <= 0 or np.isnan(total_fit):
        probs = np.ones(m) / m
    else:
        probs = fitnesses / total_fit

    cum_probs = np.cumsum(probs)
    # Asegurar que el último valor sea exactamente 1.0 para evitar desbordes numéricos
    cum_probs[-1] = 1.0

    step = 1.0 / n_parents
    start = np.random.uniform(0.0, step)
    pointers = [start + i * step for i in range(n_parents)]

    selected = []
    idx = 0
    for p in pointers:
        while idx < m and cum_probs[idx] < p:
            idx += 1
        idx = min(idx, m - 1)
        selected.append(population[idx].copy())
    return selected
