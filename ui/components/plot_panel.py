"""
Panel de visualización gráfica con Matplotlib embebido en Tkinter.
Soporta:
- 1D: Curva analítica f(x), población y óptimo.
- 2D: Vista de contorno cenital (2D) con botón interactivo para abrir la Superficie 3D.
- n > 2: Panel superior dividido en (Izquierda: Dispersión proyectada x1 vs x2 | Derecha: Gráfica de barras por cada dimensión x1..xn del mejor individuo).
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
from ui.styles import COLORS, FONTS
from ui.components.plot3d_window import Plot3DWindow

class PlotPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="Card.TFrame")

        # Barra superior de control del panel de gráficas
        self.header_frame = ttk.Frame(self, style="Card.TFrame", padding=(6, 4))
        self.header_frame.pack(fill="x", side="top")

        self.lbl_plot_title = ttk.Label(
            self.header_frame,
            text="📈 Visualización del Espacio de Búsqueda y Población",
            style="Subtitle.TLabel",
            font=FONTS["subtitle"]
        )
        self.lbl_plot_title.pack(side="left")

        # Botón para vista 3D interactiva (se activa cuando dims == 2)
        self.btn_open_3d = ttk.Button(
            self.header_frame,
            text="🌐 Abrir Superficie 3D Interactiva",
            style="Secondary.TButton",
            command=self._open_3d_view,
            state="disabled"
        )
        self.btn_open_3d.pack(side="right")

        # Figura principal: 2 filas. Fila 1 para paisajes/barras; Fila 2 para convergencia.
        self.fig = Figure(figsize=(7.5, 6.2), dpi=100, facecolor=COLORS["bg_card"])
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill="both", expand=True, padx=4, pady=4)

        # Contexto guardado de la última visualización
        self.last_expr: str = "x**2"
        self.last_a: float = -10.0
        self.last_b: float = 10.0
        self.last_dims: int = 1
        self.last_population: Optional[List[Individual]] = None
        self.last_best_ind: Optional[Individual] = None
        self.last_goal: str = "minimize"

        self.show_placeholder()

    def _open_3d_view(self):
        """Abre la ventana emergente con la gráfica 3D interactiva de la función 2D."""
        if self.last_dims == 2:
            Plot3DWindow(
                self,
                expr=self.last_expr,
                a=self.last_a,
                b=self.last_b,
                population=self.last_population,
                best_ind=self.last_best_ind,
                goal=self.last_goal
            )

    def _style_axes(self, axes_list):
        for ax in axes_list:
            ax.set_facecolor(COLORS["bg_dark"])
            ax.tick_params(colors=COLORS["fg_subtext"], labelsize=8)
            for spine in ax.spines.values():
                spine.set_color(COLORS["border"])
            ax.grid(True, linestyle="--", alpha=0.25, color=COLORS["fg_subtext"])

    def show_placeholder(self):
        self.fig.clear()
        ax_top = self.fig.add_subplot(2, 1, 1)
        ax_bottom = self.fig.add_subplot(2, 1, 2)
        self.fig.tight_layout(pad=3.0)
        self._style_axes([ax_top, ax_bottom])

        ax_top.set_title("Espacio de Búsqueda y Población (1D a n-D)", color=COLORS["primary"], fontsize=10, fontweight="bold")
        ax_top.text(0.5, 0.5, "Seleccione o previsualice una función para graficar.",
                    color=COLORS["fg_subtext"], ha="center", va="center", transform=ax_top.transAxes)

        ax_bottom.set_title("Curva de Convergencia por Generación", color=COLORS["accent"], fontsize=10, fontweight="bold")
        ax_bottom.text(0.5, 0.5, "Los datos de convergencia aparecerán durante la ejecución.",
                       color=COLORS["fg_subtext"], ha="center", va="center", transform=ax_bottom.transAxes)

        self.canvas.draw_idle()

    def plot_preview(self, expr: str, a: float, b: float, dims: int = 1):
        """Grafica la función antes de la optimización según el número de dimensiones."""
        self.last_expr = expr
        self.last_a = a
        self.last_b = b
        self.last_dims = dims

        # Habilitar o deshabilitar botón 3D
        if dims == 2:
            self.btn_open_3d.config(state="normal")
        else:
            self.btn_open_3d.config(state="disabled")

        self.fig.clear()

        try:
            ev = SafeEvaluator(expr, dimensions=dims)
        except Exception:
            ev = None

        if dims <= 2:
            ax_func = self.fig.add_subplot(2, 1, 1)
            ax_conv = self.fig.add_subplot(2, 1, 2)
            self.fig.tight_layout(pad=3.0)
            self._style_axes([ax_func, ax_conv])

            if dims == 1 and ev:
                xs = np.linspace(a, b, 400)
                ys = [ev.evaluate(x, allow_nan=True) for x in xs]
                ax_func.plot(xs, ys, color=COLORS["primary"], linewidth=2.0, label="f(x)")
                ax_func.set_title(f"Función 1D: {expr}", color=COLORS["primary"], fontsize=10, fontweight="bold")
                ax_func.set_xlabel("x", color=COLORS["fg_subtext"], fontsize=8)
                ax_func.set_ylabel("f(x)", color=COLORS["fg_subtext"], fontsize=8)
                ax_func.set_xlim(a, b)
                ax_func.legend(loc="upper right", facecolor=COLORS["bg_card"], edgecolor=COLORS["border"], labelcolor=COLORS["fg_text"])
            elif dims == 2 and ev:
                x1 = np.linspace(a, b, 70)
                x2 = np.linspace(a, b, 70)
                X1, X2 = np.meshgrid(x1, x2)
                Z = np.zeros_like(X1)
                for i in range(X1.shape[0]):
                    for j in range(X1.shape[1]):
                        Z[i, j] = ev.evaluate([X1[i, j], X2[i, j]], allow_nan=True)
                ax_func.contourf(X1, X2, Z, levels=25, cmap="viridis", alpha=0.85)
                ax_func.set_title(f"Paisaje 2D: {expr} (Haga clic en 'Abrir Superficie 3D' para vista interactiva)",
                                  color=COLORS["primary"], fontsize=9, fontweight="bold")
                ax_func.set_xlabel("x1", color=COLORS["fg_subtext"], fontsize=8)
                ax_func.set_ylabel("x2", color=COLORS["fg_subtext"], fontsize=8)
                ax_func.set_xlim(a, b)
                ax_func.set_ylim(a, b)

            ax_conv.set_title("Curva de Convergencia por Generación", color=COLORS["accent"], fontsize=10, fontweight="bold")
            ax_conv.text(0.5, 0.5, "Los datos de convergencia aparecerán durante la ejecución.",
                         color=COLORS["fg_subtext"], ha="center", va="center", transform=ax_conv.transAxes)

        else:
            # dims > 2: Arriba se divide en 2 columnas (Proyección x1 vs x2 + Gráfica de Barras por cada variable)
            ax_proj = self.fig.add_subplot(2, 2, 1)
            ax_bars = self.fig.add_subplot(2, 2, 2)
            ax_conv = self.fig.add_subplot(2, 1, 2)
            self.fig.tight_layout(pad=3.0)
            self._style_axes([ax_proj, ax_bars, ax_conv])

            # Gráfica de barras previa (valores medios como referencia)
            var_names = [f"x{i+1}" for i in range(dims)]
            mid_vals = [(a + b) / 2.0] * dims
            bars = ax_bars.bar(var_names, mid_vals, color="#89b4fa", alpha=0.7, edgecolor=COLORS["border"])
            ax_bars.set_title(f"Perfil de Variables ({dims}D)", color=COLORS["accent"], fontsize=9, fontweight="bold")
            ax_bars.set_ylabel("Valor xᵢ", color=COLORS["fg_subtext"], fontsize=8)
            ax_bars.set_ylim(a, b)
            ax_bars.axhline(0, color=COLORS["fg_subtext"], linestyle=":", alpha=0.5)

            ax_proj.set_title(f"Espacio Proyectado ({dims}D)", color=COLORS["primary"], fontsize=9, fontweight="bold")
            ax_proj.set_xlabel("x1", color=COLORS["fg_subtext"], fontsize=8)
            ax_proj.set_ylabel("x2", color=COLORS["fg_subtext"], fontsize=8)
            ax_proj.set_xlim(a, b)
            ax_proj.set_ylim(a, b)

            ax_conv.set_title("Curva de Convergencia por Generación", color=COLORS["accent"], fontsize=10, fontweight="bold")
            ax_conv.text(0.5, 0.5, "Los datos de convergencia aparecerán durante la ejecución.",
                         color=COLORS["fg_subtext"], ha="center", va="center", transform=ax_conv.transAxes)

        self.canvas.draw_idle()

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
        """Actualiza las gráficas con la población actual, óptimos y convergencia."""
        self.last_expr = expr
        self.last_a = bounds[0][0]
        self.last_b = bounds[0][1]
        self.last_dims = dims
        self.last_population = population
        self.last_best_ind = best_ind
        self.last_goal = goal

        if dims == 2:
            self.btn_open_3d.config(state="normal")
        else:
            self.btn_open_3d.config(state="disabled")

        a, b = self.last_a, self.last_b

        try:
            ev = SafeEvaluator(expr, dimensions=dims, goal=goal)
        except Exception:
            ev = None

        self.fig.clear()

        if dims <= 2:
            ax_func = self.fig.add_subplot(2, 1, 1)
            ax_conv = self.fig.add_subplot(2, 1, 2)
            self.fig.tight_layout(pad=3.0)
            self._style_axes([ax_func, ax_conv])

            if dims == 1:
                if ev:
                    xs = np.linspace(a, b, 300)
                    ys = [ev.evaluate(x, allow_nan=True) for x in xs]
                    ax_func.plot(xs, ys, color=COLORS["primary"], linewidth=1.8, label="f(x)", zorder=1)

                if population:
                    valid_inds = [ind for ind in population if abs(ind.objective_value) < 1e11]
                    pop_x = [float(ind.genes[0]) for ind in valid_inds]
                    pop_y = [ind.objective_value for ind in valid_inds]
                    if pop_x:
                        ax_func.scatter(pop_x, pop_y, color="#fab387", alpha=0.75, s=30, label="Individuos", zorder=2)

                if best_ind is not None and abs(best_ind.objective_value) < 1e11:
                    ax_func.scatter(
                        [float(best_ind.genes[0])], [best_ind.objective_value],
                        color="#f38ba8", s=130, marker="*", edgecolor="#ffffff", linewidth=1.2,
                        label=f"Mejor: x={best_ind.genes[0]:.4f}, f={best_ind.objective_value:.4f}", zorder=3
                    )
                ax_func.set_title("Paisaje f(x) e Individuos en el Espacio de Búsqueda (1D)", color=COLORS["primary"], fontsize=10, fontweight="bold")
                ax_func.set_xlabel("x", color=COLORS["fg_subtext"], fontsize=8)
                ax_func.set_ylabel("f(x)", color=COLORS["fg_subtext"], fontsize=8)
                ax_func.set_xlim(a, b)
                ax_func.legend(loc="upper right", facecolor=COLORS["bg_card"], edgecolor=COLORS["border"], labelcolor=COLORS["fg_text"], fontsize=7)

            elif dims == 2:
                if ev:
                    x1 = np.linspace(a, b, 50)
                    x2 = np.linspace(a, b, 50)
                    X1, X2 = np.meshgrid(x1, x2)
                    Z = np.zeros_like(X1)
                    for i in range(X1.shape[0]):
                        for j in range(X1.shape[1]):
                            Z[i, j] = ev.evaluate([X1[i, j], X2[i, j]], allow_nan=True)
                    ax_func.contourf(X1, X2, Z, levels=20, cmap="viridis", alpha=0.6, zorder=1)

                if population:
                    pop_x1 = [float(ind.genes[0]) for ind in population]
                    pop_x2 = [float(ind.genes[1]) for ind in population]
                    ax_func.scatter(pop_x1, pop_x2, color="#fab387", alpha=0.8, s=35, edgecolor="#11111b", label="Población (x1, x2)", zorder=2)

                if best_ind is not None:
                    ax_func.scatter(
                        [float(best_ind.genes[0])], [float(best_ind.genes[1])],
                        color="#f38ba8", s=140, marker="*", edgecolor="#ffffff", linewidth=1.2,
                        label=f"Mejor: ({best_ind.genes[0]:.3f}, {best_ind.genes[1]:.3f}), f={best_ind.objective_value:.4f}", zorder=3
                    )
                ax_func.set_title("Plano 2D (x1, x2) | Botón 'Abrir Superficie 3D' disponible", color=COLORS["primary"], fontsize=10, fontweight="bold")
                ax_func.set_xlabel("x1", color=COLORS["fg_subtext"], fontsize=8)
                ax_func.set_ylabel("x2", color=COLORS["fg_subtext"], fontsize=8)
                ax_func.set_xlim(a, b)
                ax_func.set_ylim(a, b)
                ax_func.legend(loc="upper right", facecolor=COLORS["bg_card"], edgecolor=COLORS["border"], labelcolor=COLORS["fg_text"], fontsize=7)

        else:
            # dims > 2: Panel superior dividido en (Dispersión x1 vs x2) y (Gráfica de barras por cada variable)
            ax_proj = self.fig.add_subplot(2, 2, 1)
            ax_bars = self.fig.add_subplot(2, 2, 2)
            ax_conv = self.fig.add_subplot(2, 1, 2)
            self.fig.tight_layout(pad=3.0)
            self._style_axes([ax_proj, ax_bars, ax_conv])

            # 1. Dispersión proyectada
            if population:
                pop_x1 = [float(ind.genes[0]) for ind in population]
                pop_x2 = [float(ind.genes[1]) for ind in population]
                ax_proj.scatter(pop_x1, pop_x2, color="#fab387", alpha=0.75, s=30, label="Población", zorder=2)

            if best_ind is not None:
                ax_proj.scatter(
                    [float(best_ind.genes[0])], [float(best_ind.genes[1])],
                    color="#f38ba8", s=140, marker="*", edgecolor="#ffffff", linewidth=1.2,
                    label=f"Mejor f={best_ind.objective_value:.3e}", zorder=3
                )
            ax_proj.set_title(f"Proyección (x1 vs x2) de {dims}D", color=COLORS["primary"], fontsize=9, fontweight="bold")
            ax_proj.set_xlabel("x1", color=COLORS["fg_subtext"], fontsize=8)
            ax_proj.set_ylabel("x2", color=COLORS["fg_subtext"], fontsize=8)
            ax_proj.set_xlim(a, b)
            ax_proj.set_ylim(a, b)
            ax_proj.legend(loc="upper right", facecolor=COLORS["bg_card"], edgecolor=COLORS["border"], labelcolor=COLORS["fg_text"], fontsize=7)

            # 2. Gráfica de Barras por cada dimensión (x1, x2, ... xn) del mejor individuo
            var_names = [f"x{i+1}" for i in range(dims)]
            if best_ind is not None:
                gene_values = [float(g) for g in best_ind.genes]
                # Colorear barras según sean positivas o negativas
                bar_colors = ["#a6e3a1" if v >= 0 else "#f38ba8" for v in gene_values]
                bars = ax_bars.bar(var_names, gene_values, color=bar_colors, edgecolor=COLORS["border"], alpha=0.85)
                # Anotar valor encima o debajo de cada barra
                for bar, val in zip(bars, gene_values):
                    va = "bottom" if val >= 0 else "top"
                    ax_bars.text(
                        bar.get_x() + bar.get_width() / 2.0, val,
                        f"{val:.2f}",
                        ha="center", va=va,
                        color=COLORS["fg_text"], fontsize=7, fontweight="bold"
                    )
            ax_bars.axhline(0, color=COLORS["fg_subtext"], linestyle=":", alpha=0.5)
            ax_bars.set_title(f"Valores Óptimos por Variable (x1..x{dims})", color=COLORS["accent"], fontsize=9, fontweight="bold")
            ax_bars.set_ylabel("Magnitud", color=COLORS["fg_subtext"], fontsize=8)
            ax_bars.set_ylim(a, b)
            ax_bars.tick_params(axis="x", labelsize=7)

        # Gráfica de Convergencia Generacional
        if history:
            gens = [h["generation"] for h in history]
            best_fxs = [h["best_fx"] for h in history]
            mean_fxs = [h["mean_fx"] for h in history]

            ax_conv.plot(gens, best_fxs, color="#a6e3a1", linewidth=2.0, label="Mejor f(x)")
            ax_conv.plot(gens, mean_fxs, color="#cba6f7", linewidth=1.5, linestyle="--", label="Promedio Población")

            ax_conv.set_title(f"Convergencia Evolutiva ({goal.capitalize()} en {dims}D)", color=COLORS["accent"], fontsize=10, fontweight="bold")
            ax_conv.set_xlabel("Generación", color=COLORS["fg_subtext"], fontsize=8)
            ax_conv.set_ylabel("Valor f(x)", color=COLORS["fg_subtext"], fontsize=8)
            ax_conv.legend(loc="best", facecolor=COLORS["bg_card"], edgecolor=COLORS["border"], labelcolor=COLORS["fg_text"], fontsize=8)

        self.canvas.draw_idle()
