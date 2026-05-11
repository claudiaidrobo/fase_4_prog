"""
tab_reservas.py
Pestaña de gestión de reservas en la UI Tkinter.
Permite crear, confirmar, cancelar y procesar reservas con feedback visual.
"""

# --- Dependencias UI ---
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
# --- Dependencias internas ---
from core.reserva import EstadoReserva
from core.excepciones import (
    ReservaInvalidaError,
    ReservaNoEncontradaError,
    OperacionNoPermitidaError,
    ServicioNoDisponibleError,
    ClienteNoEncontradoError,
)
from utils.gestor import Gestor
from utils.logger import Logger
from utils.gestor_reservas import GestorReservas


class TabReservas:
    """
    Pestaña 'Reservas' del notebook.
    Muestra el listado de reservas con colores por estado y
    permite ejecutar todas las transiciones del ciclo de vida.
    """

    # Colores de fila según estado de la reserva
    _COLORES_ESTADO = {
        EstadoReserva.PENDIENTE.value:  "#f39c12",
        EstadoReserva.CONFIRMADA.value: "#27ae60",
        EstadoReserva.CANCELADA.value:  "#e74c3c",
        EstadoReserva.PROCESADA.value:  "#2980b9",
    }

    def __init__(self, parent, gestor: Gestor, log: Logger):
        # --- Servicios compartidos ---
        self._gestor = gestor
        self._log = log
        self._gestor_reservas = GestorReservas(gestor, log)
        # --- Contenedor principal ---
        self.frame = tk.Frame(parent, bg="#f5f5f5")
        self._construir_ui()

    def _construir_ui(self):
        """Divide la pestaña en formulario de creación (izq) y tabla (der)."""

        # --- Panel izquierdo: formulario de nueva reserva ---
        panel_form = tk.LabelFrame(
            self.frame, text="Nueva reserva",
            bg="#f5f5f5", font=("Helvetica", 10, "bold"),
            padx=12, pady=12
        )
        panel_form.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 5), pady=10)

        # --- Campos del formulario ---
        # ID del cliente
        tk.Label(panel_form, text="ID del cliente:",
                 bg="#f5f5f5", font=("Helvetica", 9)).grid(
            row=0, column=0, sticky="w", pady=(8, 0))
        self._var_id_cliente = tk.StringVar()
        tk.Entry(panel_form, textvariable=self._var_id_cliente,
                 width=20, font=("Helvetica", 10)).grid(
            row=1, column=0, pady=(2, 0), ipady=4)

        # ID del servicio
        tk.Label(panel_form, text="ID del servicio:",
                 bg="#f5f5f5", font=("Helvetica", 9)).grid(
            row=2, column=0, sticky="w", pady=(8, 0))
        self._var_id_servicio = tk.StringVar()
        tk.Entry(panel_form, textvariable=self._var_id_servicio,
                 width=20, font=("Helvetica", 10)).grid(
            row=3, column=0, pady=(2, 0), ipady=4)

        # Horas
        tk.Label(panel_form, text="Horas:",
                 bg="#f5f5f5", font=("Helvetica", 9)).grid(
            row=4, column=0, sticky="w", pady=(8, 0))
        self._var_horas = tk.StringVar(value="1")
        tk.Entry(panel_form, textvariable=self._var_horas,
                 width=20, font=("Helvetica", 10)).grid(
            row=5, column=0, pady=(2, 0), ipady=4)

        # Impuesto
        tk.Label(panel_form, text="Impuesto (ej: 0.19):",
                 bg="#f5f5f5", font=("Helvetica", 9)).grid(
            row=6, column=0, sticky="w", pady=(8, 0))
        self._var_impuesto = tk.StringVar(value="0.19")
        tk.Entry(panel_form, textvariable=self._var_impuesto,
                 width=20, font=("Helvetica", 10)).grid(
            row=7, column=0, pady=(2, 0), ipady=4)

        # Descuento
        tk.Label(panel_form, text="Descuento (ej: 0.0):",
                 bg="#f5f5f5", font=("Helvetica", 9)).grid(
            row=8, column=0, sticky="w", pady=(8, 0))
        self._var_descuento = tk.StringVar(value="0.0")
        tk.Entry(panel_form, textvariable=self._var_descuento,
                 width=20, font=("Helvetica", 10)).grid(
            row=9, column=0, pady=(2, 0), ipady=4)

        # --- Acciones del formulario ---
        # Boton crear
        tk.Button(
            panel_form, text="Crear reserva",
            command=self._crear_reserva,
            bg="#8e44ad", fg="white",
            font=("Helvetica", 10, "bold"),
            relief=tk.FLAT, cursor="hand2",
            padx=10, pady=6
        ).grid(row=10, column=0, pady=(18, 4), sticky="ew")

        # Separador
        ttk.Separator(panel_form, orient=tk.HORIZONTAL).grid(
            row=11, column=0, sticky="ew", pady=10)

        # --- Acciones sobre reserva seleccionada ---
        tk.Label(panel_form, text="Acciones sobre reserva seleccionada:",
                 bg="#f5f5f5", font=("Helvetica", 9, "bold")).grid(
            row=12, column=0, sticky="w")

        tk.Button(
            panel_form, text="Confirmar reserva",
            command=self._confirmar_reserva,
            bg="#27ae60", fg="white",
            font=("Helvetica", 9, "bold"),
            relief=tk.FLAT, cursor="hand2",
            padx=10, pady=5
        ).grid(row=13, column=0, sticky="ew", pady=(6, 3))

        tk.Button(
            panel_form, text="Cancelar reserva",
            command=self._cancelar_reserva,
            bg="#e74c3c", fg="white",
            font=("Helvetica", 9, "bold"),
            relief=tk.FLAT, cursor="hand2",
            padx=10, pady=5
        ).grid(row=14, column=0, sticky="ew", pady=3)

        tk.Button(
            panel_form, text="Procesar reserva",
            command=self._procesar_reserva,
            bg="#2980b9", fg="white",
            font=("Helvetica", 9, "bold"),
            relief=tk.FLAT, cursor="hand2",
            padx=10, pady=5
        ).grid(row=15, column=0, sticky="ew", pady=3)

        # --- Feedback de estado ---
        self._lbl_estado = tk.Label(
            panel_form, text="",
            bg="#f5f5f5", font=("Helvetica", 9),
            wraplength=200, justify=tk.LEFT
        )
        self._lbl_estado.grid(row=16, column=0, pady=(10, 0))

        # --- Panel derecho: tabla de reservas ---
        panel_tabla = tk.LabelFrame(
            self.frame, text="Reservas registradas",
            bg="#f5f5f5", font=("Helvetica", 10, "bold"),
            padx=8, pady=8
        )
        panel_tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True,
                         padx=(5, 10), pady=10)

        # --- Definicion de columnas ---
        columnas = (
            "ID", "Cliente", "Servicio",
            "Horas", "Estado", "Costo total",
            "Creada", "Confirmada"
        )
        self._tabla = ttk.Treeview(
            panel_tabla, columns=columnas, show="headings", height=20
        )
        anchos = [90, 130, 160, 55, 90, 110, 140, 140]
        for col, ancho in zip(columnas, anchos):
            self._tabla.heading(col, text=col)
            self._tabla.column(col, width=ancho, anchor=tk.CENTER)

        # --- Estilos por estado ---
        # Tags de color por estado
        for estado, color in self._COLORES_ESTADO.items():
            self._tabla.tag_configure(estado, foreground=color)

        scroll_v = ttk.Scrollbar(panel_tabla, orient=tk.VERTICAL,
                                 command=self._tabla.yview)
        scroll_h = ttk.Scrollbar(panel_tabla, orient=tk.HORIZONTAL,
                                 command=self._tabla.xview)
        self._tabla.configure(
            yscrollcommand=scroll_v.set,
            xscrollcommand=scroll_h.set
        )
        self._tabla.pack(fill=tk.BOTH, expand=True)
        scroll_v.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_h.pack(side=tk.BOTTOM, fill=tk.X)

        tk.Button(
            panel_tabla, text="Refrescar",
            command=self.refrescar_tabla,
            bg="#2c3e50", fg="white",
            font=("Helvetica", 9), relief=tk.FLAT,
            cursor="hand2", padx=8, pady=4
        ).pack(pady=(6, 0))

    # --- Obtener reserva seleccionada en la tabla ---

    def _obtener_id_seleccionado(self) -> str | None:
        """Retorna el ID de la reserva seleccionada en la tabla, o None."""
        # --- Validacion de seleccion ---
        seleccion = self._tabla.selection()
        if not seleccion:
            messagebox.showwarning(
                "Sin selección",
                "Selecciona una reserva de la tabla primero."
            )
            return None
        return self._tabla.item(seleccion[0])["values"][0]

    # --- Acciones de reserva ---

    def _crear_reserva(self):
        """
        Lee el formulario y delega la creación al GestorReservas.
        Usa try/except/else/finally con manejo granular por tipo de excepción.
        """
        # --- Lectura de campos ---
        id_cliente  = self._var_id_cliente.get().strip()
        id_servicio = self._var_id_servicio.get().strip()

        # --- Validacion numerica ---
        try:
            horas     = float(self._var_horas.get())
            impuesto  = float(self._var_impuesto.get())
            descuento = float(self._var_descuento.get())
        except ValueError:
            self._lbl_estado.config(
                text="Error: horas, impuesto y descuento deben ser números.", fg="#e74c3c"
            )
            return

        # --- Creacion con manejo de errores ---
        try:
            reserva = self._gestor_reservas.crear_reserva(
                id_cliente, id_servicio, horas,
                impuesto=impuesto, descuento=descuento
            )

        # --- Errores esperados ---
        except ClienteNoEncontradoError as e:
            self._log.error("Reserva fallida: cliente no encontrado.", str(e))
            self._lbl_estado.config(text=f"Cliente no encontrado:\n{e}", fg="#e74c3c")

        except ServicioNoDisponibleError as e:
            self._log.error("Reserva fallida: servicio no disponible.", str(e))
            self._lbl_estado.config(text=f"Servicio no disponible:\n{e}", fg="#e74c3c")

        except ReservaInvalidaError as e:
            self._log.error("Reserva fallida: datos inválidos.", str(e))
            self._lbl_estado.config(text=f"Reserva inválida:\n{e}", fg="#e74c3c")

        # --- Error inesperado ---
        except Exception as e:
            self._log.critico("Error inesperado al crear reserva.", str(e))
            self._lbl_estado.config(text=f"Error inesperado:\n{e}", fg="#c0392b")

        # --- Exito ---
        else:
            # Solo si no hubo excepción
            self._lbl_estado.config(
                text=f"Reserva '{reserva.id}' creada exitosamente.", fg="#27ae60"
            )
            self._limpiar_formulario()
            self.refrescar_tabla()

        # --- Cierre del flujo ---
        finally:
            # Siempre refrescamos la tabla para reflejar el estado real
            self.refrescar_tabla()

    def _confirmar_reserva(self):
        """Confirma la reserva seleccionada en la tabla."""
        # --- Seleccion y validacion ---
        id_reserva = self._obtener_id_seleccionado()
        if not id_reserva:
            return

        # --- Confirmacion ---
        try:
            costo = self._gestor_reservas.confirmar_reserva(str(id_reserva))

        # --- Errores esperados ---
        except ReservaNoEncontradaError as e:
            self._lbl_estado.config(text=f"No encontrada:\n{e}", fg="#e74c3c")

        except OperacionNoPermitidaError as e:
            self._lbl_estado.config(text=f"Operación no permitida:\n{e}", fg="#e67e22")

        except ReservaInvalidaError as e:
            # Puede ser una excepción encadenada desde calcular_costo()
            causa = e.__cause__
            detalle = f"\nCausa: {causa}" if causa else ""
            self._lbl_estado.config(
                text=f"Error al confirmar:\n{e}{detalle}", fg="#e74c3c"
            )
        # --- Exito ---
        else:
            self._lbl_estado.config(
                text=f"Reserva confirmada.\nCosto: ${costo:,.2f} COP",
                fg="#27ae60"
            )
        # --- Cierre del flujo ---
        finally:
            self.refrescar_tabla()

    def _cancelar_reserva(self):
        """Cancela la reserva seleccionada, solicitando el motivo."""
        # --- Seleccion y validacion ---
        id_reserva = self._obtener_id_seleccionado()
        if not id_reserva:
            return

        # --- Solicitar motivo ---
        # Pedimos el motivo con un dialogo simple
        motivo = simpledialog.askstring(
            "Cancelar reserva",
            "Ingresa el motivo de cancelación:",
            parent=self.frame
        )
        if motivo is None:
            return  # El usuario presionó Cancelar en el diálogo

        # --- Cancelacion ---
        try:
            self._gestor_reservas.cancelar_reserva(str(id_reserva), motivo)

        # --- Errores esperados ---
        except ReservaNoEncontradaError as e:
            self._lbl_estado.config(text=f"No encontrada:\n{e}", fg="#e74c3c")

        except OperacionNoPermitidaError as e:
            self._lbl_estado.config(text=f"Operación no permitida:\n{e}", fg="#e67e22")

        else:
            self._lbl_estado.config(
                text=f"Reserva '{id_reserva}' cancelada.", fg="#e74c3c"
            )
        finally:
            self.refrescar_tabla()

    def _procesar_reserva(self):
        """Marca la reserva seleccionada como procesada."""
        # --- Seleccion y validacion ---
        id_reserva = self._obtener_id_seleccionado()
        if not id_reserva:
            return

        # --- Procesamiento ---
        try:
            self._gestor_reservas.procesar_reserva(str(id_reserva))

        # --- Errores esperados ---
        except ReservaNoEncontradaError as e:
            self._lbl_estado.config(text=f"No encontrada:\n{e}", fg="#e74c3c")

        except OperacionNoPermitidaError as e:
            self._lbl_estado.config(text=f"Operación no permitida:\n{e}", fg="#e67e22")

        # --- Exito ---
        else:
            self._lbl_estado.config(
                text=f"Reserva '{id_reserva}' procesada exitosamente.", fg="#2980b9"
            )
        # --- Cierre del flujo ---
        finally:
            self.refrescar_tabla()

    # --- Tabla ---

    def refrescar_tabla(self):
        """Repuebla la tabla con las reservas actuales del gestor."""
        # --- Limpiar tabla ---
        for fila in self._tabla.get_children():
            self._tabla.delete(fila)

        # --- Poblar con datos actuales ---
        for r in self._gestor.listar_reservas():
            d = r.to_dict()
            self._tabla.insert(
                "", tk.END,
                values=(
                    d["id"],
                    d["cliente_nombre"],
                    d["servicio_nombre"],
                    d["horas"],
                    d["estado"],
                    f"${d['costo_total']:,.2f}" if d["costo_total"] else "—",
                    d["fecha_creacion"],
                    d["fecha_confirmacion"] or "—",
                ),
                tags=(d["estado"],)
            )

    def _limpiar_formulario(self):
        """Vacía los campos del formulario de creación."""
        # --- Reset del formulario ---
        self._var_id_cliente.set("")
        self._var_id_servicio.set("")
        self._var_horas.set("1")
        self._var_impuesto.set("0.19")
        self._var_descuento.set("0.0")
        self._lbl_estado.config(text="")