"""
logger.py
Sistema de registro de eventos y errores en archivo de logs.
Todos los errores y operaciones relevantes quedan escritos en data/eventos.log.
"""

# --- Dependencias estandar ---
import os
from datetime import datetime
from enum import Enum


class NivelLog(Enum):
    """Niveles de severidad para los registros de log."""
    INFO = "INFO"
    ADVERTENCIA = "ADVERTENCIA"
    ERROR = "ERROR"
    CRITICO = "CRITICO"


class Logger:
    """
    Servicio singleton de registro de eventos.
    Escribe en archivo y mantiene los últimos registros en memoria
    para mostrarlos en la pestaña de logs de la UI.
    """

    # --- Singleton ---
    _instancia = None  # Referencia singleton

    def __new__(cls):
        """Garantiza que solo exista una instancia del Logger en todo el sistema."""
        # --- Control de instancia unica ---
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia._inicializado = False
        return cls._instancia

    def __init__(self):
        # Evitamos re-inicializar si ya está listo
        # --- Inicializacion perezosa ---
        if self._inicializado:
            return
        # Ruta del archivo de log (relativa a donde se ejecute main.py)
        self._ruta_log = os.path.join("data", "eventos.log")
        # Buffer en memoria para la UI (máximo 200 entradas)
        self._buffer: list[dict] = []
        self._max_buffer = 200
        # Creamos el directorio data/ si no existe
        os.makedirs("data", exist_ok=True)
        self._inicializado = True
        self.info("Logger inicializado correctamente.")

    def _escribir(self, nivel: NivelLog, mensaje: str, detalle: str = ""):
        """
        Método interno que construye la entrada y la escribe al archivo y al buffer.
        Usa try/except/finally para garantizar que el sistema no falla si el log falla.
        """
        # --- Construccion del registro ---
        ahora = datetime.now()
        timestamp = ahora.strftime("%Y-%m-%d %H:%M:%S")
        entrada_texto = f"[{timestamp}] [{nivel.value}] {mensaje}"
        if detalle:
            entrada_texto += f" | Detalle: {detalle}"

        entrada_dict = {
            "timestamp": timestamp,
            "nivel": nivel.value,
            "mensaje": mensaje,
            "detalle": detalle,
        }

        # --- Escritura resiliente ---
        # try/except/finally: incluso si falla la escritura en disco,
        # el buffer en memoria y la ejecucion del programa continuan
        try:
            with open(self._ruta_log, "a", encoding="utf-8") as f:
                f.write(entrada_texto + "\n")
        except OSError as e:
            # Si no podemos escribir al disco, lo anotamos solo en el buffer
            entrada_dict["detalle"] += f" [ERROR DE ESCRITURA EN DISCO: {e}]"
        finally:
            # El buffer siempre se actualiza, haya error de disco o no
            self._buffer.append(entrada_dict)
            if len(self._buffer) > self._max_buffer:
                self._buffer.pop(0)

    # --- API pública del logger ---

    def info(self, mensaje: str, detalle: str = ""):
        """Registra un evento informativo (operación exitosa)."""
        # --- Entrada informativa ---
        self._escribir(NivelLog.INFO, mensaje, detalle)

    def advertencia(self, mensaje: str, detalle: str = ""):
        """Registra una advertencia (error recuperable o dato sospechoso)."""
        # --- Entrada de advertencia ---
        self._escribir(NivelLog.ADVERTENCIA, mensaje, detalle)

    def error(self, mensaje: str, detalle: str = ""):
        """Registra un error (operación fallida, excepción capturada)."""
        # --- Entrada de error ---
        self._escribir(NivelLog.ERROR, mensaje, detalle)

    def critico(self, mensaje: str, detalle: str = ""):
        """Registra un error crítico que compromete la integridad del sistema."""
        # --- Entrada critica ---
        self._escribir(NivelLog.CRITICO, mensaje, detalle)

    def obtener_registros(self, nivel: NivelLog = None) -> list[dict]:
        """
        Retorna los registros del buffer en memoria.
        Si se pasa un nivel, filtra por ese nivel de severidad.
        """
        # --- Lectura con filtro opcional ---
        if nivel:
            return [r for r in self._buffer if r["nivel"] == nivel.value]
        return self._buffer.copy()

    def limpiar_buffer(self):
        """Limpia el buffer en memoria (no afecta el archivo en disco)."""
        # --- Limpieza del buffer ---
        self._buffer.clear()