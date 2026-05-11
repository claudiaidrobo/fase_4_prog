"""
tab_simulacion.py
Pestaña de simulación automática de las 10 operaciones requeridas.
Muestra el progreso en tiempo real y el reporte final con colores.
"""

# --- Dependencias UI ---
import tkinter as tk
from tkinter import ttk
# --- Dependencias internas ---
from simulacion.simulacion import Simulacion
from utils.gestor import Gestor
from utils.logger import Logger


class TabSimulacion:
    """
    Pestaña 'Simulación' del notebook.
    Un botón dispara las 10 operaciones y el resultado de cada una
    aparece en la tabla con indicador visual de éxito / error controlado
    / fallo inesperado.
    """

    # Colores para los tres tipos de resultado posibles
    _COLOR_EXITO          = "#27ae60"   # Verde  — operación exitosa
    _COLOR_ERROR_CTRL     = "#e67e22"   # Naranja — error esperado y capturado
    _COLOR_FALLO          = "#e74c3c"   # Rojo    — fallo inesperado

    def __init__(self, parent, gestor: Gestor, log: Logger):
        # --- Servicios compartidos ---
        self._gestor = gestor
        self._log = log
        self._simulacion = Simulacion(gestor, log)
        # --- Contenedor principal ---
        self.frame = tk.Frame(parent, bg="#f5f5f5")
        self._construir_ui()

    def _construir_ui(self):
        """Panel superior con botón y resumen, tabla inferior con resultados."""

        # --- Encabezado ---
        panel_top = tk.Frame(self.frame, bg="#f5f5f5")
        panel_top.pack(fill=tk.X, padx=14, pady=(14, 6))

        tk.Label(
            panel_top,
            text="Simulación automática de 10 operaciones",
            bg="#f5f5f5", font=("Helvetica", 12, "bold"), fg="#2c3e50"
        ).pack(side=tk.LEFT)

        self._btn_ejecutar = tk.Button(
            panel_top,
            text="▶  Ejecutar simulación",
            command=self._ejecutar,
            bg="#8e44ad", fg="white",
            font=("Helvetica", 10, "bold"),
            relief=tk.FLAT, cursor="hand2",
            padx=16, pady=6
        )
        self._btn_ejecutar.pack(side=tk.RIGHT)

        # --- Leyenda de colores ---
        panel_leyenda = tk.Frame(self.frame, bg="#f5f5f5")
        panel_leyenda.pack(fill=tk.X, padx=14, pady=(0, 8))

        for texto, color in [
            ("● Operación exitosa",          self._COLOR_EXITO),
            ("● Error controlado esperado",  self._COLOR_ERROR_CTRL),
            ("● Fallo inesperado",           self._COLOR_FALLO),
        ]:
            tk.Label(
                panel_leyenda, text=texto,
                bg="#f5f5f5", fg=color,
                font=("Helvetica", 9)
            ).pack(side=tk.LEFT, padx=(0, 24))

        # --- Barra de resumen ---
        self._lbl_resumen = tk.Label(
            self.frame, text="",
            bg="#f5f5f5", font=("Helvetica", 10),
            fg="#2c3e50"
        )
        self._lbl_resumen.pack(padx=14, anchor="w")

        # --- Tabla de resultados ---
        panel_tabla = tk.Frame(self.frame, bg="#f5f5f5")
        panel_tabla.pack(fill=tk.BOTH, expand=True, padx=14, pady=(4, 14))

        columnas = ("Operación", "Descripción", "Resultado", "Detalle")
        self._tabla = ttk.Treeview(
            panel_tabla, columns=columnas, show="headings", height=14
        )
        anchos = [80, 280, 150, 400]
        for col, ancho in zip(columnas, anchos):
            self._tabla.heading(col, text=col)
            self._tabla.column(col, width=ancho,
                               anchor=tk.CENTER if ancho < 200 else tk.W)

        # --- Estilos por resultado ---
        # Tags para colorear filas
        self._tabla.tag_configure("exito",      foreground=self._COLOR_EXITO)
        self._tabla.tag_configure("error_ctrl", foreground=self._COLOR_ERROR_CTRL)
        self._tabla.tag_configure("fallo",      foreground=self._COLOR_FALLO)

        scroll_v = ttk.Scrollbar(panel_tabla, orient=tk.VERTICAL,
                                 command=self._tabla.yview)
        scroll_h = ttk.Scrollbar(panel_tabla, orient=tk.HORIZONTAL,
                                 command=self._tabla.xview)
        self._tabla.configure(
            yscrollcommand=scroll_v.set,
            xscrollcommand=scroll_h.set
        )
        self._tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_v.pack(side=tk.RIGHT,  fill=tk.Y)
        scroll_h.pack(side=tk.BOTTOM, fill=tk.X)

        # --- Barra de progreso ---
        self._progreso = ttk.Progressbar(
            self.frame, orient=tk.HORIZONTAL,
            length=400, mode="determinate"
        )
        self._progreso.pack(padx=14, pady=(0, 10), fill=tk.X)

    def _ejecutar(self):
        """
        Deshabilita el botón, corre la simulación y puebla la tabla.
        Actualiza la barra de progreso después de cada operación.
        """
        # --- Preparar UI ---
        # Limpiamos tabla y progreso
        for fila in self._tabla.get_children():
            self._tabla.delete(fila)
        self._progreso["value"] = 0
        self._lbl_resumen.config(text="Ejecutando simulación...")
        self._btn_ejecutar.config(state=tk.DISABLED, text="Ejecutando...")
        self.frame.update_idletasks()

        # --- Ejecutar simulacion ---
        try:
            resultados = self._simulacion.ejecutar()
        except Exception as e:
            self._log.critico("La simulación terminó con un error inesperado.", str(e))
            self._lbl_resumen.config(
                text=f"Error inesperado durante la simulación: {e}",
                fg="#e74c3c"
            )
            return
        finally:
            self._btn_ejecutar.config(state=tk.NORMAL, text="▶  Ejecutar simulación")

        # --- Poblar tabla y progreso ---
        total = len(resultados)
        exitos = errores_ctrl = fallos = 0

        for i, r in enumerate(resultados):
            # Determinar tag y etiqueta de resultado
            if not r["exito"]:
                tag = "fallo"
                etiqueta = "✗ Fallo inesperado"
                fallos += 1
            elif r["esperaba_error"]:
                tag = "error_ctrl"
                etiqueta = "⚠ Error controlado"
                errores_ctrl += 1
            else:
                tag = "exito"
                etiqueta = "✓ Éxito"
                exitos += 1

            self._tabla.insert(
                "", tk.END,
                values=(r["op"], r["descripcion"], etiqueta, r["detalle"]),
                tags=(tag,)
            )

            # Actualizar progreso visualmente tras cada fila
            self._progreso["value"] = ((i + 1) / total) * 100
            self.frame.update_idletasks()

        # --- Resumen final ---
        self._lbl_resumen.config(
            text=(
                f"Completado — "
                f"Exitosas: {exitos}  |  "
                f"Errores controlados: {errores_ctrl}  |  "
                f"Fallos inesperados: {fallos}"
            ),
            fg="#27ae60" if fallos == 0 else "#e74c3c"
        )