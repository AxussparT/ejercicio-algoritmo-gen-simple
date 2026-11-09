"""
Panel para la comparativa directa entre Algoritmo Genético (AG)
y Enjambre de Partículas (Particle Swarm Optimization - PSO con pyswarm).
Incluye preajustes para Esfera 2D y Rastrigin n-D (como en el problema propuesto),
gráficas comparativas de convergencia, tabla de rendimiento y
visualización interactiva 3D comparativa (mostrando los óptimos de AG y PSO sobre la superficie).
"""
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, Any, List, Optional
import numpy as np

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from ui.styles import COLORS, FONTS
from logica.ga_engine import GAEngine
from logica.pso_engine import PSOEngine
from logica.evaluator import detect_dimensions
from ui.components.plot3d_window import Plot3DWindow
from almacenamiento.experiment_logger import ExperimentLogger

COMPARISON_PRESETS = {
    "Esfera 2D (x1² + x2² en [-10, 10])": {
        "expression": "x1**2 + x2**2",
        "dimensions": 2,
        "bounds": (-10.0, 10.0),
        "goal": "minimize",
        "optimum_fx": 0.0,
        "description": "Función Esfera 2D: f(x) = x₁² + x₂², sujeto a -10 ≤ x₁, x₂ ≤ 10"
    },
    "Rastrigin 2D (A=10 en [-5.12, 5.12])": {
        "expression": "20 + (x1**2 - 10*cos(2*pi*x1)) + (x2**2 - 10*cos(2*pi*x2))",
        "dimensions": 2,
        "bounds": (-5.12, 5.12),
        "goal": "minimize",
        "optimum_fx": 0.0,
        "description": "Rastrigin 2D: f(x) = 10*n + Σ [xᵢ² - 10*cos(2πxᵢ)] con n=2"
    },
    "Rastrigin N-D (sum(x² - 10*cos(2πx)) en [-5.12, 5.12])": {
        "expression": "10*len(x) + sum(x**2 - 10*cos(2*pi*x))",
        "dimensions": 5,
        "bounds": (-5.12, 5.12),
        "goal": "minimize",
        "optimum_fx": 0.0,
        "description": "Rastrigin generalizada n-D con vector completo x"
    },
    "Personalizada...": {
        "expression": "x1**2 + x2**2",
        "dimensions": 2,
        "bounds": (-10.0, 10.0),
        "goal": "minimize",
        "optimum_fx": 0.0,
        "description": "Ingrese cualquier expresión matemática válida"
    }
}

class ComparisonPanel(ttk.Frame):
    def __init__(self, parent, logger: Optional[ExperimentLogger] = None):
        super().__init__(parent, style="TFrame")
        self.logger = logger if logger is not None else ExperimentLogger()
        self.last_run_id: Optional[str] = None
        
        self.preset_var = tk.StringVar(value="Esfera 2D (x1² + x2² en [-10, 10])")
        self.expression_var = tk.StringVar(value="x1**2 + x2**2")
        self.dims_var = tk.IntVar(value=2)
        self.lb_var = tk.DoubleVar(value=-10.0)
        self.ub_var = tk.DoubleVar(value=10.0)
        self.goal_var = tk.StringVar(value="minimize")
        
        # Parámetros compartidos
        self.pop_size_var = tk.IntVar(value=40)
        self.max_iter_var = tk.IntVar(value=50)
        self.seed_var = tk.StringVar(value="42")
        
        # Parámetros específicos PSO
        self.omega_var = tk.DoubleVar(value=0.5)
        self.phip_var = tk.DoubleVar(value=0.5)
        self.phig_var = tk.DoubleVar(value=0.5)

        # Formato numérico: 'decimal' o 'scientific'
        self.number_format_var = tk.StringVar(value="decimal")
        self.decimal_precision_var = tk.IntVar(value=6)
        
        # Estado y últimos resultados almacenados para refresco de formato y vista 3D
        self.is_running = False
        self.last_ga_res: Optional[Dict[str, Any]] = None
        self.last_pso_res: Optional[Dict[str, Any]] = None
        self.last_goal: str = "minimize"
        self.last_expr: str = "x1**2 + x2**2"
        self.last_a: float = -10.0
        self.last_b: float = 10.0
        self.last_dims: int = 2
        
        self._build_ui()
        self._check_3d_button_state()
        
    def _build_ui(self):
        main_box = ttk.Frame(self, style="TFrame")
        main_box.pack(fill="both", expand=True, padx=8, pady=8)
        
        # --- COLUMNA IZQUIERDA: Configuración (con scroll) ---
        left_card = ttk.Frame(main_box, style="Card.TFrame", width=420)
        left_card.pack(side="left", fill="both", padx=(0, 6))
        left_card.pack_propagate(False)
        
        left_canvas = tk.Canvas(left_card, bg=COLORS["bg_card"], highlightthickness=0)
        left_scroll = ttk.Scrollbar(left_card, orient="vertical", command=left_canvas.yview)
        scroll_content = ttk.Frame(left_canvas, style="Card.TFrame")
        
        scroll_content.bind("<Configure>", lambda e: left_canvas.configure(scrollregion=left_canvas.bbox("all")))
        left_canvas.create_window((0, 0), window=scroll_content, anchor="nw", width=400)
        left_canvas.configure(yscrollcommand=left_scroll.set)
        
        left_canvas.pack(side="left", fill="both", expand=True)
        left_scroll.pack(side="right", fill="y")
        
        # 1. Grupo de Función
        grp_func = ttk.LabelFrame(scroll_content, text=" 1. Función y Dominio ", style="TLabelframe", padding=10)
        grp_func.pack(fill="x", padx=6, pady=6)
        
        ttk.Label(grp_func, text="Ecuación a evaluar:", style="Card.TLabel").grid(row=0, column=0, sticky="w", pady=2)
        cb_preset = ttk.Combobox(grp_func, textvariable=self.preset_var, values=list(COMPARISON_PRESETS.keys()), state="readonly", width=34)
        cb_preset.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 6))
        cb_preset.bind("<<ComboboxSelected>>", self._on_preset_change)
        
        ttk.Label(grp_func, text="Expresión f(x):", style="Card.TLabel").grid(row=2, column=0, sticky="w", pady=2)
        ttk.Entry(grp_func, textvariable=self.expression_var, width=34).grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 6))
        self.expression_var.trace_add("write", lambda *args: self._check_3d_button_state())
        
        # Dimensiones y Límites
        f_dim = ttk.Frame(grp_func, style="Card.TFrame")
        f_dim.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(0, 6))
        ttk.Label(f_dim, text="Dim (n):", style="Card.TLabel").pack(side="left")
        sp_dim = ttk.Spinbox(f_dim, from_=1, to=100, textvariable=self.dims_var, width=5, command=self._check_3d_button_state)
        sp_dim.pack(side="left", padx=(4, 15))
        sp_dim.bind("<KeyRelease>", lambda e: self._check_3d_button_state())
        
        ttk.Label(f_dim, text="[a, b]:", style="Card.TLabel").pack(side="left")
        ttk.Entry(f_dim, textvariable=self.lb_var, width=6).pack(side="left", padx=2)
        ttk.Label(f_dim, text="a", style="Card.TLabel").pack(side="left", padx=1)
        ttk.Entry(f_dim, textvariable=self.ub_var, width=6).pack(side="left", padx=2)
        
        # Objetivo
        f_goal = ttk.Frame(grp_func, style="Card.TFrame")
        f_goal.grid(row=5, column=0, columnspan=2, sticky="w", pady=(2, 4))
        ttk.Label(f_goal, text="Objetivo:", style="Card.TLabel").pack(side="left", padx=(0, 8))
        tk.Radiobutton(f_goal, text="Minimizar", variable=self.goal_var, value="minimize",
                       bg=COLORS["bg_card"], fg=COLORS["fg_text"], selectcolor=COLORS["bg_dark"]).pack(side="left", padx=4)
        tk.Radiobutton(f_goal, text="Maximizar", variable=self.goal_var, value="maximize",
                       bg=COLORS["bg_card"], fg=COLORS["fg_text"], selectcolor=COLORS["bg_dark"]).pack(side="left", padx=4)

        # 2. Grupo de Parámetros Equivalentes
        grp_params = ttk.LabelFrame(scroll_content, text=" 2. Parámetros Equivalentes ", style="TLabelframe", padding=10)
        grp_params.pack(fill="x", padx=6, pady=6)
        
        f_shared = ttk.Frame(grp_params, style="Card.TFrame")
        f_shared.pack(fill="x", pady=2)
        
        ttk.Label(f_shared, text="Población / Enjambre (N):", style="Card.TLabel").grid(row=0, column=0, sticky="w", pady=3)
        ttk.Spinbox(f_shared, from_=10, to=500, textvariable=self.pop_size_var, width=8).grid(row=0, column=1, sticky="e", pady=3)
        
        ttk.Label(f_shared, text="Generaciones / Iteraciones (T):", style="Card.TLabel").grid(row=1, column=0, sticky="w", pady=3)
        ttk.Spinbox(f_shared, from_=5, to=1000, textvariable=self.max_iter_var, width=8).grid(row=1, column=1, sticky="e", pady=3)
        
        ttk.Label(f_shared, text="Semilla aleatoria (Seed):", style="Card.TLabel").grid(row=2, column=0, sticky="w", pady=3)
        ttk.Entry(f_shared, textvariable=self.seed_var, width=8).grid(row=2, column=1, sticky="e", pady=3)

        # 3. Hiperparámetros PSO (pyswarm)
        grp_pso = ttk.LabelFrame(scroll_content, text=" 3. Hiperparámetros PSO (pyswarm) ", style="TLabelframe", padding=10)
        grp_pso.pack(fill="x", padx=6, pady=6)
        
        f_pso = ttk.Frame(grp_pso, style="Card.TFrame")
        f_pso.pack(fill="x", pady=2)
        ttk.Label(f_pso, text="Inercia (ω - omega):", style="Card.TLabel").grid(row=0, column=0, sticky="w", pady=3)
        ttk.Entry(f_pso, textvariable=self.omega_var, width=8).grid(row=0, column=1, sticky="e", pady=3)
        
        ttk.Label(f_pso, text="Cognitivo (φp - phip):", style="Card.TLabel").grid(row=1, column=0, sticky="w", pady=3)
        ttk.Entry(f_pso, textvariable=self.phip_var, width=8).grid(row=1, column=1, sticky="e", pady=3)
        
        ttk.Label(f_pso, text="Social (φg - phig):", style="Card.TLabel").grid(row=2, column=0, sticky="w", pady=3)
        ttk.Entry(f_pso, textvariable=self.phig_var, width=8).grid(row=2, column=1, sticky="e", pady=3)

        # 4. Formato de Nomenclatura Numérica
        grp_fmt = ttk.LabelFrame(scroll_content, text=" 4. Formato de Nomenclatura Numérica ", style="TLabelframe", padding=10)
        grp_fmt.pack(fill="x", padx=6, pady=6)

        f_fmt_radios = ttk.Frame(grp_fmt, style="Card.TFrame")
        f_fmt_radios.pack(fill="x", pady=2)

        tk.Radiobutton(
            f_fmt_radios, text="Decimal clásico (0.000000)", variable=self.number_format_var, value="decimal",
            bg=COLORS["bg_card"], fg=COLORS["fg_text"], selectcolor=COLORS["bg_dark"],
            command=self._on_format_changed
        ).pack(side="left", padx=(0, 10))

        tk.Radiobutton(
            f_fmt_radios, text="Científica (1.23e-10)", variable=self.number_format_var, value="scientific",
            bg=COLORS["bg_card"], fg=COLORS["fg_text"], selectcolor=COLORS["bg_dark"],
            command=self._on_format_changed
        ).pack(side="left")

        f_prec = ttk.Frame(grp_fmt, style="Card.TFrame")
        f_prec.pack(fill="x", pady=(6, 2))
        ttk.Label(f_prec, text="Decimales a mostrar:", style="Card.TLabel").pack(side="left")
        sp_prec = ttk.Spinbox(f_prec, from_=2, to=14, textvariable=self.decimal_precision_var, width=5, command=self._on_format_changed)
        sp_prec.pack(side="left", padx=8)
        sp_prec.bind("<KeyRelease>", lambda e: self._on_format_changed())

        # Botón de Ejecutar Comparativa
        self.btn_run = ttk.Button(scroll_content, text="⚡ Ejecutar Comparativa (AG vs PSO)", style="Action.TButton", command=self.start_comparison)
        self.btn_run.pack(fill="x", padx=6, pady=10)

        self.lbl_status = ttk.Label(scroll_content, text="Listo para ejecutar comparativa.", style="Subtext.TLabel", font=FONTS["metric_lbl"])
        self.lbl_status.pack(fill="x", padx=6, pady=(0, 8))

        # --- COLUMNA DERECHA: Visualización y Tabla ---
        right_box = ttk.Frame(main_box, style="TFrame")
        right_box.pack(side="right", fill="both", expand=True, padx=(6, 0))

        # Barra superior sobre la gráfica con botón 3D interactivo
        graph_header = ttk.Frame(right_box, style="Card.TFrame", padding=(8, 4))
        graph_header.pack(fill="x", side="top", pady=(0, 4))

        ttk.Label(graph_header, text="📈 Curvas de Convergencia AG vs PSO", style="Subtitle.TLabel").pack(side="left")

        self.btn_open_3d = ttk.Button(
            graph_header,
            text="🌐 Abrir Paisaje 3D Comparativo",
            style="Secondary.TButton",
            command=self._open_3d_comparison_view,
            state="normal"
        )
        self.btn_open_3d.pack(side="right")

        # 1. Gráfica de convergencia comparativa
        self.fig = Figure(figsize=(6.5, 4.0), dpi=100, facecolor=COLORS["bg_card"])
        self.ax = self.fig.add_subplot(1, 1, 1)
        self.fig.tight_layout(pad=3.0)
        self._style_axis()

        self.canvas = FigureCanvasTkAgg(self.fig, master=right_box)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill="both", expand=True, pady=(0, 6))
        self._show_placeholder_plot()

        # 2. Barra de Herramientas de la Tabla
        tbl_frame = ttk.Frame(right_box, style="Card.TFrame", padding=10)
        tbl_frame.pack(fill="x", side="bottom")

        top_tbl = ttk.Frame(tbl_frame, style="Card.TFrame")
        top_tbl.pack(fill="x", pady=(0, 6))

        ttk.Label(top_tbl, text="📊 Resumen Comparativo de Rendimiento", style="Subtitle.TLabel").pack(side="left")

        # Botones de acción rápida en la cabecera de la tabla
        self.btn_export_comp = ttk.Button(
            top_tbl,
            text="💾 Exportar CSV / TXT",
            style="Secondary.TButton",
            command=self._export_current_comparison
        )
        self.btn_export_comp.pack(side="right", padx=(6, 0))

        self.btn_toggle_fmt = ttk.Button(
            top_tbl,
            text="🔀 Alternar Decimal / Científica",
            style="Secondary.TButton",
            command=self._toggle_number_format
        )
        self.btn_toggle_fmt.pack(side="right")

        columns = ("metric", "ga_val", "pso_val", "winner")
        self.tree = ttk.Treeview(tbl_frame, columns=columns, show="headings", height=5)
        self.tree.heading("metric", text="Métrica")
        self.tree.heading("ga_val", text="Algoritmo Genético (AG)")
        self.tree.heading("pso_val", text="Enjambre Partículas (PSO)")
        self.tree.heading("winner", text="Mejor Rendimiento")

        self.tree.column("metric", width=180, anchor="w")
        self.tree.column("ga_val", width=170, anchor="center")
        self.tree.column("pso_val", width=170, anchor="center")
        self.tree.column("winner", width=130, anchor="center")

        self.tree.pack(fill="x", expand=True)

    def _check_3d_button_state(self):
        """Habilita o deshabilita el botón 3D según la dimensionalidad actual."""
        try:
            dims = int(self.dims_var.get())
            if dims == 2:
                self.btn_open_3d.config(state="normal")
            else:
                self.btn_open_3d.config(state="disabled")
        except Exception:
            self.btn_open_3d.config(state="disabled")

    def _open_3d_comparison_view(self):
        """Abre la ventana 3D interactiva mostrando la superficie y los óptimos encontrados por AG y PSO."""
        expr = self.expression_var.get().strip()
        dims = int(self.dims_var.get())
        if dims != 2:
            messagebox.showinfo("Superficie 3D", "La visualización 3D está disponible para funciones bidimensionales (2D).")
            return

        try:
            lb = float(self.lb_var.get())
            ub = float(self.ub_var.get())
        except ValueError:
            lb, ub = -10.0, 10.0

        goal = self.goal_var.get()

        # Extraer óptimos si ya se ejecutó la comparativa
        ga_pt = None
        pso_pt = None

        if self.last_ga_res and self.last_ga_res.get("best_x") is not None:
            gx = self.last_ga_res["best_x"]
            if isinstance(gx, (list, np.ndarray)) and len(gx) >= 2:
                ga_pt = (float(gx[0]), float(gx[1]), float(self.last_ga_res["best_fx"]))

        if self.last_pso_res and self.last_pso_res.get("best_x") is not None:
            px = self.last_pso_res["best_x"]
            if isinstance(px, (list, np.ndarray)) and len(px) >= 2:
                pso_pt = (float(px[0]), float(px[1]), float(self.last_pso_res["best_fx"]))

        Plot3DWindow(
            self,
            expr=expr,
            a=lb,
            b=ub,
            goal=goal,
            ga_best=ga_pt,
            pso_best=pso_pt,
            title_extra="Comparativa AG vs PSO"
        )

    def _format_number(self, val: float) -> str:
        """Formatea un número según la selección actual del usuario (decimal limpio o notación científica)."""
        if val is None:
            return "--"
        prec = max(2, min(14, int(self.decimal_precision_var.get())))
        mode = self.number_format_var.get()

        if mode == "scientific":
            return f"{val:.{prec}e}"
        else:
            rounded = round(val, prec)
            if abs(rounded) == 0.0:
                rounded = 0.0
            formatted = f"{rounded:.{prec}f}"
            return formatted

    def _format_vector(self, vec) -> str:
        """Formatea un vector solución (o escalar) respetando la opción de decimal vs científica."""
        if vec is None:
            return "--"
        if isinstance(vec, (int, float, np.floating, np.integer)):
            return self._format_number(float(vec))

        try:
            arr = np.asarray(vec, dtype=float).flatten()
            formatted_items = [self._format_number(float(v)) for v in arr]
            if len(formatted_items) == 1:
                return formatted_items[0]
            return "[" + ", ".join(formatted_items) + "]"
        except Exception:
            return str(vec)

    def _toggle_number_format(self):
        """Alterna directamente entre Decimal y Científica."""
        curr = self.number_format_var.get()
        new_mode = "scientific" if curr == "decimal" else "decimal"
        self.number_format_var.set(new_mode)
        self._on_format_changed()

    def _on_format_changed(self):
        """Actualiza la visualización de la tabla y la gráfica si ya hay resultados generados."""
        if self.last_ga_res and self.last_pso_res:
            self._render_results_table(self.last_ga_res, self.last_pso_res, self.last_goal)
            self._render_plot(self.last_ga_res, self.last_pso_res, self.last_goal)

    def _style_axis(self):
        self.ax.set_facecolor(COLORS["bg_dark"])
        self.ax.tick_params(colors=COLORS["fg_subtext"], labelsize=8)
        for spine in self.ax.spines.values():
            spine.set_color(COLORS["border"])
        self.ax.grid(True, linestyle="--", alpha=0.25, color=COLORS["fg_subtext"])

    def _show_placeholder_plot(self):
        self.ax.clear()
        self._style_axis()
        self.ax.set_title("Curva de Convergencia Comparativa: AG vs PSO", color=COLORS["primary"], fontsize=10, fontweight="bold")
        self.ax.text(0.5, 0.5, "Presione 'Ejecutar Comparativa' para comparar AG y PSO en tiempo real.",
                     color=COLORS["fg_subtext"], ha="center", va="center", transform=self.ax.transAxes)
        self.canvas.draw_idle()

    def _on_preset_change(self, event=None):
        name = self.preset_var.get()
        if name in COMPARISON_PRESETS:
            d = COMPARISON_PRESETS[name]
            self.expression_var.set(d["expression"])
            self.dims_var.set(d["dimensions"])
            self.lb_var.set(d["bounds"][0])
            self.ub_var.set(d["bounds"][1])
            self.goal_var.set(d["goal"])
            self._check_3d_button_state()

    def start_comparison(self):
        if self.is_running:
            return
        
        expr = self.expression_var.get().strip()
        dims = int(self.dims_var.get())
        lb = float(self.lb_var.get())
        ub = float(self.ub_var.get())
        if lb >= ub:
            messagebox.showerror("Error de límites", "El límite inferior (a) debe ser menor que el superior (b).")
            return

        self.is_running = True
        self.btn_run.config(state="disabled")
        self.lbl_status.config(text="Ejecutando comparación en segundo plano...")

        for item in self.tree.get_children():
            self.tree.delete(item)

        thread = threading.Thread(target=self._run_benchmarks, daemon=True)
        thread.start()

    def _run_benchmarks(self):
        expr = self.expression_var.get().strip()
        dims = int(self.dims_var.get())
        lb = float(self.lb_var.get())
        ub = float(self.ub_var.get())
        goal = self.goal_var.get()
        pop_size = int(self.pop_size_var.get())
        max_iter = int(self.max_iter_var.get())
        
        seed_val = None
        if self.seed_var.get().strip():
            try:
                seed_val = int(self.seed_var.get().strip())
            except ValueError:
                seed_val = 42

        # 1. Configuración AG
        ga_config = {
            "expression": expr,
            "dimensions": dims,
            "bounds": [(lb, ub)] * dims,
            "goal": goal,
            "pop_size": pop_size,
            "max_generations": max_iter,
            "pc": 0.85,
            "pm": 0.1,
            "seed": seed_val,
            "selection_method": "Torneo",
            "selection_params": {"k": 3},
            "crossover_method": "BLX-α",
            "crossover_params": {"alpha": 0.5},
            "mutation_method": "No uniforme",
            "mutation_params": {"b": 1.5},
            "replacement_method": "Generacional con elitismo",
            "replacement_params": {"n_elite": 2}
        }

        # 2. Configuración PSO
        pso_config = {
            "expression": expr,
            "dimensions": dims,
            "bounds": [(lb, ub)] * dims,
            "goal": goal,
            "swarmsize": pop_size,
            "maxiter": max_iter,
            "omega": float(self.omega_var.get()),
            "phip": float(self.phip_var.get()),
            "phig": float(self.phig_var.get()),
            "seed": seed_val
        }

        try:
            ga_eng = GAEngine(ga_config)
            ga_res = ga_eng.run()

            pso_eng = PSOEngine(pso_config)
            pso_res = pso_eng.run()

            self.after(0, lambda: self._update_results(ga_res, pso_res, goal, expr, lb, ub, dims))
        except Exception as e:
            self.after(0, lambda: self._handle_error(str(e)))

    def _handle_error(self, err_msg: str):
        self.is_running = False
        self.btn_run.config(state="normal")
        self.lbl_status.config(text=f"Error: {err_msg}")
        messagebox.showerror("Error en Comparativa", err_msg)

    def _update_results(self, ga_res: Dict[str, Any], pso_res: Dict[str, Any], goal: str, expr: str, lb: float, ub: float, dims: int):
        self.is_running = False
        self.btn_run.config(state="normal")

        self.last_ga_res = ga_res
        self.last_pso_res = pso_res
        self.last_goal = goal
        self.last_expr = expr
        self.last_a = lb
        self.last_b = ub
        self.last_dims = dims

        # Guardar registro en el Historial incluyendo todos los hiperparámetros de AG y PSO
        try:
            comp_cfg = {
                "preset_name": self.preset_var.get(),
                "expression": expr,
                "dimensions": dims,
                "bounds": [(lb, ub)] * dims,
                "goal": goal,
                "pop_size": int(self.pop_size_var.get()),
                "max_generations": int(self.max_iter_var.get()),
                "seed": self.seed_var.get().strip(),
                "omega": float(self.omega_var.get()),
                "phip": float(self.phip_var.get()),
                "phig": float(self.phig_var.get())
            }
            self.last_run_id = self.logger.save_comparison_run(comp_cfg, ga_res, pso_res)
            self.lbl_status.config(text=f"Comparativa completada y guardada en Historial ({self.last_run_id}).")
        except Exception:
            self.lbl_status.config(text="Comparativa completada exitosamente.")

        self._check_3d_button_state()
        self._render_plot(ga_res, pso_res, goal)
        self._render_results_table(ga_res, pso_res, goal)

    def _export_current_comparison(self):
        """Permite exportar los resultados actuales de la comparativa a CSV o TXT."""
        if not self.last_run_id:
            messagebox.showinfo("Exportar", "Ejecute primero la comparativa para poder exportar sus resultados.")
            return
        dest = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Archivo CSV (Evolución)", "*.csv"), ("Reporte Completo TXT", "*.txt")],
            initialfile=f"{self.last_run_id}"
        )
        if not dest:
            return
        if dest.lower().endswith(".txt"):
            ok = self.logger.export_txt_report(self.last_run_id, dest)
        else:
            ok = self.logger.export_history_to_csv(self.last_run_id, dest)
        if ok:
            messagebox.showinfo("Exportación Exitosa", f"Archivo exportado correctamente en:\n{dest}")
        else:
            messagebox.showerror("Error", "No se pudo exportar el archivo.")

    def set_data(self, config: Dict[str, Any]):
        """Carga los parámetros e hiperparámetros desde un registro del Historial."""
        self.preset_var.set(config.get("preset_name", "Personalizada..."))
        self.expression_var.set(config.get("expression", "x1**2 + x2**2"))
        self.dims_var.set(config.get("dimensions", 2))
        bounds = config.get("bounds", [(-10.0, 10.0)])
        self.lb_var.set(bounds[0][0])
        self.ub_var.set(bounds[0][1])
        self.goal_var.set(config.get("goal", "minimize"))
        self.pop_size_var.set(config.get("pop_size", 40))
        self.max_iter_var.set(config.get("max_generations", 50))
        if config.get("seed") is not None:
            self.seed_var.set(str(config.get("seed")))
        pso_hp = config.get("pso_hyperparameters", {})
        self.omega_var.set(pso_hp.get("omega", config.get("omega", 0.5)))
        self.phip_var.set(pso_hp.get("phip", config.get("phip", 0.5)))
        self.phig_var.set(pso_hp.get("phig", config.get("phig", 0.5)))
        self._check_3d_button_state()

    def _render_plot(self, ga_res: Dict[str, Any], pso_res: Dict[str, Any], goal: str):
        self.ax.clear()
        self._style_axis()

        ga_hist = ga_res.get("history", [])
        pso_hist = pso_res.get("history", [])

        ga_min_str = self._format_number(ga_res['best_fx'])
        pso_min_str = self._format_number(pso_res['best_fx'])

        if ga_hist:
            ga_gens = [h["generation"] for h in ga_hist]
            ga_fx = [h["best_fx"] for h in ga_hist]
            self.ax.plot(ga_gens, ga_fx, color="#89b4fa", linewidth=2.2, label=f"AG (Mejor f={ga_min_str})")

        if pso_hist:
            pso_iters = [h["iteration"] for h in pso_hist]
            pso_fx = [h["best_fx"] for h in pso_hist]
            self.ax.plot(pso_iters, pso_fx, color="#a6e3a1", linewidth=2.2, linestyle="--", label=f"PSO (Mejor f={pso_min_str})")

        self.ax.set_title(f"Convergencia Comparativa: AG vs PSO ({goal.capitalize()})", color=COLORS["primary"], fontsize=10, fontweight="bold")
        self.ax.set_xlabel("Generación / Iteración", color=COLORS["fg_subtext"], fontsize=8)
        self.ax.set_ylabel("Mejor f(x)", color=COLORS["fg_subtext"], fontsize=8)
        self.ax.legend(loc="best", facecolor=COLORS["bg_card"], edgecolor=COLORS["border"], labelcolor=COLORS["fg_text"], fontsize=8)
        self.canvas.draw_idle()

    def _render_results_table(self, ga_res: Dict[str, Any], pso_res: Dict[str, Any], goal: str):
        ga_fx = ga_res["best_fx"]
        pso_fx = pso_res["best_fx"]

        if goal == "minimize":
            best_fx_winner = "PSO" if pso_fx < ga_fx else ("AG" if ga_fx < pso_fx else "Empate")
        else:
            best_fx_winner = "PSO" if pso_fx > ga_fx else ("AG" if ga_fx > pso_fx else "Empate")

        time_winner = "PSO" if pso_res["execution_time"] < ga_res["execution_time"] else "AG"
        evals_winner = "PSO" if pso_res["total_evaluations"] < ga_res["total_evaluations"] else "AG"

        # Aplicar formato de nomenclatura (Decimal vs Científica)
        ga_fx_str = self._format_number(ga_fx)
        pso_fx_str = self._format_number(pso_fx)

        ga_x_str = self._format_vector(ga_res["best_x"])
        pso_x_str = self._format_vector(pso_res["best_x"])

        rows = [
            ("Mejor f(x) alcanzado", ga_fx_str, pso_fx_str, best_fx_winner),
            ("Tiempo de ejecución", f"{ga_res['execution_time']:.4f} s", f"{pso_res['execution_time']:.4f} s", time_winner),
            ("Total de evaluaciones", f"{ga_res['total_evaluations']}", f"{pso_res['total_evaluations']}", evals_winner),
            ("Mejor x*", ga_x_str, pso_x_str, "-")
        ]

        for item in self.tree.get_children():
            self.tree.delete(item)

        for r in rows:
            self.tree.insert("", "end", values=r)
