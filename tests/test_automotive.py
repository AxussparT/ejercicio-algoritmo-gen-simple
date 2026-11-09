"""
Pruebas unitarias para verificar el cálculo de las funciones objetivo,
ecuaciones físicas no lineales, restricciones de diseño y algoritmos
del Reto de Diseño Automotriz Multiobjetivo (Sección 5 de Entregables).
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from logica.automotive_model import (
    evaluate_vehicle,
    evaluate_scalarized,
    run_automotive_ga,
    run_automotive_pso,
    run_automotive_moo
)


class TestAutomotiveOptimization(unittest.TestCase):
    def test_base_vehicle_evaluation(self):
        # Vehículo base sin mejoras: P=80 kW, r=0, a=0, b=0, g=3.3, h=0
        info = evaluate_vehicle([80.0, 0.0, 0.0, 0.0, 3.3, 0.0])
        self.assertAlmostEqual(info["mass"], 1450.0, places=2)
        self.assertAlmostEqual(info["cd"], 0.34, places=3)
        self.assertAlmostEqual(info["crr"], 0.013, places=4)
        self.assertAlmostEqual(info["c_fab"], 190000.0, places=0)
        # Con solo 80 kW no alcanza 200 km/h ni acelera en <= 9 s, por lo que debe ser infactible
        self.assertFalse(info["is_feasible"])
        self.assertGreater(info["constraints"][0], 0.0)  # V_max < 200

    def test_feasible_balanced_vehicle(self):
        # Vehículo equilibrado: P=145 kW, r=0.45, a=0.55, b=0.60, g=3.45, h=0.50
        info = evaluate_vehicle([145.0, 0.45, 0.55, 0.60, 3.45, 0.50])
        self.assertGreaterEqual(info["v_max"], 200.0)
        self.assertLessEqual(info["t_0_100"], 9.0)
        self.assertLessEqual(info["c_fab"], 315000.0)
        self.assertLessEqual(info["mass"], 1500.0)
        self.assertTrue(info["is_feasible"])
        # Verificar promedio ponderado exacto de consumo (20% a 60km/h, 50% a 90km/h, 30% a 120km/h)
        expected_c = 0.20 * info["c_60"] + 0.50 * info["c_90"] + 0.30 * info["c_120"]
        self.assertAlmostEqual(info["c_comb"], expected_c, places=6)

    def test_ga_and_pso_find_feasible_designs(self):
        ga_res = run_automotive_ga(pop_size=30, max_generations=25, seed=42)
        pso_res = run_automotive_pso(swarmsize=30, maxiter=25, seed=42)
        self.assertTrue(ga_res["vehicle"]["is_feasible"])
        self.assertTrue(pso_res["vehicle"]["is_feasible"])

    def test_moo_pareto_front_and_final_challenge(self):
        # Prueba con reducción de presupuesto del 10% (Desafío Final: $283,500 MXN)
        moo_res = run_automotive_moo(algorithm_name="NSGA-III", max_cost_limit=283500.0, pop_size=40, n_gen=25, seed=42)
        self.assertGreater(moo_res["n_pareto"], 0)
        for s in moo_res["solutions"]:
            self.assertTrue(s["is_feasible"])
            self.assertLessEqual(s["c_fab"], 283500.0)
            self.assertGreaterEqual(s["v_max"], 200.0)
            self.assertLessEqual(s["t_0_100"], 9.0)
            self.assertLessEqual(s["mass"], 1500.0)


if __name__ == "__main__":
    unittest.main()
