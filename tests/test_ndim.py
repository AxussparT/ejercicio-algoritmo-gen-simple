"""
Prueba unitaria para verificar optimización en problemas multidimensionales (n-D).
"""
import sys
import os
import unittest
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from logica.evaluator import SafeEvaluator, detect_dimensions
from logica.ga_engine import GAEngine

class TestNDimGA(unittest.TestCase):
    def test_dimensions_detection(self):
        self.assertEqual(detect_dimensions("x**2"), 1)
        self.assertEqual(detect_dimensions("x1**2 + x2**2 + x3**2"), 3)
        self.assertEqual(detect_dimensions("x**2 + y**2"), 2)
        self.assertEqual(detect_dimensions("x**2 + y**2 + z**2"), 3)
        self.assertEqual(detect_dimensions("x[0]**2 + x[1]**2 + x[2]**2"), 3)
        self.assertEqual(detect_dimensions("sum(x**2)"), 1) # Si es solo 'x', 1 por defecto (configurable manual)

    def test_sphere_3d_optimization(self):
        # f(x) = sum(x**2) en 3D, x1, x2, x3 en [-5, 5]
        config = {
            "function_name": "Esfera 3D",
            "expression": "sum(x**2)",
            "dimensions": 3,
            "bounds": [(-5.0, 5.0)] * 3,
            "goal": "minimize",
            "pop_size": 40,
            "max_generations": 50,
            "pc": 0.85,
            "pm": 0.15,
            "seed": 42,
            "selection_method": "Torneo",
            "selection_params": {"k": 3},
            "crossover_method": "BLX-α",
            "crossover_params": {"alpha": 0.5},
            "mutation_method": "No uniforme",
            "mutation_params": {"b": 1.5},
            "replacement_method": "Generacional con elitismo",
            "replacement_params": {"n_elite": 2}
        }

        engine = GAEngine(config)
        results = engine.run()

        self.assertIsNotNone(results["best_x"])
        self.assertEqual(len(results["best_x"]), 3)
        self.assertLess(results["best_fx"], 0.2)
        for val in results["best_x"]:
            self.assertLess(abs(val), 0.3)

    def test_2d_variables_names(self):
        # f(x1, x2) = x1**2 + x2**2
        config = {
            "function_name": "Suma de Cuadrados 2D",
            "expression": "x1**2 + x2**2",
            "dimensions": 2,
            "bounds": [(-5.0, 5.0)] * 2,
            "goal": "minimize",
            "pop_size": 30,
            "max_generations": 40,
            "pc": 0.8,
            "pm": 0.1,
            "seed": 100,
            "selection_method": "Ranking lineal",
            "selection_params": {"a_max": 1.5},
            "crossover_method": "Aritmético",
            "crossover_params": {"a": 0.3},
            "mutation_method": "Uniforme",
            "mutation_params": {},
            "replacement_method": "Generacional con elitismo",
            "replacement_params": {"n_elite": 1}
        }

        engine = GAEngine(config)
        results = engine.run()
        self.assertLess(results["best_fx"], 0.1)

if __name__ == "__main__":
    unittest.main()
