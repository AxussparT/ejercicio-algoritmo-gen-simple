"""
Definición de estilos visuales modernos y limpios para la interfaz gráfica.
Paleta inspirada en temas modernos tipo Slate / Dark Clean.
"""
import tkinter as tk
from tkinter import ttk

COLORS = {
    "bg_dark": "#181825",
    "bg_card": "#1e1e2e",
    "bg_card_secondary": "#252538",
    "border": "#313244",
    "fg_text": "#cdd6f4",
    "fg_subtext": "#a6adc8",
    "primary": "#89b4fa",       # Azul suave
    "primary_hover": "#b4befe",
    "success": "#a6e3a1",       # Verde suave (Iniciar)
    "success_hover": "#94e2d5",
    "danger": "#f38ba8",        # Rojo suave (Detener)
    "danger_hover": "#eba0ac",
    "warning": "#f9e2af",       # Amarillo suave
    "accent": "#cba6f7",        # Púrpura suave
    "entry_bg": "#313244",
    "entry_fg": "#ffffff"
}

FONTS = {
    "title": ("Segoe UI", 13, "bold"),
    "subtitle": ("Segoe UI", 10, "bold"),
    "body": ("Segoe UI", 9),
    "mono": ("Consolas", 9),
    "metric_val": ("Segoe UI", 12, "bold"),
    "metric_lbl": ("Segoe UI", 8)
}

def apply_theme(root: tk.Tk):
    """Configura los estilos de ttk para armonizar con el tema moderno."""
    style = ttk.Style(root)
    style.theme_use("clam")

    # Configuración de frames y labels
    style.configure("TFrame", background=COLORS["bg_dark"])
    style.configure("Card.TFrame", background=COLORS["bg_card"], relief="flat")
    style.configure("SecondaryCard.TFrame", background=COLORS["bg_card_secondary"], relief="flat")

    style.configure("TLabel", background=COLORS["bg_dark"], foreground=COLORS["fg_text"], font=FONTS["body"])
    style.configure("Card.TLabel", background=COLORS["bg_card"], foreground=COLORS["fg_text"], font=FONTS["body"])
    style.configure("Subtext.TLabel", background=COLORS["bg_card"], foreground=COLORS["fg_subtext"], font=FONTS["body"])
    style.configure("Title.TLabel", background=COLORS["bg_card"], foreground=COLORS["primary"], font=FONTS["title"])
    style.configure("Subtitle.TLabel", background=COLORS["bg_card"], foreground=COLORS["accent"], font=FONTS["subtitle"])

    # Botones
    style.configure(
        "Action.TButton",
        background=COLORS["success"],
        foreground="#11111b",
        font=FONTS["subtitle"],
        padding=6,
        borderwidth=0
    )
    style.map("Action.TButton", background=[("active", COLORS["success_hover"])])

    style.configure(
        "Stop.TButton",
        background=COLORS["danger"],
        foreground="#11111b",
        font=FONTS["subtitle"],
        padding=6,
        borderwidth=0
    )
    style.map("Stop.TButton", background=[("active", COLORS["danger_hover"])])

    style.configure(
        "Secondary.TButton",
        background=COLORS["bg_card_secondary"],
        foreground=COLORS["fg_text"],
        font=FONTS["body"],
        padding=5,
        borderwidth=1,
        relief="flat"
    )
    style.map("Secondary.TButton", background=[("active", COLORS["border"])])

    # Combobox y Entry
    style.configure(
        "TCombobox",
        fieldbackground=COLORS["entry_bg"],
        background=COLORS["bg_card_secondary"],
        foreground=COLORS["entry_fg"],
        font=FONTS["body"],
        arrowcolor=COLORS["primary"]
    )
    style.map("TCombobox", fieldbackground=[("readonly", COLORS["entry_bg"])])

    style.configure(
        "TEntry",
        fieldbackground=COLORS["entry_bg"],
        foreground=COLORS["entry_fg"],
        insertcolor=COLORS["fg_text"],
        font=FONTS["body"]
    )

    style.configure(
        "TLabelframe",
        background=COLORS["bg_card"],
        foreground=COLORS["primary"],
        bordercolor=COLORS["border"]
    )
    style.configure(
        "TLabelframe.Label",
        background=COLORS["bg_card"],
        foreground=COLORS["primary"],
        font=FONTS["subtitle"]
    )
