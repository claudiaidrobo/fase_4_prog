"""
asesoria.py
Servicio concreto: Asesorías especializadas (legal, técnica, financiera, etc.).
"""

# --- Dependencias internas ---
from core.servicio import Servicio
from core.excepciones import ServicioInvalidoError


# --- Configuracion de niveles ---
# Niveles de especializacion validos con su multiplicador de costo
NIVELES_ESPECIALIZACION = {
    "junior":   1.0,
    "senior":   1.5,
    "experto":  2.0,
}


class AsesoriaEspecializada(Servicio):
    """
    Servicio de asesoría profesional especializada.
    El costo varía según el nivel del asesor y si la sesión
    es presencial (agrega un cargo adicional) o virtual.
    """

    # --- Constantes del servicio ---
    CARGO_PRESENCIAL = 30_000  # Cargo fijo por sesion presencial

    def __init__(self, id_servicio: str, nombre: str, precio_base: float,
                 especialidad: str = "General",
                 nivel: str = "junior",
                 disponible: bool = True):
        """
        Args:
            especialidad: Área de la asesoría (ej: 'Legal', 'Técnica').
            nivel: Nivel del asesor ('junior', 'senior', 'experto').

        Raises:
            ServicioInvalidoError: si el nivel no es válido.
        """
        super().__init__(id_servicio, nombre, precio_base, disponible)

        # --- Validacion del nivel ---
        nivel_lower = nivel.lower()
        if nivel_lower not in NIVELES_ESPECIALIZACION:
            raise ServicioInvalidoError(
                f"Nivel '{nivel}' no válido. Opciones: "
                f"{', '.join(NIVELES_ESPECIALIZACION.keys())}"
            )

        # --- Estado interno ---
        self.__especialidad = especialidad
        self.__nivel = nivel_lower
        self.__multiplicador = NIVELES_ESPECIALIZACION[nivel_lower]

    @property
    def especialidad(self) -> str:
        # --- Acceso de solo lectura ---
        return self.__especialidad

    @property
    def nivel(self) -> str:
        # --- Acceso de solo lectura ---
        return self.__nivel

    def calcular_costo(self, horas: float, **kwargs) -> float:
        """
        Calcula el costo de la asesoría.

        Parámetros opcionales vía kwargs:
            - impuesto (float): porcentaje de IVA, ej: 0.19.
            - descuento (float): porcentaje de descuento, ej: 0.05.
            - presencial (bool): si la sesión es presencial (agrega cargo fijo).
            - num_sesiones (int): número de sesiones (default 1).

        Raises:
            ServicioInvalidoError: si horas <= 0 o num_sesiones <= 0.
        """
        # --- Validacion de horas ---
        if horas <= 0:
            raise ServicioInvalidoError(
                f"Las horas deben ser mayores a 0. Recibido: {horas}"
            )

        # --- Validacion de sesiones ---
        num_sesiones = kwargs.get("num_sesiones", 1)
        if num_sesiones <= 0:
            raise ServicioInvalidoError(
                f"El número de sesiones debe ser mayor a 0. Recibido: {num_sesiones}"
            )

        # --- Costo base con multiplicador ---
        costo = self.precio_base * self.__multiplicador * horas * num_sesiones

        # --- Cargo adicional si es presencial ---
        if kwargs.get("presencial", False):
            costo += self.CARGO_PRESENCIAL * num_sesiones

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
        multiplicador = NIVELES_ESPECIALIZACION[self.__nivel]
        return (
            f"Asesoría: {self.nombre}\n"
            f"Especialidad: {self.__especialidad}\n"
            f"Nivel del asesor: {self.__nivel.capitalize()} "
            f"(x{multiplicador} sobre precio base)\n"
            f"Precio base: ${self.precio_base:,.0f} por hora\n"
            f"Cargo presencial: ${self.CARGO_PRESENCIAL:,.0f} por sesión (opcional)"
        )

    def to_dict(self) -> dict:
        # --- Serializacion extendida ---
        datos = super().to_dict()
        datos["especialidad"] = self.__especialidad
        datos["nivel"] = self.__nivel
        datos["multiplicador"] = self.__multiplicador
        return datos

    def __str__(self) -> str:
        # --- Representacion corta ---
        return (
            f"[ASESORÍA] {self.nombre} | {self.__especialidad} "
            f"| Nivel: {self.__nivel.capitalize()} "
            f"| ${self.precio_base:,.0f}/hr"
        )