"""
Motor de optimización por Enjambre de Partículas (Particle Swarm Optimization - PSO)
usando la librería pyswarm.
Permite optimizar funciones multivariadas (1D hasta n-D) y rastrear la convergencia por iteración.
"""
import time
from typing import Dict, Any, List, Optional, Tuple, Callable
import numpy as np
from pyswarm import pso
from logica.evaluator import SafeEvaluator

class PSOEngine:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.dimensions = int(config.get("dimensions", 2))
        
        raw_bounds = config.get("bounds", [(-10.0, 10.0)])
        if len(raw_bounds) == 1 and self.dimensions > 1:
            self.bounds = [raw_bounds[0]] * self.dimensions
        else:
            self.bounds = list(raw_bounds)
            
        self.lb = np.array([b[0] for b in self.bounds], dtype=float)
        self.ub = np.array([b[1] for b in self.bounds], dtype=float)
        
        self.swarmsize = int(config.get("swarmsize", config.get("pop_size", 40)))
        self.maxiter = int(config.get("maxiter", config.get("max_generations", 60)))
        self.omega = float(config.get("omega", 0.5))
        self.phip = float(config.get("phip", 0.5))
        self.phig = float(config.get("phig", 0.5))
        self.seed = config.get("seed", None)
        
        self.expression = config.get("expression", "x1**2 + x2**2")
        self.goal = config.get("goal", "minimize")
        self.evaluator = SafeEvaluator(self.expression, dimensions=self.dimensions, goal=self.goal)
        
        self.history: List[Dict[str, Any]] = []
        self.total_evaluations: int = 0
        self.execution_time: float = 0.0
        self.best_x: Optional[np.ndarray] = None
        self.best_fx: Optional[float] = None
        
    def run(self, callback: Optional[Callable[[int, Dict[str, Any]], None]] = None) -> Dict[str, Any]:
        """
        Ejecuta PSO y rastrea la curva de mejor valor f(x) encontrado por iteración.
        """
        start_time = time.time()
        self.history = []
        self.total_evaluations = 0
        
        curr_best_fx = float("inf")
        curr_best_x = None
        current_iter = 0
        
        def obj_func(x):
            nonlocal curr_best_fx, curr_best_x, current_iter
            self.total_evaluations += 1
            raw_val = self.evaluator.evaluate(x)
            
            # PSO siempre minimiza internamente; si el objetivo es maximizar, invertimos el signo
            val_to_minimize = raw_val if self.goal == "minimize" else -raw_val
            
            if val_to_minimize < curr_best_fx:
                curr_best_fx = val_to_minimize
                curr_best_x = np.array(x, dtype=float)
                
            if self.total_evaluations % self.swarmsize == 0:
                current_iter = self.total_evaluations // self.swarmsize
                real_fx = curr_best_fx if self.goal == "minimize" else -curr_best_fx
                step_data = {
                    "iteration": current_iter,
                    "best_fx": float(real_fx),
                    "best_x": curr_best_x.tolist() if curr_best_x is not None else [],
                    "evaluations": self.total_evaluations
                }
                self.history.append(step_data)
                if callback:
                    callback(current_iter, step_data)
                    
            return val_to_minimize

        res = pso(
            obj_func,
            self.lb,
            self.ub,
            swarmsize=self.swarmsize,
            omega=self.omega,
            phip=self.phip,
            phig=self.phig,
            maxiter=self.maxiter,
            minstep=1e-9,
            minfunc=1e-9,
            seed=int(self.seed) if self.seed is not None else None,
            particle_output=True
        )
        
        self.execution_time = time.time() - start_time
        final_best_x = np.asarray(res.x, dtype=float)
        real_best_fx = float(self.evaluator.evaluate(final_best_x))
        
        self.best_x = final_best_x
        self.best_fx = real_best_fx
        
        # Formatear vector solución
        if len(final_best_x) == 1:
            best_x_fmt = f"{final_best_x[0]:.4f}"
            best_x_val = float(final_best_x[0])
        else:
            best_x_fmt = "[" + ", ".join(f"{v:.4f}" for v in final_best_x) + "]"
            best_x_val = final_best_x.tolist()
            
        return {
            "best_x": best_x_val,
            "best_x_formatted": best_x_fmt,
            "best_fx": real_best_fx,
            "iterations": getattr(res, "nit", self.maxiter),
            "total_evaluations": self.total_evaluations,
            "execution_time": self.execution_time,
            "success": getattr(res, "success", True),
            "history": self.history
        }
