"""
Pruebas unitarias para validar cada operador evolutivo de '05_hiperparametros'.
"""
import sys
import os
import unittest
import numpy as np

# Asegurar path al módulo raíz
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from logica.individual import Individual
from logica.selection import (
    roulette_wheel_selection,
    linear_ranking_selection,
    non_linear_ranking_selection,
    tournament_selection,
    stochastic_universal_sampling
)
from logica.crossover import (
    uniform_crossover,
    arithmetic_crossover,
    flat_crossover,
    blx_alpha_crossover,
    pmx_crossover,
    ox_crossover,
    cx_crossover
)
from logica.mutation import (
    uniform_mutation,
    non_uniform_mutation,
    swap_mutation
)
from logica.replacement import (
    generational_replacement_with_elitism,
    steady_state_replacement,
    crowding_replacement
)

class TestOperators(unittest.TestCase):
    def setUp(self):
        np.random.seed(42)
        # Población de prueba con 4 individuos como en el PDF
        self.pop = [
            Individual([10.0], bounds=[(0.0, 50.0)]),
            Individual([20.0], bounds=[(0.0, 50.0)]),
            Individual([30.0], bounds=[(0.0, 50.0)]),
            Individual([40.0], bounds=[(0.0, 50.0)])
        ]
        # Asignar fitness correspondiente
        self.pop[0].fitness = 10.0
        self.pop[1].fitness = 20.0
        self.pop[2].fitness = 30.0
        self.pop[3].fitness = 40.0

    def test_roulette_selection(self):
        selected = roulette_wheel_selection(self.pop, n_parents=4)
        self.assertEqual(len(selected), 4)

    def test_linear_ranking_selection(self):
        selected = linear_ranking_selection(self.pop, n_parents=4, a_max=1.6)
        self.assertEqual(len(selected), 4)

    def test_non_linear_ranking_selection(self):
        selected = non_linear_ranking_selection(self.pop, n_parents=4, q=0.5)
        self.assertEqual(len(selected), 4)

    def test_tournament_selection(self):
        selected = tournament_selection(self.pop, n_parents=2, k=2)
        self.assertEqual(len(selected), 2)

    def test_sus_selection(self):
        selected = stochastic_universal_sampling(self.pop, n_parents=4)
        self.assertEqual(len(selected), 4)

    def test_crossovers(self):
        p1 = Individual([2.0], bounds=[(0.0, 10.0)])
        p2 = Individual([6.0], bounds=[(0.0, 10.0)])

        # Aritmético: a = 0.25 -> h1 = 0.25*2 + 0.75*6 = 5.0, h2 = 0.75*2 + 0.25*6 = 3.0
        h1, h2 = arithmetic_crossover(p1, p2, a=0.25)
        self.assertAlmostEqual(h1.x, 5.0, places=4)
        self.assertAlmostEqual(h2.x, 3.0, places=4)

        # Plano: entre 2 y 6
        h1, h2 = flat_crossover(p1, p2)
        self.assertTrue(2.0 <= h1.x <= 6.0)
        self.assertTrue(2.0 <= h2.x <= 6.0)

        # BLX-alpha: con alpha=0.5, [0, 8]
        h1, h2 = blx_alpha_crossover(p1, p2, alpha=0.5)
        self.assertTrue(0.0 <= h1.x <= 8.0)
        self.assertTrue(0.0 <= h2.x <= 8.0)

        # Uniforme
        h1, h2 = uniform_crossover(p1, p2)
        self.assertTrue(h1.x in (2.0, 6.0) or (0.0 <= h1.x <= 10.0))

    def test_permutations_crossover(self):
        # Probar operadores basados en secuencias con arrays vectoriales
        p1 = Individual([1, 2, 3, 4, 5, 6, 7, 8], bounds=[(1, 8)]*8)
        p2 = Individual([3, 7, 5, 1, 6, 8, 2, 4], bounds=[(1, 8)]*8)
        h1, h2 = pmx_crossover(p1, p2)
        self.assertEqual(len(set(h1.genes)), 8)
        self.assertEqual(len(set(h2.genes)), 8)

        h1, h2 = ox_crossover(p1, p2)
        self.assertEqual(len(set(h1.genes)), 8)

        h1, h2 = cx_crossover(p1, p2)
        self.assertEqual(len(set(h1.genes)), 8)

    def test_mutations(self):
        ind = Individual([4.0], bounds=[(0.0, 10.0)])
        # Uniforme
        m_u = uniform_mutation(ind, p_mut=1.0)
        self.assertTrue(0.0 <= m_u.x <= 10.0)

        # No uniforme al inicio (t=0, cambio mayor) y al final (t=90, cambio menor)
        m_early = non_uniform_mutation(ind, p_mut=1.0, current_gen=0, max_gen=100, b=1.0)
        m_late = non_uniform_mutation(ind, p_mut=1.0, current_gen=95, max_gen=100, b=1.0)
        self.assertTrue(0.0 <= m_early.x <= 10.0)
        self.assertTrue(0.0 <= m_late.x <= 10.0)

    def test_replacements(self):
        current_pop = [
            Individual([10.0]), Individual([20.0]), Individual([30.0]), Individual([40.0])
        ]
        current_pop[0].fitness = 10.0
        current_pop[1].fitness = 20.0
        current_pop[2].fitness = 30.0
        current_pop[3].fitness = 40.0

        offspring = [Individual([25.0]), Individual([35.0])]
        offspring[0].fitness = 25.0
        offspring[1].fitness = 35.0

        # Steady-state: reemplaza los 2 peores (fitness 10 y 20)
        new_pop = steady_state_replacement(current_pop, offspring, n_replace=2)
        self.assertEqual(len(new_pop), 4)
        fits = sorted([ind.fitness for ind in new_pop])
        self.assertEqual(fits, [25.0, 30.0, 35.0, 40.0])

        # Crowding
        crowd_pop = crowding_replacement(current_pop, offspring, crowding_factor=3)
        self.assertEqual(len(crowd_pop), 4)

if __name__ == "__main__":
    unittest.main()
