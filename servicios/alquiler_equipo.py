"""
alquiler_equipo.py
Servicio concreto: Alquiler de equipos tecnológicos (laptops, proyectores, etc.).
"""

# --- Dependencias internas ---
from core.servicio import Servicio
from core.excepciones import ServicioInvalidoError


class AlquilerEquipo(Servicio):
    """
    Servicio de alquiler de equipos tecnológicos.
    El costo depende de las horas, la cantidad de unidades solicitadas
    y si se requiere soporte técnico durante el alquiler.
    """

    # --- Constantes del servicio ---
    # Costo por hora adicional de soporte tecnico por equipo
    COSTO_SOPORTE_POR_HORA = 25_000

    def __init__(self, id_servicio: str, nombre: str, precio_base: float,
                 stock_disponible: int = 5, disponible: bool = True):
        """
        Args:
            stock_disponible: Unidades del equipo disponibles para alquilar.
        """
        # --- Estado base del servicio ---
        super().__init__(id_servicio, nombre, precio_base, disponible)

        # --- Validacion de stock ---
        if stock_disponible < 0:
            raise ServicioInvalidoError(
                f"El stock no puede ser negativo. Recibido: {stock_disponible}"
            )
        self.__stock_disponible = stock_disponible

    @property
    def stock_disponible(self) -> int:
        # --- Acceso de solo lectura ---
        return self.__stock_disponible

    def calcular_costo(self, horas: float, **kwargs) -> float:
        """
        Calcula el costo total del alquiler.

        Parámetros opcionales vía kwargs:
            - impuesto (float): porcentaje de IVA, ej: 0.19.
            - descuento (float): porcentaje de descuento, ej: 0.10.
            - cantidad (int): número de unidades a alquilar (default 1).
            - con_soporte (bool): si incluye técnico de soporte (default False).

        Raises:
            ServicioInvalidoError: si horas <= 0 o cantidad > stock_disponible.
        """
        # --- Validacion de horas ---
        if horas <= 0:
            raise ServicioInvalidoError(
                f"Las horas deben ser mayores a 0. Recibido: {horas}"
            )

        # --- Validacion de cantidad ---
        cantidad = kwargs.get("cantidad", 1)
        if cantidad <= 0:
            raise ServicioInvalidoError(
                f"La cantidad debe ser mayor a 0. Recibido: {cantidad}"
            )
        if cantidad > self.__stock_disponible:
            raise ServicioInvalidoError(
                f"Solo hay {self.__stock_disponible} unidades de '{self.nombre}' "
                f"disponibles, pero se solicitaron {cantidad}."
            )

        # --- Costo base ---
        # Costo base: precio/hora * horas * unidades
        costo = self.precio_base * horas * cantidad

        # --- Soporte tecnico ---
        # Soporte tecnico: costo por hora por cada unidad alquilada
        if kwargs.get("con_soporte", False):
            costo += self.COSTO_SOPORTE_POR_HORA * horas * cantidad

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
        # --- Descripcion legible ---
        return (
            f"Alquiler de equipo: {self.nombre}\n"
            f"Stock disponible: {self.__stock_disponible} unidades\n"
            f"Precio base: ${self.precio_base:,.0f} por hora/unidad\n"
            f"Soporte técnico: ${self.COSTO_SOPORTE_POR_HORA:,.0f}/hr por unidad (opcional)"
        )

    def to_dict(self) -> dict:
        # --- Serializacion extendida ---
        datos = super().to_dict()
        datos["stock_disponible"] = self.__stock_disponible
        datos["costo_soporte_hora"] = self.COSTO_SOPORTE_POR_HORA
        return datos

    def __str__(self) -> str:
        # --- Representacion corta ---
        return (
            f"[EQUIPO] {self.nombre} | Stock: {self.__stock_disponible} "
            f"| ${self.precio_base:,.0f}/hr por unidad"
        )