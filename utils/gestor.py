"""
gestor.py
Repositorio en memoria del sistema Software FJ.
Centraliza el almacenamiento y búsqueda de clientes, servicios y reservas
usando listas de Python (sin base de datos).
"""

# --- Dependencias internas ---
from utils.logger import Logger


class Gestor:
    """
    Repositorio singleton que actúa como fuente de verdad del sistema.
    Todas las entidades viven aquí mientras la app está en ejecución.
    """

    # --- Singleton ---
    _instancia = None

    def __new__(cls):
        # --- Control de instancia unica ---
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia._inicializado = False
        return cls._instancia

    def __init__(self):
        # --- Inicializacion perezosa ---
        if self._inicializado:
            return
        self._clientes: list = []
        self._servicios: list = []
        self._reservas: list = []
        self._log = Logger()
        self._inicializado = True
        self._log.info("Gestor de datos inicializado.")

    # --- Clientes ---

    def agregar_cliente(self, cliente) -> bool:
        """
        Registra un cliente en el sistema.
        Verifica que no exista otro cliente con el mismo email.
        """
        # --- Validacion de duplicados ---
        try:
            if self.buscar_cliente_por_email(cliente.email):
                raise ValueError(
                    f"Ya existe un cliente con el email '{cliente.email}'."
                )
            self._clientes.append(cliente)
            self._log.info(f"Cliente registrado: {cliente}")
            return True
        except ValueError as e:
            # --- Registro del error de negocio ---
            self._log.error("No se pudo registrar el cliente.", str(e))
            raise

    def buscar_cliente_por_id(self, id_cliente: str):
        """Busca un cliente por su ID. Retorna None si no existe."""
        # --- Busqueda lineal ---
        for c in self._clientes:
            if c.id == id_cliente:
                return c
        return None

    def buscar_cliente_por_email(self, email: str):
        """Busca un cliente por email. Retorna None si no existe."""
        # --- Normalizacion de email ---
        for c in self._clientes:
            if c.email == email.lower():
                return c
        return None

    def listar_clientes(self) -> list:
        """Retorna una copia de la lista de clientes registrados."""
        # --- Copia defensiva ---
        return self._clientes.copy()

    def eliminar_cliente(self, id_cliente: str) -> bool:
        """
        Elimina un cliente por su ID.
        No permite eliminar un cliente que tenga reservas activas
        (pendientes o confirmadas).

        Raises:
            ValueError: Si el cliente no existe o tiene reservas activas.
        """
        cliente = self.buscar_cliente_por_id(id_cliente)
        if not cliente:
            raise ValueError(f"No existe un cliente con ID '{id_cliente}'.")

        # Verificamos que no tenga reservas activas
        reservas_activas = [
            r for r in self._reservas
            if r.cliente.id == id_cliente
            and r.estado.value in ("Pendiente", "Confirmada")
        ]
        if reservas_activas:
            ids = ", ".join(r.id for r in reservas_activas)
            raise ValueError(
                f"El cliente '{cliente.nombre}' tiene reservas activas ({ids}). "
                f"Cancélalas antes de eliminar el cliente."
            )

        self._clientes.remove(cliente)
        self._log.advertencia(
            f"Cliente eliminado: {cliente.nombre}",
            f"ID: {id_cliente}"
        )
        return True

    def eliminar_todos_los_clientes(self) -> int:
        """
        Elimina todos los clientes que NO tengan reservas activas.
        Retorna el número de clientes eliminados.
        """
        eliminados = 0
        # Iteramos sobre una copia para poder modificar la lista original
        for cliente in self._clientes.copy():
            reservas_activas = [
                r for r in self._reservas
                if r.cliente.id == cliente.id
                and r.estado.value in ("Pendiente", "Confirmada")
            ]
            if not reservas_activas:
                self._clientes.remove(cliente)
                eliminados += 1

        self._log.advertencia(
            f"Eliminación masiva de clientes.",
            f"Clientes eliminados: {eliminados}"
        )
        return eliminados

    # --- Servicios ---

    def agregar_servicio(self, servicio) -> bool:
        """Registra un servicio en el catálogo del sistema."""
        # --- Registro simple con log ---
        try:
            self._servicios.append(servicio)
            self._log.info(f"Servicio registrado: {servicio}")
            return True
        except Exception as e:
            # --- Registro de error inesperado ---
            self._log.error("No se pudo registrar el servicio.", str(e))
            raise

    def buscar_servicio_por_id(self, id_servicio: str):
        """Busca un servicio por ID. Retorna None si no existe."""
        # --- Busqueda lineal ---
        for s in self._servicios:
            if s.id == id_servicio:
                return s
        return None

    def listar_servicios(self) -> list:
        """Retorna una copia del catálogo de servicios."""
        # --- Copia defensiva ---
        return self._servicios.copy()

    # --- Reservas ---

    def agregar_reserva(self, reserva) -> bool:
        """Registra una reserva en el sistema."""
        # --- Registro simple con log ---
        try:
            self._reservas.append(reserva)
            self._log.info(f"Reserva registrada: {reserva}")
            return True
        except Exception as e:
            # --- Registro de error inesperado ---
            self._log.error("No se pudo registrar la reserva.", str(e))
            raise

    def buscar_reserva_por_id(self, id_reserva: str):
        """Busca una reserva por ID. Retorna None si no existe."""
        # --- Busqueda lineal ---
        for r in self._reservas:
            if r.id == id_reserva:
                return r
        return None

    def listar_reservas(self) -> list:
        """Retorna una copia de la lista de reservas."""
        # --- Copia defensiva ---
        return self._reservas.copy()

    # --- Estadísticas ---

    def resumen(self) -> dict:
        """Retorna estadísticas generales del sistema para la UI."""
        # --- Conteos basicos ---
        return {
            "clientes": len(self._clientes),
            "servicios": len(self._servicios),
            "reservas": len(self._reservas),
        }