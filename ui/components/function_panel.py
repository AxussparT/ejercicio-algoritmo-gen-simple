"""
Panel de configuración para la función objetivo (1D hasta n-D).
Incluye detección automática de dimensiones al escribir y entrada manual.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Tuple, Dict, Any
from benchmarks.test_functions import BENCHMARK_FUNCTIONS
from logica.evaluator import SafeEvaluator, detect_dimensions
from ui.styles import COLORS, FONTS

class FunctionPanel(ttk.LabelFrame):
    def __init__(self, parent, on_preview_callback: Callable[[str, float, float, int], None] = None):
        super().__init__(parent, text=" 1. Función Objetivo f(x) ", style="TLabelframe", padding=10)
        self.on_preview_callback = on_preview_callback

        # Variables
        self.selected_preset_var = tk.StringVar(value="Esfera 1D (Convexa simple)")
        self.expression_var = tk.StringVar(value="x**2")
        self.dimensions_var = tk.IntVar(value=1)
        self.detected_info_var = tk.StringVar(value="(Auto: 1D)")
        self.lower_bound_var = tk.DoubleVar(value=-10.0)
        self.upper_bound_var = tk.DoubleVar(value=10.0)
        self.goal_var = tk.StringVar(value="minimize")

        self._is_updating_programmatically = False

        self._build_ui()

        # Rastrear escritura en la expresión para autodetección inmediata
        self.expression_var.trace_add("write", self._on_expression_typed)

    def _build_ui(self):
        row = 0
        # 1. Selector de Predefinidas
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

        # 3. Entrada Manual de Dimensiones y Detección Automática (Justo debajo de la expresión)
        row += 1
        ttk.Label(self, text="Dimensiones (n):", style="Card.TLabel").grid(row=row, column=0, sticky="w", pady=(0, 2))
        
        dims_frame = ttk.Frame(self, style="Card.TFrame")
        dims_frame.grid(row=row, column=1, columnspan=2, sticky="ew", pady=(0, 6))
        
        # Spinbox para entrada manual
        self.spin_dims = ttk.Spinbox(dims_frame, from_=1, to=100, textvariable=self.dimensions_var, width=5)
        self.spin_dims.pack(side="left", padx=(0, 6))
        
        # Etiqueta indicadora de detección automática
        self.lbl_detected = ttk.Label(dims_frame, textvariable=self.detected_info_var, font=FONTS["metric_lbl"], foreground=COLORS["accent"], background=COLORS["bg_card"])
        self.lbl_detected.pack(side="left", padx=(2, 8))

        # Botón sutil para forzar detección si se desea
        self.btn_auto = ttk.Button(dims_frame, text="⚡ Detectar", style="Secondary.TButton", command=self._force_detect_dimensions)
        self.btn_auto.pack(side="right")

        # 4. Intervalo [a, b]
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

        # 5. Objetivo (Minimizar / Maximizar)
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

        # 6. Botón de Previsualización rápida
        row += 1
        self.btn_preview = ttk.Button(self, text="🔍 Previsualizar Función", style="Secondary.TButton", command=self._preview)
        self.btn_preview.grid(row=row, column=0, columnspan=3, sticky="ew", pady=(4, 0))

    def _on_expression_typed(self, *args):
        """Detecta automáticamente el número de dimensiones mientras el usuario escribe."""
        if self._is_updating_programmatically:
            return
        expr = self.expression_var.get()
        detected = detect_dimensions(expr)
        self.detected_info_var.set(f"(Auto: {detected}D)")
        # Si la expresión tiene variables multidimensionales evidentes, actualiza el valor de dimensiones
        if detected > 1:
            self.dimensions_var.set(detected)

    def _force_detect_dimensions(self):
        expr = self.expression_var.get()
        detected = detect_dimensions(expr)
        self.dimensions_var.set(detected)
        self.detected_info_var.set(f"(Auto: {detected}D)")

    def _on_preset_change(self, event=None):
        name = self.selected_preset_var.get()
        if name in BENCHMARK_FUNCTIONS:
            data = BENCHMARK_FUNCTIONS[name]
            self._is_updating_programmatically = True
            try:
                self.expression_var.set(data["formula"])
                dims = data.get("dimensions", 1)
                self.dimensions_var.set(dims)
                self.detected_info_var.set(f"(Preset: {dims}D)")
                self.lower_bound_var.set(data["bounds"][0])
                self.upper_bound_var.set(data["bounds"][1])
                self.goal_var.set(data["goal"])
            finally:
                self._is_updating_programmatically = False

            if self.on_preview_callback:
                self.on_preview_callback(data["formula"], data["bounds"][0], data["bounds"][1], dims)

    def _preview(self):
        expr = self.expression_var.get().strip()
        try:
            lb = float(self.lower_bound_var.get())
            ub = float(self.upper_bound_var.get())
            dims = max(1, int(self.dimensions_var.get()))
            if lb >= ub:
                messagebox.showerror("Error de Intervalo", "El límite inferior (a) debe ser menor que el superior (b).")
                return
            ev = SafeEvaluator(expr, dimensions=dims)
            # Prueba de evaluación con vector de ceros o puntos del dominio
            test_point = [ (lb + ub) / 2.0 ] * dims
            ev(test_point)
            if self.on_preview_callback:
                self.on_preview_callback(expr, lb, ub, dims)
        except Exception as e:
            messagebox.showerror("Error en Función", f"No se pudo evaluar la función en {dims}D:\n{str(e)}")

    def get_data(self) -> Dict[str, Any]:
        expr = self.expression_var.get().strip()
        lb = float(self.lower_bound_var.get())
        ub = float(self.upper_bound_var.get())
        dims = max(1, int(self.dimensions_var.get()))
        if lb >= ub:
            raise ValueError("El límite inferior 'a' debe ser menor que 'b'.")
        
        SafeEvaluator(expr, dimensions=dims)
        
        return {
            "function_name": self.selected_preset_var.get(),
            "expression": expr,
            "dimensions": dims,
            "bounds": [(lb, ub)] * dims,
            "goal": self.goal_var.get()
        }

    def set_data(self, data: Dict[str, Any]):
        self._is_updating_programmatically = True
        try:
            self.selected_preset_var.set(data.get("function_name", "Personalizada..."))
            self.expression_var.set(data.get("expression", "x**2"))
            dims = data.get("dimensions", 1)
            self.dimensions_var.set(dims)
            self.detected_info_var.set(f"(Cargado: {dims}D)")
            bounds = data.get("bounds", [(-10.0, 10.0)])
            self.lower_bound_var.set(bounds[0][0])
            self.upper_bound_var.set(bounds[0][1])
            self.goal_var.set(data.get("goal", "minimize"))
        finally:
            self._is_updating_programmatically = False
