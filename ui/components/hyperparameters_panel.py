"""
Panel de configuración para operadores evolutivos e hiperparámetros.
Muestra secciones limpias y sub-paneles dinámicos que se adaptan automáticamente
según el método elegido, evitando la sobresaturación visual.
"""
import tkinter as tk
from tkinter import ttk
from typing import Dict, Any
from ui.styles import COLORS, FONTS

class HyperparametersPanel(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, text=" 2. Operadores Evolutivos e Hiperparámetros ", style="TLabelframe", padding=10)

        # Variables Generales
        self.pop_size_var = tk.IntVar(value=40)
        self.max_gen_var = tk.IntVar(value=60)
        self.seed_var = tk.StringVar(value="")

        # Variables de Selección
        self.sel_method_var = tk.StringVar(value="Torneo")
        self.k_tournament_var = tk.IntVar(value=2)
        self.a_max_var = tk.DoubleVar(value=1.6)
        self.q_var = tk.DoubleVar(value=0.5)

        # Variables de Cruce
        self.cross_method_var = tk.StringVar(value="BLX-α")
        self.pc_var = tk.DoubleVar(value=0.85)
        self.alpha_var = tk.DoubleVar(value=0.5)
        self.arith_a_var = tk.DoubleVar(value=0.25)
        self.p_mask_var = tk.DoubleVar(value=0.5)

        # Variables de Mutación
        self.mut_method_var = tk.StringVar(value="No uniforme")
        self.pm_var = tk.DoubleVar(value=0.10)
        self.b_var = tk.DoubleVar(value=1.0)

        # Variables de Sustitución
        self.rep_method_var = tk.StringVar(value="Generacional con elitismo")
        self.n_elite_var = tk.IntVar(value=2)
        self.n_replace_var = tk.IntVar(value=4)
        self.cf_var = tk.IntVar(value=3)

        self._build_ui()

    def _build_ui(self):
        # -------------------------------------------------------------
        # SELECCIÓN
        # -------------------------------------------------------------
        ttk.Label(self, text="Método de Selección:", style="Subtitle.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 2))
        
        sel_methods = [
            "Torneo",
            "Ruleta proporcional",
            "Ranking lineal",
            "Ranking no lineal",
            "Muestreo estocástico universal"
        ]
        self.combo_sel = ttk.Combobox(self, textvariable=self.sel_method_var, values=sel_methods, state="readonly", width=30)
        self.combo_sel.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 4))
        self.combo_sel.bind("<<ComboboxSelected>>", self._update_sel_subpanel)

        self.sel_subframe = ttk.Frame(self, style="SecondaryCard.TFrame", padding=4)
        self.sel_subframe.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 8))

        # -------------------------------------------------------------
        # CRUCE / COMBINACIÓN
        # -------------------------------------------------------------
        ttk.Label(self, text="Método de Cruce:", style="Subtitle.TLabel").grid(row=3, column=0, sticky="w", pady=(0, 2))
        
        cross_methods = [
            "BLX-α",
            "Aritmético",
            "Plano",
            "Uniforme",
            "PMX",
            "OX",
            "CX"
        ]
        self.combo_cross = ttk.Combobox(self, textvariable=self.cross_method_var, values=cross_methods, state="readonly", width=30)
        self.combo_cross.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(0, 4))
        self.combo_cross.bind("<<ComboboxSelected>>", self._update_cross_subpanel)

        self.cross_subframe = ttk.Frame(self, style="SecondaryCard.TFrame", padding=4)
        self.cross_subframe.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(0, 8))

        # -------------------------------------------------------------
        # MUTACIÓN
        # -------------------------------------------------------------
        ttk.Label(self, text="Método de Mutación:", style="Subtitle.TLabel").grid(row=6, column=0, sticky="w", pady=(0, 2))
        
        mut_methods = [
            "Uniforme",
            "No uniforme",
            "Por intercambio"
        ]
        self.combo_mut = ttk.Combobox(self, textvariable=self.mut_method_var, values=mut_methods, state="readonly", width=30)
        self.combo_mut.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(0, 4))
        self.combo_mut.bind("<<ComboboxSelected>>", self._update_mut_subpanel)

        self.mut_subframe = ttk.Frame(self, style="SecondaryCard.TFrame", padding=4)
        self.mut_subframe.grid(row=8, column=0, columnspan=2, sticky="ew", pady=(0, 8))

        # -------------------------------------------------------------
        # SUSTITUCIÓN / REEMPLAZO
        # -------------------------------------------------------------
        ttk.Label(self, text="Método de Sustitución:", style="Subtitle.TLabel").grid(row=9, column=0, sticky="w", pady=(0, 2))
        
        rep_methods = [
            "Generacional con elitismo",
            "Steady-state",
            "Factor de crowding"
        ]
        self.combo_rep = ttk.Combobox(self, textvariable=self.rep_method_var, values=rep_methods, state="readonly", width=30)
        self.combo_rep.grid(row=10, column=0, columnspan=2, sticky="ew", pady=(0, 4))
        self.combo_rep.bind("<<ComboboxSelected>>", self._update_rep_subpanel)

        self.rep_subframe = ttk.Frame(self, style="SecondaryCard.TFrame", padding=4)
        self.rep_subframe.grid(row=11, column=0, columnspan=2, sticky="ew", pady=(0, 8))

        # -------------------------------------------------------------
        # PARÁMETROS GLOBALES (Población, Generaciones, Semilla)
        # -------------------------------------------------------------
        glob_frame = ttk.Frame(self, style="Card.TFrame")
        glob_frame.grid(row=12, column=0, columnspan=2, sticky="ew", pady=(0, 4))

        ttk.Label(glob_frame, text="Población (N):", style="Card.TLabel").pack(side="left")
        ttk.Entry(glob_frame, textvariable=self.pop_size_var, width=6).pack(side="left", padx=(3, 10))

        ttk.Label(glob_frame, text="Generaciones (T):", style="Card.TLabel").pack(side="left")
        ttk.Entry(glob_frame, textvariable=self.max_gen_var, width=6).pack(side="left", padx=(3, 4))

        # Menú desplegable opcional para más ajustes
        self.show_more = False
        self.btn_toggle_advanced = ttk.Button(
            self, text="⚙ Ajustes Opcionales (Semilla)...", style="Secondary.TButton", command=self._toggle_advanced
        )
        self.btn_toggle_advanced.grid(row=13, column=0, columnspan=2, sticky="ew", pady=(4, 0))

        self.adv_frame = ttk.Frame(self, style="SecondaryCard.TFrame", padding=4)
        ttk.Label(self.adv_frame, text="Semilla aleatoria (opcional):", style="Card.TLabel").pack(side="left")
        ttk.Entry(self.adv_frame, textvariable=self.seed_var, width=10).pack(side="left", padx=5)

        # Construir subpaneles dinámicos iniciales
        self._update_sel_subpanel()
        self._update_cross_subpanel()
        self._update_mut_subpanel()
        self._update_rep_subpanel()

    def _toggle_advanced(self):
        self.show_more = not self.show_more
        if self.show_more:
            self.adv_frame.grid(row=14, column=0, columnspan=2, sticky="ew", pady=4)
            self.btn_toggle_advanced.config(text="▲ Ocultar Ajustes Opcionales")
        else:
            self.adv_frame.grid_forget()
            self.btn_toggle_advanced.config(text="⚙ Ajustes Opcionales (Semilla)...")

    # -------------------------------------------------------------
    # Actualizaciones de subpaneles dinámicos
    # -------------------------------------------------------------
    def _update_sel_subpanel(self, event=None):
        for widget in self.sel_subframe.winfo_children():
            widget.destroy()

        method = self.sel_method_var.get()
        if method == "Torneo":
            ttk.Label(self.sel_subframe, text="Tamaño del torneo (k):", style="Subtext.TLabel").pack(side="left")
            ttk.Entry(self.sel_subframe, textvariable=self.k_tournament_var, width=5).pack(side="left", padx=5)
        elif method == "Ranking lineal":
            ttk.Label(self.sel_subframe, text="amax (1.0 - 2.0):", style="Subtext.TLabel").pack(side="left")
            ttk.Entry(self.sel_subframe, textvariable=self.a_max_var, width=5).pack(side="left", padx=5)
        elif method == "Ranking no lineal":
            ttk.Label(self.sel_subframe, text="Factor q (0 - 1):", style="Subtext.TLabel").pack(side="left")
            ttk.Entry(self.sel_subframe, textvariable=self.q_var, width=5).pack(side="left", padx=5)
        else:
            ttk.Label(self.sel_subframe, text="Sin parámetros extra requeridos", style="Subtext.TLabel").pack(side="left")

    def _update_cross_subpanel(self, event=None):
        for widget in self.cross_subframe.winfo_children():
            widget.destroy()

        # Probabilidad de cruce siempre presente
        ttk.Label(self.cross_subframe, text="Pc:", style="Subtext.TLabel").pack(side="left")
        ttk.Entry(self.cross_subframe, textvariable=self.pc_var, width=5).pack(side="left", padx=(2, 8))

        method = self.cross_method_var.get()
        if method == "BLX-α":
            ttk.Label(self.cross_subframe, text="α:", style="Subtext.TLabel").pack(side="left")
            ttk.Entry(self.cross_subframe, textvariable=self.alpha_var, width=5).pack(side="left", padx=2)
        elif method == "Aritmético":
            ttk.Label(self.cross_subframe, text="Ponderación a:", style="Subtext.TLabel").pack(side="left")
            ttk.Entry(self.cross_subframe, textvariable=self.arith_a_var, width=5).pack(side="left", padx=2)
        elif method == "Uniforme":
            ttk.Label(self.cross_subframe, text="P_máscara:", style="Subtext.TLabel").pack(side="left")
            ttk.Entry(self.cross_subframe, textvariable=self.p_mask_var, width=5).pack(side="left", padx=2)

    def _update_mut_subpanel(self, event=None):
        for widget in self.mut_subframe.winfo_children():
            widget.destroy()

        ttk.Label(self.mut_subframe, text="Pm:", style="Subtext.TLabel").pack(side="left")
        ttk.Entry(self.mut_subframe, textvariable=self.pm_var, width=5).pack(side="left", padx=(2, 8))

        method = self.mut_method_var.get()
        if method == "No uniforme":
            ttk.Label(self.mut_subframe, text="Parámetro b:", style="Subtext.TLabel").pack(side="left")
            ttk.Entry(self.mut_subframe, textvariable=self.b_var, width=5).pack(side="left", padx=2)

    def _update_rep_subpanel(self, event=None):
        for widget in self.rep_subframe.winfo_children():
            widget.destroy()

        method = self.rep_method_var.get()
        if method == "Generacional con elitismo":
            ttk.Label(self.rep_subframe, text="Élites conservados:", style="Subtext.TLabel").pack(side="left")
            ttk.Entry(self.rep_subframe, textvariable=self.n_elite_var, width=5).pack(side="left", padx=5)
        elif method == "Steady-state":
            ttk.Label(self.rep_subframe, text="Reemplazos (n):", style="Subtext.TLabel").pack(side="left")
            ttk.Entry(self.rep_subframe, textvariable=self.n_replace_var, width=5).pack(side="left", padx=5)
        elif method == "Factor de crowding":
            ttk.Label(self.rep_subframe, text="Muestra (CF):", style="Subtext.TLabel").pack(side="left")
            ttk.Entry(self.rep_subframe, textvariable=self.cf_var, width=5).pack(side="left", padx=5)

    def get_data(self) -> Dict[str, Any]:
        """Recupera y valida los parámetros del panel."""
        pop_size = int(self.pop_size_var.get())
        max_gen = int(self.max_gen_var.get())
        if pop_size < 4:
            raise ValueError("El tamaño de población debe ser de al menos 4.")
        if max_gen < 1:
            raise ValueError("Las generaciones deben ser al menos 1.")

        seed_str = self.seed_var.get().strip()
        seed = int(seed_str) if seed_str else None

        # Selección
        sel_method = self.sel_method_var.get()
        sel_params = {}
        if sel_method == "Torneo":
            sel_params["k"] = max(1, int(self.k_tournament_var.get()))
        elif sel_method == "Ranking lineal":
            sel_params["a_max"] = float(self.a_max_var.get())
        elif sel_method == "Ranking no lineal":
            sel_params["q"] = float(self.q_var.get())

        # Cruce
        cross_method = self.cross_method_var.get()
        cross_params = {}
        if cross_method == "BLX-α":
            cross_params["alpha"] = float(self.alpha_var.get())
        elif cross_method == "Aritmético":
            cross_params["a"] = float(self.arith_a_var.get())
        elif cross_method == "Uniforme":
            cross_params["p_mask"] = float(self.p_mask_var.get())

        # Mutación
        mut_method = self.mut_method_var.get()
        mut_params = {}
        if mut_method == "No uniforme":
            mut_params["b"] = float(self.b_var.get())

        # Sustitución
        rep_method = self.rep_method_var.get()
        rep_params = {}
        if rep_method == "Generacional con elitismo":
            rep_params["n_elite"] = int(self.n_elite_var.get())
        elif rep_method == "Steady-state":
            rep_params["n_replace"] = int(self.n_replace_var.get())
        elif rep_method == "Factor de crowding":
            rep_params["cf"] = int(self.cf_var.get())

        return {
            "pop_size": pop_size,
            "max_generations": max_gen,
            "seed": seed,
            "pc": float(self.pc_var.get()),
            "pm": float(self.pm_var.get()),
            "selection_method": sel_method,
            "selection_params": sel_params,
            "crossover_method": cross_method,
            "crossover_params": cross_params,
            "mutation_method": mut_method,
            "mutation_params": mut_params,
            "replacement_method": rep_method,
            "replacement_params": rep_params
        }

    def set_data(self, data: Dict[str, Any]):
        """Carga una configuración guardada."""
        self.pop_size_var.set(data.get("pop_size", 40))
        self.max_gen_var.set(data.get("max_generations", 60))
        seed = data.get("seed", "")
        self.seed_var.set("" if seed is None else str(seed))
        self.pc_var.set(data.get("pc", 0.85))
        self.pm_var.set(data.get("pm", 0.10))

        if "selection_method" in data:
            self.sel_method_var.set(data["selection_method"])
            params = data.get("selection_params", {})
            if "k" in params: self.k_tournament_var.set(params["k"])
            if "a_max" in params: self.a_max_var.set(params["a_max"])
            if "q" in params: self.q_var.set(params["q"])
            self._update_sel_subpanel()

        if "crossover_method" in data:
            self.cross_method_var.set(data["crossover_method"])
            params = data.get("crossover_params", {})
            if "alpha" in params: self.alpha_var.set(params["alpha"])
            if "a" in params: self.arith_a_var.set(params["a"])
            if "p_mask" in params: self.p_mask_var.set(params["p_mask"])
            self._update_cross_subpanel()

        if "mutation_method" in data:
            self.mut_method_var.set(data["mutation_method"])
            params = data.get("mutation_params", {})
            if "b" in params: self.b_var.set(params["b"])
            self._update_mut_subpanel()

        if "replacement_method" in data:
            self.rep_method_var.set(data["replacement_method"])
            params = data.get("replacement_params", {})
            if "n_elite" in params: self.n_elite_var.set(params["n_elite"])
            if "n_replace" in params: self.n_replace_var.set(params["n_replace"])
            if "cf" in params: self.cf_var.set(params["cf"])
            self._update_rep_subpanel()
