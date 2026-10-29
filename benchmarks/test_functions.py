"""
Catálogo de funciones de prueba (benchmarks) clásicas.
Soporta problemas univariados (1D) y multivariados (2D, 3D, ... nD).
"""
from typing import Dict, Any, Tuple

BENCHMARK_FUNCTIONS: Dict[str, Dict[str, Any]] = {
    "Esfera 1D (Convexa simple)": {
        "formula": "x**2",
        "dimensions": 1,
        "bounds": (-10.0, 10.0),
        "optimum_x": 0.0,
        "optimum_f": 0.0,
        "goal": "minimize",
        "description": "Función unimodal cuadrática f(x) = x². Mínimo global en x = 0."
    },
    "Esfera N-D (sum(x**2))": {
        "formula": "sum(x**2)",
        "dimensions": 3,
        "bounds": (-10.0, 10.0),
        "optimum_x": [0.0, 0.0, 0.0],
        "optimum_f": 0.0,
        "goal": "minimize",
        "description": "Función Esfera generalizada en N dimensiones. Mínimo en x = [0, 0, ...]."
    },
    "Rastrigin 1D (Altamente multimodal)": {
        "formula": "10 + x**2 - 10 * cos(2 * pi * x)",
        "dimensions": 1,
        "bounds": (-5.12, 5.12),
        "optimum_x": 0.0,
        "optimum_f": 0.0,
        "goal": "minimize",
        "description": "Función multimodal con múltiples mínimos locales periódicos. Mínimo global en x = 0."
    },
    "Rastrigin 2D (x1, x2)": {
        "formula": "20 + (x1**2 - 10*cos(2*pi*x1)) + (x2**2 - 10*cos(2*pi*x2))",
        "dimensions": 2,
        "bounds": (-5.12, 5.12),
        "optimum_x": [0.0, 0.0],
        "optimum_f": 0.0,
        "goal": "minimize",
        "description": "Rastrigin bidimensional con múltiples picos locales. Mínimo en (0, 0)."
    },
    "Ackley 1D (Multimodal con valle central)": {
        "formula": "-20 * exp(-0.2 * abs(x)) - exp(cos(2 * pi * x)) + 20 + e",
        "dimensions": 1,
        "bounds": (-5.0, 5.0),
        "optimum_x": 0.0,
        "optimum_f": 0.0,
        "goal": "minimize",
        "description": "Función de Ackley en 1D. Mínimo global pronunciado en x = 0 rodeado de ondulaciones."
    },
    "Ackley 2D (x, y)": {
        "formula": "-20*exp(-0.2*sqrt(0.5*(x**2 + y**2))) - exp(0.5*(cos(2*pi*x) + cos(2*pi*y))) + 20 + e",
        "dimensions": 2,
        "bounds": (-5.0, 5.0),
        "optimum_x": [0.0, 0.0],
        "optimum_f": 0.0,
        "goal": "minimize",
        "description": "Ackley 2D usando coordenadas espaciales x, y. Mínimo en (0, 0)."
    },
    "Rosenbrock 1D / Valle": {
        "formula": "(1 - x)**2 + 100 * (x - x**2)**2",
        "dimensions": 1,
        "bounds": (-2.0, 2.0),
        "optimum_x": 1.0,
        "optimum_f": 0.0,
        "goal": "minimize",
        "description": "Variante univariada tipo banana/valle. Mínimo en x = 1."
    },
    "Rosenbrock 2D (x1, x2)": {
        "formula": "(1 - x1)**2 + 100 * (x2 - x1**2)**2",
        "dimensions": 2,
        "bounds": (-2.0, 2.0),
        "optimum_x": [1.0, 1.0],
        "optimum_f": 0.0,
        "goal": "minimize",
        "description": "Clásica función Banana de Rosenbrock en 2D. Mínimo global en (1, 1)."
    },
    "Picos de Michalewicz 1D": {
        "formula": "-sin(x) * (sin(1 * x**2 / pi))**20",
        "dimensions": 1,
        "bounds": (0.0, 3.14159),
        "optimum_x": 2.2029,
        "optimum_f": -1.8013,
        "goal": "minimize",
        "description": "Función con valles empinados y mesetas planas."
    },
    "Maximización de Seno Amortiguado": {
        "formula": "sin(10 * x) * x + cos(5 * x)",
        "dimensions": 1,
        "bounds": (0.0, 10.0),
        "optimum_x": 8.01,
        "optimum_f": 8.7,
        "goal": "maximize",
        "description": "Función oscilatoria creciente en amplitud para probar maximización."
    },
    "Griewank 1D": {
        "formula": "(x**2 / 4000) - cos(x) + 1",
        "dimensions": 1,
        "bounds": (-10.0, 10.0),
        "optimum_x": 0.0,
        "optimum_f": 0.0,
        "goal": "minimize",
        "description": "Función con múltiples oscilaciones que disminuyen hacia el centro."
    }
}
