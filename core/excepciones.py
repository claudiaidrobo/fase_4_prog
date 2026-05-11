"""
excepciones.py
Excepciones personalizadas del sistema Software FJ.
Permiten identificar y manejar errores del dominio de forma controlada.
"""

# --- Jerarquia base de excepciones ---
class SoftwareFJError(Exception):
    """Excepción base del sistema. Toda excepción propia hereda de esta."""
    pass


# --- Excepciones de clientes ---
class ClienteInvalidoError(SoftwareFJError):
    """Se lanza cuando los datos de un cliente no superan las validaciones."""
    pass


class ClienteNoEncontradoError(SoftwareFJError):
    """Se lanza cuando se busca un cliente que no existe en el sistema."""
    pass


# --- Excepciones de servicios ---
class ServicioInvalidoError(SoftwareFJError):
    """Se lanza cuando los parámetros de un servicio son incorrectos."""
    pass


class ServicioNoDisponibleError(SoftwareFJError):
    """Se lanza cuando se intenta operar sobre un servicio no disponible."""
    pass


# --- Excepciones de reservas ---
class ReservaInvalidaError(SoftwareFJError):
    """Se lanza cuando una reserva no puede crearse o procesarse."""
    pass


class ReservaNoEncontradaError(SoftwareFJError):
    """Se lanza cuando se busca una reserva que no existe."""
    pass


# --- Excepciones de reglas de negocio ---
class OperacionNoPermitidaError(SoftwareFJError):
    """
    Se lanza cuando se intenta una operación no válida dado el estado actual
    del sistema (por ejemplo, cancelar una reserva ya cancelada).
    """
    pass