"""
entidad_base.py
Clase abstracta raíz del sistema Software FJ.
Define la interfaz mínima que toda entidad del dominio debe implementar.
"""

# --- Dependencias estandar ---
from abc import ABC, abstractmethod
from datetime import datetime


class EntidadBase(ABC):
    """
    Clase abstracta que representa cualquier entidad del sistema.
    Aplica abstracción y sirve como contrato base para Cliente, Servicio y Reserva.
    """

    def __init__(self, id_entidad: str):
        # --- Identidad y trazabilidad ---
        # Identificador único, encapsulado con name mangling (__) para que
        # no sea accesible directamente desde fuera de la clase
        self.__id = id_entidad
        # Fecha de creación registrada automáticamente al instanciar
        self.__fecha_creacion = datetime.now()

    @property
    def id(self) -> str:
        # --- Acceso de solo lectura ---
        """Retorna el identificador único de la entidad (solo lectura)."""
        return self.__id

    @property
    def fecha_creacion(self) -> datetime:
        # --- Acceso de solo lectura ---
        """Retorna la fecha y hora de creación de la entidad (solo lectura)."""
        return self.__fecha_creacion

    @abstractmethod
    def validar(self) -> bool:
        # --- Contrato de validacion ---
        """
        Valida que la entidad tenga datos consistentes.
        Toda subclase DEBE implementar este método.
        """
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        # --- Contrato de serializacion ---
        """
        Serializa la entidad como diccionario.
        Usado para mostrar datos en la UI y en los registros de log.
        """
        pass

    @abstractmethod
    def __str__(self) -> str:
        # --- Contrato de representacion legible ---
        """Representación legible de la entidad para la interfaz gráfica."""
        pass

    def __repr__(self) -> str:
        # --- Representacion tecnica ---
        """Representación técnica para depuración."""
        return f"{self.__class__.__name__}(id='{self.__id}')"