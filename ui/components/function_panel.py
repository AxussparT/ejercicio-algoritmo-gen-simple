"""
Panel de configuración para la función objetivo univariada f(x).
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Tuple, Dict, Any
from benchmarks.test_functions import BENCHMARK_FUNCTIONS
from logica.evaluator import SafeEvaluator
from ui.styles import COLORS, FONTS

class FunctionPanel(ttk.LabelFrame):
    def __init__(self, parent, on_preview_callback: Callable[[str, float, float], None] = None):
        super().__init__(parent, text=" 1. Función Objetivo f(x) ", style="TLabelframe", padding=10)
        self.on_preview_callback = on_preview_callback

        # Variables
        self.selected_preset_var = tk.StringVar(value="Esfera 1D (Convexa simple)")
        self.expression_var = tk.StringVar(value="x**2")
        self.lower_bound_var = tk.DoubleVar(value=-10.0)
        self.upper_bound_var = tk.DoubleVar(value=10.0)
        self.goal_var = tk.StringVar(value="minimize")

        self._build_ui()

    def _build_ui(self):
        # 1. Selector de Predefinidas
        row = 0
        ttk.Label(self, text="Función de prueba:", style="Card.TLabel").grid(row=row, column=0, sticky="w", pady=(0, 2))
        
        preset_names = list(BENCHMARK_FUNCTIONS.keys()) + ["Personalizada..."]
        self.combo_presets = ttk.Combobox(self, textvariable=self.selected_preset_var, values=preset_names, state="readonly", width=34)
        self.combo_presets.grid(row=row, column=1, columnspan=2, sticky="ew", pady=(0, 6))
        self.combo_presets.bind("<<ComboboxSelected>>", self._on_preset_change)

        # 2. Expresión f(x)
        row += 1
        ttk.Label(self, text="Expresión f(x):", style="Card.TLabel").grid(row=row, column=0, sticky="w", pady=(0, 2))
        self.entry_expr = ttk.Entry(self, textvariable=self.expression_var, width=34)
        self.entry_expr.grid(row=row, column=1, columnspan=2, sticky="ew", pady=(0, 6))

        # 3. Intervalo [a, b]
        row += 1
        ttk.Label(self, text="Intervalo [a, b]:", style="Card.TLabel").grid(row=row, column=0, sticky="w", pady=(0, 2))
        
        bounds_frame = ttk.Frame(self, style="Card.TFrame")
        bounds_frame.grid(row=row, column=1, columnspan=2, sticky="ew", pady=(0, 6))
        
        ttk.Label(bounds_frame, text="a:", style="Card.TLabel").pack(side="left")
        self.entry_lb = ttk.Entry(bounds_frame, textvariable=self.lower_bound_var, width=7)
        self.entry_lb.pack(side="left", padx=(2, 8))
        
        ttk.Label(bounds_frame, text="b:", style="Card.TLabel").pack(side="left")
        self.entry_ub = ttk.Entry(bounds_frame, textvariable=self.upper_bound_var, width=7)
        self.entry_ub.pack(side="left", padx=(2, 8))

        # 4. Objetivo (Minimizar / Maximizar)
        row += 1
        ttk.Label(self, text="Objetivo:", style="Card.TLabel").grid(row=row, column=0, sticky="w", pady=(0, 2))
        
        goal_frame = ttk.Frame(self, style="Card.TFrame")
        goal_frame.grid(row=row, column=1, columnspan=2, sticky="w", pady=(0, 6))
        
        self.rb_min = tk.Radiobutton(
            goal_frame, text="Minimizar", variable=self.goal_var, value="minimize",
            bg=COLORS["bg_card"], fg=COLORS["fg_text"], selectcolor=COLORS["bg_dark"],
            activebackground=COLORS["bg_card"], activeforeground=COLORS["primary"]
        )
        self.rb_min.pack(side="left", padx=(0, 10))

        self.rb_max = tk.Radiobutton(
            goal_frame, text="Maximizar", variable=self.goal_var, value="maximize",
            bg=COLORS["bg_card"], fg=COLORS["fg_text"], selectcolor=COLORS["bg_dark"],
            activebackground=COLORS["bg_card"], activeforeground=COLORS["primary"]
        )
        self.rb_max.pack(side="left")

        # 5. Botón de Previsualización rápida
        row += 1
        self.btn_preview = ttk.Button(self, text="🔍 Previsualizar Curva", style="Secondary.TButton", command=self._preview)
        self.btn_preview.grid(row=row, column=0, columnspan=3, sticky="ew", pady=(4, 0))

    def _on_preset_change(self, event=None):
        name = self.selected_preset_var.get()
        if name in BENCHMARK_FUNCTIONS:
            data = BENCHMARK_FUNCTIONS[name]
            self.expression_var.set(data["formula"])
            self.lower_bound_var.set(data["bounds"][0])
            self.upper_bound_var.set(data["bounds"][1])
            self.goal_var.set(data["goal"])
            if self.on_preview_callback:
                self.on_preview_callback(data["formula"], data["bounds"][0], data["bounds"][1])

    def _preview(self):
        expr = self.expression_var.get().strip()
        try:
            lb = float(self.lower_bound_var.get())
            ub = float(self.upper_bound_var.get())
            if lb >= ub:
                messagebox.showerror("Error de Intervalo", "El límite inferior (a) debe ser estrictamente menor que el superior (b).")
                return
            # Probar evaluador
            ev = SafeEvaluator(expr)
            ev(lb)
            if self.on_preview_callback:
                self.on_preview_callback(expr, lb, ub)
        except Exception as e:
            messagebox.showerror("Error en Función", f"No se pudo evaluar la función:\n{str(e)}")

    def get_data(self) -> Dict[str, Any]:
        expr = self.expression_var.get().strip()
        lb = float(self.lower_bound_var.get())
        ub = float(self.upper_bound_var.get())
        if lb >= ub:
            raise ValueError("El límite inferior 'a' debe ser menor que 'b'.")
        
        # Validar evaluador
        SafeEvaluator(expr)
        
        return {
            "function_name": self.selected_preset_var.get(),
            "expression": expr,
            "bounds": [(lb, ub)],
            "goal": self.goal_var.get()
        }

    def set_data(self, data: Dict[str, Any]):
        self.selected_preset_var.set(data.get("function_name", "Personalizada..."))
        self.expression_var.set(data.get("expression", "x**2"))
        bounds = data.get("bounds", [(-10.0, 10.0)])
        self.lower_bound_var.set(bounds[0][0])
        self.upper_bound_var.set(bounds[0][1])
        self.goal_var.set(data.get("goal", "minimize"))
