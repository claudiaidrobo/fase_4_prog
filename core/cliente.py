"""
cliente.py
Clase Cliente con validaciones robustas y encapsulación de datos personales.
"""

# --- Dependencias estandar ---
import re
import uuid
# --- Dependencias internas ---
from core.entidad_base import EntidadBase
from core.excepciones import ClienteInvalidoError


class Cliente(EntidadBase):
    """
    Representa un cliente de Software FJ.
    Aplica encapsulación estricta: los atributos sensibles solo se modifican
    a través de setters que validan los datos antes de asignarlos.
    """

    # --- Patrones de validacion ---
    # Expresion regular para validar formato de email
    _PATRON_EMAIL = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$")
    # Expresion regular: solo digitos, espacios, +, -, parentesis; 7-15 chars
    _PATRON_TELEFONO = re.compile(r"^[\d\s\+\-\(\)]{7,15}$")

    def __init__(self, nombre: str, email: str, telefono: str, id_cliente: str = None):
        """
        Inicializa un Cliente validando todos sus datos antes de asignarlos.

        Args:
            nombre: Nombre completo (mínimo 3 caracteres, solo letras y espacios).
            email: Correo electrónico en formato válido.
            telefono: Número de contacto (7-15 dígitos).
            id_cliente: ID único; si no se pasa, se genera automáticamente con uuid.

        Raises:
            ClienteInvalidoError: Si algún dato no cumple las reglas de validación.
        """
        # --- Identidad y estado inicial ---
        # Generamos el ID antes de llamar al super para poder pasarlo
        id_generado = id_cliente if id_cliente else str(uuid.uuid4())[:8].upper()
        super().__init__(id_generado)

        # --- Validacion por setters ---
        # Usamos los setters para aplicar validacion desde el constructor
        self.nombre = nombre
        self.email = email
        self.telefono = telefono

        # --- Asociaciones internas ---
        # Lista interna de IDs de reservas asociadas a este cliente
        self.__reservas_ids: list[str] = []

    # --- Propiedades con validación (encapsulación) ---

    @property
    def nombre(self) -> str:
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str):
        # --- Reglas de validacion de nombre ---
        # Validacion: no vacio, minimo 3 chars, solo letras y espacios
        if not valor or not valor.strip():
            raise ClienteInvalidoError("El nombre no puede estar vacío.")
        valor = valor.strip()
        if len(valor) < 3:
            raise ClienteInvalidoError(
                f"El nombre '{valor}' es demasiado corto (mínimo 3 caracteres)."
            )
        if not re.match(r"^[A-Za-záéíóúÁÉÍÓÚüÜñÑ\s]+$", valor):
            raise ClienteInvalidoError(
                f"El nombre '{valor}' contiene caracteres no permitidos."
            )
        self.__nombre = valor

    @property
    def email(self) -> str:
        return self.__email

    @email.setter
    def email(self, valor: str):
        # --- Reglas de validacion de email ---
        if not valor or not valor.strip():
            raise ClienteInvalidoError("El email no puede estar vacío.")
        valor = valor.strip().lower()
        if not self._PATRON_EMAIL.match(valor):
            raise ClienteInvalidoError(
                f"El email '{valor}' no tiene un formato válido."
            )
        self.__email = valor

    @property
    def telefono(self) -> str:
        return self.__telefono

    @telefono.setter
    def telefono(self, valor: str):
        # --- Reglas de validacion de telefono ---
        if not valor or not valor.strip():
            raise ClienteInvalidoError("El teléfono no puede estar vacío.")
        valor = valor.strip()
        if not self._PATRON_TELEFONO.match(valor):
            raise ClienteInvalidoError(
                f"El teléfono '{valor}' no tiene un formato válido (7-15 dígitos)."
            )
        self.__telefono = valor

    # --- Gestión de reservas asociadas ---

    # --- API de asociaciones ---
    def agregar_reserva_id(self, id_reserva: str):
        """Registra el ID de una reserva asociada a este cliente."""
        if id_reserva not in self.__reservas_ids:
            self.__reservas_ids.append(id_reserva)

    def obtener_reservas_ids(self) -> list:
        """Retorna una copia de la lista de IDs de reservas (inmutable externamente)."""
        return self.__reservas_ids.copy()

    # --- Métodos abstractos implementados ---

    # --- Contrato de EntidadBase ---
    def validar(self) -> bool:
        """
        Verifica que el cliente tiene todos sus datos en un estado consistente.
        Retorna True si es válido. En uso normal siempre es True porque los setters
        ya validan, pero sirve como doble verificación.
        """
        try:
            assert self.nombre and len(self.nombre) >= 3
            assert self._PATRON_EMAIL.match(self.email)
            assert self._PATRON_TELEFONO.match(self.telefono)
            return True
        except AssertionError:
            return False

    def to_dict(self) -> dict:
        """Serializa el cliente como diccionario para la UI y los logs."""
        return {
            "id": self.id,
            "nombre": self.__nombre,
            "email": self.__email,
            "telefono": self.__telefono,
            "reservas": len(self.__reservas_ids),
            "registrado": self.fecha_creacion.strftime("%Y-%m-%d %H:%M:%S"),
        }

    def __str__(self) -> str:
        return f"[{self.id}] {self.__nombre} — {self.__email} | Tel: {self.__telefono}"