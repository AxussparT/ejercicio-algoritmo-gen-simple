"""
Ventana Principal de la Aplicación de Algoritmo Genético.
Diseño moderno, limpio y reactivo con ejecución en hilo secundario.
"""
import os
import time
import queue
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, List

from ui.styles import apply_theme, COLORS, FONTS
from ui.components.function_panel import FunctionPanel
from ui.components.hyperparameters_panel import HyperparametersPanel
from ui.components.plot_panel import PlotPanel
from ui.components.metrics_panel import MetricsPanel
from ui.components.history_dialog import HistoryDialog

from logica.ga_engine import GAEngine
from almacenamiento.experiment_logger import ExperimentLogger

class MainWindow:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Algoritmo Genético Configurable - Optimización Univariada f(x)")
        self.root.geometry("1240x820")
        self.root.minsize(950, 550)
        self.root.configure(bg=COLORS["bg_dark"])

        apply_theme(self.root)

        # Sistema de colas para comunicación segura entre hilos
        self.update_queue = queue.Queue()
        self.current_engine: GAEngine = None
        self.worker_thread: threading.Thread = None
        self.logger = ExperimentLogger()

        self._build_layout()
        self._check_queue()

        # Previsualizar función inicial
        self.root.after(200, self._initial_preview)

    def _build_layout(self):
        # 1. Barra de Herramientas Superior
        toolbar = ttk.Frame(self.root, style="Card.TFrame", padding=(14, 10))
        toolbar.pack(fill="x", side="top", padx=10, pady=(10, 5))

        title_lbl = ttk.Label(toolbar, text="🧬 ALGORITMO GENÉTICO", style="Title.TLabel")
        title_lbl.pack(side="left", padx=(0, 20))

        # Botones Principales
        self.btn_run = ttk.Button(toolbar, text="▶ Iniciar Optimización", style="Action.TButton", command=self.start_optimization)
        self.btn_run.pack(side="left", padx=(0, 8))

        self.btn_stop = ttk.Button(toolbar, text="⏹ Detener", style="Stop.TButton", command=self.stop_optimization, state="disabled")
        self.btn_stop.pack(side="left", padx=(0, 15))

        self.btn_history = ttk.Button(toolbar, text="📋 Historial y Registros", style="Secondary.TButton", command=self.open_history)
        self.btn_history.pack(side="left", padx=(0, 8))

        # Indicador derecho
        self.lbl_mode_info = ttk.Label(
            toolbar, text="Optimización Univariada f(x) | Todos los métodos 05_hiperparametros",
            style="Subtext.TLabel", font=FONTS["body"]
        )
        self.lbl_mode_info.pack(side="right")

        # 2. Contenedor Principal (Panel Izquierdo: Configuración, Panel Derecho: Visualización)
        content_pane = ttk.Frame(self.root, style="TFrame")
        content_pane.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        # --- PANEL IZQUIERDO: Configuración con Scrollbar ---
        left_container = ttk.Frame(content_pane, style="Card.TFrame", width=420)
        left_container.pack(side="left", fill="both", padx=(0, 5))
        left_container.pack_propagate(False)

        canvas_left = tk.Canvas(left_container, bg=COLORS["bg_card"], highlightthickness=0)
        scrollbar_left = ttk.Scrollbar(left_container, orient="vertical", command=canvas_left.yview)
        self.scrollable_left = ttk.Frame(canvas_left, style="Card.TFrame")

        self.scrollable_left.bind(
            "<Configure>",
            lambda e: canvas_left.configure(scrollregion=canvas_left.bbox("all"))
        )

        canvas_left.create_window((0, 0), window=self.scrollable_left, anchor="nw", width=400)
        canvas_left.configure(yscrollcommand=scrollbar_left.set)

        canvas_left.pack(side="left", fill="both", expand=True)
        scrollbar_left.pack(side="right", fill="y")

        # Soporte para rueda del ratón en panel izquierdo
        def _on_left_mousewheel(event):
            canvas_left.yview_scroll(int(-1 * (event.delta / 120)), "units")
        left_container.bind("<Enter>", lambda e: canvas_left.bind_all("<MouseWheel>", _on_left_mousewheel))
        left_container.bind("<Leave>", lambda e: canvas_left.unbind_all("<MouseWheel>"))

        # Insertar paneles de configuración
        self.function_panel = FunctionPanel(self.scrollable_left, on_preview_callback=self._on_preview_function)
        self.function_panel.pack(fill="x", padx=8, pady=(8, 6))

        self.hyperparams_panel = HyperparametersPanel(self.scrollable_left)
        self.hyperparams_panel.pack(fill="x", padx=8, pady=(4, 8))

        # --- PANEL DERECHO: Gráficas y Métricas con Scrollbar ---
        right_container = ttk.Frame(content_pane, style="TFrame")
        right_container.pack(side="right", fill="both", expand=True, padx=(5, 0))

        canvas_right = tk.Canvas(right_container, bg=COLORS["bg_dark"], highlightthickness=0)
        scrollbar_right = ttk.Scrollbar(right_container, orient="vertical", command=canvas_right.yview)
        self.scrollable_right = ttk.Frame(canvas_right, style="TFrame")

        window_id_right = canvas_right.create_window((0, 0), window=self.scrollable_right, anchor="nw")

        def _on_right_frame_configure(event):
            canvas_right.configure(scrollregion=canvas_right.bbox("all"))

        def _on_right_canvas_configure(event):
            # Adaptar el ancho del contenido interno al ancho disponible de la ventana
            canvas_right.itemconfig(window_id_right, width=event.width)

        self.scrollable_right.bind("<Configure>", _on_right_frame_configure)
        canvas_right.bind("<Configure>", _on_right_canvas_configure)
        canvas_right.configure(yscrollcommand=scrollbar_right.set)

        canvas_right.pack(side="left", fill="both", expand=True)
        scrollbar_right.pack(side="right", fill="y")

        # Soporte para rueda del ratón en panel derecho
        def _on_right_mousewheel(event):
            canvas_right.yview_scroll(int(-1 * (event.delta / 120)), "units")
        right_container.bind("<Enter>", lambda e: canvas_right.bind_all("<MouseWheel>", _on_right_mousewheel))
        right_container.bind("<Leave>", lambda e: canvas_right.unbind_all("<MouseWheel>"))

        self.plot_panel = PlotPanel(self.scrollable_right)
        self.plot_panel.pack(fill="x", expand=True, pady=(0, 6))

        self.metrics_panel = MetricsPanel(self.scrollable_right)
        self.metrics_panel.pack(fill="x", pady=(0, 10))

    def _initial_preview(self):
        try:
            f_data = self.function_panel.get_data()
            a, b = f_data["bounds"][0]
            dims = f_data.get("dimensions", 1)
            self.plot_panel.plot_preview(f_data["expression"], a, b, dims)
        except Exception:
            pass

    def _on_preview_function(self, expr: str, a: float, b: float, dims: int = 1):
        self.plot_panel.plot_preview(expr, a, b, dims)

    def start_optimization(self):
        """Inicia el algoritmo genético en un hilo separado."""
        try:
            f_data = self.function_panel.get_data()
            h_data = self.hyperparams_panel.get_data()
        except Exception as e:
            messagebox.showerror("Error de Configuración", str(e))
            return

        # Combinar configuración
        config = {**f_data, **h_data}

        # Actualizar UI a estado de ejecución
        self.btn_run.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.btn_history.config(state="disabled")
        self.metrics_panel.reset()
        self.metrics_panel.update_metrics(
            status="Ejecutando generación inicial...",
            max_gen=config["max_generations"]
        )

        self.current_config = config
        self.current_engine = GAEngine(config)

        # Iniciar hilo de trabajo
        self.worker_thread = threading.Thread(
            target=self._run_worker,
            args=(self.current_engine, config),
            daemon=True
        )
        self.worker_thread.start()

    def _run_worker(self, engine: GAEngine, config: Dict[str, Any]):
        start_t = time.time()
        last_update_t = 0.0

        def step_callback(gen: int, stats: Dict[str, Any], best_ind, population):
            nonlocal last_update_t
            curr_t = time.time()
            # Enviar actualización a la UI (en cada paso o cada 40ms para mantener suavidad)
            if (curr_t - last_update_t > 0.035) or gen == 0 or gen == engine.max_generations:
                last_update_t = curr_t
                pop_copy = [ind.copy() for ind in population]
                best_copy = best_ind.copy() if best_ind else None
                history_copy = list(engine.history)
                elapsed = curr_t - start_t
                self.update_queue.put({
                    "type": "step",
                    "gen": gen,
                    "stats": stats,
                    "best_ind": best_copy,
                    "population": pop_copy,
                    "history": history_copy,
                    "elapsed": elapsed
                })
            # Pequeña pausa opcional para permitir visualización progresiva fluida
            time.sleep(0.015)

        results = engine.run(callback=step_callback)
        self.update_queue.put({
            "type": "finish",
            "results": results,
            "config": config
        })

    def _check_queue(self):
        """Consume los mensajes enviados por el hilo de ejecución para actualizar Tkinter."""
        try:
            while not self.update_queue.empty():
                msg = self.update_queue.get_nowait()
                msg_type = msg.get("type")

                if msg_type == "step":
                    gen = msg["gen"]
                    stats = msg["stats"]
                    best_ind = msg["best_ind"]
                    pop = msg["population"]
                    history = msg["history"]
                    elapsed = msg["elapsed"]
                    max_gen = self.current_config["max_generations"]
                    goal = self.current_config["goal"]
                    bounds = self.current_config["bounds"]
                    dims = self.current_config.get("dimensions", 1)

                    # Actualizar métricas
                    status_text = f"Ejecutando... Gen {gen}/{max_gen} ({dims}D)"
                    self.metrics_panel.update_metrics(
                        status=status_text,
                        best_x=stats.get("best_x_formatted", stats.get("best_x")),
                        best_fx=stats["best_fx"],
                        best_fitness=stats["best_fitness"],
                        current_gen=gen,
                        max_gen=max_gen,
                        evaluations=stats["evaluations"],
                        elapsed_time=elapsed
                    )

                    # Actualizar gráficas
                    self.plot_panel.update_plots(
                        expr=self.current_config["expression"],
                        bounds=bounds,
                        population=pop,
                        best_ind=best_ind,
                        history=history,
                        goal=goal,
                        dims=dims
                    )

                elif msg_type == "finish":
                    results = msg["results"]
                    config = msg["config"]

                    # Guardar registro de la corrida automáticamente
                    run_id = self.logger.save_run(config, results)

                    status_msg = "Completado con éxito" if not results.get("stopped_early") else "Interrumpido por el usuario"
                    self.metrics_panel.update_metrics(
                        status=status_msg,
                        best_x=results.get("best_x_formatted", results["best_x"]),
                        best_fx=results["best_fx"],
                        best_fitness=results["best_fitness"],
                        current_gen=results["best_generation"],
                        max_gen=config["max_generations"],
                        evaluations=results["total_evaluations"],
                        elapsed_time=results["execution_time"]
                    )

                    # Restaurar botones
                    self.btn_run.config(state="normal")
                    self.btn_stop.config(state="disabled")
                    self.btn_history.config(state="normal")

        except Exception:
            pass

        finally:
            self.root.after(40, self._check_queue)

    def stop_optimization(self):
        """Detiene de inmediato la ejecución en curso."""
        if self.current_engine:
            self.current_engine.stop()
            self.metrics_panel.status_var.set("Deteniendo ejecución...")
            self.btn_stop.config(state="disabled")

    def open_history(self):
        """Abre el diálogo modal de historial de experimentos."""
        HistoryDialog(self.root, self.logger, on_load_config_callback=self._load_config_from_history)

    def _load_config_from_history(self, config: Dict[str, Any]):
        """Transfiere los parámetros de un experimento anterior a los paneles."""
        self.function_panel.set_data(config)
        self.hyperparams_panel.set_data(config)
        bounds = config.get("bounds", [(-10.0, 10.0)])
        dims = config.get("dimensions", 1)
        self.plot_panel.plot_preview(config.get("expression", "x**2"), bounds[0][0], bounds[0][1], dims)
