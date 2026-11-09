"""
Gestor de persistencia e historial de experimentos para las 3 modalidades del sistema:
1. Algoritmo Genético Univariado / Multivariado (AG)
2. Comparativa AG vs Enjambre de Partículas (PSO con pyswarm)
3. Diseño Automotriz Multiobjetivo (AG, PSO, NSGA-II, NSGA-III, C-TAEA, SMS-EMOA y Experimento 10 Semillas)

Almacena todas las ejecuciones en JSON estructurado incluyendo todos los hiperparámetros
de cada método, genera reportes detallados en TXT y permite exportar resultados completos a CSV y TXT.
"""
import os
import json
import csv
import shutil
from datetime import datetime
from typing import Dict, Any, List


class ExperimentLogger:
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            curr_file_dir = os.path.dirname(os.path.abspath(__file__))
            self.records_dir = os.path.join(curr_file_dir, "registros")
        else:
            self.records_dir = base_dir

        os.makedirs(self.records_dir, exist_ok=True)

    # =========================================================================
    # 1. GUARDADO DE EJECUCIÓN ESTÁNDAR AG (PESTAÑA 1)
    # =========================================================================
    def save_run(self, config: Dict[str, Any], results: Dict[str, Any]) -> str:
        """Guarda una corrida del Algoritmo Genético (Pestaña 1) en JSON y TXT."""
        now = datetime.now()
        timestamp_str = now.strftime("%Y%m%d_%H%M%S")
        func_name = config.get("function_name", "custom_func").replace(" ", "_").replace("/", "_")
        run_id = f"run_{timestamp_str}_AG_{func_name}"

        record = {
            "run_id": run_id,
            "experiment_type": "ga",
            "timestamp": now.isoformat(),
            "date_readable": now.strftime("%Y-%m-%d %H:%M:%S"),
            "display_title": f"[AG] {config.get('function_name', 'Personalizada')}",
            "display_metric": results.get("best_fx"),
            "configuration": {
                "experiment_type": "ga",
                "function_name": config.get("function_name", "Personalizada"),
                "expression": config.get("expression", "x**2"),
                "dimensions": config.get("dimensions", 1),
                "bounds": config.get("bounds", [(-10.0, 10.0)]),
                "goal": config.get("goal", "minimize"),
                "pop_size": config.get("pop_size", 40),
                "max_generations": config.get("max_generations", 60),
                "pc": config.get("pc", 0.8),
                "pm": config.get("pm", 0.1),
                "seed": config.get("seed", None),
                "selection_method": config.get("selection_method", "Torneo"),
                "selection_params": config.get("selection_params", {}),
                "crossover_method": config.get("crossover_method", "BLX-α"),
                "crossover_params": config.get("crossover_params", {}),
                "mutation_method": config.get("mutation_method", "Uniforme"),
                "mutation_params": config.get("mutation_params", {}),
                "replacement_method": config.get("replacement_method", "Generacional con elitismo"),
                "replacement_params": config.get("replacement_params", {})
            },
            "results_summary": {
                "best_x": results.get("best_x"),
                "best_fx": results.get("best_fx"),
                "best_fitness": results.get("best_fitness"),
                "best_generation": results.get("best_generation"),
                "total_evaluations": results.get("total_evaluations"),
                "execution_time_seconds": results.get("execution_time"),
                "stopped_early": results.get("stopped_early", False)
            },
            "history": results.get("history", [])
        }

        self._save_files(run_id, record, self._write_txt_ga)
        return run_id

    # =========================================================================
    # 2. GUARDADO DE COMPARATIVA AG VS PSO (PESTAÑA 2)
    # =========================================================================
    def save_comparison_run(
        self,
        config: Dict[str, Any],
        ga_res: Dict[str, Any],
        pso_res: Dict[str, Any]
    ) -> str:
        """Guarda una corrida comparativa AG vs PSO (Pestaña 2) con todos los hiperparámetros."""
        now = datetime.now()
        timestamp_str = now.strftime("%Y%m%d_%H%M%S")
        preset_short = config.get("preset_name", "Comparativa").split(" (")[0].replace(" ", "_")
        run_id = f"run_{timestamp_str}_COMP_{preset_short}"

        goal = config.get("goal", "minimize")
        ga_fx = ga_res.get("best_fx", 0.0)
        pso_fx = pso_res.get("best_fx", 0.0)
        best_overall = min(ga_fx, pso_fx) if goal == "minimize" else max(ga_fx, pso_fx)

        record = {
            "run_id": run_id,
            "experiment_type": "comparison",
            "timestamp": now.isoformat(),
            "date_readable": now.strftime("%Y-%m-%d %H:%M:%S"),
            "display_title": f"[AG vs PSO] {config.get('preset_name', config.get('expression', ''))}",
            "display_metric": best_overall,
            "configuration": {
                "experiment_type": "comparison",
                "preset_name": config.get("preset_name", "Personalizada..."),
                "expression": config.get("expression", "x1**2 + x2**2"),
                "dimensions": config.get("dimensions", 2),
                "bounds": config.get("bounds", [(-10.0, 10.0), (-10.0, 10.0)]),
                "goal": goal,
                "pop_size": config.get("pop_size", 40),
                "max_generations": config.get("max_generations", 50),
                "seed": config.get("seed", 42),
                "ga_hyperparameters": config.get("ga_hyperparameters", {
                    "pop_size": config.get("pop_size", 40),
                    "max_generations": config.get("max_generations", 50),
                    "pc": 0.85,
                    "pm": 0.10,
                    "selection_method": "Torneo",
                    "selection_params": {"k": 3},
                    "crossover_method": "BLX-α",
                    "crossover_params": {"alpha": 0.5},
                    "mutation_method": "No uniforme",
                    "mutation_params": {"b": 1.5},
                    "replacement_method": "Generacional con elitismo",
                    "replacement_params": {"n_elite": 2}
                }),
                "pso_hyperparameters": config.get("pso_hyperparameters", {
                    "swarmsize": config.get("pop_size", 40),
                    "maxiter": config.get("max_generations", 50),
                    "omega": config.get("omega", 0.5),
                    "phip": config.get("phip", 0.5),
                    "phig": config.get("phig", 0.5),
                    "minstep": 1e-9,
                    "minfunc": 1e-9
                })
            },
            "results_summary": {
                "best_fx": best_overall,
                "ga": {
                    "best_x": ga_res.get("best_x"),
                    "best_x_formatted": ga_res.get("best_x_formatted"),
                    "best_fx": ga_fx,
                    "execution_time": ga_res.get("execution_time"),
                    "total_evaluations": ga_res.get("total_evaluations")
                },
                "pso": {
                    "best_x": pso_res.get("best_x"),
                    "best_x_formatted": pso_res.get("best_x_formatted"),
                    "best_fx": pso_fx,
                    "execution_time": pso_res.get("execution_time"),
                    "total_evaluations": pso_res.get("total_evaluations")
                }
            },
            "ga_history": ga_res.get("history", []),
            "pso_history": pso_res.get("history", [])
        }

        self._save_files(run_id, record, self._write_txt_comparison)
        return run_id

    # =========================================================================
    # 3. GUARDADO DE DISEÑO AUTOMOTRIZ MULTIOBJETIVO (PESTAÑA 3)
    # =========================================================================
    def save_automotive_run(
        self,
        config: Dict[str, Any],
        ga_res: Dict[str, Any],
        pso_res: Dict[str, Any],
        moo_res: Dict[str, Any]
    ) -> str:
        """
        Guarda una ejecución completa del Reto de Diseño Automotriz Multiobjetivo
        (AG + PSO + Frente de Pareto MOO) incluyendo todos los hiperparámetros de los 3 métodos
        y todas las soluciones encontradas.
        """
        now = datetime.now()
        timestamp_str = now.strftime("%Y%m%d_%H%M%S")
        moo_alg = moo_res.get("algorithm", "NSGA-III")
        scen_short = config.get("scenario", "Deportivo").split(" (")[0].replace(" ", "_")
        run_id = f"run_{timestamp_str}_AUTO_{scen_short}_{moo_alg}"

        pop_size = config.get("pop_size", 55)
        max_gen = config.get("max_generations", 60)
        seed = config.get("seed", 42)
        max_cost = config.get("max_cost_limit", 315000.0)
        challenge_active = bool(config.get("challenge_mode", False))

        record = {
            "run_id": run_id,
            "experiment_type": "automotive",
            "timestamp": now.isoformat(),
            "date_readable": now.strftime("%Y-%m-%d %H:%M:%S"),
            "display_title": f"[Automotriz {moo_alg}] {scen_short}" + (" (-10% Presup.)" if challenge_active else ""),
            "display_metric": ga_res.get("best_j"),
            "configuration": {
                "experiment_type": "automotive",
                "scenario": config.get("scenario", "Diseño Deportivo (Prioriza Velocidad)"),
                "weights": {
                    "w_vel": config.get("w_vel", 0.65),
                    "w_cons": config.get("w_cons", 0.15),
                    "w_cost": config.get("w_cost", 0.20)
                },
                "challenge_mode": challenge_active,
                "max_cost_limit": max_cost,
                "constraints_spec": {
                    "v_max_min_kmh": 200.0,
                    "t_0_100_max_s": 9.0,
                    "c_fab_max_mxn": max_cost,
                    "mass_max_kg": 1500.0,
                    "driving_cycle_weights": "20% a 60 km/h | 50% a 90 km/h | 30% a 120 km/h"
                },
                "decision_variables_bounds": {
                    "P_potencia_kW": [80.0, 200.0],
                    "r_reduccion_peso": [0.0, 1.0],
                    "a_aerodinamica": [0.0, 1.0],
                    "b_neumaticos": [0.0, 1.0],
                    "g_transmision": [2.8, 4.2],
                    "h_eficiencia_termica": [0.0, 1.0]
                },
                "pop_size": pop_size,
                "max_generations": max_gen,
                "seed": seed,
                "moo_algorithm": moo_alg,
                "hyperparameters_all_methods": {
                    "AG_Uniobjetivo": {
                        "pop_size": pop_size,
                        "max_generations": max_gen,
                        "pc_prob_cruce": 0.85,
                        "pm_prob_mutacion": 0.15,
                        "selection_method": "Torneo",
                        "selection_params": {"k": 3},
                        "crossover_method": "BLX-α",
                        "crossover_params": {"alpha": 0.45},
                        "mutation_method": "No uniforme",
                        "mutation_params": {"b": 1.8},
                        "replacement_method": "Generacional con elitismo",
                        "replacement_params": {"n_elite": 2},
                        "scalarization": "Suma Ponderada Normalizada Min-Max + Penalización Exterior (lambda=250)",
                        "seed": seed
                    },
                    "PSO_Uniobjetivo_pyswarm": {
                        "swarmsize": pop_size,
                        "maxiter": max_gen,
                        "omega_inercia": 0.5,
                        "phip_cognitivo": 0.5,
                        "phig_social": 0.5,
                        "minstep": 1e-9,
                        "minfunc": 1e-9,
                        "scalarization": "Suma Ponderada Normalizada Min-Max + Penalización Exterior (lambda=250)",
                        "seed": seed
                    },
                    "Multiobjetivo_Pymoo": {
                        "algorithm": moo_alg,
                        "pop_size": pop_size,
                        "n_gen": max_gen,
                        "n_var": 6,
                        "n_obj": 3,
                        "n_ieq_constr": 4,
                        "reference_directions": "Das-Dennis (n_partitions=9, 55 direcciones)" if moo_alg in ("NSGA-III", "C-TAEA") else "N/A (Crowding / HV)",
                        "crossover_operator": "SBX (Simulated Binary Crossover)",
                        "mutation_operator": "Polynomial Mutation (PM)",
                        "constraint_handling": "Principio de Dominancia con Restricciones de Deb",
                        "seed": seed
                    }
                }
            },
            "results_summary": {
                "best_fx": ga_res.get("best_j"),
                "ga_result": {
                    "best_j": ga_res.get("best_j"),
                    "execution_time": ga_res.get("execution_time"),
                    "total_evaluations": ga_res.get("total_evaluations"),
                    "vehicle": ga_res.get("vehicle")
                },
                "pso_result": {
                    "best_j": pso_res.get("best_j"),
                    "execution_time": pso_res.get("execution_time"),
                    "total_evaluations": pso_res.get("total_evaluations"),
                    "vehicle": pso_res.get("vehicle")
                },
                "moo_result": {
                    "algorithm": moo_alg,
                    "n_pareto_solutions": moo_res.get("n_pareto", 0),
                    "execution_time": moo_res.get("execution_time"),
                    "total_evaluations": moo_res.get("total_evaluations"),
                    "representatives": moo_res.get("representatives", {})
                }
            },
            "pareto_front_solutions": moo_res.get("solutions", []),
            "ga_history": ga_res.get("history", []),
            "pso_history": pso_res.get("history", [])
        }

        self._save_files(run_id, record, self._write_txt_automotive)
        return run_id

    # =========================================================================
    # 4. GUARDADO DE EXPERIMENTO ESTADÍSTICO 10 SEMILLAS (PARTE IV)
    # =========================================================================
    def save_automotive_10seeds_run(
        self,
        config: Dict[str, Any],
        stats: Dict[str, Any]
    ) -> str:
        """Guarda el experimento estadístico de 10 semillas aleatorias (Parte IV) en JSON y TXT."""
        now = datetime.now()
        timestamp_str = now.strftime("%Y%m%d_%H%M%S")
        scen_short = config.get("scenario", "Deportivo").split(" (")[0].replace(" ", "_")
        run_id = f"run_{timestamp_str}_AUTO_10SEEDS_{scen_short}"

        ga_s = stats["ga_summary"]
        pso_s = stats["pso_summary"]

        record = {
            "run_id": run_id,
            "experiment_type": "automotive_10seeds",
            "timestamp": now.isoformat(),
            "date_readable": now.strftime("%Y-%m-%d %H:%M:%S"),
            "display_title": f"[10 Semillas Automotriz] {scen_short}",
            "display_metric": ga_s.get("mean_j"),
            "configuration": {
                "experiment_type": "automotive",
                "scenario": config.get("scenario", "Diseño Deportivo (Prioriza Velocidad)"),
                "weights": {
                    "w_vel": config.get("w_vel", 0.65),
                    "w_cons": config.get("w_cons", 0.15),
                    "w_cost": config.get("w_cost", 0.20)
                },
                "challenge_mode": bool(config.get("challenge_mode", False)),
                "max_cost_limit": config.get("max_cost_limit", 315000.0),
                "n_seeds": stats.get("n_seeds", 10),
                "seeds_used": [100 + i * 37 for i in range(stats.get("n_seeds", 10))],
                "pop_size": config.get("pop_size", 40),
                "max_generations": config.get("max_generations", 40),
                "moo_algorithm": config.get("moo_algorithm", "NSGA-III"),
                "hyperparameters_all_methods": {
                    "AG": {
                        "pop_size": 40,
                        "max_generations": 40,
                        "pc": 0.85,
                        "pm": 0.15,
                        "selection": "Torneo (k=3)",
                        "crossover": "BLX-α (alpha=0.45)",
                        "mutation": "No uniforme (b=1.8)",
                        "replacement": "Generacional con elitismo (n_elite=2)"
                    },
                    "PSO": {
                        "swarmsize": 40,
                        "maxiter": 40,
                        "omega": 0.5,
                        "phip": 0.5,
                        "phig": 0.5
                    }
                }
            },
            "results_summary": {
                "best_fx": ga_s.get("best_j"),
                "ga_summary": {k: v for k, v in ga_s.items() if k != "best_run"},
                "pso_summary": {k: v for k, v in pso_s.items() if k != "best_run"}
            },
            "individual_runs": [
                {
                    "seed_index": idx + 1,
                    "seed": 100 + idx * 37,
                    "ga_best_j": r_ga["best_j"],
                    "ga_v_max": r_ga["vehicle"]["v_max"],
                    "ga_c_comb": r_ga["vehicle"]["c_comb"],
                    "ga_c_fab": r_ga["vehicle"]["c_fab"],
                    "ga_t_0_100": r_ga["vehicle"]["t_0_100"],
                    "ga_mass": r_ga["vehicle"]["mass"],
                    "ga_feasible": r_ga["vehicle"]["is_feasible"],
                    "ga_time_s": r_ga["execution_time"],
                    "pso_best_j": r_pso["best_j"],
                    "pso_v_max": r_pso["vehicle"]["v_max"],
                    "pso_c_comb": r_pso["vehicle"]["c_comb"],
                    "pso_c_fab": r_pso["vehicle"]["c_fab"],
                    "pso_t_0_100": r_pso["vehicle"]["t_0_100"],
                    "pso_mass": r_pso["vehicle"]["mass"],
                    "pso_feasible": r_pso["vehicle"]["is_feasible"],
                    "pso_time_s": r_pso["execution_time"]
                }
                for idx, (r_ga, r_pso) in enumerate(zip(stats["ga_runs"], stats["pso_runs"]))
            ]
        }

        self._save_files(run_id, record, self._write_txt_automotive_10seeds)
        return run_id

    # =========================================================================
    # ESCRITURA DE ARCHIVOS JSON Y REPORTES TXT
    # =========================================================================
    def _save_files(self, run_id: str, record: Dict[str, Any], txt_writer_fn):
        json_path = os.path.join(self.records_dir, f"{run_id}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(record, f, indent=4, ensure_ascii=False)

        txt_path = os.path.join(self.records_dir, f"{run_id}.txt")
        txt_writer_fn(txt_path, record)

    def _write_txt_ga(self, filepath: str, record: Dict[str, Any]):
        cfg = record["configuration"]
        res = record["results_summary"]
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("======================================================================\n")
            f.write("           REPORTE DE EJECUCIÓN - ALGORITMO GENÉTICO (AG)             \n")
            f.write("======================================================================\n")
            f.write(f"ID Ejecución:    {record['run_id']}\n")
            f.write(f"Fecha y Hora:    {record['date_readable']}\n\n")
            f.write("--- CONFIGURACIÓN DEL PROBLEMA ---\n")
            f.write(f"Función:         {cfg['function_name']}\n")
            f.write(f"Expresión f(x):  {cfg['expression']}\n")
            f.write(f"Dimensiones (n): {cfg.get('dimensions', 1)}\n")
            f.write(f"Intervalo [a,b]: {cfg['bounds'][0]}\n")
            f.write(f"Objetivo:        {cfg['goal'].upper()}\n")
            f.write(f"Semilla:         {cfg['seed']}\n\n")
            f.write("--- HIPERPARÁMETROS DEL ALGORITMO GENÉTICO ---\n")
            f.write(f"Población (N):   {cfg['pop_size']}\n")
            f.write(f"Generaciones(T): {cfg['max_generations']}\n")
            f.write(f"Prob. Cruce:     {cfg['pc']}\n")
            f.write(f"Prob. Mutación:  {cfg['pm']}\n\n")
            f.write("--- MÉTODOS EVOLUTIVOS CONFIGURADOS ---\n")
            f.write(f"Selección:       {cfg['selection_method']} -> {cfg['selection_params']}\n")
            f.write(f"Cruce:           {cfg['crossover_method']} -> {cfg['crossover_params']}\n")
            f.write(f"Mutación:        {cfg['mutation_method']} -> {cfg['mutation_params']}\n")
            f.write(f"Sustitución:     {cfg['replacement_method']} -> {cfg['replacement_params']}\n\n")
            f.write("--- RESULTADOS NUMÉRICOS OBTENIDOS ---\n")
            if res['best_x'] is not None:
                if isinstance(res['best_x'], (int, float)):
                    f.write(f"Mejor x:                 {res['best_x']:.8f}\n")
                else:
                    f.write(f"Mejor x (vector):        {res['best_x']}\n")
            else:
                f.write("Mejor x:                 N/A\n")
            f.write(f"Mejor f(x):              {res['best_fx']:.8f}\n" if res['best_fx'] is not None else "Mejor f(x): N/A\n")
            f.write(f"Mejor Aptitud (Fitness): {res['best_fitness']:.8f}\n" if res['best_fitness'] is not None else "Fitness: N/A\n")
            f.write(f"Generación del hallazgo: {res['best_generation']}\n")
            f.write(f"Evaluaciones totales:    {res['total_evaluations']}\n")
            f.write(f"Tiempo de ejecución:     {res['execution_time_seconds']:.4f} segundos\n")
            f.write(f"Interrupción anticipada: {'Sí' if res['stopped_early'] else 'No'}\n")
            f.write("======================================================================\n")

    def _write_txt_comparison(self, filepath: str, record: Dict[str, Any]):
        cfg = record["configuration"]
        res = record["results_summary"]
        ga_h = cfg.get("ga_hyperparameters", {})
        pso_h = cfg.get("pso_hyperparameters", {})
        ga_r = res["ga"]
        pso_r = res["pso"]

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("======================================================================\n")
            f.write("      REPORTE COMPARATIVO: ALGORITMO GENÉTICO (AG) VS ENJAMBRE (PSO)  \n")
            f.write("======================================================================\n")
            f.write(f"ID Ejecución:    {record['run_id']}\n")
            f.write(f"Fecha y Hora:    {record['date_readable']}\n\n")
            f.write("--- 1. CONFIGURACIÓN DEL PROBLEMA ---\n")
            f.write(f"Preajuste:       {cfg.get('preset_name')}\n")
            f.write(f"Expresión f(x):  {cfg.get('expression')}\n")
            f.write(f"Dimensiones (n): {cfg.get('dimensions')}\n")
            f.write(f"Dominio [a, b]:  {cfg.get('bounds')[0]}\n")
            f.write(f"Objetivo:        {cfg.get('goal', 'minimize').upper()}\n")
            f.write(f"Semilla (Seed):  {cfg.get('seed')}\n\n")

            f.write("--- 2. HIPERPARÁMETROS DE ALGORITMO GENÉTICO (AG) ---\n")
            f.write(f"Tamaño Población (N): {ga_h.get('pop_size')}\n")
            f.write(f"Generaciones (T):     {ga_h.get('max_generations')}\n")
            f.write(f"Prob. Cruce (Pc):     {ga_h.get('pc')}\n")
            f.write(f"Prob. Mutación (Pm):  {ga_h.get('pm')}\n")
            f.write(f"Selección:            {ga_h.get('selection_method')} {ga_h.get('selection_params')}\n")
            f.write(f"Cruce:                {ga_h.get('crossover_method')} {ga_h.get('crossover_params')}\n")
            f.write(f"Mutación:             {ga_h.get('mutation_method')} {ga_h.get('mutation_params')}\n")
            f.write(f"Sustitución:          {ga_h.get('replacement_method')} {ga_h.get('replacement_params')}\n\n")

            f.write("--- 3. HIPERPARÁMETROS DE ENJAMBRE DE PARTÍCULAS (PSO - pyswarm) ---\n")
            f.write(f"Tamaño Enjambre (S):  {pso_h.get('swarmsize')}\n")
            f.write(f"Iteraciones Máx (T):  {pso_h.get('maxiter')}\n")
            f.write(f"Inercia (omega):      {pso_h.get('omega')}\n")
            f.write(f"Cognitivo (phip):     {pso_h.get('phip')}\n")
            f.write(f"Social (phig):        {pso_h.get('phig')}\n")
            f.write(f"Umbral paso/función:  minstep={pso_h.get('minstep')}, minfunc={pso_h.get('minfunc')}\n\n")

            f.write("--- 4. RESULTADOS COMPARATIVOS OBTENIDOS ---\n")
            f.write(f"[AG]  Mejor f(x*):       {ga_r['best_fx']:.10f}  ({ga_r['best_fx']:.4e})\n")
            f.write(f"[AG]  Mejor x*:          {ga_r['best_x_formatted']}\n")
            f.write(f"[AG]  Tiempo / Evals:    {ga_r['execution_time']:.4f} s  |  {ga_r['total_evaluations']} evaluaciones\n\n")
            f.write(f"[PSO] Mejor f(x*):       {pso_r['best_fx']:.10f}  ({pso_r['best_fx']:.4e})\n")
            f.write(f"[PSO] Mejor x*:          {pso_r['best_x_formatted']}\n")
            f.write(f"[PSO] Tiempo / Evals:    {pso_r['execution_time']:.4f} s  |  {pso_r['total_evaluations']} evaluaciones\n")
            f.write("======================================================================\n")

    def _write_txt_automotive(self, filepath: str, record: Dict[str, Any]):
        cfg = record["configuration"]
        res = record["results_summary"]
        hps = cfg["hyperparameters_all_methods"]
        ag_hp = hps["AG_Uniobjetivo"]
        pso_hp = hps["PSO_Uniobjetivo_pyswarm"]
        moo_hp = hps["Multiobjetivo_Pymoo"]

        def fmt_vehicle(title: str, v: Dict[str, Any], extra_line: str = "") -> str:
            if not v:
                return f"  {title}: N/A\n"
            x = v["x"]
            status = "FACTIBLE (Cumple las 4 restricciones)" if v["is_feasible"] else "INFACTIBLE"
            lines = [
                f"  >>> {title} [{status}]",
                f"      Variables [P, r, a, b, g, h]: P={x[0]:.2f} kW, r={x[1]:.4f}, a={x[2]:.4f}, b={x[3]:.4f}, g={x[4]:.4f}, h={x[5]:.4f}",
                f"      Objetivos:   V_máx = {v['v_max']:.2f} km/h | Consumo Pond. = {v['c_comb']:.3f} L/100km | Costo = ${v['c_fab']:,.2f} MXN",
                f"      Desglose Consumo: 60km/h={v['c_60']:.2f} L | 90km/h={v['c_90']:.2f} L | 120km/h={v['c_120']:.2f} L",
                f"      Física y Restricciones: 0-100 km/h = {v['t_0_100']:.2f} s (<=9s) | Masa = {v['mass']:.1f} kg (<=1500kg) | Cd={v['cd']:.3f} | Efic.Térm={v['eta_thermal']*100:.1f}%"
            ]
            if extra_line:
                lines.append(f"      {extra_line}")
            return "\n".join(lines) + "\n\n"

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("================================================================================\n")
            f.write("     REPORTE DE OPTIMIZACIÓN - DISEÑO AUTOMOTRIZ MULTIOBJETIVO (AG/PSO/MOO)     \n")
            f.write("================================================================================\n")
            f.write(f"ID Ejecución:          {record['run_id']}\n")
            f.write(f"Fecha y Hora:          {record['date_readable']}\n")
            f.write(f"Escenario Ponderado:   {cfg['scenario']}\n")
            f.write(f"Pesos (w_v, w_c, w_$): ({cfg['weights']['w_vel']}, {cfg['weights']['w_cons']}, {cfg['weights']['w_cost']})\n")
            f.write(f"Desafío Final (-10%):  {'ACTIVO (Tope $283,500 MXN)' if cfg['challenge_mode'] else 'Inactivo (Tope estándar $315,000 MXN)'}\n\n")

            f.write("--- 1. HIPERPARÁMETROS DE TODOS LOS MÉTODOS EJECUTADOS ---\n")
            f.write("[A] ALGORITMO GENÉTICO SIMPLE (AG):\n")
            f.write(f"    • Población (N): {ag_hp['pop_size']} | Generaciones (T): {ag_hp['max_generations']} | Semilla: {ag_hp['seed']}\n")
            f.write(f"    • Prob. Cruce (Pc): {ag_hp['pc_prob_cruce']} | Prob. Mutación (Pm): {ag_hp['pm_prob_mutacion']}\n")
            f.write(f"    • Operadores: Selección={ag_hp['selection_method']} {ag_hp['selection_params']}, "
                    f"Cruce={ag_hp['crossover_method']} {ag_hp['crossover_params']}, "
                    f"Mutación={ag_hp['mutation_method']} {ag_hp['mutation_params']}, "
                    f"Reemplazo={ag_hp['replacement_method']} {ag_hp['replacement_params']}\n")
            f.write(f"    • Agregación: {ag_hp['scalarization']}\n\n")

            f.write("[B] ENJAMBRE DE PARTÍCULAS (PSO - pyswarm):\n")
            f.write(f"    • Enjambre (S): {pso_hp['swarmsize']} | Iteraciones (T): {pso_hp['maxiter']} | Semilla: {pso_hp['seed']}\n")
            f.write(f"    • Inercia (omega): {pso_hp['omega_inercia']} | Cognitivo (phip): {pso_hp['phip_cognitivo']} | Social (phig): {pso_hp['phig_social']}\n")
            f.write(f"    • Umbrales: minstep={pso_hp['minstep']}, minfunc={pso_hp['minfunc']}\n\n")

            f.write(f"[C] ALGORITMO MULTIOBJETIVO PARETO ({moo_hp['algorithm']} - pymoo):\n")
            f.write(f"    • Algoritmo: {moo_hp['algorithm']} | Población: {moo_hp['pop_size']} | Generaciones: {moo_hp['n_gen']} | Semilla: {moo_hp['seed']}\n")
            f.write(f"    • Direcciones de Referencia: {moo_hp['reference_directions']}\n")
            f.write(f"    • Operadores MOO: Cruce={moo_hp['crossover_operator']} | Mutación={moo_hp['mutation_operator']}\n")
            f.write(f"    • Manejo de Restricciones: {moo_hp['constraint_handling']}\n\n")

            f.write("--- 2. RESULTADOS UNIOBJETIVO (PARTE II Y III-A/B) ---\n")
            ga_r = res["ga_result"]
            pso_r = res["pso_result"]
            f.write(fmt_vehicle(
                "ALGORITMO GENÉTICO (AG)",
                ga_r["vehicle"],
                f"J(x) Agregado = {ga_r['best_j']:.6f} | Tiempo = {ga_r['execution_time']:.4f} s | Evaluaciones = {ga_r['total_evaluations']}"
            ))
            f.write(fmt_vehicle(
                "ENJAMBRE DE PARTÍCULAS (PSO)",
                pso_r["vehicle"],
                f"J(x) Agregado = {pso_r['best_j']:.6f} | Tiempo = {pso_r['execution_time']:.4f} s | Evaluaciones = {pso_r['total_evaluations']}"
            ))

            moo_r = res["moo_result"]
            f.write(f"--- 3. FRENTE DE PARETO MULTIOBJETIVO ({moo_r['algorithm']} - {moo_r['n_pareto_solutions']} SOLUCIONES NO DOMINADAS) ---\n")
            f.write(f"Tiempo de ejecución MOO: {moo_r['execution_time']:.4f} s | Evaluaciones: {moo_r['total_evaluations']}\n\n")
            for rep_title, rep_v in moo_r.get("representatives", {}).items():
                f.write(fmt_vehicle(f"{moo_r['algorithm']} - {rep_title}", rep_v))

            f.write("================================================================================\n")

    def _write_txt_automotive_10seeds(self, filepath: str, record: Dict[str, Any]):
        cfg = record["configuration"]
        ga_s = record["results_summary"]["ga_summary"]
        pso_s = record["results_summary"]["pso_summary"]
        runs = record.get("individual_runs", [])

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("================================================================================\n")
            f.write("   REPORTE ESTADÍSTICO DE 10 SEMILLAS - DISEÑO AUTOMOTRIZ (PARTE IV: AG vs PSO) \n")
            f.write("================================================================================\n")
            f.write(f"ID Ejecución:        {record['run_id']}\n")
            f.write(f"Fecha y Hora:        {record['date_readable']}\n")
            f.write(f"Escenario:           {cfg['scenario']}\n")
            f.write(f"Pesos:               w_vel={cfg['weights']['w_vel']}, w_cons={cfg['weights']['w_cons']}, w_cost={cfg['weights']['w_cost']}\n")
            f.write(f"Tope Presupuestal:   ${cfg['max_cost_limit']:,.2f} MXN\n")
            f.write(f"Semillas Evaluadas:  {cfg['seeds_used']}\n\n")

            f.write("--- 1. HIPERPARÁMETROS FIJOS EN LAS 10 CORRIDAS ---\n")
            f.write(f"AG:  {cfg['hyperparameters_all_methods']['AG']}\n")
            f.write(f"PSO: {cfg['hyperparameters_all_methods']['PSO']}\n\n")

            f.write("--- 2. RESUMEN ESTADÍSTICO DESCRIPTIVO (10 REPETICIONES) ---\n")
            f.write(f"Métrica                      | Algoritmo Genético (AG) | Enjambre Partículas (PSO)\n")
            f.write(f"-----------------------------|-------------------------|--------------------------\n")
            f.write(f"Media J(x) Ponderado         | {ga_s['mean_j']:23.6f} | {pso_s['mean_j']:24.6f}\n")
            f.write(f"Desviación Estándar J(x)     | {ga_s['std_j']:23.6f} | {pso_s['std_j']:24.6f}\n")
            f.write(f"Mejor J(x)                   | {ga_s['best_j']:23.6f} | {pso_s['best_j']:24.6f}\n")
            f.write(f"Peor J(x)                    | {ga_s['worst_j']:23.6f} | {pso_s['worst_j']:24.6f}\n")
            f.write(f"Velocidad Máx Media (km/h)   | {ga_s['mean_v_max']:23.2f} | {pso_s['mean_v_max']:24.2f}\n")
            f.write(f"Consumo Medio (L/100km)      | {ga_s['mean_c_comb']:23.3f} | {pso_s['mean_c_comb']:24.3f}\n")
            f.write(f"Costo Medio ($ MXN)          | ${ga_s['mean_c_fab']:22,.2f} | ${pso_s['mean_c_fab']:23,.2f}\n")
            f.write(f"Tasa de Factibilidad (%)     | {ga_s['feasibility_rate']:22.1f}% | {pso_s['feasibility_rate']:23.1f}%\n")
            f.write(f"Tiempo Medio por Corrida (s) | {ga_s['mean_time']:22.4f}s | {pso_s['mean_time']:23.4f}s\n\n")

            f.write("--- 3. DESGLOSE DE LAS 10 REPETICIONES POR SEMILLA ---\n")
            for r in runs:
                f.write(
                    f"Corrida #{r['seed_index']:02d} (Seed={r['seed']}): "
                    f"AG [J={r['ga_best_j']:.5f}, V={r['ga_v_max']:.1f}, C={r['ga_c_comb']:.2f}, $={r['ga_c_fab']:,.0f}] | "
                    f"PSO [J={r['pso_best_j']:.5f}, V={r['pso_v_max']:.1f}, C={r['pso_c_comb']:.2f}, $={r['pso_c_fab']:,.0f}]\n"
                )
            f.write("================================================================================\n")

    # =========================================================================
    # EXPORTACIÓN UNIVERSAL A CSV Y TXT
    # =========================================================================
    def export_history_to_csv(self, run_id: str, dest_csv_path: str) -> bool:
        """
        Exporta los datos completos de cualquier tipo de experimento a CSV:
        - 'ga': Evolución generacional.
        - 'comparison': Curva comparativa iteración por iteración (AG vs PSO).
        - 'automotive': Tabla completa de soluciones (AG, PSO, Representativos y Frente de Pareto completo con sus 6 variables y 4 restricciones).
        - 'automotive_10seeds': Desglose de las 10 repeticiones por semilla.
        """
        json_path = os.path.join(self.records_dir, f"{run_id}.json")
        if not os.path.exists(json_path):
            return False

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        exp_type = data.get("experiment_type", "ga")

        with open(dest_csv_path, "w", newline="", encoding="utf-8-sig") as f:
            if exp_type == "ga":
                history = data.get("history", [])
                if not history:
                    return False
                keys = ["generation", "evaluations", "best_x", "best_fx", "best_fitness", "mean_fx", "std_fx", "mean_fitness"]
                writer = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
                writer.writeheader()
                for row in history:
                    writer.writerow(row)
                return True

            elif exp_type == "comparison":
                ga_h = data.get("ga_history", [])
                pso_h = data.get("pso_history", [])
                max_len = max(len(ga_h), len(pso_h))
                writer = csv.writer(f)
                writer.writerow(["iteracion", "ag_mejor_fx", "ag_promedio_fx", "pso_mejor_fx", "pso_evaluaciones"])
                for i in range(max_len):
                    g_row = ga_h[i] if i < len(ga_h) else {}
                    p_row = pso_h[i] if i < len(pso_h) else {}
                    writer.writerow([
                        i,
                        g_row.get("best_fx", ""),
                        g_row.get("mean_fx", ""),
                        p_row.get("best_fx", ""),
                        p_row.get("evaluations", "")
                    ])
                return True

            elif exp_type == "automotive":
                writer = csv.writer(f)
                writer.writerow([
                    "Metodo_o_Perfil", "Es_Factible", "V_max_kmh", "Consumo_Pond_L100km",
                    "Consumo_60kmh", "Consumo_90kmh", "Consumo_120kmh", "Costo_Fab_MXN",
                    "Acel_0_100_s", "Masa_kg", "Cd", "Crr", "Efic_Termica",
                    "P_kW", "r_peso", "a_aero", "b_neum", "g_trans", "h_term"
                ])

                def write_v(label: str, v: Dict[str, Any]):
                    if not v:
                        return
                    x = v.get("x", [0]*6)
                    writer.writerow([
                        label,
                        "SI" if v.get("is_feasible") else "NO",
                        round(v.get("v_max", 0), 4),
                        round(v.get("c_comb", 0), 4),
                        round(v.get("c_60", 0), 4),
                        round(v.get("c_90", 0), 4),
                        round(v.get("c_120", 0), 4),
                        round(v.get("c_fab", 0), 2),
                        round(v.get("t_0_100", 0), 4),
                        round(v.get("mass", 0), 2),
                        round(v.get("cd", 0), 4),
                        round(v.get("crr", 0), 5),
                        round(v.get("eta_thermal", 0), 4),
                        round(x[0], 4), round(x[1], 4), round(x[2], 4),
                        round(x[3], 4), round(x[4], 4), round(x[5], 4)
                    ])

                res_s = data.get("results_summary", {})
                write_v("AG_Optimo_Uniobjetivo", res_s.get("ga_result", {}).get("vehicle"))
                write_v("PSO_Optimo_Uniobjetivo", res_s.get("pso_result", {}).get("vehicle"))

                moo_r = res_s.get("moo_result", {})
                alg_name = moo_r.get("algorithm", "MOO")
                for rep_k, rep_v in moo_r.get("representatives", {}).items():
                    write_v(f"{alg_name}_{rep_k}", rep_v)

                for idx, sol in enumerate(data.get("pareto_front_solutions", []), start=1):
                    write_v(f"{alg_name}_Pareto_Sol_{idx:02d}", sol)
                return True

            elif exp_type == "automotive_10seeds":
                runs = data.get("individual_runs", [])
                if not runs:
                    return False
                keys = list(runs[0].keys())
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                for r in runs:
                    writer.writerow(r)
                return True

        return False

    def export_txt_report(self, run_id: str, dest_txt_path: str) -> bool:
        """Copia/exporta el reporte completo TXT (con todos los hiperparámetros y resultados) a la ruta elegida."""
        src_txt = os.path.join(self.records_dir, f"{run_id}.txt")
        if not os.path.exists(src_txt):
            return False
        shutil.copyfile(src_txt, dest_txt_path)
        return True

    def list_experiments(self) -> List[Dict[str, Any]]:
        """Retorna la lista de ejecuciones guardadas de todas las pestañas, ordenadas de la más reciente a la más antigua."""
        experiments = []
        for filename in os.listdir(self.records_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(self.records_dir, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        cfg = data.get("configuration", {})
                        res = data.get("results_summary", {})
                        title = data.get("display_title") or cfg.get("function_name", "Ejecución")
                        metric = data.get("display_metric")
                        if metric is None:
                            metric = res.get("best_fx")
                        experiments.append({
                            "run_id": data.get("run_id", filename[:-5]),
                            "experiment_type": data.get("experiment_type", cfg.get("experiment_type", "ga")),
                            "timestamp": data.get("timestamp", ""),
                            "date_readable": data.get("date_readable", ""),
                            "function": title,
                            "best_x": res.get("best_x"),
                            "best_fx": metric,
                            "json_path": filepath
                        })
                except Exception:
                    continue
        experiments.sort(key=lambda x: x["timestamp"], reverse=True)
        return experiments

    def load_experiment(self, run_id: str) -> Dict[str, Any]:
        """Carga el registro JSON completo de un experimento."""
        json_path = os.path.join(self.records_dir, f"{run_id}.json")
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
