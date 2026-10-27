"""
Punto de entrada principal de la aplicación Algoritmo Genético Univariado.
Permite optimizar cualquier función univariada f(x) con todos los métodos de '05_hiperparametros'.
"""
import sys
import os
import tkinter as tk

# Asegurar que el directorio del proyecto esté en sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ui.main_window import MainWindow

def main():
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()
