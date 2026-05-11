"""
tab_clientes.py
Pestaña de gestión de clientes en la UI Tkinter.
Permite registrar, listar, eliminar por selección y eliminar todos los clientes.
"""

# --- Dependencias UI ---
import tkinter as tk
from tkinter import ttk, messagebox
# --- Dependencias internas ---
from core.cliente import Cliente
from core.excepciones import ClienteInvalidoError
from utils.gestor import Gestor
from utils.logger import Logger


class TabClientes:
    """
    Pestaña 'Clientes' del notebook principal.
    Contiene un formulario de registro y una tabla con los clientes existentes,
    más botones para eliminar clientes individuales o en masa.
    """

    def __init__(self, parent, gestor: Gestor, log: Logger):
        # --- Servicios compartidos ---
        self._gestor = gestor
        self._log = log
        # --- Contenedor principal ---
        self.frame = tk.Frame(parent, bg="#f5f5f5")
        self._construir_ui()

    def _construir_ui(self):
        """Divide la pestaña en panel izquierdo (formulario) y derecho (tabla)."""

        # --- Panel izquierdo: formulario de registro ---
        panel_form = tk.LabelFrame(
            self.frame, text="Registrar nuevo cliente",
            bg="#f5f5f5", font=("Helvetica", 10, "bold"),
            padx=12, pady=12
        )
        panel_form.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 5), pady=10)

        # --- Campos del formulario ---
        campos = [
            ("Nombre completo:", "nombre"),
            ("Email:",           "email"),
            ("Teléfono:",        "telefono"),
        ]
        self._vars = {}

        for i, (etiqueta, clave) in enumerate(campos):
            tk.Label(
                panel_form, text=etiqueta,
                bg="#f5f5f5", font=("Helvetica", 9)
            ).grid(row=i * 2, column=0, sticky="w", pady=(8, 0))

            var = tk.StringVar()
            self._vars[clave] = var
            tk.Entry(
                panel_form, textvariable=var,
                width=28, font=("Helvetica", 10)
            ).grid(row=i * 2 + 1, column=0, pady=(2, 0), ipady=4)

        # --- Acciones del formulario ---
        # Boton registrar
        tk.Button(
            panel_form, text="Registrar cliente",
            command=self._registrar_cliente,
            bg="#2980b9", fg="white",
            font=("Helvetica", 10, "bold"),
            relief=tk.FLAT, cursor="hand2",
            padx=10, pady=6
        ).grid(row=7, column=0, pady=(20, 4), sticky="ew")

        # Boton limpiar
        tk.Button(
            panel_form, text="Limpiar campos",
            command=self._limpiar_campos,
            bg="#95a5a6", fg="white",
            font=("Helvetica", 9),
            relief=tk.FLAT, cursor="hand2",
            padx=10, pady=4
        ).grid(row=8, column=0, sticky="ew")

        # --- Feedback de estado ---
        # Etiqueta de feedback
        self._lbl_estado = tk.Label(
            panel_form, text="",
            bg="#f5f5f5", font=("Helvetica", 9),
            wraplength=200, justify=tk.LEFT
        )
        self._lbl_estado.grid(row=9, column=0, pady=(10, 0))

        # --- Panel derecho: tabla de clientes ---
        panel_tabla = tk.LabelFrame(
            self.frame, text="Clientes registrados",
            bg="#f5f5f5", font=("Helvetica", 10, "bold"),
            padx=8, pady=8
        )
        panel_tabla.pack(
            side=tk.LEFT, fill=tk.BOTH, expand=True,
            padx=(5, 10), pady=10
        )

        # --- Definicion de columnas ---
        columnas = ("ID", "Nombre", "Email", "Teléfono", "Reservas", "Registrado")
        self._tabla = ttk.Treeview(
            panel_tabla, columns=columnas,
            show="headings", height=18
        )

        anchos = [70, 160, 200, 120, 70, 140]
        for col, ancho in zip(columnas, anchos):
            self._tabla.heading(col, text=col)
            self._tabla.column(col, width=ancho, anchor=tk.CENTER)

        scroll_v = ttk.Scrollbar(
            panel_tabla, orient=tk.VERTICAL,
            command=self._tabla.yview
        )
        scroll_h = ttk.Scrollbar(
            panel_tabla, orient=tk.HORIZONTAL,
            command=self._tabla.xview
        )
        self._tabla.configure(
            yscrollcommand=scroll_v.set,
            xscrollcommand=scroll_h.set
        )
        self._tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_v.pack(side=tk.RIGHT,  fill=tk.Y)
        scroll_h.pack(side=tk.BOTTOM, fill=tk.X)

        # --- Acciones de la tabla ---
        # Botones apilados verticalmente bajo la tabla
        frame_botones = tk.Frame(panel_tabla, bg="#f5f5f5")
        frame_botones.pack(pady=(6, 0))

        tk.Button(
            frame_botones, text="Refrescar lista",
            command=self._refrescar_tabla,
            bg="#27ae60", fg="white",
            font=("Helvetica", 9), relief=tk.FLAT,
            cursor="hand2", padx=8, pady=4
        ).pack(fill=tk.X, pady=(0, 4))

        tk.Button(
            frame_botones, text="Eliminar seleccionado",
            command=self._eliminar_cliente,
            bg="#e74c3c", fg="white",
            font=("Helvetica", 9), relief=tk.FLAT,
            cursor="hand2", padx=8, pady=4
        ).pack(fill=tk.X, pady=(0, 4))

        tk.Button(
            frame_botones, text="Eliminar todos",
            command=self._eliminar_todos,
            bg="#7f8c8d", fg="white",
            font=("Helvetica", 9), relief=tk.FLAT,
            cursor="hand2", padx=8, pady=4
        ).pack(fill=tk.X)

    # --- Registro ---

    def _registrar_cliente(self):
        """
        Lee el formulario, crea un Cliente y lo registra en el gestor.
        Usa try/except/else/finally para feedback claro en cada caso.
        """
        # --- Lectura de campos ---
        nombre   = self._vars["nombre"].get()
        email    = self._vars["email"].get()
        telefono = self._vars["telefono"].get()

        # --- Registro con manejo de errores ---
        try:
            cliente = Cliente(nombre, email, telefono)
            self._gestor.agregar_cliente(cliente)

        # --- Errores esperados ---
        except ClienteInvalidoError as e:
            self._log.error("Datos inválidos al registrar cliente.", str(e))
            self._lbl_estado.config(
                text=f"Error de validación:\n{e}", fg="#e74c3c"
            )
        except ValueError as e:
            self._log.advertencia("Intento de registro duplicado.", str(e))
            self._lbl_estado.config(
                text=f"Atención:\n{e}", fg="#e67e22"
            )
        # --- Error inesperado ---
        except Exception as e:
            self._log.critico("Error inesperado al registrar cliente.", str(e))
            self._lbl_estado.config(
                text=f"Error inesperado:\n{e}", fg="#c0392b"
            )
        # --- Exito ---
        else:
            self._lbl_estado.config(
                text=f"Cliente '{nombre}' registrado exitosamente.",
                fg="#27ae60"
            )
            self._limpiar_campos()
            self._refrescar_tabla()
        # --- Cierre del flujo ---
        finally:
            pass

    # --- Eliminación individual ---

    def _eliminar_cliente(self):
        """
        Elimina el cliente seleccionado en la tabla previa confirmación.
        Bloquea la eliminación si el cliente tiene reservas activas.
        """
        # --- Validacion de seleccion ---
        seleccion = self._tabla.selection()
        if not seleccion:
            self._lbl_estado.config(
                text="Selecciona un cliente de la lista primero.",
                fg="#e67e22"
            )
            return

        item       = self._tabla.item(seleccion[0])
        id_cliente = item["values"][0]
        nombre     = item["values"][1]

        # --- Confirmacion del usuario ---
        confirmar = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Seguro que quieres eliminar al cliente '{nombre}' "
            f"(ID: {id_cliente})?\n"
            f"Esta acción no se puede deshacer."
        )
        if not confirmar:
            return

        # --- Eliminacion y manejo de errores ---
        try:
            self._gestor.eliminar_cliente(str(id_cliente))

        except ValueError as e:
            self._log.error(
                f"No se pudo eliminar el cliente '{id_cliente}'.", str(e)
            )
            self._lbl_estado.config(
                text=f"No se pudo eliminar:\n{e}", fg="#e74c3c"
            )
        except Exception as e:
            self._log.critico("Error inesperado al eliminar cliente.", str(e))
            self._lbl_estado.config(
                text=f"Error inesperado:\n{e}", fg="#c0392b"
            )
        else:
            self._lbl_estado.config(
                text=f"Cliente '{nombre}' eliminado correctamente.",
                fg="#27ae60"
            )
        finally:
            self._refrescar_tabla()

    # --- Eliminación masiva ---

    def _eliminar_todos(self):
        """
        Elimina todos los clientes sin reservas activas previa confirmación.
        Informa cuántos quedaron protegidos si los hubiera.
        """
        # --- Precondicion ---
        total = len(self._gestor.listar_clientes())
        if total == 0:
            self._lbl_estado.config(
                text="No hay clientes registrados.", fg="#e67e22"
            )
            return

        # --- Confirmacion masiva ---
        confirmar = messagebox.askyesno(
            "Confirmar eliminación masiva",
            f"Hay {total} cliente(s) registrados.\n"
            f"Se eliminarán todos los que no tengan reservas activas.\n\n"
            f"¿Continuar?"
        )
        if not confirmar:
            return

        # --- Eliminacion y manejo de errores ---
        try:
            eliminados = self._gestor.eliminar_todos_los_clientes()

        # --- Error inesperado ---
        except Exception as e:
            self._log.critico("Error inesperado en eliminación masiva.", str(e))
            self._lbl_estado.config(
                text=f"Error inesperado:\n{e}", fg="#c0392b"
            )
        # --- Feedback de resultado ---
        else:
            restantes = len(self._gestor.listar_clientes())
            if restantes > 0:
                self._lbl_estado.config(
                    text=(
                        f"{eliminados} cliente(s) eliminados. "
                        f"{restantes} protegido(s) por reservas activas."
                    ),
                    fg="#e67e22"
                )
            else:
                self._lbl_estado.config(
                    text=f"{eliminados} cliente(s) eliminados correctamente.",
                    fg="#27ae60"
                )
        # --- Cierre del flujo ---
        finally:
            self._refrescar_tabla()

    # --- Helpers ---

    def _refrescar_tabla(self):
        """Limpia y repuebla la tabla con los clientes actuales del gestor."""
        # --- Limpiar tabla ---
        for fila in self._tabla.get_children():
            self._tabla.delete(fila)
        # --- Poblar con datos actuales ---
        for cliente in self._gestor.listar_clientes():
            d = cliente.to_dict()
            self._tabla.insert("", tk.END, values=(
                d["id"], d["nombre"], d["email"],
                d["telefono"], d["reservas"], d["registrado"]
            ))

    def _limpiar_campos(self):
        """Vacía todos los campos del formulario y limpia el mensaje de estado."""
        # --- Reset del formulario ---
        for var in self._vars.values():
            var.set("")
        self._lbl_estado.config(text="")