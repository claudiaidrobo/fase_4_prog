"""
ventana_principal.py  — Fase 2
Añade la pestaña de Servicios y carga servicios de demostración al inicio.
"""

# --- Dependencias UI ---
import tkinter as tk
from tkinter import ttk
# --- Dependencias internas ---
from ui.tab_clientes import TabClientes
from ui.tab_servicios import TabServicios
from ui.tab_logs import TabLogs
from utils.gestor import Gestor
from utils.logger import Logger
from servicios.reserva_sala import ReservaSala
from servicios.alquiler_equipo import AlquilerEquipo
from servicios.asesoria import AsesoriaEspecializada


class VentanaPrincipal:

    def __init__(self):
        # --- Servicios globales ---
        self._gestor = Gestor()
        self._log = Logger()

        # --- Ventana raiz ---
        self._root = tk.Tk()
        self._root.title("Software FJ — Sistema de Gestión")
        self._root.geometry("1050x680")
        self._root.minsize(900, 560)
        self._root.configure(bg="#f5f5f5")

        # --- Precarga y construccion UI ---
        self._precargar_servicios()
        self._construir_ui()
        self._log.info("Interfaz gráfica Fase 2 iniciada.")

    def _precargar_servicios(self):
        """
        Registra servicios de demostración en el gestor al arrancar.
        Usa try/except para que un servicio mal configurado no rompa el inicio.
        """
        # --- Servicios de demostracion ---
        demos = [
            ReservaSala("SALA-01", "Sala Amazonas", 80_000, capacidad_max=12),
            ReservaSala("SALA-02", "Sala Pacífico", 120_000, capacidad_max=30),
            AlquilerEquipo("EQ-01", "Laptop HP ProBook", 35_000, stock_disponible=8),
            AlquilerEquipo("EQ-02", "Proyector Epson 4K", 50_000, stock_disponible=3),
            AsesoriaEspecializada(
                "AS-01", "Asesoría Legal Corporativa",
                90_000, especialidad="Legal", nivel="senior"
            ),
            AsesoriaEspecializada(
                "AS-02", "Consultoría Técnica IT",
                75_000, especialidad="Tecnología", nivel="experto"
            ),
        ]
        # --- Registro con tolerancia a fallos ---
        for servicio in demos:
            try:
                self._gestor.agregar_servicio(servicio)
            except Exception as e:
                self._log.error(f"Error al precargar servicio '{servicio.nombre}'.", str(e))

    def _construir_ui(self):
        # --- Encabezado ---
        frame_header = tk.Frame(self._root, bg="#2c3e50", height=50)
        frame_header.pack(fill=tk.X)
        tk.Label(
            frame_header,
            text="Software FJ — Gestión de Clientes, Servicios y Reservas",
            bg="#2c3e50", fg="white",
            font=("Helvetica", 13, "bold"), pady=12
        ).pack()

        # --- Notebook con pestanas ---
        self._notebook = ttk.Notebook(self._root)
        self._notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- Pestañas principales ---
        self._tab_clientes = TabClientes(self._notebook, self._gestor, self._log)
        self._notebook.add(self._tab_clientes.frame, text="  Clientes  ")

        self._tab_servicios = TabServicios(self._notebook, self._gestor, self._log)
        self._notebook.add(self._tab_servicios.frame, text="  Servicios  ")

        self._tab_logs = TabLogs(self._notebook, self._log)
        self._notebook.add(self._tab_logs.frame, text="  Logs  ")

        # --- Eventos UI ---
        self._notebook.bind("<<NotebookTabChanged>>", self._al_cambiar_tab)

        # --- Cargar catalogo al iniciar ---
        self._tab_servicios.refrescar_catalogo()

    def _al_cambiar_tab(self, evento):
        # --- Sincronizar vistas por pestaña ---
        idx = self._notebook.index(self._notebook.select())
        if idx == 1:
            self._tab_servicios.refrescar_catalogo()
        elif idx == 2:
            self._tab_logs.refrescar()

    def ejecutar(self):
        # --- Loop principal ---
        self._root.mainloop()