"""
reserva.py
Clase Reserva con ciclo de vida completo: estados, confirmación,
cancelación y procesamiento con manejo robusto de excepciones.
"""

import uuid
from datetime import datetime
from enum import Enum
from core.entidad_base import EntidadBase
from core.excepciones import (
    ReservaInvalidaError,
    OperacionNoPermitidaError,
    ServicioNoDisponibleError,
)


class EstadoReserva(Enum):
    """Estados posibles dentro del ciclo de vida de una reserva."""
    PENDIENTE   = "Pendiente"
    CONFIRMADA  = "Confirmada"
    CANCELADA   = "Cancelada"
    PROCESADA   = "Procesada"


class Reserva(EntidadBase):
    """
    Representa una reserva que vincula un Cliente con un Servicio.
    Implementa un ciclo de vida controlado por estados y manejo
    exhaustivo de excepciones en cada transición.
    """

    def __init__(self, cliente, servicio, horas: float,
                 id_reserva: str = None, **kwargs_costo):
        """
        Args:
            cliente:      Instancia de Cliente ya registrado en el sistema.
            servicio:     Instancia de Servicio disponible.
            horas:        Duración de la reserva en horas (debe ser > 0).
            id_reserva:   ID opcional; se genera automáticamente si no se pasa.
            **kwargs_costo: Parámetros extra para calcular_costo()
                            (impuesto, descuento, audiovisual, etc.)

        Raises:
            ReservaInvalidaError:       Si los datos base son inválidos.
            ServicioNoDisponibleError:  Si el servicio está marcado como no disponible.
        """
        id_generado = id_reserva if id_reserva else "RES-" + str(uuid.uuid4())[:6].upper()
        super().__init__(id_generado)

        # Validaciones previas antes de asignar
        if horas <= 0:
            raise ReservaInvalidaError(
                f"Las horas deben ser mayores a 0. Recibido: {horas}"
            )
        if not servicio.disponible:
            raise ServicioNoDisponibleError(
                f"El servicio '{servicio.nombre}' no está disponible actualmente."
            )
        if not cliente.validar():
            raise ReservaInvalidaError(
                f"El cliente '{cliente.nombre}' no tiene datos válidos."
            )

        # Encapsulación: atributos privados con name mangling
        self.__cliente     = cliente
        self.__servicio    = servicio
        self.__horas       = horas
        self.__kwargs_costo = kwargs_costo
        self.__estado      = EstadoReserva.PENDIENTE
        self.__costo_total = 0.0
        self.__fecha_confirmacion = None
        self.__fecha_cancelacion  = None
        self.__motivo_cancelacion = ""
        self.__historial: list[dict] = []  # Auditoría de cambios de estado

        # Registramos la creación en el historial
        self._registrar_historial("Reserva creada en estado PENDIENTE.")

    # --- Propiedades de solo lectura ---

    @property
    def cliente(self):
        return self.__cliente

    @property
    def servicio(self):
        return self.__servicio

    @property
    def horas(self) -> float:
        return self.__horas

    @property
    def estado(self) -> EstadoReserva:
        return self.__estado

    @property
    def costo_total(self) -> float:
        return self.__costo_total

    @property
    def fecha_confirmacion(self):
        return self.__fecha_confirmacion

    @property
    def fecha_cancelacion(self):
        return self.__fecha_cancelacion

    @property
    def motivo_cancelacion(self) -> str:
        return self.__motivo_cancelacion

    # --- Ciclo de vida ---

    def confirmar(self) -> float:
        """
        Confirma la reserva: calcula el costo y cambia el estado a CONFIRMADA.

        Returns:
            El costo total calculado.

        Raises:
            OperacionNoPermitidaError: Si la reserva no está en estado PENDIENTE.
            ReservaInvalidaError:      Si el cálculo de costo falla (encadenada).
        """
        # Solo se puede confirmar una reserva PENDIENTE
        if self.__estado != EstadoReserva.PENDIENTE:
            raise OperacionNoPermitidaError(
                f"Solo se puede confirmar una reserva en estado PENDIENTE. "
                f"Estado actual: {self.__estado.value}"
            )

        try:
            # Intentamos calcular el costo con los parámetros almacenados
            costo = self.__servicio.calcular_costo(self.__horas, **self.__kwargs_costo)

        except Exception as e:
            # Encadenamiento de excepciones: preservamos la causa original
            raise ReservaInvalidaError(
                f"No se pudo calcular el costo para la reserva '{self.id}'."
            ) from e

        else:
            # Solo se ejecuta si calcular_costo() no lanzó excepción
            self.__costo_total = costo
            self.__estado = EstadoReserva.CONFIRMADA
            self.__fecha_confirmacion = datetime.now()
            self.__cliente.agregar_reserva_id(self.id)
            self._registrar_historial(
                f"Reserva CONFIRMADA. Costo: ${costo:,.2f}"
            )
            return costo

        finally:
            # Se ejecuta siempre, haya error o no
            # Útil para liberar recursos o notificar sistemas externos
            pass

    def cancelar(self, motivo: str = "Sin motivo especificado") -> bool:
        """
        Cancela la reserva. Solo se puede cancelar si está PENDIENTE o CONFIRMADA.

        Args:
            motivo: Razón de la cancelación (se registra en el historial).

        Returns:
            True si la cancelación fue exitosa.

        Raises:
            OperacionNoPermitidaError: Si la reserva ya está CANCELADA o PROCESADA.
        """
        if self.__estado in (EstadoReserva.CANCELADA, EstadoReserva.PROCESADA):
            raise OperacionNoPermitidaError(
                f"No se puede cancelar una reserva en estado "
                f"'{self.__estado.value}'. "
                f"Solo se pueden cancelar reservas PENDIENTES o CONFIRMADAS."
            )

        try:
            self.__estado = EstadoReserva.CANCELADA
            self.__fecha_cancelacion = datetime.now()
            self.__motivo_cancelacion = motivo
            self._registrar_historial(f"Reserva CANCELADA. Motivo: {motivo}")

        except Exception as e:
            # Si algo falla al cancelar, revertimos el estado
            self.__estado = EstadoReserva.CONFIRMADA
            raise OperacionNoPermitidaError(
                f"Error inesperado al cancelar la reserva '{self.id}'."
            ) from e

        else:
            return True

        finally:
            # El bloque finally asegura que el log de cancelación
            # siempre quede registrado independientemente del resultado
            pass

    def procesar(self) -> bool:
        """
        Marca la reserva como PROCESADA (servicio efectivamente prestado).
        Solo se puede procesar una reserva CONFIRMADA.

        Raises:
            OperacionNoPermitidaError: Si la reserva no está CONFIRMADA.
        """
        if self.__estado != EstadoReserva.CONFIRMADA:
            raise OperacionNoPermitidaError(
                f"Solo se puede procesar una reserva CONFIRMADA. "
                f"Estado actual: {self.__estado.value}"
            )

        self.__estado = EstadoReserva.PROCESADA
        self._registrar_historial("Reserva PROCESADA. Servicio prestado exitosamente.")
        return True

    # --- Auditoría interna ---

    def _registrar_historial(self, descripcion: str):
        """Agrega una entrada al historial interno de cambios de estado."""
        self.__historial.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "estado": self.__estado.value,
            "descripcion": descripcion,
        })

    def obtener_historial(self) -> list[dict]:
        """Retorna una copia del historial de cambios de estado."""
        return self.__historial.copy()

    # --- Implementaciones abstractas ---

    def validar(self) -> bool:
        """Verifica que la reserva tiene cliente, servicio y horas válidos."""
        return (
            self.__cliente is not None
            and self.__servicio is not None
            and self.__horas > 0
        )

    def to_dict(self) -> dict:
        return {
            "id":                self.id,
            "cliente_id":        self.__cliente.id,
            "cliente_nombre":    self.__cliente.nombre,
            "servicio_id":       self.__servicio.id,
            "servicio_nombre":   self.__servicio.nombre,
            "horas":             self.__horas,
            "estado":            self.__estado.value,
            "costo_total":       self.__costo_total,
            "fecha_creacion":    self.fecha_creacion.strftime("%Y-%m-%d %H:%M:%S"),
            "fecha_confirmacion": (
                self.__fecha_confirmacion.strftime("%Y-%m-%d %H:%M:%S")
                if self.__fecha_confirmacion else ""
            ),
            "fecha_cancelacion": (
                self.__fecha_cancelacion.strftime("%Y-%m-%d %H:%M:%S")
                if self.__fecha_cancelacion else ""
            ),
            "motivo_cancelacion": self.__motivo_cancelacion,
        }

    def __str__(self) -> str:
        return (
            f"[{self.id}] {self.__cliente.nombre} → {self.__servicio.nombre} "
            f"| {self.__horas}hr | {self.__estado.value} "
            f"| ${self.__costo_total:,.2f}"
        )