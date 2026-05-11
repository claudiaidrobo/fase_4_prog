"""
tab_servicios.py
Pestaña de catálogo y calculadora de costos de servicios.
"""

# --- Dependencias UI ---
import tkinter as tk
from tkinter import ttk, messagebox
# --- Dependencias internas ---
from servicios.reserva_sala import ReservaSala
from servicios.alquiler_equipo import AlquilerEquipo
from servicios.asesoria import AsesoriaEspecializada
from core.excepciones import ServicioInvalidoError
from utils.gestor import Gestor
from utils.logger import Logger


class TabServicios:
    """
    Pestaña 'Servicios' del notebook.
    Muestra el catálogo de servicios y permite calcular costos
    con parámetros configurables (horas, impuesto, descuento, opcionales).
    """

    def __init__(self, parent, gestor: Gestor, log: Logger):
        # --- Servicios compartidos ---
        self._gestor = gestor
        self._log = log
        # --- Contenedor y estado ---
        self.frame = tk.Frame(parent, bg="#f5f5f5")
        self._servicio_seleccionado = None
        self._construir_ui()

    def _construir_ui(self):
        """Divide la pestaña en tabla de catálogo (arriba) y calculadora (abajo)."""

        # --- Panel superior: catálogo ---
        panel_catalogo = tk.LabelFrame(
            self.frame, text="Catálogo de servicios",
            bg="#f5f5f5", font=("Helvetica", 10, "bold"),
            padx=8, pady=8
        )
        panel_catalogo.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 4))

        # --- Definicion de columnas ---
        columnas = ("ID", "Tipo", "Nombre", "Precio base", "Disponible", "Detalles")
        self._tabla = ttk.Treeview(
            panel_catalogo, columns=columnas, show="headings", height=8
        )
        anchos = [70, 90, 180, 120, 80, 280]
        for col, ancho in zip(columnas, anchos):
            self._tabla.heading(col, text=col)
            self._tabla.column(col, width=ancho, anchor=tk.CENTER)

        scroll = ttk.Scrollbar(panel_catalogo, orient=tk.VERTICAL,
                               command=self._tabla.yview)
        self._tabla.configure(yscrollcommand=scroll.set)
        self._tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # --- Eventos de seleccion ---
        # Al seleccionar una fila se carga el servicio en la calculadora
        self._tabla.bind("<<TreeviewSelect>>", self._al_seleccionar)

        tk.Button(
            panel_catalogo, text="Refrescar catálogo",
            command=self.refrescar_catalogo,
            bg="#27ae60", fg="white", font=("Helvetica", 9),
            relief=tk.FLAT, cursor="hand2", padx=8, pady=4
        ).pack(pady=(6, 0))

        # --- Panel inferior: calculadora de costos ---
        panel_calc = tk.LabelFrame(
            self.frame, text="Calculadora de costos",
            bg="#f5f5f5", font=("Helvetica", 10, "bold"),
            padx=12, pady=10
        )
        panel_calc.pack(fill=tk.X, padx=10, pady=(4, 10))

        # --- Fila 1: servicio seleccionado + horas ---
        fila1 = tk.Frame(panel_calc, bg="#f5f5f5")
        fila1.pack(fill=tk.X, pady=4)

        tk.Label(fila1, text="Servicio:", bg="#f5f5f5",
                 font=("Helvetica", 9)).pack(side=tk.LEFT)
        self._lbl_servicio = tk.Label(
            fila1, text="(ninguno seleccionado)",
            bg="#f5f5f5", fg="#7f8c8d", font=("Helvetica", 9, "italic")
        )
        self._lbl_servicio.pack(side=tk.LEFT, padx=(6, 30))

        tk.Label(fila1, text="Horas:", bg="#f5f5f5",
                 font=("Helvetica", 9)).pack(side=tk.LEFT)
        self._var_horas = tk.StringVar(value="1")
        tk.Entry(fila1, textvariable=self._var_horas, width=6,
                 font=("Helvetica", 10)).pack(side=tk.LEFT, padx=(4, 20))

        tk.Label(fila1, text="Impuesto (0-1):", bg="#f5f5f5",
                 font=("Helvetica", 9)).pack(side=tk.LEFT)
        self._var_impuesto = tk.StringVar(value="0.19")
        tk.Entry(fila1, textvariable=self._var_impuesto, width=6,
                 font=("Helvetica", 10)).pack(side=tk.LEFT, padx=(4, 20))

        tk.Label(fila1, text="Descuento (0-1):", bg="#f5f5f5",
                 font=("Helvetica", 9)).pack(side=tk.LEFT)
        self._var_descuento = tk.StringVar(value="0.0")
        tk.Entry(fila1, textvariable=self._var_descuento, width=6,
                 font=("Helvetica", 10)).pack(side=tk.LEFT, padx=4)

        # --- Fila 2: opcionales segun tipo de servicio ---
        fila2 = tk.Frame(panel_calc, bg="#f5f5f5")
        fila2.pack(fill=tk.X, pady=4)

        # Opcion sala: audiovisual + num_personas
        self._var_audiovisual = tk.BooleanVar()
        self._chk_audiovisual = tk.Checkbutton(
            fila2, text="Equipo audiovisual",
            variable=self._var_audiovisual, bg="#f5f5f5",
            font=("Helvetica", 9)
        )
        self._chk_audiovisual.pack(side=tk.LEFT, padx=(0, 16))

        tk.Label(fila2, text="Personas/Unidades:",
                 bg="#f5f5f5", font=("Helvetica", 9)).pack(side=tk.LEFT)
        self._var_cantidad = tk.StringVar(value="1")
        tk.Entry(fila2, textvariable=self._var_cantidad, width=5,
                 font=("Helvetica", 10)).pack(side=tk.LEFT, padx=(4, 20))

        # Opcion equipo: soporte tecnico
        self._var_soporte = tk.BooleanVar()
        self._chk_soporte = tk.Checkbutton(
            fila2, text="Con soporte técnico",
            variable=self._var_soporte, bg="#f5f5f5",
            font=("Helvetica", 9)
        )
        self._chk_soporte.pack(side=tk.LEFT, padx=(0, 16))

        # Opcion asesoria: presencial + sesiones
        self._var_presencial = tk.BooleanVar()
        self._chk_presencial = tk.Checkbutton(
            fila2, text="Presencial",
            variable=self._var_presencial, bg="#f5f5f5",
            font=("Helvetica", 9)
        )
        self._chk_presencial.pack(side=tk.LEFT, padx=(0, 16))

        tk.Label(fila2, text="Sesiones:",
                 bg="#f5f5f5", font=("Helvetica", 9)).pack(side=tk.LEFT)
        self._var_sesiones = tk.StringVar(value="1")
        tk.Entry(fila2, textvariable=self._var_sesiones, width=4,
                 font=("Helvetica", 10)).pack(side=tk.LEFT, padx=4)

        # --- Fila 3: boton calcular + resultado ---
        fila3 = tk.Frame(panel_calc, bg="#f5f5f5")
        fila3.pack(fill=tk.X, pady=(8, 4))

        tk.Button(
            fila3, text="Calcular costo",
            command=self._calcular_costo,
            bg="#8e44ad", fg="white",
            font=("Helvetica", 10, "bold"),
            relief=tk.FLAT, cursor="hand2",
            padx=12, pady=6
        ).pack(side=tk.LEFT)

        self._lbl_resultado = tk.Label(
            fila3, text="",
            bg="#f5f5f5", font=("Helvetica", 13, "bold"),
            fg="#2c3e50"
        )
        self._lbl_resultado.pack(side=tk.LEFT, padx=20)

        self._lbl_descripcion = tk.Label(
            panel_calc, text="",
            bg="#f5f5f5", fg="#7f8c8d",
            font=("Helvetica", 9), justify=tk.LEFT, wraplength=800
        )
        self._lbl_descripcion.pack(anchor="w", pady=(4, 0))

    def _al_seleccionar(self, evento):
        """Carga el servicio seleccionado en la calculadora."""
        # --- Leer seleccion de la tabla ---
        seleccion = self._tabla.selection()
        if not seleccion:
            return

        item = self._tabla.item(seleccion[0])
        id_servicio = item["values"][0]
        servicio = self._gestor.buscar_servicio_por_id(str(id_servicio))

        # --- Sincronizar UI con el servicio ---
        if servicio:
            self._servicio_seleccionado = servicio
            self._lbl_servicio.config(
                text=str(servicio), fg="#2c3e50", font=("Helvetica", 9)
            )
            self._lbl_descripcion.config(text=servicio.describir())
            self._lbl_resultado.config(text="")

    def _calcular_costo(self):
        """
        Lee los parámetros del formulario y llama a calcular_costo()
        del servicio seleccionado. Usa try/except/else para feedback claro.
        """
        # --- Validacion de seleccion ---
        if not self._servicio_seleccionado:
            messagebox.showwarning("Sin selección", "Selecciona un servicio del catálogo primero.")
            return

        # --- Parseo de parametros numericos ---
        try:
            horas = float(self._var_horas.get())
            impuesto = float(self._var_impuesto.get())
            descuento = float(self._var_descuento.get())
            cantidad = int(self._var_cantidad.get())
            sesiones = int(self._var_sesiones.get())

        except ValueError as e:
            self._log.error("Parámetros inválidos en calculadora.", str(e))
            messagebox.showerror("Error", "Verifica que los campos numéricos tengan valores válidos.")
            return

        # --- Construir kwargs segun el tipo de servicio ---
        kwargs = {
            "impuesto": impuesto,
            "descuento": descuento,
            "audiovisual": self._var_audiovisual.get(),
            "num_personas": cantidad,
            "cantidad": cantidad,
            "con_soporte": self._var_soporte.get(),
            "presencial": self._var_presencial.get(),
            "num_sesiones": sesiones,
        }

        # --- Calculo con manejo de errores de negocio ---
        try:
            costo = self._servicio_seleccionado.calcular_costo(horas, **kwargs)

        except ServicioInvalidoError as e:
            self._log.error(
                f"Error al calcular costo de '{self._servicio_seleccionado.nombre}'.",
                str(e)
            )
            self._lbl_resultado.config(
                text=f"Error: {e}", fg="#e74c3c", font=("Helvetica", 10)
            )
        else:
            # --- Exito y feedback visual ---
            self._log.info(
                f"Costo calculado para '{self._servicio_seleccionado.nombre}'.",
                f"{horas}hr → ${costo:,.2f}"
            )
            self._lbl_resultado.config(
                text=f"Costo total: ${costo:,.2f} COP",
                fg="#27ae60", font=("Helvetica", 13, "bold")
            )

    def refrescar_catalogo(self):
        """Repuebla la tabla con los servicios actuales del gestor."""
        # --- Limpiar tabla ---
        for fila in self._tabla.get_children():
            self._tabla.delete(fila)

        # --- Poblar con datos actuales ---
        for s in self._gestor.listar_servicios():
            d = s.to_dict()
            tipo = d["tipo"].replace("ReservaSala", "Sala") \
                            .replace("AlquilerEquipo", "Equipo") \
                            .replace("AsesoriaEspecializada", "Asesoría")
            self._tabla.insert("", tk.END, values=(
                d["id"],
                tipo,
                d["nombre"],
                f"${d['precio_base']:,.0f}",
                "Sí" if d["disponible"] else "No",
                s.describir().replace("\n", " | ")
            ))