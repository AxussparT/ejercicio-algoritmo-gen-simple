"""
Operadores de mutación según '05_hiperparametros':
- Mutación uniforme
- Mutación no uniforme (dependiente de la generación)
- Mutación por intercambio (Swap)
"""
from typing import List, Tuple
import numpy as np
from .individual import Individual

def uniform_mutation(ind: Individual, p_mut: float = 0.1) -> Individual:
    """
    Mutación uniforme:
    Sustituye el gen elegido por un valor sorteado uniformemente en [LB, UB].
    x'_j ~ U(LB_j, UB_j)
    """
    new_ind = ind.copy()
    for j in range(len(new_ind.genes)):
        if np.random.rand() < p_mut:
            lb, ub = new_ind.bounds[j] if j < len(new_ind.bounds) else (-10.0, 10.0)
            new_ind.genes[j] = np.random.uniform(lb, ub)
    new_ind.clamp_bounds()
    return new_ind

def non_uniform_mutation(ind: Individual, p_mut: float = 0.1, current_gen: int = 0, max_gen: int = 100, b: float = 1.0) -> Individual:
    """
    Mutación no uniforme:
    El cambio tiende a ser mayor al inicio (t=0) y menor hacia el final (t->T).
    Δ(t, y) = y * [1 - r^( (1 - t/T)^b )]
    con r ~ U[0, 1].
    """
    new_ind = ind.copy()
    T = max(1, max_gen)
    t = min(current_gen, T)
    exponent = (1.0 - (t / float(T))) ** b

    for j in range(len(new_ind.genes)):
        if np.random.rand() < p_mut:
            lb, ub = new_ind.bounds[j] if j < len(new_ind.bounds) else (-10.0, 10.0)
            x_val = new_ind.genes[j]
            r = np.random.rand()
            
            # Sorteo de dirección: hacia arriba (a=0) o hacia abajo (a=1)
            direction_up = np.random.rand() < 0.5
            if direction_up:
                y = ub - x_val
                delta = y * (1.0 - (r ** exponent))
                new_ind.genes[j] = x_val + delta
            else:
                y = x_val - lb
                delta = y * (1.0 - (r ** exponent))
                new_ind.genes[j] = x_val - delta

    new_ind.clamp_bounds()
    return new_ind

def swap_mutation(ind: Individual, p_mut: float = 0.1) -> Individual:
    """
    Mutación por intercambio:
    Elige dos posiciones al azar e intercambia sus elementos.
    Conserva la validez en representaciones de permutación.
    En representaciones univariadas, intercambia respecto al centro o perturba el gen.
    """
    new_ind = ind.copy()
    if np.random.rand() < p_mut:
        n = len(new_ind.genes)
        if n >= 2:
            i, j = np.random.choice(n, size=2, replace=False)
            new_ind.genes[i], new_ind.genes[j] = new_ind.genes[j], new_ind.genes[i]
        else:
            # En individuo univariado, refleja el gen respecto al centro del intervalo
            lb, ub = new_ind.bounds[0]
            center = (lb + ub) / 2.0
            dist = new_ind.genes[0] - center
            # Intercambia el lado respecto al centro con una pequeña fluctuación
            new_ind.genes[0] = center - dist + np.random.normal(0, 0.05 * (ub - lb))
    new_ind.clamp_bounds()
    return new_ind
