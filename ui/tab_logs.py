"""
tab_logs.py
Pestaña de visualización de logs en tiempo real dentro de la UI Tkinter.
"""

# --- Dependencias UI ---
import tkinter as tk
from tkinter import ttk
# --- Dependencias internas ---
from utils.logger import Logger, NivelLog


class TabLogs:
    """
    Pestaña 'Logs' que muestra los eventos registrados por el sistema.
    Permite filtrar por nivel de severidad.
    """

    # Colores por nivel de log para feedback visual
    _COLORES = {
        "INFO": "#27ae60",
        "ADVERTENCIA": "#e67e22",
        "ERROR": "#e74c3c",
        "CRITICO": "#8e44ad",
    }

    def __init__(self, parent, log: Logger):
        # --- Servicio de logs compartido ---
        self._log = log
        self.frame = tk.Frame(parent, bg="#f5f5f5")
        self._construir_ui()

    def _construir_ui(self):
        """Construye el panel de logs con filtros y tabla de eventos."""
        # --- Barra de controles ---
        barra = tk.Frame(self.frame, bg="#f5f5f5")
        barra.pack(fill=tk.X, padx=10, pady=(10, 4))

        tk.Label(barra, text="Filtrar por nivel:",
                 bg="#f5f5f5", font=("Helvetica", 9)).pack(side=tk.LEFT)

        # --- Filtro de severidad ---
        self._filtro = tk.StringVar(value="TODOS")
        opciones = ["TODOS", "INFO", "ADVERTENCIA", "ERROR", "CRITICO"]
        combo = ttk.Combobox(barra, textvariable=self._filtro,
                             values=opciones, state="readonly", width=14)
        combo.pack(side=tk.LEFT, padx=(6, 20))
        combo.bind("<<ComboboxSelected>>", lambda e: self.refrescar())

        tk.Button(
            barra, text="Refrescar", command=self.refrescar,
            bg="#2980b9", fg="white", font=("Helvetica", 9),
            relief=tk.FLAT, cursor="hand2", padx=8, pady=3
        ).pack(side=tk.LEFT)

        tk.Button(
            barra, text="Limpiar buffer", command=self._limpiar,
            bg="#95a5a6", fg="white", font=("Helvetica", 9),
            relief=tk.FLAT, cursor="hand2", padx=8, pady=3
        ).pack(side=tk.LEFT, padx=(6, 0))

        # --- Tabla de logs ---
        columnas = ("Timestamp", "Nivel", "Mensaje", "Detalle")
        self._tabla = ttk.Treeview(self.frame, columns=columnas,
                                   show="headings", height=22)

        anchos = [150, 100, 300, 300]
        for col, ancho in zip(columnas, anchos):
            self._tabla.heading(col, text=col)
            self._tabla.column(col, width=ancho)

        # --- Estilos por severidad ---
        # Configurar colores por tag de nivel
        for nivel, color in self._COLORES.items():
            self._tabla.tag_configure(nivel, foreground=color)

        scroll_v = ttk.Scrollbar(self.frame, orient=tk.VERTICAL,
                                 command=self._tabla.yview)
        scroll_h = ttk.Scrollbar(self.frame, orient=tk.HORIZONTAL,
                                 command=self._tabla.xview)
        self._tabla.configure(yscrollcommand=scroll_v.set,
                              xscrollcommand=scroll_h.set)

        self._tabla.pack(fill=tk.BOTH, expand=True, padx=10)
        scroll_v.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_h.pack(side=tk.BOTTOM, fill=tk.X, padx=10)

    def refrescar(self):
        """Recarga los registros del logger aplicando el filtro activo."""
        # --- Limpieza de la tabla ---
        for fila in self._tabla.get_children():
            self._tabla.delete(fila)

        filtro = self._filtro.get()
        nivel = None if filtro == "TODOS" else NivelLog(filtro)
        registros = self._log.obtener_registros(nivel)

        # --- Mostrar mas recientes primero ---
        for reg in reversed(registros):
            self._tabla.insert(
                "", tk.END,
                values=(reg["timestamp"], reg["nivel"],
                        reg["mensaje"], reg["detalle"]),
                tags=(reg["nivel"],)
            )

    def _limpiar(self):
        """Limpia el buffer de logs en memoria."""
        # --- Limpieza y refresco ---
        self._log.limpiar_buffer()
        self.refrescar()