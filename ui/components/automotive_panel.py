"""
Pestaña Especializada para el Reto de Diseño Automotriz Multiobjetivo.
Cubre íntegramente las Partes I, II, III, IV, V y el Desafío Final (Sección 6):
- Simulador físico no lineal en tiempo real de las 6 variables [P, r, a, b, g, h] y 4 restricciones.
- Transformación uniobjetivo con 3 escenarios (Deportivo, Ecológico, Económico) y ejecución AG vs PSO.
- Optimización Multiobjetivo pura con pymoo soportando NSGA-II y algoritmos superiores (NSGA-III, C-TAEA, SMS-EMOA).
- Visualización 2D múltiple y Frente de Pareto 3D Interactivo.
- Experimentación estadística automática con 10 semillas aleatorias (Parte IV).
- Registro automático en Historial y Exportación directa a CSV / TXT.
"""
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from mpl_toolkits.mplot3d import Axes3D

from ui.styles import COLORS, FONTS
from logica.automotive_model import (
    AUTOMOTIVE_BOUNDS,
    SCENARIO_PRESETS,
    evaluate_vehicle,
    evaluate_scalarized,
    run_automotive_ga,
    run_automotive_pso,
    run_automotive_moo,
    run_multi_seed_experiment
)
from almacenamiento.experiment_logger import ExperimentLogger


class Pareto3DWindow(tk.Toplevel):
    """Ventana emergente interactiva 3D para explorar el Frente de Pareto (Velocidad vs Consumo vs Costo)."""
    def __init__(
        self,
        parent,
        moo_res: Optional[Dict[str, Any]],
        ga_res: Optional[Dict[str, Any]],
        pso_res: Optional[Dict[str, Any]],
        max_cost_limit: float = 315000.0
    ):
        super().__init__(parent)
        alg_name = moo_res.get("algorithm", "NSGA-II") if moo_res else "Multiobjetivo"
        self.title(f"Frente de Pareto 3D Interactivo ({alg_name}) - Diseño Automotriz")
        self.geometry("980x750")
        self.minsize(760, 560)
        self.configure(bg=COLORS["bg_dark"])

        self.moo_res = moo_res
        self.ga_res = ga_res
        self.pso_res = pso_res
        self.max_cost_limit = max_cost_limit

        self._build_ui()
        self._render_3d()

    def _build_ui(self):
        header = ttk.Frame(self, style="Card.TFrame", padding=(14, 10))
        header.pack(fill="x", side="top", padx=10, pady=(10, 4))

        ttk.Label(
            header,
            text="🌐 FRENTE DE PARETO 3D INTERACTIVO: Velocidad Máx vs Consumo vs Costo",
            style="Title.TLabel"
        ).pack(side="left")

        ttk.Label(
            header,
            text="Arrastre con clic izquierdo para rotar | Clic derecho para zoom",
            style="Subtext.TLabel"
        ).pack(side="right")

        plot_frame = ttk.Frame(self, style="Card.TFrame", padding=6)
        plot_frame.pack(fill="both", expand=True, padx=10, pady=(4, 10))

        self.fig = Figure(figsize=(9.2, 6.4), dpi=100, facecolor=COLORS["bg_card"])
        self.ax3d = self.fig.add_subplot(111, projection="3d")
        self.ax3d.set_facecolor(COLORS["bg_dark"])

        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill="both", expand=True)

        toolbar_frame = ttk.Frame(plot_frame, style="Card.TFrame")
        toolbar_frame.pack(fill="x", side="bottom")
        self.toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        self.toolbar.update()

    def _render_3d(self):
        self.ax3d.clear()
        self.ax3d.set_facecolor(COLORS["bg_dark"])

        for axis in [self.ax3d.xaxis, self.ax3d.yaxis, self.ax3d.zaxis]:
            axis.pane.fill = True
            axis.pane.set_facecolor((0.12, 0.12, 0.18, 0.75))
            axis.pane.set_edgecolor(COLORS["border"])
            axis._axinfo["grid"]["color"] = (0.45, 0.47, 0.58, 0.25)

        self.ax3d.tick_params(colors=COLORS["fg_subtext"], labelsize=8)

        # 1. Nube del Frente de Pareto (MOO)
        if self.moo_res and self.moo_res.get("solutions"):
            sols = self.moo_res["solutions"]
            v_vals = [s["v_max"] for s in sols]
            c_vals = [s["c_comb"] for s in sols]
            cost_vals = [s["c_fab"] / 1000.0 for s in sols]

            sc = self.ax3d.scatter(
                v_vals, c_vals, cost_vals,
                c=cost_vals, cmap="viridis", s=50, alpha=0.88,
                edgecolors="#ffffff", linewidth=0.4,
                label=f"Frente Pareto ({self.moo_res.get('algorithm', 'MOO')}: {len(sols)} sols)"
            )
            cbar = self.fig.colorbar(sc, ax=self.ax3d, shrink=0.55, pad=0.08)
            cbar.set_label("Costo Fabricación ($ Miles MXN)", color=COLORS["fg_subtext"], fontsize=8)
            cbar.ax.yaxis.set_tick_params(color=COLORS["fg_subtext"], labelcolor=COLORS["fg_subtext"], labelsize=7)

            reps = self.moo_res.get("representatives", {})
            knee = reps.get("Mejor Compromiso (Rodilla Pareto)")
            if knee:
                self.ax3d.scatter(
                    [knee["v_max"]], [knee["c_comb"]], [knee["c_fab"] / 1000.0],
                    color="#f9e2af", s=190, marker="*", edgecolors="#11111b", linewidth=1.2,
                    zorder=12, label=f"Rodilla Pareto ({knee['v_max']:.1f} km/h, {knee['c_comb']:.2f} L)"
                )

        # 2. Óptimo AG Uniobjetivo
        if self.ga_res and self.ga_res.get("vehicle"):
            gv = self.ga_res["vehicle"]
            self.ax3d.scatter(
                [gv["v_max"]], [gv["c_comb"]], [gv["c_fab"] / 1000.0],
                color="#89b4fa", s=140, marker="^", edgecolors="#ffffff", linewidth=1.2,
                zorder=11, label=f"Óptimo AG ({gv['v_max']:.1f} km/h, ${gv['c_fab']/1000:.1f}k)"
            )

        # 3. Óptimo PSO Uniobjetivo
        if self.pso_res and self.pso_res.get("vehicle"):
            pv = self.pso_res["vehicle"]
            self.ax3d.scatter(
                [pv["v_max"]], [pv["c_comb"]], [pv["c_fab"] / 1000.0],
                color="#a6e3a1", s=140, marker="P", edgecolors="#11111b", linewidth=1.2,
                zorder=11, label=f"Óptimo PSO ({pv['v_max']:.1f} km/h, ${pv['c_fab']/1000:.1f}k)"
            )

        self.ax3d.set_xlabel("Velocidad Máx (km/h) [Maximizar ↑]", color=COLORS["fg_text"], fontsize=9, labelpad=8)
        self.ax3d.set_ylabel("Consumo (L/100km) [Minimizar ↓]", color=COLORS["fg_text"], fontsize=9, labelpad=8)
        self.ax3d.set_zlabel("Costo ($ Miles MXN) [Minimizar ↓]", color=COLORS["fg_text"], fontsize=9, labelpad=8)
        self.ax3d.set_title(
            f"Espacio Objetivo 3D | Límite Presupuesto: ${self.max_cost_limit:,.0f} MXN",
            color=COLORS["primary"], fontsize=10.5, fontweight="bold", pad=12
        )

        self.ax3d.legend(
            loc="upper left", facecolor=COLORS["bg_card"], edgecolor=COLORS["border"],
            labelcolor=COLORS["fg_text"], fontsize=8
        )
        self.ax3d.view_init(elev=24, azim=-48)
        self.fig.tight_layout()
        self.canvas.draw_idle()


class AutomotivePanel(ttk.Frame):
    def __init__(self, parent, logger: Optional[ExperimentLogger] = None):
        super().__init__(parent, style="TFrame")
        self.logger = logger
        self.last_run_id: Optional[str] = None
        self.last_10seeds_run_id: Optional[str] = None

        # Variables de escenario y pesos (Parte II)
        self.scenario_var = tk.StringVar(value="Diseño Deportivo (Prioriza Velocidad)")
        self.w_vel_var = tk.DoubleVar(value=0.65)
        self.w_cons_var = tk.DoubleVar(value=0.15)
        self.w_cost_var = tk.DoubleVar(value=0.20)

        # Desafío Final (Sección 6: -10% presupuesto -> $283,500 MXN)
        self.challenge_mode_var = tk.BooleanVar(value=False)

        # Algoritmo Multiobjetivo y parámetros compartidos (Parte III)
        self.moo_algo_var = tk.StringVar(value="NSGA-III")
        self.pop_size_var = tk.IntVar(value=55)
        self.max_gen_var = tk.IntVar(value=60)
        self.seed_var = tk.IntVar(value=42)

        # Hiperparámetros específicos de AG y PSO
        self.pc_var = tk.DoubleVar(value=0.85)
        self.pm_var = tk.DoubleVar(value=0.15)
        self.omega_var = tk.DoubleVar(value=0.50)
        self.phip_var = tk.DoubleVar(value=0.50)
        self.phig_var = tk.DoubleVar(value=0.50)

        # Variables del Simulador Interactivo [P, r, a, b, g, h]
        self.sim_P_var = tk.DoubleVar(value=145.0)
        self.sim_r_var = tk.DoubleVar(value=0.45)
        self.sim_a_var = tk.DoubleVar(value=0.55)
        self.sim_b_var = tk.DoubleVar(value=0.60)
        self.sim_g_var = tk.DoubleVar(value=3.45)
        self.sim_h_var = tk.DoubleVar(value=0.50)

        # Estado y resultados en memoria
        self.is_running = False
        self.last_ga_res: Optional[Dict[str, Any]] = None
        self.last_pso_res: Optional[Dict[str, Any]] = None
        self.last_moo_res: Optional[Dict[str, Any]] = None
        self.row_vehicles: Dict[str, List[float]] = {}

        self._build_ui()
        self._update_simulator_display()

    def _get_max_cost_limit(self) -> float:
        return 283500.0 if self.challenge_mode_var.get() else 315000.0

    def _build_ui(self):
        main_box = ttk.Frame(self, style="TFrame")
        main_box.pack(fill="both", expand=True, padx=6, pady=6)

        # =========================================================
        # COLUMNA IZQUIERDA: Configuración y Simulador en Vivo
        # =========================================================
        left_card = ttk.Frame(main_box, style="Card.TFrame", width=435)
        left_card.pack(side="left", fill="both", padx=(0, 6))
        left_card.pack_propagate(False)

        left_canvas = tk.Canvas(left_card, bg=COLORS["bg_card"], highlightthickness=0)
        left_scroll = ttk.Scrollbar(left_card, orient="vertical", command=left_canvas.yview)
        scroll_content = ttk.Frame(left_canvas, style="Card.TFrame")

        scroll_content.bind("<Configure>", lambda e: left_canvas.configure(scrollregion=left_canvas.bbox("all")))
        left_canvas.create_window((0, 0), window=scroll_content, anchor="nw", width=415)
        left_canvas.configure(yscrollcommand=left_scroll.set)

        left_canvas.pack(side="left", fill="both", expand=True)
        left_scroll.pack(side="right", fill="y")

        # Soporte rueda de ratón en columna izquierda
        def _on_left_wheel(event):
            left_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        left_card.bind("<Enter>", lambda e: left_canvas.bind_all("<MouseWheel>", _on_left_wheel))
        left_card.bind("<Leave>", lambda e: left_canvas.unbind_all("<MouseWheel>"))

        # --- 1. Escenario de Decisión y Desafío Final (Parte II y VI) ---
        grp_scen = ttk.LabelFrame(scroll_content, text=" 1. Escenario de Diseño y Restricciones ", style="TLabelframe", padding=8)
        grp_scen.pack(fill="x", padx=6, pady=(6, 4))

        ttk.Label(grp_scen, text="Escenario de ponderación (AG y PSO):", style="Card.TLabel").pack(anchor="w")
        cb_scen = ttk.Combobox(grp_scen, textvariable=self.scenario_var, values=list(SCENARIO_PRESETS.keys()), state="readonly", width=36)
        cb_scen.pack(fill="x", pady=(2, 6))
        cb_scen.bind("<<ComboboxSelected>>", self._on_scenario_changed)

        w_frame = ttk.Frame(grp_scen, style="Card.TFrame")
        w_frame.pack(fill="x", pady=2)
        ttk.Label(w_frame, text="w_vel:", style="Card.TLabel").pack(side="left")
        ttk.Entry(w_frame, textvariable=self.w_vel_var, width=5).pack(side="left", padx=(2, 8))
        ttk.Label(w_frame, text="w_cons:", style="Card.TLabel").pack(side="left")
        ttk.Entry(w_frame, textvariable=self.w_cons_var, width=5).pack(side="left", padx=(2, 8))
        ttk.Label(w_frame, text="w_costo:", style="Card.TLabel").pack(side="left")
        ttk.Entry(w_frame, textvariable=self.w_cost_var, width=5).pack(side="left", padx=2)

        # Checkbutton Desafío Final Sección 6
        chk_challenge = tk.Checkbutton(
            grp_scen,
            text="🔥 Desafío Final (-10% Presupuesto: Máx $283,500 MXN)",
            variable=self.challenge_mode_var,
            bg=COLORS["bg_card"],
            fg=COLORS["warning"],
            selectcolor=COLORS["bg_dark"],
            activebackground=COLORS["bg_card"],
            activeforeground=COLORS["warning"],
            font=FONTS["body"],
            command=self._update_simulator_display
        )
        chk_challenge.pack(anchor="w", pady=(6, 2))

        # --- 2. Algoritmos Bioinspirados y Multiobjetivo (Parte III) ---
        grp_alg = ttk.LabelFrame(scroll_content, text=" 2. Algoritmos Bioinspirados (AG + PSO + MOO) ", style="TLabelframe", padding=8)
        grp_alg.pack(fill="x", padx=6, pady=4)

        ttk.Label(grp_alg, text="Algoritmo Multiobjetivo (Frente de Pareto):", style="Card.TLabel").grid(row=0, column=0, columnspan=2, sticky="w")
        moo_options = ["NSGA-II", "NSGA-III", "C-TAEA", "SMS-EMOA"]
        cb_moo = ttk.Combobox(grp_alg, textvariable=self.moo_algo_var, values=moo_options, state="readonly", width=18)
        cb_moo.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(2, 6))

        ttk.Label(grp_alg, text="Población / Enjambre (N):", style="Card.TLabel").grid(row=2, column=0, sticky="w", pady=2)
        ttk.Spinbox(grp_alg, from_=20, to=200, textvariable=self.pop_size_var, width=7).grid(row=2, column=1, sticky="e", pady=2)

        ttk.Label(grp_alg, text="Generaciones / Iteraciones (T):", style="Card.TLabel").grid(row=3, column=0, sticky="w", pady=2)
        ttk.Spinbox(grp_alg, from_=15, to=300, textvariable=self.max_gen_var, width=7).grid(row=3, column=1, sticky="e", pady=2)

        ttk.Label(grp_alg, text="Semilla Aleatoria (Seed):", style="Card.TLabel").grid(row=4, column=0, sticky="w", pady=2)
        ttk.Entry(grp_alg, textvariable=self.seed_var, width=8).grid(row=4, column=1, sticky="e", pady=2)

        # Sub-fila de Hiperparámetros AG y PSO
        hp_sub = ttk.Frame(grp_alg, style="Card.TFrame")
        hp_sub.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(6, 2))

        ag_row = ttk.Frame(hp_sub, style="Card.TFrame")
        ag_row.pack(fill="x", pady=1)
        ttk.Label(ag_row, text="AG  -> Pc:", style="Card.TLabel").pack(side="left")
        ttk.Entry(ag_row, textvariable=self.pc_var, width=5).pack(side="left", padx=(2, 8))
        ttk.Label(ag_row, text="Pm:", style="Card.TLabel").pack(side="left")
        ttk.Entry(ag_row, textvariable=self.pm_var, width=5).pack(side="left", padx=(2, 0))

        pso_row = ttk.Frame(hp_sub, style="Card.TFrame")
        pso_row.pack(fill="x", pady=1)
        ttk.Label(pso_row, text="PSO -> ω:", style="Card.TLabel").pack(side="left")
        ttk.Entry(pso_row, textvariable=self.omega_var, width=4).pack(side="left", padx=(2, 6))
        ttk.Label(pso_row, text="φp:", style="Card.TLabel").pack(side="left")
        ttk.Entry(pso_row, textvariable=self.phip_var, width=4).pack(side="left", padx=(2, 6))
        ttk.Label(pso_row, text="φg:", style="Card.TLabel").pack(side="left")
        ttk.Entry(pso_row, textvariable=self.phig_var, width=4).pack(side="left", padx=(2, 0))

        # Botones de ejecución
        self.btn_run_all = ttk.Button(
            scroll_content,
            text="🚀 Ejecutar AG + PSO + Frente de Pareto",
            style="Action.TButton",
            command=self.start_full_optimization
        )
        self.btn_run_all.pack(fill="x", padx=6, pady=(6, 4))

        btn_row = ttk.Frame(scroll_content, style="Card.TFrame")
        btn_row.pack(fill="x", padx=6, pady=(0, 4))

        self.btn_10seeds = ttk.Button(
            btn_row,
            text="🎲 10 Semillas (Parte IV)",
            style="Secondary.TButton",
            command=self.start_10seeds_experiment
        )
        self.btn_10seeds.pack(side="left", fill="x", expand=True, padx=(0, 3))

        self.btn_pareto3d = ttk.Button(
            btn_row,
            text="🌐 Pareto 3D Interactivo",
            style="Secondary.TButton",
            command=self.open_pareto_3d
        )
        self.btn_pareto3d.pack(side="right", fill="x", expand=True, padx=(3, 0))

        self.lbl_status = ttk.Label(
            scroll_content,
            text="Listo. Presione 'Ejecutar' o explore el simulador.",
            style="Subtext.TLabel",
            font=FONTS["metric_lbl"]
        )
        self.lbl_status.pack(fill="x", padx=6, pady=(0, 4))

        # --- 3. Simulador Interactivo de Vehículo en Tiempo Real (Parte I) ---
        grp_sim = ttk.LabelFrame(scroll_content, text=" 3. Simulador Físico de Automóvil (En Vivo) ", style="TLabelframe", padding=8)
        grp_sim.pack(fill="x", padx=6, pady=4)

        sim_vars = [
            ("P: Potencia (80-200 kW)", self.sim_P_var, 80.0, 200.0, 1.0),
            ("r: Reducción peso (0-1)", self.sim_r_var, 0.0, 1.0, 0.02),
            ("a: Aerodinámica (0-1)", self.sim_a_var, 0.0, 1.0, 0.02),
            ("b: Neumáticos (0-1)", self.sim_b_var, 0.0, 1.0, 0.02),
            ("g: Transmisión (2.8-4.2)", self.sim_g_var, 2.8, 4.2, 0.05),
            ("h: Efic. térmica (0-1)", self.sim_h_var, 0.0, 1.0, 0.02)
        ]

        for idx, (label_txt, var, v_min, v_max, step) in enumerate(sim_vars):
            row_f = ttk.Frame(grp_sim, style="Card.TFrame")
            row_f.pack(fill="x", pady=1)
            ttk.Label(row_f, text=label_txt, style="Card.TLabel", width=23).pack(side="left")
            scale = tk.Scale(
                row_f, variable=var, from_=v_min, to=v_max, resolution=step,
                orient="horizontal", showvalue=True, length=135,
                bg=COLORS["bg_card"], fg=COLORS["fg_text"], highlightthickness=0,
                troughcolor=COLORS["bg_dark"], activebackground=COLORS["primary"],
                font=FONTS["metric_lbl"],
                command=lambda _v: self._update_simulator_display()
            )
            scale.pack(side="right")

        self.lbl_sim_out = ttk.Label(
            grp_sim,
            text="",
            style="Card.TLabel",
            font=FONTS["mono"],
            justify="left"
        )
        self.lbl_sim_out.pack(fill="x", pady=(6, 2))

        self.lbl_sim_feas = ttk.Label(
            grp_sim,
            text="",
            style="Subtitle.TLabel",
            font=FONTS["subtitle"]
        )
        self.lbl_sim_feas.pack(anchor="w", pady=(2, 0))

        # =========================================================
        # COLUMNA DERECHA: Dashboard 2x2 de Gráficas + Tabla
        # =========================================================
        right_box = ttk.Frame(main_box, style="TFrame")
        right_box.pack(side="right", fill="both", expand=True, padx=(4, 0))

        # 1. Figura con 4 Subplots (2x2)
        self.fig = Figure(figsize=(7.6, 5.0), dpi=100, facecolor=COLORS["bg_card"])
        self.ax_conv = self.fig.add_subplot(2, 2, 1)
        self.ax_pareto_vc = self.fig.add_subplot(2, 2, 2)
        self.ax_pareto_cost = self.fig.add_subplot(2, 2, 3)
        self.ax_bars = self.fig.add_subplot(2, 2, 4)
        self.fig.tight_layout(pad=2.4)

        self.canvas = FigureCanvasTkAgg(self.fig, master=right_box)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill="both", expand=True, pady=(0, 6))
        self._show_placeholder_plots()

        # 2. Tabla Comparativa de Diseños Encontrados (inferior)
        tbl_card = ttk.Frame(right_box, style="Card.TFrame", padding=8)
        tbl_card.pack(fill="x", side="bottom")

        hdr_tbl = ttk.Frame(tbl_card, style="Card.TFrame")
        hdr_tbl.pack(fill="x", pady=(0, 4))
        ttk.Label(
            hdr_tbl,
            text="🏆 Comparativa de Diseños Automotrices Óptimos (Clic en una fila para cargarla en el Simulador)",
            style="Subtitle.TLabel"
        ).pack(side="left")

        self.btn_export = ttk.Button(
            hdr_tbl,
            text="💾 Exportar CSV / TXT",
            style="Secondary.TButton",
            command=self._export_current_automotive,
            state="disabled"
        )
        self.btn_export.pack(side="right")

        cols = ("perfil", "vmax", "consumo", "costo", "acel", "masa", "vars", "estado")
        self.tree = ttk.Treeview(tbl_card, columns=cols, show="headings", height=6)
        self.tree.heading("perfil", text="Algoritmo / Perfil de Diseño")
        self.tree.heading("vmax", text="V_máx (km/h)")
        self.tree.heading("consumo", text="Consumo (L/100km)")
        self.tree.heading("costo", text="Costo ($ MXN)")
        self.tree.heading("acel", text="0-100 (s)")
        self.tree.heading("masa", text="Masa (kg)")
        self.tree.heading("vars", text="Variables [P, r, a, b, g, h]")
        self.tree.heading("estado", text="Factibilidad")

        self.tree.column("perfil", width=185, anchor="w")
        self.tree.column("vmax", width=85, anchor="center")
        self.tree.column("consumo", width=105, anchor="center")
        self.tree.column("costo", width=100, anchor="center")
        self.tree.column("acel", width=70, anchor="center")
        self.tree.column("masa", width=75, anchor="center")
        self.tree.column("vars", width=195, anchor="center")
        self.tree.column("estado", width=85, anchor="center")

        self.tree.pack(fill="x", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_table_row_selected)

    def _style_all_axes(self):
        for ax in [self.ax_conv, self.ax_pareto_vc, self.ax_pareto_cost, self.ax_bars]:
            ax.set_facecolor(COLORS["bg_dark"])
            ax.tick_params(colors=COLORS["fg_subtext"], labelsize=7.5)
            for spine in ax.spines.values():
                spine.set_color(COLORS["border"])
            ax.grid(True, linestyle="--", alpha=0.22, color=COLORS["fg_subtext"])

    def _show_placeholder_plots(self):
        for ax in [self.ax_conv, self.ax_pareto_vc, self.ax_pareto_cost, self.ax_bars]:
            ax.clear()
        self._style_all_axes()

        self.ax_conv.set_title("1. Convergencia Uniobjetivo (AG vs PSO)", color=COLORS["primary"], fontsize=8.5, fontweight="bold")
        self.ax_pareto_vc.set_title("2. Frente de Pareto: Velocidad vs Consumo", color=COLORS["accent"], fontsize=8.5, fontweight="bold")
        self.ax_pareto_cost.set_title("3. Frente de Pareto: Costo vs Velocidad", color=COLORS["success"], fontsize=8.5, fontweight="bold")
        self.ax_bars.set_title("4. Perfil de Variables Óptimas Normalizadas", color=COLORS["warning"], fontsize=8.5, fontweight="bold")

        for ax in [self.ax_conv, self.ax_pareto_vc, self.ax_pareto_cost, self.ax_bars]:
            ax.text(0.5, 0.5, "Presione 'Ejecutar AG + PSO + Frente de Pareto'",
                    color=COLORS["fg_subtext"], ha="center", va="center", fontsize=8, transform=ax.transAxes)

        self.fig.tight_layout(pad=2.2)
        self.canvas.draw_idle()

    def _on_scenario_changed(self, event=None):
        scen = self.scenario_var.get()
        if scen in SCENARIO_PRESETS:
            w1, w2, w3 = SCENARIO_PRESETS[scen]["weights"]
            self.w_vel_var.set(w1)
            self.w_cons_var.set(w2)
            self.w_cost_var.set(w3)

    def _update_simulator_display(self):
        try:
            x_sim = [
                float(self.sim_P_var.get()),
                float(self.sim_r_var.get()),
                float(self.sim_a_var.get()),
                float(self.sim_b_var.get()),
                float(self.sim_g_var.get()),
                float(self.sim_h_var.get())
            ]
            max_cost = self._get_max_cost_limit()
            info = evaluate_vehicle(x_sim, max_cost_limit=max_cost)

            txt = (
                f"• Velocidad Máx : {info['v_max']:6.1f} km/h  (Mín: 200 km/h)\n"
                f"• Acel. 0-100   : {info['t_0_100']:6.2f} s     (Máx: 9.00 s)\n"
                f"• Consumo Pond. : {info['c_comb']:6.2f} L/100 (60:{info['c_60']:.1f}|90:{info['c_90']:.1f}|120:{info['c_120']:.1f})\n"
                f"• Costo Fabr.   : ${info['c_fab']:9,.0f} (Máx: ${max_cost:,.0f})\n"
                f"• Masa Total    : {info['mass']:6.1f} kg    (Máx: 1,500 kg)\n"
                f"• Cd / Efic.Térm: {info['cd']:.3f} / {info['eta_thermal']*100:.1f}%"
            )
            self.lbl_sim_out.config(text=txt)

            if info["is_feasible"]:
                self.lbl_sim_feas.config(text="✅ DISEÑO FACTIBLE (Cumple las 4 restricciones)", foreground=COLORS["success"])
            else:
                reasons = []
                if info["constraints"][0] > 0: reasons.append("V<200")
                if info["constraints"][1] > 0: reasons.append("0-100>9s")
                if info["constraints"][2] > 0: reasons.append("Costo Excedido")
                if info["constraints"][3] > 0: reasons.append("Masa>1500kg")
                self.lbl_sim_feas.config(text=f"❌ INFACTIBLE: {', '.join(reasons)}", foreground=COLORS["danger"])
        except Exception:
            pass

    def _on_table_row_selected(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        item_id = sel[0]
        if item_id in self.row_vehicles:
            vec = self.row_vehicles[item_id]
            self.sim_P_var.set(round(vec[0], 1))
            self.sim_r_var.set(round(vec[1], 3))
            self.sim_a_var.set(round(vec[2], 3))
            self.sim_b_var.set(round(vec[3], 3))
            self.sim_g_var.set(round(vec[4], 3))
            self.sim_h_var.set(round(vec[5], 3))
            self._update_simulator_display()

    def open_pareto_3d(self):
        if not self.last_moo_res and not self.last_ga_res:
            messagebox.showinfo("Pareto 3D", "Ejecute primero la optimización para visualizar el Frente de Pareto 3D.")
            return
        Pareto3DWindow(
            self,
            moo_res=self.last_moo_res,
            ga_res=self.last_ga_res,
            pso_res=self.last_pso_res,
            max_cost_limit=self._get_max_cost_limit()
        )

    def start_full_optimization(self):
        if self.is_running:
            return
        self.is_running = True
        self.btn_run_all.config(state="disabled")
        self.btn_10seeds.config(state="disabled")
        self.lbl_status.config(text="Ejecutando AG, PSO y Frente de Pareto Multiobjetivo...")

        for item in self.tree.get_children():
            self.tree.delete(item)
        self.row_vehicles.clear()

        threading.Thread(target=self._worker_full_optimization, daemon=True).start()

    def _worker_full_optimization(self):
        try:
            weights = (
                float(self.w_vel_var.get()),
                float(self.w_cons_var.get()),
                float(self.w_cost_var.get())
            )
            max_cost = self._get_max_cost_limit()
            pop_size = int(self.pop_size_var.get())
            max_gen = int(self.max_gen_var.get())
            seed = int(self.seed_var.get())
            moo_algo = self.moo_algo_var.get()
            pc = float(self.pc_var.get())
            pm = float(self.pm_var.get())
            omega = float(self.omega_var.get())
            phip = float(self.phip_var.get())
            phig = float(self.phig_var.get())

            ga_res = run_automotive_ga(
                weights=weights,
                max_cost_limit=max_cost,
                pop_size=pop_size,
                max_generations=max_gen,
                pc=pc,
                pm=pm,
                seed=seed
            )

            pso_res = run_automotive_pso(
                weights=weights,
                max_cost_limit=max_cost,
                swarmsize=pop_size,
                maxiter=max_gen,
                omega=omega,
                phip=phip,
                phig=phig,
                seed=seed
            )

            moo_res = run_automotive_moo(
                algorithm_name=moo_algo,
                max_cost_limit=max_cost,
                pop_size=pop_size,
                n_gen=max_gen,
                seed=seed
            )

            config = {
                "scenario": self.scenario_var.get(),
                "weights": list(weights),
                "challenge_mode": bool(self.challenge_mode_var.get()),
                "max_cost_limit": max_cost,
                "moo_algorithm": moo_algo,
                "pop_size": pop_size,
                "max_generations": max_gen,
                "seed": seed,
                "pc": pc,
                "pm": pm,
                "omega": omega,
                "phip": phip,
                "phig": phig
            }

            self.after(0, lambda: self._on_optimization_finished(config, ga_res, pso_res, moo_res, max_cost))
        except Exception as e:
            self.after(0, lambda: self._on_worker_error(str(e)))

    def _on_worker_error(self, err_msg: str):
        self.is_running = False
        self.btn_run_all.config(state="normal")
        self.btn_10seeds.config(state="normal")
        self.lbl_status.config(text=f"Error: {err_msg}")
        messagebox.showerror("Error en Optimización Automotriz", err_msg)

    def _on_optimization_finished(
        self,
        config: Dict[str, Any],
        ga_res: Dict[str, Any],
        pso_res: Dict[str, Any],
        moo_res: Dict[str, Any],
        max_cost: float
    ):
        self.is_running = False
        self.btn_run_all.config(state="normal")
        self.btn_10seeds.config(state="normal")

        self.last_ga_res = ga_res
        self.last_pso_res = pso_res
        self.last_moo_res = moo_res

        # Registrar automáticamente en el Historial y Registros
        if self.logger:
            try:
                self.last_run_id = self.logger.save_automotive_run(config, ga_res, pso_res, moo_res)
                self.btn_export.config(state="normal")
            except Exception:
                pass

        self.lbl_status.config(
            text=f"Completado y guardado en Historial: AG ({ga_res['execution_time']:.2f}s) | "
                 f"PSO ({pso_res['execution_time']:.2f}s) | {moo_res['algorithm']} ({moo_res['n_pareto']} sols Pareto)"
        )

        # Renderizar las 4 gráficas y poblar la tabla
        self._render_dashboard_plots(ga_res, pso_res, moo_res, max_cost)
        self._populate_solutions_table(ga_res, pso_res, moo_res)

    def _export_current_automotive(self):
        if not self.logger or not self.last_run_id:
            messagebox.showinfo("Exportar", "Ejecute primero la optimización automotriz.")
            return

        path = filedialog.asksaveasfilename(
            parent=self,
            title="Exportar Resultados de Diseño Automotriz",
            defaultextension=".csv",
            initialfile=f"diseno_automotriz_{self.last_run_id}.csv",
            filetypes=[
                ("Archivo CSV (Tabla + Frente de Pareto + Convergencia)", "*.csv"),
                ("Reporte Detallado de Texto (TXT)", "*.txt")
            ]
        )
        if not path:
            return
        try:
            if path.lower().endswith(".txt"):
                self.logger.export_txt_report(self.last_run_id, path)
            else:
                self.logger.export_history_to_csv(self.last_run_id, path)
            messagebox.showinfo("Exportación Exitosa", f"Resultados automotrices exportados en:\n{path}")
        except Exception as e:
            messagebox.showerror("Error al exportar", str(e))

    def set_data(self, config: Dict[str, Any]):
        """Carga los hiperparámetros guardados desde el Historial y Registros."""
        if "scenario" in config:
            self.scenario_var.set(config["scenario"])
        if "weights" in config and len(config["weights"]) == 3:
            self.w_vel_var.set(config["weights"][0])
            self.w_cons_var.set(config["weights"][1])
            self.w_cost_var.set(config["weights"][2])
        if "challenge_mode" in config:
            self.challenge_mode_var.set(bool(config["challenge_mode"]))
        if "moo_algorithm" in config:
            self.moo_algo_var.set(config["moo_algorithm"])
        if "pop_size" in config:
            self.pop_size_var.set(int(config["pop_size"]))
        if "max_generations" in config:
            self.max_gen_var.set(int(config["max_generations"]))
        if "seed" in config and config["seed"] is not None:
            self.seed_var.set(int(config["seed"]))
        if "pc" in config:
            self.pc_var.set(float(config["pc"]))
        if "pm" in config:
            self.pm_var.set(float(config["pm"]))
        if "omega" in config:
            self.omega_var.set(float(config["omega"]))
        if "phip" in config:
            self.phip_var.set(float(config["phip"]))
        if "phig" in config:
            self.phig_var.set(float(config["phig"]))
        self._update_simulator_display()

    def _render_dashboard_plots(
        self,
        ga_res: Dict[str, Any],
        pso_res: Dict[str, Any],
        moo_res: Dict[str, Any],
        max_cost: float
    ):
        for ax in [self.ax_conv, self.ax_pareto_vc, self.ax_pareto_cost, self.ax_bars]:
            ax.clear()
        self._style_all_axes()

        # 1. Gráfica de Convergencia Uniobjetivo (AG vs PSO)
        ga_h = ga_res.get("history", [])
        pso_h = pso_res.get("history", [])
        if ga_h:
            self.ax_conv.plot(
                [h["generation"] for h in ga_h],
                [h["best_j"] for h in ga_h],
                color="#89b4fa", linewidth=2.0, label=f"AG (J={ga_res['best_j']:.4f})"
            )
        if pso_h:
            self.ax_conv.plot(
                [h["generation"] for h in pso_h],
                [h["best_j"] for h in pso_h],
                color="#a6e3a1", linewidth=2.0, linestyle="--", label=f"PSO (J={pso_res['best_j']:.4f})"
            )
        self.ax_conv.set_title("1. Convergencia Función Agregada J(x)", color=COLORS["primary"], fontsize=8.5, fontweight="bold")
        self.ax_conv.set_xlabel("Generación / Iteración", color=COLORS["fg_subtext"], fontsize=7.5)
        self.ax_conv.set_ylabel("J(x) Ponderado", color=COLORS["fg_subtext"], fontsize=7.5)
        self.ax_conv.legend(loc="upper right", facecolor=COLORS["bg_card"], edgecolor=COLORS["border"], labelcolor=COLORS["fg_text"], fontsize=7)

        # 2. Frente de Pareto 2D: Velocidad Máx vs Consumo
        sols = moo_res.get("solutions", [])
        alg_label = moo_res.get("algorithm", "MOO")
        if sols:
            v_arr = [s["v_max"] for s in sols]
            c_arr = [s["c_comb"] for s in sols]
            cost_arr = [s["c_fab"] for s in sols]
            self.ax_pareto_vc.scatter(
                v_arr, c_arr, c=cost_arr, cmap="viridis", s=28, alpha=0.85, label=f"Pareto {alg_label}"
            )

        gv = ga_res["vehicle"]
        pv = pso_res["vehicle"]
        self.ax_pareto_vc.scatter([gv["v_max"]], [gv["c_comb"]], color="#89b4fa", s=95, marker="^", edgecolor="#ffffff", zorder=4, label="AG")
        self.ax_pareto_vc.scatter([pv["v_max"]], [pv["c_comb"]], color="#a6e3a1", s=95, marker="P", edgecolor="#11111b", zorder=4, label="PSO")

        knee = moo_res.get("representatives", {}).get("Mejor Compromiso (Rodilla Pareto)")
        if knee:
            self.ax_pareto_vc.scatter([knee["v_max"]], [knee["c_comb"]], color="#f9e2af", s=130, marker="*", edgecolor="#11111b", zorder=5, label="Compromiso")

        self.ax_pareto_vc.set_title(f"2. Frente Pareto ({alg_label}): Velocidad vs Consumo", color=COLORS["accent"], fontsize=8.5, fontweight="bold")
        self.ax_pareto_vc.set_xlabel("Velocidad Máx (km/h) [↑]", color=COLORS["fg_subtext"], fontsize=7.5)
        self.ax_pareto_vc.set_ylabel("Consumo (L/100km) [↓]", color=COLORS["fg_subtext"], fontsize=7.5)
        self.ax_pareto_vc.legend(loc="best", facecolor=COLORS["bg_card"], edgecolor=COLORS["border"], labelcolor=COLORS["fg_text"], fontsize=6.5)

        # 3. Frente de Pareto 2D: Costo vs Velocidad Máx
        if sols:
            self.ax_pareto_cost.scatter(
                [s["c_fab"] / 1000.0 for s in sols],
                [s["v_max"] for s in sols],
                c=[s["c_comb"] for s in sols],
                cmap="plasma", s=28, alpha=0.85, label=f"Pareto {alg_label}"
            )
        self.ax_pareto_cost.scatter([gv["c_fab"] / 1000.0], [gv["v_max"]], color="#89b4fa", s=95, marker="^", edgecolor="#ffffff", zorder=4, label="AG")
        self.ax_pareto_cost.scatter([pv["c_fab"] / 1000.0], [pv["v_max"]], color="#a6e3a1", s=95, marker="P", edgecolor="#11111b", zorder=4, label="PSO")
        if knee:
            self.ax_pareto_cost.scatter([knee["c_fab"] / 1000.0], [knee["v_max"]], color="#f9e2af", s=130, marker="*", edgecolor="#11111b", zorder=5, label="Compromiso")

        self.ax_pareto_cost.axvline(max_cost / 1000.0, color=COLORS["danger"], linestyle=":", linewidth=1.4, label=f"Tope ${max_cost/1000:.0f}k")
        self.ax_pareto_cost.set_title("3. Frente Pareto: Costo ($k MXN) vs Velocidad", color=COLORS["success"], fontsize=8.5, fontweight="bold")
        self.ax_pareto_cost.set_xlabel("Costo de Fabricación (Miles $ MXN) [↓]", color=COLORS["fg_subtext"], fontsize=7.5)
        self.ax_pareto_cost.set_ylabel("Velocidad Máx (km/h) [↑]", color=COLORS["fg_subtext"], fontsize=7.5)
        self.ax_pareto_cost.legend(loc="best", facecolor=COLORS["bg_card"], edgecolor=COLORS["border"], labelcolor=COLORS["fg_text"], fontsize=6.5)

        # 4. Gráfica de Barras de Variables Normalizadas [P, r, a, b, g, h] en [0, 1]
        def norm_x(x_list):
            return [
                (x_list[i] - AUTOMOTIVE_BOUNDS[i][0]) / (AUTOMOTIVE_BOUNDS[i][1] - AUTOMOTIVE_BOUNDS[i][0])
                for i in range(6)
            ]

        labels = ["P", "r", "a", "b", "g", "h"]
        x_pos = np.arange(len(labels))
        width = 0.25

        ga_norm = norm_x(gv["x"])
        pso_norm = norm_x(pv["x"])
        self.ax_bars.bar(x_pos - width, ga_norm, width, label="AG", color="#89b4fa", alpha=0.85)
        self.ax_bars.bar(x_pos, pso_norm, width, label="PSO", color="#a6e3a1", alpha=0.85)
        if knee:
            knee_norm = norm_x(knee["x"])
            self.ax_bars.bar(x_pos + width, knee_norm, width, label="Compromiso MOO", color="#f9e2af", alpha=0.85)

        self.ax_bars.set_xticks(x_pos)
        self.ax_bars.set_xticklabels(labels, color=COLORS["fg_text"], fontsize=8)
        self.ax_bars.set_ylim(0, 1.15)
        self.ax_bars.set_title("4. ADN del Vehículo (Variables Normalizadas 0-1)", color=COLORS["warning"], fontsize=8.5, fontweight="bold")
        self.ax_bars.set_ylabel("Nivel [0 - 1]", color=COLORS["fg_subtext"], fontsize=7.5)
        self.ax_bars.legend(loc="upper right", facecolor=COLORS["bg_card"], edgecolor=COLORS["border"], labelcolor=COLORS["fg_text"], fontsize=6.5)

        self.fig.tight_layout(pad=2.2)
        self.canvas.draw_idle()

    def _populate_solutions_table(
        self,
        ga_res: Dict[str, Any],
        pso_res: Dict[str, Any],
        moo_res: Dict[str, Any]
    ):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.row_vehicles.clear()

        def add_vehicle_row(label: str, v_info: Dict[str, Any]):
            if not v_info:
                return
            x = v_info["x"]
            vars_str = f"[{x[0]:.0f}kW, r={x[1]:.2f}, a={x[2]:.2f}, b={x[3]:.2f}, g={x[4]:.2f}, h={x[5]:.2f}]"
            feas_str = "✅ Factible" if v_info["is_feasible"] else "❌ Infactible"
            row_vals = (
                label,
                f"{v_info['v_max']:.2f}",
                f"{v_info['c_comb']:.2f}",
                f"${v_info['c_fab']:,.0f}",
                f"{v_info['t_0_100']:.2f} s",
                f"{v_info['mass']:.1f}",
                vars_str,
                feas_str
            )
            item_id = self.tree.insert("", "end", values=row_vals)
            self.row_vehicles[item_id] = list(x)

        scen_short = self.scenario_var.get().split(" (")[0]
        add_vehicle_row(f"🧬 AG ({scen_short})", ga_res.get("vehicle"))
        add_vehicle_row(f"🐝 PSO ({scen_short})", pso_res.get("vehicle"))

        alg_name = moo_res.get("algorithm", "MOO")
        reps = moo_res.get("representatives", {})
        for rep_name, rep_info in reps.items():
            add_vehicle_row(f"🌟 {alg_name}: {rep_name}", rep_info)

    # =========================================================
    # PARTE IV: EXPERIMENTACIÓN ESTADÍSTICA CON 10 SEMILLAS
    # =========================================================
    def start_10seeds_experiment(self):
        if self.is_running:
            return
        self.is_running = True
        self.btn_run_all.config(state="disabled")
        self.btn_10seeds.config(state="disabled")
        self.lbl_status.config(text="Ejecutando 10 repeticiones con diferentes semillas para AG y PSO (Parte IV)...")

        threading.Thread(target=self._worker_10seeds, daemon=True).start()

    def _worker_10seeds(self):
        try:
            weights = (
                float(self.w_vel_var.get()),
                float(self.w_cons_var.get()),
                float(self.w_cost_var.get())
            )
            max_cost = self._get_max_cost_limit()
            pop_size = int(self.pop_size_var.get())
            max_gen = int(self.max_gen_var.get())

            stats = run_multi_seed_experiment(
                weights=weights,
                max_cost_limit=max_cost,
                n_seeds=10,
                pop_size=pop_size,
                max_iter=max_gen
            )
            config_10 = {
                "scenario": self.scenario_var.get(),
                "weights": list(weights),
                "challenge_mode": bool(self.challenge_mode_var.get()),
                "max_cost_limit": max_cost,
                "n_seeds": 10,
                "pop_size": pop_size,
                "max_generations": max_gen,
                "pc": float(self.pc_var.get()),
                "pm": float(self.pm_var.get()),
                "omega": float(self.omega_var.get()),
                "phip": float(self.phip_var.get()),
                "phig": float(self.phig_var.get())
            }
            self.after(0, lambda: self._show_10seeds_dialog(config_10, stats, max_cost))
        except Exception as e:
            self.after(0, lambda: self._on_worker_error(str(e)))

    def _show_10seeds_dialog(self, config_10: Dict[str, Any], stats: Dict[str, Any], max_cost: float):
        self.is_running = False
        self.btn_run_all.config(state="normal")
        self.btn_10seeds.config(state="normal")

        if self.logger:
            try:
                self.last_10seeds_run_id = self.logger.save_automotive_10seeds_run(config_10, stats)
            except Exception:
                pass

        self.lbl_status.config(text="Experimento estadístico de 10 semillas completado y guardado en Historial.")

        dlg = tk.Toplevel(self)
        dlg.title("Resultados Estadísticos de 10 Repeticiones (Parte IV)")
        dlg.geometry("780x420")
        dlg.configure(bg=COLORS["bg_dark"])

        card = ttk.Frame(dlg, style="Card.TFrame", padding=14)
        card.pack(fill="both", expand=True, padx=12, pady=12)

        hdr = ttk.Frame(card, style="Card.TFrame")
        hdr.pack(fill="x", pady=(0, 10))

        scen_name = self.scenario_var.get()
        ttk.Label(
            hdr,
            text=f"📊 Estadísticas sobre 10 Semillas Aleatorias | {scen_name} (Tope: ${max_cost:,.0f} MXN)",
            style="Title.TLabel"
        ).pack(side="left")

        def _export_10seeds():
            if not self.logger or not self.last_10seeds_run_id:
                return
            path = filedialog.asksaveasfilename(
                parent=dlg,
                title="Exportar Estadísticas de 10 Semillas",
                defaultextension=".csv",
                initialfile=f"automotriz_10semillas_{self.last_10seeds_run_id}.csv",
                filetypes=[
                    ("Archivo CSV (Resumen + 10 Corridas)", "*.csv"),
                    ("Reporte Detallado de Texto (TXT)", "*.txt")
                ]
            )
            if not path:
                return
            try:
                if path.lower().endswith(".txt"):
                    self.logger.export_txt_report(self.last_10seeds_run_id, path)
                else:
                    self.logger.export_history_to_csv(self.last_10seeds_run_id, path)
                messagebox.showinfo("Exportación Exitosa", f"Estadísticas de 10 semillas guardadas en:\n{path}", parent=dlg)
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=dlg)

        ttk.Button(
            hdr,
            text="💾 Exportar CSV / TXT",
            style="Secondary.TButton",
            command=_export_10seeds
        ).pack(side="right")

        cols = ("metric", "ga", "pso", "winner")
        tree = ttk.Treeview(card, columns=cols, show="headings", height=8)
        tree.heading("metric", text="Estadístico (10 ejecuciones)")
        tree.heading("ga", text="Algoritmo Genético (AG)")
        tree.heading("pso", text="Enjambre de Partículas (PSO)")
        tree.heading("winner", text="Superior")

        tree.column("metric", width=230, anchor="w")
        tree.column("ga", width=180, anchor="center")
        tree.column("pso", width=180, anchor="center")
        tree.column("winner", width=110, anchor="center")
        tree.pack(fill="both", expand=True)

        ga_s = stats["ga_summary"]
        pso_s = stats["pso_summary"]

        rows = [
            ("Media de J(x) Ponderado (Menor=Mejor)", f"{ga_s['mean_j']:.5f}", f"{pso_s['mean_j']:.5f}", "AG" if ga_s["mean_j"] < pso_s["mean_j"] else "PSO"),
            ("Desviación Estándar de J(x) (Estabilidad)", f"±{ga_s['std_j']:.5f}", f"±{pso_s['std_j']:.5f}", "AG" if ga_s["std_j"] < pso_s["std_j"] else "PSO"),
            ("Mejor J(x) de las 10 corridas", f"{ga_s['best_j']:.5f}", f"{pso_s['best_j']:.5f}", "AG" if ga_s["best_j"] < pso_s["best_j"] else "PSO"),
            ("Peor J(x) de las 10 corridas", f"{ga_s['worst_j']:.5f}", f"{pso_s['worst_j']:.5f}", "AG" if ga_s["worst_j"] < pso_s["worst_j"] else "PSO"),
            ("Velocidad Máx Promedio (km/h)", f"{ga_s['mean_v_max']:.2f} km/h", f"{pso_s['mean_v_max']:.2f} km/h", "-"),
            ("Consumo Promedio (L/100km)", f"{ga_s['mean_c_comb']:.2f} L/100km", f"{pso_s['mean_c_comb']:.2f} L/100km", "-"),
            ("Costo Promedio ($ MXN)", f"${ga_s['mean_c_fab']:,.0f}", f"${pso_s['mean_c_fab']:,.0f}", "-"),
            ("Tasa de Factibilidad / Tiempo Medio", f"{ga_s['feasibility_rate']:.0f}% ({ga_s['mean_time']:.3f}s)", f"{pso_s['feasibility_rate']:.0f}% ({pso_s['mean_time']:.3f}s)", "PSO (Tiempo)")
        ]

        for r in rows:
            tree.insert("", "end", values=r)
