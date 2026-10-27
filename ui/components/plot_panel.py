"""
Panel de visualización gráfica con Matplotlib embebido en Tkinter.
Muestra:
1. Paisaje de la función f(x) con la población y el óptimo encontrado.
2. Curva de convergencia generacional (Mejor vs Promedio).
"""
import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Any, Optional
import numpy as np

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from logica.evaluator import SafeEvaluator
from logica.individual import Individual
from ui.styles import COLORS

class PlotPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="Card.TFrame")

        # Configurar figura de Matplotlib con fondo adaptado al tema oscuro
        self.fig = Figure(figsize=(7.5, 6.2), dpi=100, facecolor=COLORS["bg_card"])
        self.ax_func = self.fig.add_subplot(2, 1, 1)
        self.ax_conv = self.fig.add_subplot(2, 1, 2)
        self.fig.tight_layout(pad=3.0)

        # Embeber canvas en Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill="both", expand=True, padx=4, pady=4)

        self._style_axes()
        self.show_placeholder()

    def _style_axes(self):
        for ax in [self.ax_func, self.ax_conv]:
            ax.set_facecolor(COLORS["bg_dark"])
            ax.tick_params(colors=COLORS["fg_subtext"], labelsize=8)
            for spine in ax.spines.values():
                spine.set_color(COLORS["border"])
            ax.grid(True, linestyle="--", alpha=0.25, color=COLORS["fg_subtext"])

    def show_placeholder(self):
        """Muestra una pantalla inicial antes de ejecutar o seleccionar."""
        self.ax_func.clear()
        self.ax_conv.clear()
        self._style_axes()

        self.ax_func.set_title("Paisaje de la Función f(x) y Población", color=COLORS["primary"], fontsize=10, fontweight="bold")
        self.ax_func.text(0.5, 0.5, "Seleccione o previsualice una función para graficar.",
                          color=COLORS["fg_subtext"], ha="center", va="center", transform=self.ax_func.transAxes)

        self.ax_conv.set_title("Curva de Convergencia por Generación", color=COLORS["accent"], fontsize=10, fontweight="bold")
        self.ax_conv.text(0.5, 0.5, "Los datos de convergencia aparecerán durante la ejecución.",
                          color=COLORS["fg_subtext"], ha="center", va="center", transform=self.ax_conv.transAxes)

        self.canvas.draw_idle()

    def plot_preview(self, expr: str, a: float, b: float):
        """Grafica la función pura antes de iniciar la optimización."""
        self.ax_func.clear()
        self._style_axes()

        try:
            ev = SafeEvaluator(expr)
            xs = np.linspace(a, b, 400)
            ys = ev.evaluate(xs)

            self.ax_func.plot(xs, ys, color=COLORS["primary"], linewidth=2.0, label="f(x)")
            self.ax_func.set_title(f"Función: {expr}", color=COLORS["primary"], fontsize=10, fontweight="bold")
            self.ax_func.set_xlabel("x", color=COLORS["fg_subtext"], fontsize=8)
            self.ax_func.set_ylabel("f(x)", color=COLORS["fg_subtext"], fontsize=8)
            self.ax_func.set_xlim(a, b)
            self.ax_func.legend(loc="upper right", facecolor=COLORS["bg_card"], edgecolor=COLORS["border"], labelcolor=COLORS["fg_text"])
            self.canvas.draw_idle()
        except Exception:
            pass

    def update_plots(
        self,
        expr: str,
        a: float,
        b: float,
        population: List[Individual],
        best_ind: Optional[Individual],
        history: List[Dict[str, Any]],
        goal: str = "minimize"
    ):
        """Actualiza ambas gráficas con la población actual y la convergencia histórica."""
        # 1. Gráfica de Paisaje y Población
        self.ax_func.clear()
        self._style_axes()

        try:
            ev = SafeEvaluator(expr)
            xs = np.linspace(a, b, 300)
            ys = ev.evaluate(xs)
            self.ax_func.plot(xs, ys, color=COLORS["primary"], linewidth=1.8, label="f(x)", zorder=1)
        except Exception:
            pass

        # Graficar individuos actuales
        if population:
            pop_x = [ind.x for ind in population]
            pop_y = [ind.objective_value for ind in population]
            self.ax_func.scatter(pop_x, pop_y, color="#fab387", alpha=0.75, s=30, label="Individuos", zorder=2)

        # Destacar mejor solución
        if best_ind is not None:
            self.ax_func.scatter(
                [best_ind.x], [best_ind.objective_value],
                color="#f38ba8", s=130, marker="*", edgecolor="#ffffff", linewidth=1.2,
                label=f"Mejor: x={best_ind.x:.4f}, f={best_ind.objective_value:.4f}", zorder=3
            )

        self.ax_func.set_title(f"Paisaje f(x) e Individuos en el Espacio de Búsqueda", color=COLORS["primary"], fontsize=10, fontweight="bold")
        self.ax_func.set_xlabel("x", color=COLORS["fg_subtext"], fontsize=8)
        self.ax_func.set_ylabel("f(x)", color=COLORS["fg_subtext"], fontsize=8)
        self.ax_func.set_xlim(a, b)
        self.ax_func.legend(loc="best", facecolor=COLORS["bg_card"], edgecolor=COLORS["border"], labelcolor=COLORS["fg_text"], fontsize=7)

        # 2. Gráfica de Convergencia
        self.ax_conv.clear()
        self._style_axes()

        if history:
            gens = [h["generation"] for h in history]
            best_fxs = [h["best_fx"] for h in history]
            mean_fxs = [h["mean_fx"] for h in history]

            self.ax_conv.plot(gens, best_fxs, color="#a6e3a1", linewidth=2.0, label="Mejor f(x)")
            self.ax_conv.plot(gens, mean_fxs, color="#cba6f7", linewidth=1.5, linestyle="--", label="Promedio Población")

            self.ax_conv.set_title(f"Convergencia Evolutiva ({goal.capitalize()})", color=COLORS["accent"], fontsize=10, fontweight="bold")
            self.ax_conv.set_xlabel("Generación", color=COLORS["fg_subtext"], fontsize=8)
            self.ax_conv.set_ylabel("Valor f(x)", color=COLORS["fg_subtext"], fontsize=8)
            self.ax_conv.legend(loc="best", facecolor=COLORS["bg_card"], edgecolor=COLORS["border"], labelcolor=COLORS["fg_text"], fontsize=8)

        self.canvas.draw_idle()
