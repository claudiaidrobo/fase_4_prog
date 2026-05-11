"""
reserva_sala.py
Servicio concreto: Reserva de salas de reuniones o conferencias.
Hereda de Servicio e implementa calcular_costo() con lógica propia.
"""

# --- Dependencias internas ---
from core.servicio import Servicio
from core.excepciones import ServicioInvalidoError


class ReservaSala(Servicio):
    """
    Servicio de reserva de salas para reuniones o eventos.
    El costo depende de las horas, la capacidad de personas
    y si se requiere equipamiento audiovisual adicional.
    """

    # --- Constantes del servicio ---
    # Costo adicional fijo por uso de equipo audiovisual
    COSTO_AUDIOVISUAL = 50_000

    def __init__(self, id_servicio: str, nombre: str, precio_base: float,
                 capacidad_max: int = 10, disponible: bool = True):
        """
        Args:
            capacidad_max: Número máximo de personas que admite la sala.
        """
        # --- Estado base del servicio ---
        super().__init__(id_servicio, nombre, precio_base, disponible)

        # --- Validacion de capacidad ---
        # Validamos que la capacidad sea un numero positivo
        if capacidad_max <= 0:
            raise ServicioInvalidoError(
                f"La capacidad máxima debe ser mayor a 0. Recibido: {capacidad_max}"
            )
        self.__capacidad_max = capacidad_max

    @property
    def capacidad_max(self) -> int:
        # --- Acceso de solo lectura ---
        return self.__capacidad_max

    def calcular_costo(self, horas: float, **kwargs) -> float:
        """
        Calcula el costo total de la reserva de sala.

        Parámetros opcionales vía kwargs:
            - impuesto (float): porcentaje de IVA a aplicar, ej: 0.19 para 19%.
            - descuento (float): porcentaje de descuento, ej: 0.10 para 10%.
            - audiovisual (bool): si se usa equipo adicional (agrega costo fijo).
            - num_personas (int): cantidad de personas (valida contra capacidad_max).

        Raises:
            ServicioInvalidoError: si horas <= 0 o num_personas > capacidad_max.
        """
        # --- Validacion de horas ---
        if horas <= 0:
            raise ServicioInvalidoError(
                f"Las horas deben ser mayores a 0. Recibido: {horas}"
            )

        # --- Validacion de personas si se proporciono ---
        num_personas = kwargs.get("num_personas", 1)
        if num_personas > self.__capacidad_max:
            raise ServicioInvalidoError(
                f"La sala '{self.nombre}' tiene capacidad para {self.__capacidad_max} "
                f"personas, pero se solicitaron {num_personas}."
            )

        # --- Costo base ---
        # Costo base: precio por hora * numero de horas
        costo = self.precio_base * horas

        # --- Adicional por equipo audiovisual ---
        if kwargs.get("audiovisual", False):
            costo += self.COSTO_AUDIOVISUAL

        # --- Descuento (antes del impuesto) ---
        descuento = kwargs.get("descuento", 0.0)
        if descuento < 0 or descuento >= 1:
            raise ServicioInvalidoError(
                f"El descuento debe estar entre 0 y 1. Recibido: {descuento}"
            )
        costo *= (1 - descuento)

        # --- Impuesto ---
        impuesto = kwargs.get("impuesto", 0.0)
        if impuesto < 0:
            raise ServicioInvalidoError(
                f"El impuesto no puede ser negativo. Recibido: {impuesto}"
            )
        costo *= (1 + impuesto)

        return round(costo, 2)

    def describir(self) -> str:
        """Retorna descripción completa del servicio para la UI."""
        # --- Descripcion legible ---
        return (
            f"Sala de reuniones: {self.nombre}\n"
            f"Capacidad: {self.__capacidad_max} personas\n"
            f"Precio base: ${self.precio_base:,.0f} por hora\n"
            f"Audiovisual adicional: ${self.COSTO_AUDIOVISUAL:,.0f} (opcional)"
        )

    def to_dict(self) -> dict:
        """Extiende el diccionario base con datos propios de la sala."""
        # --- Serializacion extendida ---
        datos = super().to_dict()
        datos["capacidad_max"] = self.__capacidad_max
        datos["costo_audiovisual"] = self.COSTO_AUDIOVISUAL
        return datos

    def __str__(self) -> str:
        # --- Representacion corta ---
        return (
            f"[SALA] {self.nombre} | Cap: {self.__capacidad_max} personas "
            f"| ${self.precio_base:,.0f}/hr"
        )