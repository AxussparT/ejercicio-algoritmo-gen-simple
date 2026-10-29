"""
Panel de visualización numérica de métricas y estado en tiempo real.
"""
import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional
from ui.styles import COLORS, FONTS

class MetricsPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="Card.TFrame", padding=6)

        # Variables de estado y métricas
        self.status_var = tk.StringVar(value="Listo para iniciar")
        self.best_x_var = tk.StringVar(value="--")
        self.best_fx_var = tk.StringVar(value="--")
        self.fitness_var = tk.StringVar(value="--")
        self.gen_var = tk.StringVar(value="0 / 0")
        self.evals_var = tk.StringVar(value="0")
        self.time_var = tk.StringVar(value="0.00 s")

        self._build_ui()

    def _build_ui(self):
        # Fila 1: Barra de Estado con progreso textual
        status_bar = ttk.Frame(self, style="SecondaryCard.TFrame", padding=4)
        status_bar.pack(fill="x", pady=(0, 6))

        ttk.Label(status_bar, text="Estado:", style="Subtitle.TLabel").pack(side="left", padx=(4, 6))
        self.lbl_status = ttk.Label(status_bar, textvariable=self.status_var, style="Card.TLabel", font=FONTS["subtitle"])
        self.lbl_status.pack(side="left")

        # Fila 2: Cuadrícula de métricas en tarjetas
        metrics_grid = ttk.Frame(self, style="Card.TFrame")
        metrics_grid.pack(fill="x")

        # Columnas de tarjetas métricas
        cards = [
            ("Mejor x", self.best_x_var, COLORS["primary"]),
            ("Mejor f(x)", self.best_fx_var, COLORS["success"]),
            ("Aptitud (Fitness)", self.fitness_var, COLORS["accent"]),
            ("Generación", self.gen_var, COLORS["warning"]),
            ("Evaluaciones", self.evals_var, COLORS["fg_text"]),
            ("Tiempo", self.time_var, COLORS["fg_subtext"])
        ]

        for i, (title, var, color) in enumerate(cards):
            card_f = ttk.Frame(metrics_grid, style="SecondaryCard.TFrame", padding=6)
            card_f.grid(row=0, column=i, sticky="nsew", padx=3)
            metrics_grid.columnconfigure(i, weight=1)

            lbl_t = ttk.Label(card_f, text=title, font=FONTS["metric_lbl"], background=COLORS["bg_card_secondary"], foreground=COLORS["fg_subtext"])
            lbl_t.pack(anchor="center")

            lbl_v = tk.Label(card_f, textvariable=var, font=FONTS["metric_val"], bg=COLORS["bg_card_secondary"], fg=color)
            lbl_v.pack(anchor="center")

    def update_metrics(
        self,
        status: str,
        best_x: Any = None,
        best_fx: Optional[float] = None,
        best_fitness: Optional[float] = None,
        current_gen: int = 0,
        max_gen: int = 0,
        evaluations: int = 0,
        elapsed_time: float = 0.0
    ):
        self.status_var.set(status)
        if best_x is not None:
            if isinstance(best_x, (int, float)):
                self.best_x_var.set(f"{best_x:.6f}")
            elif isinstance(best_x, (list, tuple)):
                if len(best_x) <= 3:
                    s = ", ".join(f"{v:.3f}" for v in best_x)
                    self.best_x_var.set(f"[{s}]")
                else:
                    s = f"[{best_x[0]:.2f}, {best_x[1]:.2f}, ...]"
                    self.best_x_var.set(s)
            else:
                self.best_x_var.set(str(best_x))
        if best_fx is not None:
            self.best_fx_var.set(f"{best_fx:.6f}")
        if best_fitness is not None:
            self.fitness_var.set(f"{best_fitness:.4f}")
        self.gen_var.set(f"{current_gen} / {max_gen}")
        self.evals_var.set(str(evaluations))
        self.time_var.set(f"{elapsed_time:.2f} s")

    def reset(self):
        self.status_var.set("Listo")
        self.best_x_var.set("--")
        self.best_fx_var.set("--")
        self.fitness_var.set("--")
        self.gen_var.set("0 / 0")
        self.evals_var.set("0")
        self.time_var.set("0.00 s")
