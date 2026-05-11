"""
tab_clientes.py
Pestaña de gestión de clientes en la UI Tkinter.
Permite registrar nuevos clientes y ver la lista de registrados.
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
    Contiene un formulario de registro y una tabla con los clientes existentes.
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
        campos = [("Nombre completo:", "nombre"), ("Email:", "email"), ("Teléfono:", "telefono")]
        self._vars = {}

        for i, (etiqueta, clave) in enumerate(campos):
            tk.Label(panel_form, text=etiqueta, bg="#f5f5f5",
                     font=("Helvetica", 9)).grid(row=i*2, column=0, sticky="w", pady=(8, 0))
            var = tk.StringVar()
            self._vars[clave] = var
            entry = tk.Entry(panel_form, textvariable=var, width=28,
                             font=("Helvetica", 10))
            entry.grid(row=i*2+1, column=0, pady=(2, 0), ipady=4)

        # --- Acciones del formulario ---
        # Boton de registro
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

        # --- Estado y feedback ---
        # Etiqueta de estado/feedback
        self._lbl_estado = tk.Label(
            panel_form, text="", bg="#f5f5f5",
            font=("Helvetica", 9), wraplength=200, justify=tk.LEFT
        )
        self._lbl_estado.grid(row=9, column=0, pady=(10, 0))

        # --- Panel derecho: tabla de clientes ---
        panel_tabla = tk.LabelFrame(
            self.frame, text="Clientes registrados",
            bg="#f5f5f5", font=("Helvetica", 10, "bold"),
            padx=8, pady=8
        )
        panel_tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True,
                         padx=(5, 10), pady=10)

        # --- Definicion de columnas ---
        columnas = ("ID", "Nombre", "Email", "Teléfono", "Reservas", "Registrado")
        self._tabla = ttk.Treeview(panel_tabla, columns=columnas,
                                   show="headings", height=18)

        anchos = [70, 160, 200, 120, 70, 140]
        for col, ancho in zip(columnas, anchos):
            self._tabla.heading(col, text=col)
            self._tabla.column(col, width=ancho, anchor=tk.CENTER)

        scroll = ttk.Scrollbar(panel_tabla, orient=tk.VERTICAL,
                               command=self._tabla.yview)
        self._tabla.configure(yscrollcommand=scroll.set)
        self._tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # --- Acciones de la tabla ---
        # Boton refrescar tabla
        tk.Button(
            panel_tabla, text="Refrescar lista",
            command=self._refrescar_tabla,
            bg="#27ae60", fg="white",
            font=("Helvetica", 9), relief=tk.FLAT,
            cursor="hand2", padx=8, pady=4
        ).pack(pady=(6, 0))

    def _registrar_cliente(self):
        """
        Lee los campos del formulario, intenta crear un Cliente y registrarlo.
        Usa try/except/else/finally para manejar errores y dar feedback claro.
        """
        # --- Lectura de campos ---
        nombre = self._vars["nombre"].get()
        email = self._vars["email"].get()
        telefono = self._vars["telefono"].get()

        # --- Flujo de registro con manejo de errores ---
        try:
            # Intentamos crear el cliente (puede lanzar ClienteInvalidoError)
            cliente = Cliente(nombre, email, telefono)
            # Intentamos agregarlo al gestor (puede lanzar ValueError si email duplicado)
            self._gestor.agregar_cliente(cliente)

        # --- Manejo de excepciones esperadas ---
        except ClienteInvalidoError as e:
            # Error de validación en los datos del cliente
            self._log.error("Datos inválidos al registrar cliente.", str(e))
            self._lbl_estado.config(
                text=f"Error de validación:\n{e}", fg="#e74c3c"
            )
        except ValueError as e:
            # Email duplicado u otro error de negocio
            self._log.advertencia("Intento de registro duplicado.", str(e))
            self._lbl_estado.config(
                text=f"Atención:\n{e}", fg="#e67e22"
            )
        except Exception as e:
            # Cualquier error inesperado
            self._log.critico("Error inesperado al registrar cliente.", str(e))
            self._lbl_estado.config(
                text=f"Error inesperado:\n{e}", fg="#c0392b"
            )
        # --- Exito ---
        else:
            # Solo se ejecuta si NO hubo excepción
            self._lbl_estado.config(
                text=f"Cliente '{nombre}' registrado exitosamente.", fg="#27ae60"
            )
            self._limpiar_campos()
            self._refrescar_tabla()
        # --- Cierre del flujo ---
        finally:
            # Siempre se ejecuta: refrescamos la tabla pase lo que pase
            pass  # (la tabla solo se actualiza en el bloque else para no mezclar estados)

    def _refrescar_tabla(self):
        """Limpia y vuelve a poblar la tabla con los datos actuales del gestor."""
        # --- Limpieza previa ---
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
        """Vacía todos los campos del formulario."""
        # --- Reset del formulario ---
        for var in self._vars.values():
            var.set("")
        self._lbl_estado.config(text="")