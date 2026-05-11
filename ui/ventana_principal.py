"""
ventana_principal.py — Fase 4 (versión final)
Integra todas las pestañas: Clientes, Servicios, Reservas, Simulación y Logs.
"""

# --- Dependencias UI ---
import tkinter as tk
from tkinter import ttk

# --- Dependencias internas ---
from ui.tab_clientes   import TabClientes
from ui.tab_servicios  import TabServicios
from ui.tab_reservas   import TabReservas
from ui.tab_simulacion import TabSimulacion
from ui.tab_logs       import TabLogs

from utils.gestor  import Gestor
from utils.logger  import Logger

from servicios.reserva_sala    import ReservaSala
from servicios.alquiler_equipo import AlquilerEquipo
from servicios.asesoria        import AsesoriaEspecializada


class VentanaPrincipal:
    """
    Ventana raíz de la aplicación Software FJ — versión completa.
    Gestiona 5 pestañas y la precarga de servicios de demo.
    """

    def __init__(self):
        # --- Servicios globales ---
        self._gestor = Gestor()
        self._log    = Logger()

        # --- Ventana raiz ---
        self._root = tk.Tk()
        self._root.title("Software FJ — Sistema Integral de Gestión")
        self._root.minsize(950, 580)
        self._root.state("zoomed") 
        self._root.configure(bg="#f5f5f5")

        # --- Precarga y construccion UI ---
        self._precargar_servicios()
        self._construir_ui()
        self._log.info("Aplicación Software FJ iniciada — Fase 4 completa.")

    def _precargar_servicios(self):
        """
        Registra 6 servicios de demo al arrancar.
        Los IDs fijos permiten que la simulación los referencie directamente.
        """
        # --- Servicios de demo ---
        demos = [
            ReservaSala(
                "SALA-01", "Sala Amazonas",  80_000, capacidad_max=12),
            ReservaSala(
                "SALA-02", "Sala Pacífico", 120_000, capacidad_max=30),
            AlquilerEquipo(
                "EQ-01", "Laptop HP ProBook",  35_000, stock_disponible=8),
            AlquilerEquipo(
                "EQ-02", "Proyector Epson 4K", 50_000, stock_disponible=3),
            AsesoriaEspecializada(
                "AS-01", "Asesoría Legal Corporativa",
                90_000, especialidad="Legal",      nivel="senior"),
            AsesoriaEspecializada(
                "AS-02", "Consultoría Técnica IT",
                75_000, especialidad="Tecnología", nivel="experto"),
        ]
        # --- Registro con tolerancia a fallos ---
        for s in demos:
            try:
                self._gestor.agregar_servicio(s)
            except Exception as e:
                self._log.error(
                    f"Error al precargar servicio '{s.nombre}'.", str(e))

    def _construir_ui(self):
        """Construye el encabezado, el notebook y la barra de estado inferior."""

        # --- Encabezado ---
        frame_header = tk.Frame(self._root, bg="#2c3e50")
        frame_header.pack(fill=tk.X)
        tk.Label(
            frame_header,
            text="Software FJ — Sistema Integral de Gestión",
            bg="#2c3e50", fg="white",
            font=("Helvetica", 13, "bold"), pady=12
        ).pack(side=tk.LEFT, padx=20)

        # --- Indicador de estado global ---
        # Indicador de estado global (esquina superior derecha)
        self._lbl_estado_global = tk.Label(
            frame_header, text="● Sistema activo",
            bg="#2c3e50", fg="#2ecc71",
            font=("Helvetica", 9)
        )
        self._lbl_estado_global.pack(side=tk.RIGHT, padx=20)

        # --- Notebook principal ---
        self._notebook = ttk.Notebook(self._root)
        self._notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- Instanciar pestanas ---
        self._tab_clientes   = TabClientes(
            self._notebook, self._gestor, self._log)
        self._tab_servicios  = TabServicios(
            self._notebook, self._gestor, self._log)
        self._tab_reservas   = TabReservas(
            self._notebook, self._gestor, self._log)
        self._tab_simulacion = TabSimulacion(
            self._notebook, self._gestor, self._log)
        self._tab_logs       = TabLogs(
            self._notebook, self._log)

        # --- Agregar pestanas al notebook ---
        self._notebook.add(self._tab_clientes.frame,   text="  Clientes  ")
        self._notebook.add(self._tab_servicios.frame,  text="  Servicios  ")
        self._notebook.add(self._tab_reservas.frame,   text="  Reservas  ")
        self._notebook.add(self._tab_simulacion.frame, text="  Simulación  ")
        self._notebook.add(self._tab_logs.frame,       text="  Logs  ")

        # --- Cargar catalogo de servicios ---
        self._tab_servicios.refrescar_catalogo()

        # --- Barra inferior de estado ---
        barra_inferior = tk.Frame(self._root, bg="#ecf0f1", height=28)
        barra_inferior.pack(fill=tk.X, side=tk.BOTTOM)
        self._lbl_barra = tk.Label(
            barra_inferior,
            text="Listo",
            bg="#ecf0f1", fg="#7f8c8d",
            font=("Helvetica", 8), anchor="w"
        )
        self._lbl_barra.pack(side=tk.LEFT, padx=10)

        # --- Evento al cambiar de pestana ---
        self._notebook.bind("<<NotebookTabChanged>>", self._al_cambiar_tab)

    def _al_cambiar_tab(self, evento):
        """Refresca el contenido de la pestaña que se acaba de seleccionar."""
        # --- Acciones por pestana ---
        idx = self._notebook.index(self._notebook.select())
        acciones = {
            0: lambda: None,
            1: self._tab_servicios.refrescar_catalogo,
            2: self._tab_reservas.refrescar_tabla,
            3: lambda: None,
            4: self._tab_logs.refrescar,
        }
        accion = acciones.get(idx)
        if accion:
            accion()

        # --- Actualizar barra inferior ---
        r = self._gestor.resumen()
        self._lbl_barra.config(
            text=(
                f"Clientes: {r['clientes']}  |  "
                f"Servicios: {r['servicios']}  |  "
                f"Reservas: {r['reservas']}"
            )
        )

    def ejecutar(self):
        """Inicia el loop principal de Tkinter."""
        # --- Loop principal ---
        self._root.mainloop()