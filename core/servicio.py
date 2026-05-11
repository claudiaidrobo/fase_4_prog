"""
servicio.py
Clase abstracta Servicio. Define el contrato que toda especialización
(ReservaSala, AlquilerEquipo, Asesoria) debe implementar.
"""

# --- Dependencias ---
from abc import abstractmethod
from core.entidad_base import EntidadBase


class Servicio(EntidadBase):
    """
    Clase abstracta que representa un servicio ofrecido por Software FJ.
    Las subclases implementan calcular_costo() con sus propias reglas.
    """

    def __init__(self, id_servicio: str, nombre: str, precio_base: float,
                 disponible: bool = True):
        """
        Args:
            id_servicio: Identificador único del servicio.
            nombre: Nombre descriptivo del servicio.
            precio_base: Precio base en pesos colombianos (debe ser > 0).
            disponible: Si el servicio puede ser reservado actualmente.
        """
        # --- Identidad y atributos base ---
        super().__init__(id_servicio)
        self.__nombre = nombre
        self.__precio_base = precio_base
        self.__disponible = disponible

    # --- Propiedades ---

    @property
    def nombre(self) -> str:
        # --- Acceso de solo lectura ---
        return self.__nombre

    @property
    def precio_base(self) -> float:
        # --- Acceso de solo lectura ---
        return self.__precio_base

    @property
    def disponible(self) -> bool:
        # --- Estado de disponibilidad ---
        return self.__disponible

    @disponible.setter
    def disponible(self, valor: bool):
        # --- Mutador controlado ---
        self.__disponible = valor

    # --- Métodos abstractos ---

    @abstractmethod
    def calcular_costo(self, horas: float, **kwargs) -> float:
        # --- Contrato de calculo ---
        """
        Calcula el costo total del servicio.
        Las subclases reciben parámetros adicionales vía **kwargs
        (ej: impuesto, descuento, numero_personas).
        """
        pass

    @abstractmethod
    def describir(self) -> str:
        # --- Contrato de descripcion ---
        """Retorna una descripción detallada del servicio para la UI."""
        pass

    # --- Implementaciones de EntidadBase ---

    def validar(self) -> bool:
        # --- Validacion basica ---
        """Valida que el servicio tiene nombre y precio base positivo."""
        return bool(self.__nombre) and self.__precio_base > 0

    def to_dict(self) -> dict:
        # --- Serializacion simple ---
        return {
            "id": self.id,
            "nombre": self.__nombre,
            "precio_base": self.__precio_base,
            "disponible": self.__disponible,
            "tipo": self.__class__.__name__,
        }

    def __str__(self) -> str:
        # --- Representacion legible ---
        estado = "Disponible" if self.__disponible else "No disponible"
        return f"[{self.id}] {self.__nombre} — ${self.__precio_base:,.0f}/hr | {estado}"