"""
Gestor de persistencia e historial de experimentos.
Almacena ejecuciones en JSON estructurado, genera reportes en TXT y permite exportar a CSV.
"""
import os
import json
import csv
from datetime import datetime
from typing import Dict, Any, List

class ExperimentLogger:
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            # Directorio por defecto dentro de almacenamiento/registros
            curr_file_dir = os.path.dirname(os.path.abspath(__file__))
            self.records_dir = os.path.join(curr_file_dir, "registros")
        else:
            self.records_dir = base_dir

        os.makedirs(self.records_dir, exist_ok=True)

    def save_run(self, config: Dict[str, Any], results: Dict[str, Any]) -> str:
        """
        Guarda la ejecución actual en un archivo JSON completo y genera un reporte en TXT.
        Retorna el identificador o nombre base del archivo.
        """
        now = datetime.now()
        timestamp_str = now.strftime("%Y%m%d_%H%M%S")
        func_name = config.get("function_name", "custom_func").replace(" ", "_").replace("/", "_")
        run_id = f"run_{timestamp_str}_{func_name}"

        # Estructura del registro
        record = {
            "run_id": run_id,
            "timestamp": now.isoformat(),
            "date_readable": now.strftime("%Y-%m-%d %H:%M:%S"),
            "configuration": {
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

        # 1. Guardar JSON
        json_path = os.path.join(self.records_dir, f"{run_id}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(record, f, indent=4, ensure_ascii=False)

        # 2. Guardar TXT legible
        txt_path = os.path.join(self.records_dir, f"{run_id}.txt")
        self._write_txt_summary(txt_path, record)

        return run_id

    def _write_txt_summary(self, filepath: str, record: Dict[str, Any]):
        cfg = record["configuration"]
        res = record["results_summary"]
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("======================================================================\n")
            f.write(f"           REPORTE DE EJECUCIÓN - ALGORITMO GENÉTICO                \n")
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
            f.write(f"Población:       {cfg['pop_size']}\n")
            f.write(f"Generaciones:    {cfg['max_generations']}\n")
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

    def export_history_to_csv(self, run_id: str, dest_csv_path: str) -> bool:
        """Exporta la tabla generacional de un experimento a CSV."""
        json_path = os.path.join(self.records_dir, f"{run_id}.json")
        if not os.path.exists(json_path):
            return False

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        history = data.get("history", [])
        if not history:
            return False

        keys = ["generation", "evaluations", "best_x", "best_fx", "best_fitness", "mean_fx", "std_fx", "mean_fitness"]
        with open(dest_csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore')
            writer.writeheader()
            for row in history:
                writer.writerow(row)
        return True

    def list_experiments(self) -> List[Dict[str, Any]]:
        """Retorna la lista de ejecuciones guardadas, ordenadas de la más reciente a la más antigua."""
        experiments = []
        for filename in os.listdir(self.records_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(self.records_dir, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        experiments.append({
                            "run_id": data.get("run_id", filename[:-5]),
                            "timestamp": data.get("timestamp", ""),
                            "date_readable": data.get("date_readable", ""),
                            "function": data.get("configuration", {}).get("function_name", "Desconocida"),
                            "best_x": data.get("results_summary", {}).get("best_x"),
                            "best_fx": data.get("results_summary", {}).get("best_fx"),
                            "json_path": filepath
                        })
                except Exception:
                    continue
        experiments.sort(key=lambda x: x["timestamp"], reverse=True)
        return experiments

    def load_experiment(self, run_id: str) -> Dict[str, Any]:
        """Carga el registro completo de un experimento."""
        json_path = os.path.join(self.records_dir, f"{run_id}.json")
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
