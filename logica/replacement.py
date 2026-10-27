"""
Estrategias de sustitución y reemplazo según '05_hiperparametros':
- Sustitución steady-state (reemplazo de los n peores)
- Factor de crowding (reemplazo del individuo más parecido entre una muestra CF)
- Reemplazo generacional con elitismo
"""
from typing import List
import numpy as np
from .individual import Individual

def generational_replacement_with_elitism(
    current_pop: List[Individual], 
    offspring: List[Individual], 
    n_elite: int = 1
) -> List[Individual]:
    """
    Reemplazo generacional completo conservando los n_elite mejores individuos de la población actual.
    """
    m = len(current_pop)
    n_elite = max(0, min(n_elite, m))
    
    # Ordenar población actual por aptitud descendente (mejor primero)
    sorted_current = sorted(current_pop, key=lambda ind: ind.fitness, reverse=True)
    elites = [ind.copy() for ind in sorted_current[:n_elite]]
    
    # Tomar el resto de los descendientes
    needed = m - n_elite
    new_pop = elites + [ind.copy() for ind in offspring[:needed]]
    return new_pop

def steady_state_replacement(
    current_pop: List[Individual], 
    offspring: List[Individual], 
    n_replace: int = 2
) -> List[Individual]:
    """
    Sustitución steady-state:
    Reemplaza los n individuos de menor aptitud (los n peores) por los n descendientes.
    Ejemplo del PDF: Población de m=4, llegan n=2 hijos, salen los 2 peores actuales.
    """
    m = len(current_pop)
    n = max(1, min(n_replace, m, len(offspring)))
    
    # Ordenar del mejor al peor (mayor fitness a menor fitness)
    sorted_pop = sorted(current_pop, key=lambda ind: ind.fitness, reverse=True)
    
    # Mantener los m - n mejores
    survivors = [ind.copy() for ind in sorted_pop[:m - n]]
    # Incorporar los n nuevos hijos
    survivors.extend([ind.copy() for ind in offspring[:n]])
    return survivors

def crowding_replacement(
    current_pop: List[Individual], 
    offspring: List[Individual], 
    crowding_factor: int = 3,
    replace_if_better: bool = False
) -> List[Individual]:
    """
    Factor de crowding:
    Para insertar cada descendiente, toma CF individuos al azar de la población y
    reemplaza al más parecido (menor distancia en el espacio fenotípico/genotípico).
    """
    m = len(current_pop)
    cf = max(1, min(crowding_factor, m))
    
    # Copia de trabajo de la población
    new_pop = [ind.copy() for ind in current_pop]
    
    for child in offspring:
        # Elegir CF individuos al azar
        sample_indices = np.random.choice(m, size=cf, replace=False)
        
        # Encontrar el más parecido (mínima distancia euclidiana entre genes)
        best_match_idx = None
        min_dist = float('inf')
        for idx in sample_indices:
            dist = np.linalg.norm(new_pop[idx].genes - child.genes)
            if dist < min_dist:
                min_dist = dist
                best_match_idx = idx
                
        # Reemplazar al más parecido
        if best_match_idx is not None:
            if replace_if_better:
                if child.fitness >= new_pop[best_match_idx].fitness:
                    new_pop[best_match_idx] = child.copy()
            else:
                new_pop[best_match_idx] = child.copy()
                
    return new_pop
