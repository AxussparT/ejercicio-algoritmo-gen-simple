"""
Panel de visualización gráfica con Matplotlib embebido en Tkinter.
Soporta visualización adaptativa según la dimensión del problema:
- 1D: Curva analítica f(x), población y óptimo.
- 2D: Mapa de contornos y dispersión de la población en el plano (x1, x2).
- n-D: Dispersión de la población proyectada en (x1, x2) y perfil de variables del mejor individuo.
- Subplot inferior: Curva de convergencia por generación (universal para cualquier n).
"""
import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Any, Optional, Tuple
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

        self.fig = Figure(figsize=(7.5, 6.2), dpi=100, facecolor=COLORS["bg_card"])
        self.ax_func = self.fig.add_subplot(2, 1, 1)
        self.ax_conv = self.fig.add_subplot(2, 1, 2)
        self.fig.tight_layout(pad=3.0)

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
        self.ax_func.clear()
        self.ax_conv.clear()
        self._style_axes()

        self.ax_func.set_title("Espacio de Búsqueda y Población (1D a n-D)", color=COLORS["primary"], fontsize=10, fontweight="bold")
        self.ax_func.text(0.5, 0.5, "Seleccione o previsualice una función para graficar.",
                          color=COLORS["fg_subtext"], ha="center", va="center", transform=self.ax_func.transAxes)

        self.ax_conv.set_title("Curva de Convergencia por Generación", color=COLORS["accent"], fontsize=10, fontweight="bold")
        self.ax_conv.text(0.5, 0.5, "Los datos de convergencia aparecerán durante la ejecución.",
                          color=COLORS["fg_subtext"], ha="center", va="center", transform=self.ax_conv.transAxes)

        self.canvas.draw_idle()

    def plot_preview(self, expr: str, a: float, b: float, dims: int = 1):
        """Grafica la función antes de la optimización según el número de dimensiones."""
        self.ax_func.clear()
        self._style_axes()

        try:
            ev = SafeEvaluator(expr, dimensions=dims)
            if dims == 1:
                xs = np.linspace(a, b, 400)
                ys = [ev(x) for x in xs]
                self.ax_func.plot(xs, ys, color=COLORS["primary"], linewidth=2.0, label="f(x)")
                self.ax_func.set_title(f"Función 1D: {expr}", color=COLORS["primary"], fontsize=10, fontweight="bold")
                self.ax_func.set_xlabel("x", color=COLORS["fg_subtext"], fontsize=8)
                self.ax_func.set_ylabel("f(x)", color=COLORS["fg_subtext"], fontsize=8)
                self.ax_func.set_xlim(a, b)
                self.ax_func.legend(loc="upper right", facecolor=COLORS["bg_card"], edgecolor=COLORS["border"], labelcolor=COLORS["fg_text"])
            elif dims == 2:
                # Contorno 2D
                x1 = np.linspace(a, b, 80)
                x2 = np.linspace(a, b, 80)
                X1, X2 = np.meshgrid(x1, x2)
                Z = np.zeros_like(X1)
                for i in range(X1.shape[0]):
                    for j in range(X1.shape[1]):
                        Z[i, j] = ev([X1[i, j], X2[i, j]])
                
                cp = self.ax_func.contourf(X1, X2, Z, levels=25, cmap="viridis", alpha=0.85)
                self.ax_func.set_title(f"Paisaje 2D: {expr}", color=COLORS["primary"], fontsize=10, fontweight="bold")
                self.ax_func.set_xlabel("x1", color=COLORS["fg_subtext"], fontsize=8)
                self.ax_func.set_ylabel("x2", color=COLORS["fg_subtext"], fontsize=8)
                self.ax_func.set_xlim(a, b)
                self.ax_func.set_ylim(a, b)
            else:
                # n > 2: corte central o indicación analítica
                xs = np.linspace(a, b, 200)
                mid = (a + b) / 2.0
                ys = [ev([x] + [mid]*(dims-1)) for x in xs]
                self.ax_func.plot(xs, ys, color=COLORS["primary"], linewidth=1.8, label=f"Corte x1 (x2..x{dims}={mid:.1f})")
                self.ax_func.set_title(f"Función {dims}D: {expr} (Corte unidimensional de referencia)", color=COLORS["primary"], fontsize=9, fontweight="bold")
                self.ax_func.set_xlabel("x1", color=COLORS["fg_subtext"], fontsize=8)
                self.ax_func.set_ylabel("f(x)", color=COLORS["fg_subtext"], fontsize=8)
                self.ax_func.legend(loc="upper right", facecolor=COLORS["bg_card"], edgecolor=COLORS["border"], labelcolor=COLORS["fg_text"])

            self.canvas.draw_idle()
        except Exception:
            pass

    def update_plots(
        self,
        expr: str,
        bounds: List[Tuple[float, float]],
        population: List[Individual],
        best_ind: Optional[Individual],
        history: List[Dict[str, Any]],
        goal: str = "minimize",
        dims: int = 1
    ):
        """Actualiza ambas gráficas con la población actual y la convergencia."""
        self.ax_func.clear()
        self._style_axes()

        a, b = bounds[0][0], bounds[0][1]

        try:
            ev = SafeEvaluator(expr, dimensions=dims)
        except Exception:
            ev = None

        if dims == 1:
            # --- MODO 1D ---
            if ev:
                xs = np.linspace(a, b, 300)
                ys = [ev(x) for x in xs]
                self.ax_func.plot(xs, ys, color=COLORS["primary"], linewidth=1.8, label="f(x)", zorder=1)

            if population:
                pop_x = [float(ind.genes[0]) for ind in population]
                pop_y = [ind.objective_value for ind in population]
                self.ax_func.scatter(pop_x, pop_y, color="#fab387", alpha=0.75, s=30, label="Individuos", zorder=2)

            if best_ind is not None:
                self.ax_func.scatter(
                    [float(best_ind.genes[0])], [best_ind.objective_value],
                    color="#f38ba8", s=130, marker="*", edgecolor="#ffffff", linewidth=1.2,
                    label=f"Mejor: x={best_ind.genes[0]:.4f}, f={best_ind.objective_value:.4f}", zorder=3
                )
            self.ax_func.set_title("Paisaje f(x) e Individuos en el Espacio de Búsqueda (1D)", color=COLORS["primary"], fontsize=10, fontweight="bold")
            self.ax_func.set_xlabel("x", color=COLORS["fg_subtext"], fontsize=8)
            self.ax_func.set_ylabel("f(x)", color=COLORS["fg_subtext"], fontsize=8)
            self.ax_func.set_xlim(a, b)

        elif dims == 2:
            # --- MODO 2D ---
            if ev:
                x1 = np.linspace(a, b, 50)
                x2 = np.linspace(a, b, 50)
                X1, X2 = np.meshgrid(x1, x2)
                Z = np.zeros_like(X1)
                for i in range(X1.shape[0]):
                    for j in range(X1.shape[1]):
                        Z[i, j] = ev([X1[i, j], X2[i, j]])
                self.ax_func.contourf(X1, X2, Z, levels=20, cmap="viridis", alpha=0.6, zorder=1)

            if population:
                pop_x1 = [float(ind.genes[0]) for ind in population]
                pop_x2 = [float(ind.genes[1]) for ind in population]
                self.ax_func.scatter(pop_x1, pop_x2, color="#fab387", alpha=0.8, s=35, edgecolor="#11111b", label="Población (x1, x2)", zorder=2)

            if best_ind is not None:
                self.ax_func.scatter(
                    [float(best_ind.genes[0])], [float(best_ind.genes[1])],
                    color="#f38ba8", s=140, marker="*", edgecolor="#ffffff", linewidth=1.2,
                    label=f"Mejor: ({best_ind.genes[0]:.3f}, {best_ind.genes[1]:.3f}), f={best_ind.objective_value:.4f}", zorder=3
                )
            self.ax_func.set_title("Plano de Búsqueda 2D (x1, x2) y Distribución Poblacional", color=COLORS["primary"], fontsize=10, fontweight="bold")
            self.ax_func.set_xlabel("x1", color=COLORS["fg_subtext"], fontsize=8)
            self.ax_func.set_ylabel("x2", color=COLORS["fg_subtext"], fontsize=8)
            self.ax_func.set_xlim(a, b)
            self.ax_func.set_ylim(a, b)

        else:
            # --- MODO n-D (n > 2) ---
            # Scatter proyectado en las dos primeras componentes (x1, x2)
            if population:
                pop_x1 = [float(ind.genes[0]) for ind in population]
                pop_x2 = [float(ind.genes[1]) for ind in population]
                self.ax_func.scatter(pop_x1, pop_x2, color="#fab387", alpha=0.75, s=30, label="Población (x1 vs x2)", zorder=2)

            if best_ind is not None:
                self.ax_func.scatter(
                    [float(best_ind.genes[0])], [float(best_ind.genes[1])],
                    color="#f38ba8", s=140, marker="*", edgecolor="#ffffff", linewidth=1.2,
                    label=f"Mejor: f(x)={best_ind.objective_value:.4f}", zorder=3
                )
            self.ax_func.set_title(f"Población Proyectada en (x1, x2) de {dims} Dimensiones", color=COLORS["primary"], fontsize=10, fontweight="bold")
            self.ax_func.set_xlabel("x1", color=COLORS["fg_subtext"], fontsize=8)
            self.ax_func.set_ylabel("x2", color=COLORS["fg_subtext"], fontsize=8)
            self.ax_func.set_xlim(a, b)
            self.ax_func.set_ylim(a, b)

        self.ax_func.legend(loc="upper right", facecolor=COLORS["bg_card"], edgecolor=COLORS["border"], labelcolor=COLORS["fg_text"], fontsize=7)

        # 2. Gráfica de Convergencia (Universal para cualquier dimensión)
        self.ax_conv.clear()
        self._style_axes()

        if history:
            gens = [h["generation"] for h in history]
            best_fxs = [h["best_fx"] for h in history]
            mean_fxs = [h["mean_fx"] for h in history]

            self.ax_conv.plot(gens, best_fxs, color="#a6e3a1", linewidth=2.0, label="Mejor f(x)")
            self.ax_conv.plot(gens, mean_fxs, color="#cba6f7", linewidth=1.5, linestyle="--", label="Promedio Población")

            self.ax_conv.set_title(f"Convergencia Evolutiva ({goal.capitalize()} en {dims}D)", color=COLORS["accent"], fontsize=10, fontweight="bold")
            self.ax_conv.set_xlabel("Generación", color=COLORS["fg_subtext"], fontsize=8)
            self.ax_conv.set_ylabel("Valor f(x)", color=COLORS["fg_subtext"], fontsize=8)
            self.ax_conv.legend(loc="best", facecolor=COLORS["bg_card"], edgecolor=COLORS["border"], labelcolor=COLORS["fg_text"], fontsize=8)

        self.canvas.draw_idle()
