"""
ventana_principal.py
Ventana principal de la aplicación Tkinter.
En la Fase 1 solo contiene la pestaña de Clientes y la de Logs.
"""

# --- Dependencias UI ---
import tkinter as tk
from tkinter import ttk, messagebox
# --- Dependencias internas ---
from ui.tab_clientes import TabClientes
from ui.tab_logs import TabLogs
from utils.gestor import Gestor
from utils.logger import Logger


class VentanaPrincipal:
    """
    Ventana raíz de la aplicación Software FJ.
    Organiza el contenido en pestañas (Notebook de ttk).
    """

    def __init__(self):
        # --- Servicios globales ---
        self._gestor = Gestor()
        self._log = Logger()

        # --- Ventana raiz ---
        self._root = tk.Tk()
        self._root.title("Software Alejandra Idrobo — Sistema de Gestión")
        self._root.geometry("900x620")
        self._root.minsize(800, 500)
        self._root.configure(bg="#f5f5f5")

        self._construir_ui()
        self._log.info("Interfaz gráfica iniciada.")

    def _construir_ui(self):
        """Construye el layout principal: encabezado + notebook de pestañas."""
        # --- Encabezado ---
        frame_header = tk.Frame(self._root, bg="#2c3e50", height=50)
        frame_header.pack(fill=tk.X)
        tk.Label(
            frame_header,
            text="Software Alejandra Idrobo — Gestión de Clientes, Servicios y Reservas",
            bg="#2c3e50", fg="white",
            font=("Helvetica", 13, "bold"),
            pady=12
        ).pack()

        # --- Notebook con pestanas ---
        self._notebook = ttk.Notebook(self._root)
        self._notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- Fase 1: Clientes y Logs ---
        self._tab_clientes = TabClientes(self._notebook, self._gestor, self._log)
        self._notebook.add(self._tab_clientes.frame, text="  Clientes  ")

        self._tab_logs = TabLogs(self._notebook, self._log)
        self._notebook.add(self._tab_logs.frame, text="  Logs  ")

        # --- Eventos UI ---
        # Al cambiar de pestana actualizamos los logs
        self._notebook.bind("<<NotebookTabChanged>>", self._al_cambiar_tab)

    def _al_cambiar_tab(self, evento):
        """Refresca la pestaña de logs cada vez que se selecciona."""
        # --- Sincronizar vista de logs ---
        tab_actual = self._notebook.index(self._notebook.select())
        if tab_actual == 1:  # índice de la pestaña Logs
            self._tab_logs.refrescar()

    def ejecutar(self):
        """Inicia el loop principal de Tkinter."""
        # --- Loop principal ---
        self._root.mainloop()