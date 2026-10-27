"""
Prueba de integración del ciclo evolutivo completo (GAEngine) y registro de experimentos.
"""
import sys
import os
import unittest
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from logica.ga_engine import GAEngine
from almacenamiento.experiment_logger import ExperimentLogger

class TestGAEngine(unittest.TestCase):
    def test_run_sphere_convergence(self):
        config = {
            "function_name": "Esfera 1D",
            "expression": "x**2",
            "bounds": [(-5.0, 5.0)],
            "goal": "minimize",
            "pop_size": 30,
            "max_generations": 40,
            "pc": 0.8,
            "pm": 0.15,
            "seed": 42,
            "selection_method": "Torneo",
            "selection_params": {"k": 3},
            "crossover_method": "BLX-α",
            "crossover_params": {"alpha": 0.5},
            "mutation_method": "No uniforme",
            "mutation_params": {"b": 2.0},
            "replacement_method": "Generacional con elitismo",
            "replacement_params": {"n_elite": 2}
        }

        engine = GAEngine(config)
        results = engine.run()

        # Debe converger cerca de x = 0 y f(x) = 0
        best_x = results["best_x"]
        best_fx = results["best_fx"]
        self.assertIsNotNone(best_x)
        self.assertLess(abs(best_x), 0.1)
        self.assertLess(best_fx, 0.05)
        self.assertGreater(results["total_evaluations"], 0)

        # Probar logger
        logger = ExperimentLogger()
        run_id = logger.save_run(config, results)
        self.assertTrue(os.path.exists(os.path.join(logger.records_dir, f"{run_id}.json")))
        self.assertTrue(os.path.exists(os.path.join(logger.records_dir, f"{run_id}.txt")))

if __name__ == "__main__":
    unittest.main()
