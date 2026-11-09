"""
Ventana emergente interactiva 3D con Matplotlib embebido en Tkinter.
Permite rotar, hacer zoom, desplazar la vista con el ratón (o la barra de herramientas de Matplotlib)
y observar la superficie tridimensional continua f(x1, x2).
Soporta:
- Visualización para Algoritmo Genético (población y mejor individuo).
- Visualización para Comparativa AG vs PSO (mostrando el mejor punto encontrado por AG y el de PSO simultáneamente).
"""
import tkinter as tk
from tkinter import ttk
import numpy as np

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from mpl_toolkits.mplot3d import Axes3D

from logica.evaluator import SafeEvaluator
from ui.styles import COLORS, FONTS

class Plot3DWindow(tk.Toplevel):
    def __init__(
        self,
        parent,
        expr: str,
        a: float,
        b: float,
        population=None,
        best_ind=None,
        goal="minimize",
        ga_best=None,
        pso_best=None,
        title_extra=""
    ):
        super().__init__(parent)
        self.title(f"Superficie Interactiva 3D - {title_extra}" if title_extra else "Superficie Interactiva 3D - Paisaje de Optimización")
        self.geometry("940x730")
        self.minsize(720, 530)
        self.configure(bg=COLORS["bg_dark"])

        self.expr = expr
        self.a = float(a)
        self.b = float(b)
        self.population = population
        self.best_ind = best_ind
        self.goal = goal
        self.ga_best = ga_best
        self.pso_best = pso_best

        self._build_ui()
        self._plot_surface_3d()

    def _build_ui(self):
        # Header informativo
        header = ttk.Frame(self, style="Card.TFrame", padding=(12, 8))
        header.pack(fill="x", side="top", padx=10, pady=(10, 5))

        lbl_title = ttk.Label(
            header,
            text=f"🌐 Superficie 3D: {self.expr}",
            style="Title.TLabel",
            font=FONTS["title"]
        )
        lbl_title.pack(side="left")

        lbl_hint = ttk.Label(
            header,
            text="Arrastre con clic izq. para rotar | Clic der. para zoom",
            style="Subtext.TLabel",
            font=FONTS["body"]
        )
        lbl_hint.pack(side="right")

        # Contenedor del gráfico
        graph_box = ttk.Frame(self, style="TFrame")
        graph_box.pack(fill="both", expand=True, padx=10, pady=5)

        self.fig = Figure(figsize=(8.2, 6.2), dpi=100, facecolor=COLORS["bg_card"])
        self.ax = self.fig.add_subplot(1, 1, 1, projection="3d")
        self.fig.tight_layout(pad=2.5)

        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_box)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill="both", expand=True)

        # Barra de navegación estándar (Zoom, Pan, Reset view, Guardar imagen)
        toolbar_frame = ttk.Frame(self, style="Card.TFrame")
        toolbar_frame.pack(fill="x", side="bottom", padx=10, pady=(0, 10))
        self.toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        self.toolbar.update()

    def _plot_surface_3d(self):
        self.ax.clear()

        # Estilizar fondo y ejes 3D acordes a la paleta Dark
        self.ax.set_facecolor(COLORS["bg_dark"])
        try:
            self.ax.w_xaxis.set_pane_color((0.11, 0.11, 0.17, 1.0))
            self.ax.w_yaxis.set_pane_color((0.11, 0.11, 0.17, 1.0))
            self.ax.w_zaxis.set_pane_color((0.11, 0.11, 0.17, 1.0))
        except Exception:
            pass

        self.ax.tick_params(colors=COLORS["fg_subtext"], labelsize=8)
        self.ax.set_xlabel("x1", color=COLORS["fg_subtext"], fontsize=9, labelpad=8)
        self.ax.set_ylabel("x2", color=COLORS["fg_subtext"], fontsize=9, labelpad=8)
        self.ax.set_zlabel("f(x1, x2)", color=COLORS["fg_subtext"], fontsize=9, labelpad=8)

        try:
            ev = SafeEvaluator(self.expr, dimensions=2, goal=self.goal)
            n_pts = 65
            x1 = np.linspace(self.a, self.b, n_pts)
            x2 = np.linspace(self.a, self.b, n_pts)
            X1, X2 = np.meshgrid(x1, x2)
            Z = np.zeros_like(X1)

            for i in range(X1.shape[0]):
                for j in range(X1.shape[1]):
                    Z[i, j] = ev.evaluate([X1[i, j], X2[i, j]], allow_nan=True)

            # Superficie tridimensional
            surf = self.ax.plot_surface(
                X1, X2, Z,
                cmap="viridis",
                edgecolor="none",
                alpha=0.88,
                antialiased=True,
                rstride=1,
                cstride=1
            )
            self.fig.colorbar(surf, ax=self.ax, shrink=0.55, aspect=14, pad=0.08)

            # Caso 1: Población general de AG
            if self.population:
                valid_inds = [ind for ind in self.population if abs(ind.objective_value) < 1e11]
                if valid_inds:
                    px = [float(ind.genes[0]) for ind in valid_inds]
                    py = [float(ind.genes[1]) for ind in valid_inds]
                    pz = [float(ind.objective_value) for ind in valid_inds]
                    self.ax.scatter(
                        px, py, pz,
                        color="#fab387",
                        s=35,
                        edgecolor="#11111b",
                        depthshade=True,
                        label="Población"
                    )

            if self.best_ind is not None and abs(self.best_ind.objective_value) < 1e11:
                bx = float(self.best_ind.genes[0])
                by = float(self.best_ind.genes[1])
                bz = float(self.best_ind.objective_value)
                self.ax.scatter(
                    [bx], [by], [bz],
                    color="#f38ba8",
                    s=180,
                    marker="*",
                    edgecolor="#ffffff",
                    linewidth=1.2,
                    label=f"Mejor: f={bz:.4f}"
                )

            # Caso 2: Puntos comparativos AG vs PSO
            if self.ga_best is not None:
                gx, gy, gf = self.ga_best
                self.ax.scatter(
                    [gx], [gy], [gf],
                    color="#89b4fa",
                    s=180,
                    marker="*",
                    edgecolor="#ffffff",
                    linewidth=1.4,
                    label=f"Mejor AG: ({gx:.3f}, {gy:.3f}) | f={gf:.4f}"
                )

            if self.pso_best is not None:
                px, py, pf = self.pso_best
                self.ax.scatter(
                    [px], [py], [pf],
                    color="#a6e3a1",
                    s=180,
                    marker="P",  # Cruz/Plus llamativa
                    edgecolor="#11111b",
                    linewidth=1.4,
                    label=f"Mejor PSO: ({px:.3f}, {py:.3f}) | f={pf:.4f}"
                )

            self.ax.legend(loc="upper right", facecolor=COLORS["bg_card"], edgecolor=COLORS["border"], labelcolor=COLORS["fg_text"], fontsize=8)
            self.ax.set_title(f"Paisaje Tridimensional: {self.expr}", color=COLORS["primary"], fontsize=11, fontweight="bold", pad=12)

        except Exception as e:
            self.ax.text2D(0.5, 0.5, f"Error al generar superficie 3D:\n{str(e)}",
                           color=COLORS["danger"], ha="center", va="center", transform=self.ax.transAxes)

        self.canvas.draw_idle()
