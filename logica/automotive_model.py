"""
Modelo Físico-Matemático y Motores de Optimización para el Reto de Diseño Automotriz Multiobjetivo.
Implementa:
- Parte I: Variables de decisión (P, r, a, b, g, h), ecuaciones físicas no lineales,
           3 funciones objetivo (V_max, C_comb, C_fab) y 4 restricciones técnicas/económicas.
- Parte II: Transformación multiobjetivo a uniobjetivo mediante normalización Min-Max,
            suma ponderada en 3 escenarios (Deportivo, Ecológico, Económico) y penalización exterior.
- Parte III: Optimización con AG Simple, PSO (pyswarm) y Multiobjetivo puro con pymoo
             (NSGA-II, NSGA-III, C-TAEA y SMS-EMOA).
- Parte IV y VI: Experimentación estadística multasemilla (10 corridas) y Desafío Final (-10% presupuesto).
"""
import time
import math
from typing import Dict, Any, List, Tuple, Optional, Callable
import numpy as np
from pyswarm import pso

from logica.individual import Individual
from logica.population import Population
from logica.selection import tournament_selection
from logica.crossover import blx_alpha_crossover
from logica.mutation import non_uniform_mutation
from logica.replacement import generational_replacement_with_elitism

# =====================================================================
# 1. CONSTANTES DE REFERENCIA Y ESPACIO DE BÚSQUEDA (SECCIÓN 2 Y 3)
# =====================================================================
BASE_MASS = 1450.0          # kg
BASE_CD = 0.34              # Coeficiente aerodinámico inicial
FRONTAL_AREA = 2.25         # m^2
BASE_CRR = 0.013            # Coeficiente inicial de resistencia a la rodadura
AIR_DENSITY = 1.225         # kg/m^3
BASE_THERMAL_EFF = 0.25     # 25%
BASE_COST = 190000.0        # $190,000 MXN
GRAVITY = 9.81              # m/s^2
GASOLINE_ENERGY_KWH = 8.9   # kWh por litro de gasolina

# Límites de las 6 variables de decisión: [P, r, a, b, g, h]
AUTOMOTIVE_BOUNDS: List[Tuple[float, float]] = [
    (80.0, 200.0),  # P: Potencia del motor (kW)
    (0.0, 1.0),     # r: Nivel de reducción del peso
    (0.0, 1.0),     # a: Nivel de optimización aerodinámica
    (0.0, 1.0),     # b: Nivel de eficiencia de los neumáticos
    (2.8, 4.2),     # g: Relación final de transmisión
    (0.0, 1.0)      # h: Nivel de mejora de eficiencia térmica del motor
]

VARIABLE_NAMES = [
    "P (Potencia kW)",
    "r (Reducción peso)",
    "a (Aerodinámica)",
    "b (Neumáticos)",
    "g (Transmisión)",
    "h (Efic. Térmica)"
]

SCENARIO_PRESETS: Dict[str, Dict[str, Any]] = {
    "Diseño Deportivo (Prioriza Velocidad)": {
        "weights": (0.65, 0.15, 0.20),
        "description": "Prioriza maximizar la velocidad punta manteniendo consumo y costo dentro de las restricciones."
    },
    "Diseño Ecológico (Prioriza Bajo Consumo)": {
        "weights": (0.15, 0.65, 0.20),
        "description": "Prioriza minimizar el consumo ponderado (L/100 km) en los 3 ciclos de conducción."
    },
    "Diseño Económico (Prioriza Bajo Costo)": {
        "weights": (0.15, 0.20, 0.65),
        "description": "Prioriza minimizar el costo de fabricación (MXN) cumpliendo el desempeño mínimo requerido."
    },
    "Balanceado / Equitativo": {
        "weights": (0.34, 0.33, 0.33),
        "description": "Importancia simétrica entre velocidad, consumo energético y costo de producción."
    }
}

# Cotas físicas para normalización Min-Max en [0, 1]
NORM_RANGES = {
    "v_min": 180.0,
    "v_max": 265.0,
    "c_min": 4.2,
    "c_max": 11.5,
    "cost_min": 190000.0,
    "cost_max": 350000.0
}


# =====================================================================
# 2. MODELO FÍSICO-MATEMÁTICO NO LINEAL (PARTE I)
# =====================================================================
def evaluate_vehicle(x: np.ndarray | List[float], max_cost_limit: float = 315000.0) -> Dict[str, Any]:
    """
    Evalúa un vector de diseño automotriz x = [P, r, a, b, g, h] y retorna
    todas las propiedades físicas, los 3 objetivos y las 4 restricciones.
    """
    vec = np.asarray(x, dtype=float).flatten()
    P = float(np.clip(vec[0], 80.0, 200.0))
    r = float(np.clip(vec[1], 0.0, 1.0))
    a = float(np.clip(vec[2], 0.0, 1.0))
    b = float(np.clip(vec[3], 0.0, 1.0))
    g = float(np.clip(vec[4], 2.8, 4.2))
    h = float(np.clip(vec[5], 0.0, 1.0))

    # 1. Masa total del vehículo (kg):
    # Motores más grandes agregan masa (+0.9 kg/kW extra); materiales ligeros (r) reducen hasta 220 kg de forma no lineal
    mass = BASE_MASS + 0.90 * (P - 80.0) - 220.0 * (r ** 0.85)

    # 2. Coeficiente aerodinámico Cd(a) y resistencia a la rodadura Crr(b):
    cd = BASE_CD * (1.0 - 0.26 * (a ** 0.90))
    crr = BASE_CRR * (1.0 - 0.30 * (b ** 0.90))

    # 3. Eficiencia térmica efectiva del motor eta(h, P, g):
    # Crece hasta +11% con h, pero motores muy grandes y relaciones extremas tienen pérdidas por bombeo/fricción
    p_norm = (P - 80.0) / 120.0
    eta_thermal = (
        BASE_THERMAL_EFF
        + 0.11 * (h ** 0.85)
        - 0.015 * (p_norm ** 2)
        - 0.012 * ((g - 3.20) ** 2)
    )
    eta_thermal = max(0.18, min(0.40, eta_thermal))

    # 4. Objetivo 1: Velocidad Máxima V_max (km/h)
    # Acoplamiento de transmisión en velocidad punta (óptimo cerca de g = 3.45)
    eta_trans_top = 0.90 * math.exp(-0.08 * ((g - 3.45) ** 2))
    power_wheels_w = P * 1000.0 * eta_trans_top
    rolling_power_loss_w = mass * GRAVITY * crr * 52.0
    aero_factor = 0.5 * AIR_DENSITY * cd * FRONTAL_AREA
    net_aero_power = max(1000.0, power_wheels_w - rolling_power_loss_w)
    v_max_ms = (net_aero_power / aero_factor) ** (1.0 / 3.0)
    v_max_kmh = 3.6 * v_max_ms

    # 5. Aceleración de 0 a 100 km/h (s):
    # Relación corta de transmisión (g más alto) incrementa el par en rueda durante el arranque
    v_100_ms = 100.0 / 3.6
    kinetic_energy_100 = 0.5 * mass * (v_100_ms ** 2)
    effective_accel_power = P * 1000.0 * (0.58 + 0.085 * (g - 2.8)) - 4200.0 * cd
    effective_accel_power = max(15000.0, effective_accel_power)
    # Neumáticos más eficientes pero de compuesto optimizado y tracción:
    t_0_100 = (kinetic_energy_100 / effective_accel_power) + 1.15 - 0.15 * b

    # 6. Objetivo 2: Consumo de Combustible Ponderado (L/100 km)
    # Escenarios: 60 km/h (20%), 90 km/h (50%), 120 km/h (30%)
    def calc_consumption_at_speed(speed_kmh: float) -> float:
        v_ms = speed_kmh / 3.6
        f_roll = mass * GRAVITY * crr
        f_drag = 0.5 * AIR_DENSITY * cd * FRONTAL_AREA * (v_ms ** 2)
        p_traction_kw = ((f_roll + f_drag) * v_ms) / (1000.0 * 0.90)
        # Pérdida parásita del motor proporcional a la cilindrada/potencia P y régimen de giro g
        p_pumping_kw = 0.028 * P * ((g / 3.2) ** 1.3) * (speed_kmh / 90.0)
        p_total_kw = p_traction_kw + p_pumping_kw
        hours_per_100km = 100.0 / speed_kmh
        energy_kwh_100km = p_total_kw * hours_per_100km
        liters_100km = energy_kwh_100km / (eta_thermal * GASOLINE_ENERGY_KWH)
        return liters_100km

    c_60 = calc_consumption_at_speed(60.0)
    c_90 = calc_consumption_at_speed(90.0)
    c_120 = calc_consumption_at_speed(120.0)
    c_weighted = 0.20 * c_60 + 0.50 * c_90 + 0.30 * c_120

    # 7. Objetivo 3: Costo de Fabricación (MXN) con interacciones no lineales
    cost_engine = 520.0 * ((P - 80.0) ** 1.08)
    cost_lightweight = 58000.0 * (r ** 1.60)
    cost_aero = 36000.0 * (a ** 1.50)
    cost_tires = 16000.0 * (b ** 1.30)
    cost_thermal = 42000.0 * (h ** 1.50)
    cost_gearbox = 4500.0 * ((g - 3.30) ** 2)
    # Términos de interacción tecnológica no lineal:
    # 1) Chasis ultraligero con geometría aerodinámica compleja (r * a)
    # 2) Sistemas térmicos avanzados en motores de alta potencia (p_norm * h)
    cost_interaction = 18000.0 * (r * a) + 15000.0 * (p_norm * h)

    total_cost = (
        BASE_COST
        + cost_engine
        + cost_lightweight
        + cost_aero
        + cost_tires
        + cost_thermal
        + cost_gearbox
        + cost_interaction
    )

    # 8. Evaluación de las 4 restricciones de desigualdad (g_i <= 0 significa factible)
    g1_vel = 200.0 - v_max_kmh               # Velocidad máxima >= 200 km/h
    g2_acc = t_0_100 - 9.0                   # Aceleración 0-100 <= 9 s
    g3_cost = total_cost - max_cost_limit    # Costo <= $315,000 MXN (o $283,500 en desafío final)
    g4_mass = mass - 1500.0                  # Masa <= 1,500 kg

    constraints = [g1_vel, g2_acc, g3_cost, g4_mass]
    is_feasible = all(g_val <= 1e-7 for g_val in constraints)

    # Violación normalizada cuadrática para métodos de penalización
    v1 = max(0.0, g1_vel / 200.0)
    v2 = max(0.0, g2_acc / 9.0)
    v3 = max(0.0, g3_cost / max_cost_limit)
    v4 = max(0.0, g4_mass / 1500.0)
    constraint_violation = (v1 ** 2) + (v2 ** 2) + (v3 ** 2) + (v4 ** 2)

    return {
        "x": [P, r, a, b, g, h],
        "v_max": float(v_max_kmh),
        "c_comb": float(c_weighted),
        "c_60": float(c_60),
        "c_90": float(c_90),
        "c_120": float(c_120),
        "c_fab": float(total_cost),
        "mass": float(mass),
        "t_0_100": float(t_0_100),
        "cd": float(cd),
        "crr": float(crr),
        "eta_thermal": float(eta_thermal),
        "constraints": constraints,
        "is_feasible": bool(is_feasible),
        "violation": float(constraint_violation),
        "max_cost_limit": float(max_cost_limit)
    }


# =====================================================================
# 3. AGREGACIÓN UNIOBJETIVO (PARTE II)
# =====================================================================
def evaluate_scalarized(
    x: np.ndarray | List[float],
    weights: Tuple[float, float, float] = (0.34, 0.33, 0.33),
    max_cost_limit: float = 315000.0,
    penalty_factor: float = 250.0
) -> Tuple[float, Dict[str, Any]]:
    """
    Transforma las 3 funciones objetivo en un único valor escalar normalizado J(x) a minimizar,
    sumando la penalización exterior si incumple alguna de las 4 restricciones.
    """
    info = evaluate_vehicle(x, max_cost_limit=max_cost_limit)
    w_vel, w_cons, w_cost = weights
    w_sum = max(1e-9, w_vel + w_cons + w_cost)
    w_vel, w_cons, w_cost = w_vel / w_sum, w_cons / w_sum, w_cost / w_sum

    # Normalización Min-Max en sentido de minimización (0 = ideal, 1 = peor)
    f1_norm = (NORM_RANGES["v_max"] - info["v_max"]) / (NORM_RANGES["v_max"] - NORM_RANGES["v_min"])
    f2_norm = (info["c_comb"] - NORM_RANGES["c_min"]) / (NORM_RANGES["c_max"] - NORM_RANGES["c_min"])
    f3_norm = (info["c_fab"] - NORM_RANGES["cost_min"]) / (NORM_RANGES["cost_max"] - NORM_RANGES["cost_min"])

    weighted_sum = w_vel * f1_norm + w_cons * f2_norm + w_cost * f3_norm
    penalty = penalty_factor * info["violation"] + (1.5 if not info["is_feasible"] else 0.0)
    j_total = float(weighted_sum + penalty)

    info["f_norms"] = (float(f1_norm), float(f2_norm), float(f3_norm))
    info["weighted_sum"] = float(weighted_sum)
    info["j_total"] = j_total
    return j_total, info


# =====================================================================
# 4. OPTIMIZADORES UNIOBJETIVO: AG Y PSO (PARTE III-A Y III-B)
# =====================================================================
def run_automotive_ga(
    weights: Tuple[float, float, float] = (0.65, 0.15, 0.20),
    max_cost_limit: float = 315000.0,
    pop_size: int = 50,
    max_generations: int = 60,
    pc: float = 0.85,
    pm: float = 0.15,
    seed: Optional[int] = 42
) -> Dict[str, Any]:
    """Ejecuta el Algoritmo Genético sobre el modelo automotriz uniobjetivo."""
    start_t = time.time()
    if seed is not None:
        np.random.seed(int(seed))

    def obj_fn(x_vec):
        j_val, _ = evaluate_scalarized(x_vec, weights=weights, max_cost_limit=max_cost_limit)
        return j_val

    pop = Population(size=pop_size, bounds=AUTOMOTIVE_BOUNDS, seed=seed)
    total_evals = pop.evaluate(obj_fn, goal="minimize")

    best_ind = pop.best_individual(goal="minimize").copy()
    history = [{"generation": 0, "best_j": float(best_ind.objective_value)}]

    for gen in range(1, max_generations + 1):
        parents = tournament_selection(pop.individuals, pop_size, k=3)
        offspring: List[Individual] = []
        for i in range(0, len(parents), 2):
            p1 = parents[i]
            p2 = parents[i + 1] if i + 1 < len(parents) else parents[0]
            if np.random.rand() <= pc:
                h1, h2 = blx_alpha_crossover(p1, p2, alpha=0.45)
            else:
                h1, h2 = p1.copy(), p2.copy()
            offspring.append(h1)
            if len(offspring) < pop_size:
                offspring.append(h2)

        mutated = [
            non_uniform_mutation(ch, p_mut=pm, current_gen=gen, max_gen=max_generations, b=1.8)
            for ch in offspring
        ]

        for ch in mutated:
            ch.objective_value = float(obj_fn(ch.x))
            total_evals += 1

        pop.individuals = generational_replacement_with_elitism(pop.individuals, mutated, n_elite=2)
        pop.evaluate(obj_fn, goal="minimize")

        curr_best = pop.best_individual(goal="minimize")
        if curr_best.objective_value < best_ind.objective_value:
            best_ind = curr_best.copy()

        history.append({"generation": gen, "best_j": float(best_ind.objective_value)})

    elapsed = time.time() - start_t
    _, best_info = evaluate_scalarized(best_ind.genes, weights=weights, max_cost_limit=max_cost_limit)

    return {
        "algorithm": "AG",
        "best_x": best_ind.genes.tolist(),
        "best_j": float(best_ind.objective_value),
        "vehicle": best_info,
        "history": history,
        "total_evaluations": total_evals,
        "execution_time": elapsed
    }


def run_automotive_pso(
    weights: Tuple[float, float, float] = (0.65, 0.15, 0.20),
    max_cost_limit: float = 315000.0,
    swarmsize: int = 50,
    maxiter: int = 60,
    omega: float = 0.5,
    phip: float = 0.5,
    phig: float = 0.5,
    seed: Optional[int] = 42
) -> Dict[str, Any]:
    """Ejecuta PSO (pyswarm) sobre el modelo automotriz uniobjetivo."""
    start_t = time.time()
    lb = np.array([b[0] for b in AUTOMOTIVE_BOUNDS], dtype=float)
    ub = np.array([b[1] for b in AUTOMOTIVE_BOUNDS], dtype=float)

    history = []
    total_evals = 0
    curr_best_j = float("inf")

    def obj_fn(x_vec):
        nonlocal total_evals, curr_best_j
        total_evals += 1
        j_val, _ = evaluate_scalarized(x_vec, weights=weights, max_cost_limit=max_cost_limit)
        if j_val < curr_best_j:
            curr_best_j = j_val
        if total_evals % swarmsize == 0:
            it = total_evals // swarmsize
            history.append({"generation": it - 1, "best_j": float(curr_best_j)})
        return j_val

    res = pso(
        obj_fn,
        lb,
        ub,
        swarmsize=swarmsize,
        omega=omega,
        phip=phip,
        phig=phig,
        maxiter=maxiter,
        minstep=1e-9,
        minfunc=1e-9,
        seed=int(seed) if seed is not None else None
    )

    elapsed = time.time() - start_t
    best_x = np.asarray(res.x, dtype=float)
    best_j, best_info = evaluate_scalarized(best_x, weights=weights, max_cost_limit=max_cost_limit)

    return {
        "algorithm": "PSO",
        "best_x": best_x.tolist(),
        "best_j": float(best_j),
        "vehicle": best_info,
        "history": history,
        "total_evaluations": total_evals,
        "execution_time": elapsed
    }


# =====================================================================
# 5. OPTIMIZACIÓN MULTIOBJETIVO CON PYMOO: NSGA-II, NSGA-III, C-TAEA, SMS-EMOA
# =====================================================================
def run_automotive_moo(
    algorithm_name: str = "NSGA-II",
    max_cost_limit: float = 315000.0,
    pop_size: int = 64,
    n_gen: int = 70,
    seed: int = 42
) -> Dict[str, Any]:
    """
    Resuelve directamente el problema multiobjetivo (3 objetivos y 4 restricciones)
    sin agregación de pesos, usando pymoo.
    Soporta: 'NSGA-II', 'NSGA-III', 'C-TAEA' y 'SMS-EMOA'.
    """
    from pymoo.core.problem import ElementwiseProblem
    from pymoo.optimize import minimize as pymoo_minimize
    from pymoo.algorithms.moo.nsga2 import NSGA2
    from pymoo.algorithms.moo.nsga3 import NSGA3
    from pymoo.algorithms.moo.ctaea import CTAEA
    from pymoo.algorithms.moo.sms import SMSEMOA
    from pymoo.util.ref_dirs import get_reference_directions

    xl = np.array([b[0] for b in AUTOMOTIVE_BOUNDS], dtype=float)
    xu = np.array([b[1] for b in AUTOMOTIVE_BOUNDS], dtype=float)

    class AutomotiveMOOProblem(ElementwiseProblem):
        def __init__(self):
            super().__init__(n_var=6, n_obj=3, n_ieq_constr=4, xl=xl, xu=xu)

        def _evaluate(self, x, out, *args, **kwargs):
            info = evaluate_vehicle(x, max_cost_limit=max_cost_limit)
            # pymoo minimiza todos los objetivos; por tanto f1 = -V_max
            out["F"] = [-info["v_max"], info["c_comb"], info["c_fab"]]
            out["G"] = info["constraints"]

    problem = AutomotiveMOOProblem()

    # Seleccionar algoritmo multiobjetivo
    if algorithm_name == "NSGA-III":
        ref_dirs = get_reference_directions("das-dennis", 3, n_partitions=9)  # 55 direcciones uniformes
        algorithm = NSGA3(ref_dirs=ref_dirs, pop_size=max(pop_size, len(ref_dirs)))
    elif algorithm_name == "C-TAEA":
        ref_dirs = get_reference_directions("das-dennis", 3, n_partitions=9)
        algorithm = CTAEA(ref_dirs=ref_dirs)
    elif algorithm_name == "SMS-EMOA":
        algorithm = SMSEMOA(pop_size=pop_size)
    else:
        algorithm = NSGA2(pop_size=pop_size)

    start_t = time.time()
    res = pymoo_minimize(
        problem,
        algorithm,
        ("n_gen", n_gen),
        seed=int(seed),
        verbose=False
    )
    elapsed = time.time() - start_t

    # Extraer soluciones no dominadas factibles
    solutions: List[Dict[str, Any]] = []
    if res.X is not None:
        X_arr = np.atleast_2d(res.X)
        for row in X_arr:
            v_info = evaluate_vehicle(row, max_cost_limit=max_cost_limit)
            if v_info["is_feasible"]:
                solutions.append(v_info)

    # Identificar soluciones representativas del frente de Pareto:
    # 1. Máxima Velocidad, 2. Mínimo Consumo, 3. Mínimo Costo, 4. Solución Compromiso (Rodilla de Pareto)
    representatives = {}
    if solutions:
        best_speed = max(solutions, key=lambda s: s["v_max"])
        best_eco = min(solutions, key=lambda s: s["c_comb"])
        best_cost = min(solutions, key=lambda s: s["c_fab"])

        # Punto utópico en el frente actual para hallar la solución compromiso (menor distancia euclidiana normalizada)
        v_vals = np.array([s["v_max"] for s in solutions])
        c_vals = np.array([s["c_comb"] for s in solutions])
        cost_vals = np.array([s["c_fab"] for s in solutions])

        v_span = max(1e-6, np.max(v_vals) - np.min(v_vals))
        c_span = max(1e-6, np.max(c_vals) - np.min(c_vals))
        cost_span = max(1e-6, np.max(cost_vals) - np.min(cost_vals))

        best_knee = None
        min_dist = float("inf")
        for s in solutions:
            dv = (np.max(v_vals) - s["v_max"]) / v_span
            dc = (s["c_comb"] - np.min(c_vals)) / c_span
            d_cost = (s["c_fab"] - np.min(cost_vals)) / cost_span
            dist = math.sqrt(dv**2 + dc**2 + d_cost**2)
            if dist < min_dist:
                min_dist = dist
                best_knee = s

        representatives = {
            "Máxima Velocidad (Deportivo)": best_speed,
            "Mínimo Consumo (Ecológico)": best_eco,
            "Mínimo Costo (Económico)": best_cost,
            "Mejor Compromiso (Rodilla Pareto)": best_knee
        }

    return {
        "algorithm": algorithm_name,
        "solutions": solutions,
        "n_pareto": len(solutions),
        "representatives": representatives,
        "execution_time": elapsed,
        "total_evaluations": int(getattr(res.algorithm.evaluator, "n_eval", pop_size * n_gen))
    }


def run_multi_seed_experiment(
    weights: Tuple[float, float, float] = (0.65, 0.15, 0.20),
    max_cost_limit: float = 315000.0,
    n_seeds: int = 10,
    pop_size: int = 40,
    max_iter: int = 45
) -> Dict[str, Any]:
    """
    Parte IV: Ejecuta AG y PSO durante n_seeds repeticiones con semillas distintas
    y un presupuesto idéntico de evaluaciones, calculando media, desviación estándar,
    mejor valor, peor valor y porcentaje de soluciones factibles.
    """
    seeds = [100 + i * 37 for i in range(n_seeds)]
    ga_runs = []
    pso_runs = []

    for s in seeds:
        r_ga = run_automotive_ga(
            weights=weights,
            max_cost_limit=max_cost_limit,
            pop_size=pop_size,
            max_generations=max_iter,
            seed=s
        )
        r_pso = run_automotive_pso(
            weights=weights,
            max_cost_limit=max_cost_limit,
            swarmsize=pop_size,
            maxiter=max_iter,
            seed=s
        )
        ga_runs.append(r_ga)
        pso_runs.append(r_pso)

    def summarize(runs: List[Dict[str, Any]]) -> Dict[str, Any]:
        j_vals = np.array([r["best_j"] for r in runs], dtype=float)
        v_vals = np.array([r["vehicle"]["v_max"] for r in runs], dtype=float)
        c_vals = np.array([r["vehicle"]["c_comb"] for r in runs], dtype=float)
        cost_vals = np.array([r["vehicle"]["c_fab"] for r in runs], dtype=float)
        t_vals = np.array([r["execution_time"] for r in runs], dtype=float)
        feas_count = sum(1 for r in runs if r["vehicle"]["is_feasible"])
        best_idx = int(np.argmin(j_vals))

        return {
            "mean_j": float(np.mean(j_vals)),
            "std_j": float(np.std(j_vals)),
            "best_j": float(np.min(j_vals)),
            "worst_j": float(np.max(j_vals)),
            "mean_v_max": float(np.mean(v_vals)),
            "mean_c_comb": float(np.mean(c_vals)),
            "mean_c_fab": float(np.mean(cost_vals)),
            "mean_time": float(np.mean(t_vals)),
            "feasibility_rate": float(feas_count / len(runs) * 100.0),
            "best_run": runs[best_idx]
        }

    return {
        "n_seeds": n_seeds,
        "ga_summary": summarize(ga_runs),
        "pso_summary": summarize(pso_runs),
        "ga_runs": ga_runs,
        "pso_runs": pso_runs
    }

