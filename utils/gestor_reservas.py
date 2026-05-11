"""
gestor_reservas.py
Capa de servicio para operaciones sobre Reservas.
Centraliza la lógica de negocio y el manejo de excepciones,
manteniendo al Gestor (repositorio) limpio de reglas de negocio.
"""

# --- Dependencias internas ---
from core.reserva import Reserva, EstadoReserva
from core.excepciones import (
    ReservaInvalidaError,
    ReservaNoEncontradaError,
    OperacionNoPermitidaError,
    ServicioNoDisponibleError,
    ClienteNoEncontradoError,
)
from utils.gestor import Gestor
from utils.logger import Logger


class GestorReservas:
    """
    Servicio de aplicación para el ciclo de vida de reservas.
    Orquesta la interacción entre Cliente, Servicio y Reserva,
    delegando el almacenamiento al Gestor.
    """

    def __init__(self, gestor: Gestor, log: Logger):
        # --- Servicios compartidos ---
        self._gestor = gestor
        self._log = log

    def crear_reserva(self, id_cliente: str, id_servicio: str,
                      horas: float, **kwargs_costo) -> Reserva:
        """
        Crea y registra una nueva reserva en el sistema.

        Raises:
            ClienteNoEncontradoError:  Si el cliente no existe.
            ServicioNoDisponibleError: Si el servicio no existe o no está disponible.
            ReservaInvalidaError:      Si los parámetros son inválidos.
        """
        # --- Validacion de entradas ---
        # Buscamos el cliente — encadenamos excepcion si no existe
        cliente = self._gestor.buscar_cliente_por_id(id_cliente)
        if not cliente:
            raise ClienteNoEncontradoError(
                f"No existe un cliente con ID '{id_cliente}'."
            )

        # Buscamos el servicio
        servicio = self._gestor.buscar_servicio_por_id(id_servicio)
        if not servicio:
            raise ServicioNoDisponibleError(
                f"No existe un servicio con ID '{id_servicio}'."
            )

        # --- Creacion y registro ---
        try:
            # La creación de Reserva puede lanzar ReservaInvalidaError
            # o ServicioNoDisponibleError (encadenamiento implícito)
            reserva = Reserva(cliente, servicio, horas, **kwargs_costo)
            self._gestor.agregar_reserva(reserva)
            self._log.info(
                f"Reserva creada: {reserva.id}",
                f"Cliente: {cliente.nombre} | Servicio: {servicio.nombre}"
            )
            return reserva

        # --- Errores de dominio conocidos ---
        except (ReservaInvalidaError, ServicioNoDisponibleError):
            # Re-lanzamos las excepciones de dominio conocidas sin envolver
            raise

        # --- Error inesperado ---
        except Exception as e:
            # Cualquier error inesperado lo encadenamos en ReservaInvalidaError
            self._log.critico("Error inesperado al crear reserva.", str(e))
            raise ReservaInvalidaError(
                "Error inesperado al crear la reserva."
            ) from e

    def confirmar_reserva(self, id_reserva: str) -> float:
        """
        Confirma una reserva existente y retorna el costo calculado.

        Raises:
            ReservaNoEncontradaError:  Si el ID no corresponde a ninguna reserva.
            OperacionNoPermitidaError: Si la reserva no está en estado PENDIENTE.
            ReservaInvalidaError:      Si el cálculo de costo falla.
        """
        # --- Validar existencia ---
        reserva = self._gestor.buscar_reserva_por_id(id_reserva)
        if not reserva:
            raise ReservaNoEncontradaError(
                f"No existe una reserva con ID '{id_reserva}'."
            )

        # --- Confirmacion ---
        try:
            costo = reserva.confirmar()
            self._log.info(
                f"Reserva confirmada: {id_reserva}",
                f"Costo: ${costo:,.2f}"
            )
            return costo

        # --- Errores esperados ---
        except (OperacionNoPermitidaError, ReservaInvalidaError) as e:
            self._log.error(f"No se pudo confirmar la reserva '{id_reserva}'.", str(e))
            raise

        # --- Error inesperado ---
        except Exception as e:
            self._log.critico(f"Error inesperado al confirmar '{id_reserva}'.", str(e))
            raise ReservaInvalidaError(
                f"Error inesperado al confirmar la reserva '{id_reserva}'."
            ) from e

    def cancelar_reserva(self, id_reserva: str, motivo: str = "") -> bool:
        """
        Cancela una reserva existente.

        Raises:
            ReservaNoEncontradaError:  Si el ID no existe.
            OperacionNoPermitidaError: Si el estado no permite cancelación.
        """
        # --- Validar existencia ---
        reserva = self._gestor.buscar_reserva_por_id(id_reserva)
        if not reserva:
            raise ReservaNoEncontradaError(
                f"No existe una reserva con ID '{id_reserva}'."
            )

        # --- Cancelacion ---
        try:
            resultado = reserva.cancelar(motivo or "Cancelada por el usuario.")
            self._log.advertencia(
                f"Reserva cancelada: {id_reserva}",
                f"Motivo: {motivo}"
            )
            return resultado

        # --- Error de negocio ---
        except OperacionNoPermitidaError as e:
            self._log.error(f"No se pudo cancelar la reserva '{id_reserva}'.", str(e))
            raise

    def procesar_reserva(self, id_reserva: str) -> bool:
        """
        Marca una reserva como procesada (servicio efectivamente prestado).

        Raises:
            ReservaNoEncontradaError:  Si el ID no existe.
            OperacionNoPermitidaError: Si la reserva no está CONFIRMADA.
        """
        # --- Validar existencia ---
        reserva = self._gestor.buscar_reserva_por_id(id_reserva)
        if not reserva:
            raise ReservaNoEncontradaError(
                f"No existe una reserva con ID '{id_reserva}'."
            )

        # --- Procesamiento ---
        try:
            resultado = reserva.procesar()
            self._log.info(f"Reserva procesada exitosamente: {id_reserva}")
            return resultado

        # --- Error de negocio ---
        except OperacionNoPermitidaError as e:
            self._log.error(f"No se pudo procesar la reserva '{id_reserva}'.", str(e))
            raise

    def listar_por_estado(self, estado: EstadoReserva) -> list:
        """Filtra las reservas por estado."""
        # --- Filtro simple ---
        return [
            r for r in self._gestor.listar_reservas()
            if r.estado == estado
        ]