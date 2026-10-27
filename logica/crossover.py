"""
Operadores de cruce según '05_hiperparametros':
- Cruce uniforme
- Cruce aritmético
- Cruce plano
- Cruce BLX-α
- Cruce PMX (Partially Mapped Crossover)
- Cruce OX (Order Crossover)
- Cruce CX (Cycle Crossover)
"""
from typing import Tuple, List
import numpy as np
from .individual import Individual

def uniform_crossover(p1: Individual, p2: Individual, p_mask: float = 0.5) -> Tuple[Individual, Individual]:
    """
    Cruce uniforme:
    Una máscara binaria decide de qué padre toma cada gen el hijo 1.
    El hijo 2 toma los valores complementarios.
    """
    h1_genes = np.copy(p1.genes)
    h2_genes = np.copy(p2.genes)
    
    n_genes = len(p1.genes)
    if n_genes == 1:
        # En individuo univariado, se realiza cruce uniforme sobre la descomposición o sorteo
        if np.random.rand() < p_mask:
            h1_genes[0], h2_genes[0] = p1.genes[0], p2.genes[0]
        else:
            h1_genes[0], h2_genes[0] = p2.genes[0], p1.genes[0]
    else:
        mask = np.random.rand(n_genes) < p_mask
        h1_genes[mask] = p1.genes[mask]
        h1_genes[~mask] = p2.genes[~mask]
        h2_genes[mask] = p2.genes[mask]
        h2_genes[~mask] = p1.genes[~mask]

    c1 = Individual(h1_genes, p1.bounds)
    c2 = Individual(h2_genes, p2.bounds)
    c1.clamp_bounds()
    c2.clamp_bounds()
    return c1, c2

def arithmetic_crossover(p1: Individual, p2: Individual, a: float = 0.25) -> Tuple[Individual, Individual]:
    """
    Cruce aritmético:
    Combina los valores parentales mediante media ponderada:
    H1 = a * P1 + (1 - a) * P2
    H2 = (1 - a) * P1 + a * P2
    con 0 <= a <= 1.
    """
    a = np.clip(a, 0.0, 1.0)
    h1_genes = a * p1.genes + (1.0 - a) * p2.genes
    h2_genes = (1.0 - a) * p1.genes + a * p2.genes

    c1 = Individual(h1_genes, p1.bounds)
    c2 = Individual(h2_genes, p2.bounds)
    c1.clamp_bounds()
    c2.clamp_bounds()
    return c1, c2

def flat_crossover(p1: Individual, p2: Individual) -> Tuple[Individual, Individual]:
    """
    Cruce plano:
    Para cada gen sortea un valor uniforme entre el menor y mayor de los padres:
    h_j ~ U(min(p1_j, p2_j), max(p1_j, p2_j))
    """
    mins = np.minimum(p1.genes, p2.genes)
    maxs = np.maximum(p1.genes, p2.genes)
    
    # Evitar intervalos degenerados
    diffs = maxs - mins
    zero_mask = diffs < 1e-12
    maxs[zero_mask] += 1e-12

    h1_genes = np.random.uniform(mins, maxs)
    h2_genes = np.random.uniform(mins, maxs)

    c1 = Individual(h1_genes, p1.bounds)
    c2 = Individual(h2_genes, p2.bounds)
    c1.clamp_bounds()
    c2.clamp_bounds()
    return c1, c2

def blx_alpha_crossover(p1: Individual, p2: Individual, alpha: float = 0.5) -> Tuple[Individual, Individual]:
    """
    Cruce BLX-α:
    Amplía el intervalo de cada gen en una proporción α de su longitud I = |p1 - p2|:
    h ~ U(min - α*I, max + α*I)
    """
    mins = np.minimum(p1.genes, p2.genes)
    maxs = np.maximum(p1.genes, p2.genes)
    intervals = maxs - mins
    
    lower = mins - alpha * intervals
    upper = maxs + alpha * intervals
    
    diffs = upper - lower
    zero_mask = diffs < 1e-12
    upper[zero_mask] += 1e-12

    h1_genes = np.random.uniform(lower, upper)
    h2_genes = np.random.uniform(lower, upper)

    c1 = Individual(h1_genes, p1.bounds)
    c2 = Individual(h2_genes, p2.bounds)
    c1.clamp_bounds()
    c2.clamp_bounds()
    return c1, c2

# ==============================================================================
# Operadores de cruce para permutaciones / secuencias (PMX, OX, CX)
# ==============================================================================

def pmx_crossover_vector(parent1: np.ndarray, parent2: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Partially Mapped Crossover (PMX) sobre arrays numéricos de permutación.
    """
    size = len(parent1)
    if size < 2:
        return parent1.copy(), parent2.copy()

    cxpoint1 = np.random.randint(0, size - 1)
    cxpoint2 = np.random.randint(cxpoint1 + 1, size)

    def _pmx_single(p1, p2):
        child = [None] * size
        # Copiar segmento
        child[cxpoint1:cxpoint2] = p1[cxpoint1:cxpoint2]
        
        # Mapear elementos del segmento de p2
        for i in range(cxpoint1, cxpoint2):
            val = p2[i]
            if val not in child[cxpoint1:cxpoint2]:
                curr = val
                pos = i
                while cxpoint1 <= pos < cxpoint2:
                    val_in_p1 = p1[pos]
                    pos = list(p2).index(val_in_p1)
                child[pos] = curr
                
        # Completar con el resto de p2
        for i in range(size):
            if child[i] is None:
                child[i] = p2[i]
        return np.array(child, dtype=float)

    h1 = _pmx_single(parent1, parent2)
    h2 = _pmx_single(parent2, parent1)
    return h1, h2

def ox_crossover_vector(parent1: np.ndarray, parent2: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Order Crossover (OX) para secuencias/permutaciones.
    """
    size = len(parent1)
    if size < 2:
        return parent1.copy(), parent2.copy()

    cx1 = np.random.randint(0, size - 1)
    cx2 = np.random.randint(cx1 + 1, size)

    def _ox_single(p1, p2):
        child = [None] * size
        child[cx1:cx2] = p1[cx1:cx2]
        
        copied_set = set(child[cx1:cx2])
        p2_order = [x for x in list(p2[cx2:]) + list(p2[:cx2]) if x not in copied_set]
        
        idx = cx2
        for val in p2_order:
            if idx >= size:
                idx = 0
            while child[idx] is not None:
                idx = (idx + 1) % size
            child[idx] = val
        return np.array(child, dtype=float)

    h1 = _ox_single(parent1, parent2)
    h2 = _ox_single(parent2, parent1)
    return h1, h2

def cx_crossover_vector(parent1: np.ndarray, parent2: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Cycle Crossover (CX) para secuencias/permutaciones.
    """
    size = len(parent1)
    if size < 2:
        return parent1.copy(), parent2.copy()

    def _cx_single(p1, p2):
        child = [None] * size
        cycle = 0
        visited = set()
        
        while len(visited) < size:
            # Buscar inicio del ciclo
            start_idx = 0
            while start_idx < size and start_idx in visited:
                start_idx += 1
            if start_idx >= size:
                break
                
            curr_idx = start_idx
            cycle_indices = []
            while curr_idx not in visited:
                visited.add(curr_idx)
                cycle_indices.append(curr_idx)
                val_in_p2 = p2[curr_idx]
                curr_idx = list(p1).index(val_in_p2)
                
            source = p1 if cycle % 2 == 0 else p2
            for idx in cycle_indices:
                child[idx] = source[idx]
            cycle += 1
            
        for i in range(size):
            if child[i] is None:
                child[i] = p2[i]
        return np.array(child, dtype=float)

    h1 = _cx_single(parent1, parent2)
    h2 = _cx_single(parent2, parent1)
    return h1, h2

def pmx_crossover(p1: Individual, p2: Individual) -> Tuple[Individual, Individual]:
    """Adaptador de PMX: compatible con vectores de permutación y valores univariados."""
    if len(p1.genes) > 1:
        g1, g2 = pmx_crossover_vector(p1.genes, p2.genes)
    else:
        # Para gen univariado continuo, genera recombinación combinando bits/dígitos o interpolación
        a = 0.5
        g1 = np.array([a * p1.genes[0] + (1 - a) * p2.genes[0]])
        g2 = np.array([(1 - a) * p1.genes[0] + a * p2.genes[0]])
    c1, c2 = Individual(g1, p1.bounds), Individual(g2, p2.bounds)
    c1.clamp_bounds(); c2.clamp_bounds()
    return c1, c2

def ox_crossover(p1: Individual, p2: Individual) -> Tuple[Individual, Individual]:
    """Adaptador de OX: compatible con vectores de permutación y valores univariados."""
    if len(p1.genes) > 1:
        g1, g2 = ox_crossover_vector(p1.genes, p2.genes)
    else:
        g1 = np.array([p1.genes[0]])
        g2 = np.array([p2.genes[0]])
    c1, c2 = Individual(g1, p1.bounds), Individual(g2, p2.bounds)
    c1.clamp_bounds(); c2.clamp_bounds()
    return c1, c2

def cx_crossover(p1: Individual, p2: Individual) -> Tuple[Individual, Individual]:
    """Adaptador de CX: compatible con vectores de permutación y valores univariados."""
    if len(p1.genes) > 1:
        g1, g2 = cx_crossover_vector(p1.genes, p2.genes)
    else:
        g1 = np.array([p2.genes[0]])
        g2 = np.array([p1.genes[0]])
    c1, c2 = Individual(g1, p1.bounds), Individual(g2, p2.bounds)
    c1.clamp_bounds(); c2.clamp_bounds()
    return c1, c2
