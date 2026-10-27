"""
Diálogo modal para visualizar el historial de ejecuciones,
cargar configuraciones previas y exportar reportes en TXT y CSV.
"""
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Callable, Dict, Any

from almacenamiento.experiment_logger import ExperimentLogger
from ui.styles import COLORS, FONTS

class HistoryDialog(tk.Toplevel):
    def __init__(self, parent, logger: ExperimentLogger, on_load_config_callback: Callable[[Dict[str, Any]], None]):
        super().__init__(parent)
        self.title("Historial de Experimentos y Registros")
        self.geometry("820x540")
        self.configure(bg=COLORS["bg_dark"])
        self.transient(parent)
        self.grab_set()

        self.logger = logger
        self.on_load_config = on_load_config_callback

        self._build_ui()
        self._load_list()

    def _build_ui(self):
        # Título
        header = ttk.Frame(self, style="Card.TFrame", padding=10)
        header.pack(fill="x")
        ttk.Label(header, text="📋 Registro de Experimentos Ejecutados", style="Title.TLabel").pack(side="left")

        # Contenedor principal con dos mitades (Lista a la izquierda, Detalle a la derecha)
        main_split = ttk.Frame(self, style="TFrame", padding=10)
        main_split.pack(fill="both", expand=True)

        # Panel Izquierdo: Lista de ejecuciones
        left_frame = ttk.LabelFrame(main_split, text=" Ejecuciones Guardadas ", style="TLabelframe", padding=6)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 6))

        columns = ("Fecha", "Función", "Mejor f(x)")
        self.tree = ttk.Treeview(left_frame, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("Fecha", text="Fecha / Hora")
        self.tree.heading("Función", text="Función")
        self.tree.heading("Mejor f(x)", text="Mejor f(x)")

        self.tree.column("Fecha", width=140, anchor="center")
        self.tree.column("Función", width=160, anchor="w")
        self.tree.column("Mejor f(x)", width=100, anchor="center")

        tree_scroll = ttk.Scrollbar(left_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)

        self.tree.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self._on_select_item)

        # Panel Derecho: Visualizador del reporte TXT
        right_frame = ttk.LabelFrame(main_split, text=" Resumen del Experimento ", style="TLabelframe", padding=6)
        right_frame.pack(side="right", fill="both", expand=True, padx=(6, 0))

        self.txt_summary = tk.Text(
            right_frame, wrap="word", bg=COLORS["bg_card_secondary"], fg=COLORS["fg_text"],
            font=FONTS["mono"], insertbackground=COLORS["primary"], relief="flat"
        )
        txt_scroll = ttk.Scrollbar(right_frame, orient="vertical", command=self.txt_summary.yview)
        self.txt_summary.configure(yscrollcommand=txt_scroll.set)

        self.txt_summary.pack(side="left", fill="both", expand=True)
        txt_scroll.pack(side="right", fill="y")

        # Barra de botones inferior
        bottom_bar = ttk.Frame(self, style="Card.TFrame", padding=10)
        bottom_bar.pack(fill="x")

        self.btn_load = ttk.Button(bottom_bar, text="📥 Cargar Parámetros en UI", style="Action.TButton", command=self._load_selected)
        self.btn_load.pack(side="left", padx=5)

        self.btn_export_csv = ttk.Button(bottom_bar, text="📊 Exportar a CSV", style="Secondary.TButton", command=self._export_csv)
        self.btn_export_csv.pack(side="left", padx=5)

        self.btn_open_txt = ttk.Button(bottom_bar, text="📄 Abrir TXT en Explorador", style="Secondary.TButton", command=self._open_txt)
        self.btn_open_txt.pack(side="left", padx=5)

        ttk.Button(bottom_bar, text="Cerrar", style="Secondary.TButton", command=self.destroy).pack(side="right", padx=5)

    def _load_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        experiments = self.logger.list_experiments()
        self.exp_map = {}
        for exp in experiments:
            run_id = exp["run_id"]
            best_fx = exp["best_fx"]
            fx_str = f"{best_fx:.6f}" if best_fx is not None else "--"
            item_id = self.tree.insert("", "end", values=(exp["date_readable"], exp["function"], fx_str))
            self.exp_map[item_id] = exp

        if self.exp_map:
            first_item = list(self.exp_map.keys())[0]
            self.tree.selection_set(first_item)
            self._display_experiment(self.exp_map[first_item]["run_id"])

    def _on_select_item(self, event=None):
        selected = self.tree.selection()
        if selected:
            item_id = selected[0]
            exp = self.exp_map.get(item_id)
            if exp:
                self._display_experiment(exp["run_id"])

    def _display_experiment(self, run_id: str):
        self.current_run_id = run_id
        txt_path = os.path.join(self.logger.records_dir, f"{run_id}.txt")
        self.txt_summary.delete("1.0", "end")
        if os.path.exists(txt_path):
            with open(txt_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.txt_summary.insert("1.0", content)
        else:
            self.txt_summary.insert("1.0", "No se encontró el archivo de reporte .txt.")

    def _load_selected(self):
        if not hasattr(self, "current_run_id") or not self.current_run_id:
            messagebox.showinfo("Aviso", "Seleccione una ejecución del listado.")
            return
        data = self.logger.load_experiment(self.current_run_id)
        config = data.get("configuration", {})
        if self.on_load_config:
            self.on_load_config(config)
            messagebox.showinfo("Configuración Cargada", "La configuración del experimento ha sido transferida a la interfaz principal.")
            self.destroy()

    def _export_csv(self):
        if not hasattr(self, "current_run_id") or not self.current_run_id:
            return
        dest = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Archivos CSV", "*.csv")],
            initialfile=f"{self.current_run_id}_evolucion.csv"
        )
        if dest:
            ok = self.logger.export_history_to_csv(self.current_run_id, dest)
            if ok:
                messagebox.showinfo("Exportación Exitosa", f"Datos generacionales exportados a:\n{dest}")
            else:
                messagebox.showerror("Error", "No se pudo exportar el historial a CSV.")

    def _open_txt(self):
        if not hasattr(self, "current_run_id") or not self.current_run_id:
            return
        txt_path = os.path.join(self.logger.records_dir, f"{self.current_run_id}.txt")
        if os.path.exists(txt_path):
            os.startfile(txt_path)
