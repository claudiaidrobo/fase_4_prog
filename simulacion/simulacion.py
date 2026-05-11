"""
simulacion.py
Ejecuta las 10 operaciones requeridas por el enunciado de forma automática.
Mezcla registros válidos e inválidos para demostrar el manejo de excepciones.
"""

# --- Dependencias internas ---
from core.cliente import Cliente
from core.excepciones import (
    ClienteInvalidoError,
    ClienteNoEncontradoError,
    ReservaInvalidaError,
    ReservaNoEncontradaError,
    OperacionNoPermitidaError,
    ServicioNoDisponibleError,
)
from utils.gestor import Gestor
from utils.logger import Logger
from utils.gestor_reservas import GestorReservas


class Simulacion:
    """
    Ejecuta 10 operaciones predefinidas sobre el sistema y retorna
    un reporte con el resultado de cada una.
    Cada operación está documentada con su intención y resultado esperado.
    """

    def __init__(self, gestor: Gestor, log: Logger):
        # --- Servicios compartidos ---
        self._gestor = gestor
        self._log = log
        self._gestor_reservas = GestorReservas(gestor, log)
        # --- Buffer de resultados ---
        self._resultados: list[dict] = []

    def ejecutar(self) -> list[dict]:
        """
        Corre las 10 operaciones en secuencia.
        Retorna la lista de resultados para mostrar en la UI.
        """
        # --- Preparacion ---
        self._resultados.clear()
        self._log.info("=" * 55)
        self._log.info("INICIO DE SIMULACIÓN — 10 operaciones")
        self._log.info("=" * 55)

        # --- Ejecucion secuencial de operaciones ---
        self._op01_cliente_valido()
        self._op02_cliente_valido()
        self._op03_cliente_email_invalido()
        self._op04_cliente_nombre_invalido()
        self._op05_reserva_valida_sala()
        self._op06_reserva_valida_equipo()
        self._op07_reserva_cliente_inexistente()
        self._op08_reserva_confirmada_y_procesada()
        self._op09_cancelar_reserva_ya_procesada()
        self._op10_reserva_horas_invalidas()

        # --- Resumen final ---
        self._log.info("=" * 55)
        self._log.info(f"SIMULACIÓN COMPLETADA — {len(self._resultados)} operaciones")
        exitos  = sum(1 for r in self._resultados if r["exito"])
        fallos  = len(self._resultados) - exitos
        self._log.info(f"Exitosas: {exitos} | Con error controlado: {fallos}")
        self._log.info("=" * 55)

        return self._resultados

    # ---------------------------------------------------------------
    # Operaciones individuales
    # ---------------------------------------------------------------

    def _op01_cliente_valido(self):
        """OP-01: Registrar un cliente con datos correctos. Debe tener éxito."""
        # --- Caso feliz de cliente ---
        op = "OP-01"
        descripcion = "Registrar cliente válido (Ana Torres)"
        try:
            cliente = Cliente("Ana Torres", "ana.torres@email.com", "3001234567",
                              id_cliente="CLI-001")
            self._gestor.agregar_cliente(cliente)
            self._ok(op, descripcion, f"Cliente registrado: {cliente.id}")

        except Exception as e:
            self._fallo(op, descripcion, str(e))

    def _op02_cliente_valido(self):
        """OP-02: Registrar un segundo cliente válido. Debe tener éxito."""
        # --- Segundo caso feliz de cliente ---
        op = "OP-02"
        descripcion = "Registrar cliente válido (Carlos Ruiz)"
        try:
            cliente = Cliente("Carlos Ruiz", "carlos.ruiz@empresa.co", "3109876543",
                              id_cliente="CLI-002")
            self._gestor.agregar_cliente(cliente)
            self._ok(op, descripcion, f"Cliente registrado: {cliente.id}")

        except Exception as e:
            self._fallo(op, descripcion, str(e))

    def _op03_cliente_email_invalido(self):
        """OP-03: Intentar registrar un cliente con email malformado.
        Debe lanzar ClienteInvalidoError y ser capturado."""
        # --- Validacion de email ---
        op = "OP-03"
        descripcion = "Registrar cliente con email inválido (esperado: error)"
        try:
            # 'correo-sin-arroba.com' no cumple el patrón de email
            cliente = Cliente("Luis Pérez", "correo-sin-arroba.com", "3201111111",
                              id_cliente="CLI-003")
            self._gestor.agregar_cliente(cliente)
            # Si llegamos aquí, la validación no funcionó
            self._fallo(op, descripcion, "La validación NO detectó el email inválido.")

        except ClienteInvalidoError as e:
            # Este es el comportamiento esperado
            self._log.error(f"[{op}] Excepción capturada correctamente.", str(e))
            self._ok(op, descripcion,
                     f"ClienteInvalidoError capturada: {e}", esperaba_error=True)

        except Exception as e:
            self._fallo(op, descripcion, f"Excepción inesperada: {e}")

    def _op04_cliente_nombre_invalido(self):
        """OP-04: Intentar registrar un cliente con nombre de 1 carácter.
        Debe lanzar ClienteInvalidoError."""
        # --- Validacion de nombre ---
        op = "OP-04"
        descripcion = "Registrar cliente con nombre muy corto (esperado: error)"
        try:
            cliente = Cliente("X", "x.valido@email.com", "3001112233",
                              id_cliente="CLI-004")
            self._gestor.agregar_cliente(cliente)
            self._fallo(op, descripcion, "La validación NO detectó el nombre inválido.")

        except ClienteInvalidoError as e:
            self._log.error(f"[{op}] Excepción capturada correctamente.", str(e))
            self._ok(op, descripcion,
                     f"ClienteInvalidoError capturada: {e}", esperaba_error=True)

        except Exception as e:
            self._fallo(op, descripcion, f"Excepción inesperada: {e}")

    def _op05_reserva_valida_sala(self):
        """OP-05: Crear y confirmar una reserva de sala válida para CLI-001.
        Debe calcular el costo correctamente."""
        # --- Reserva valida de sala ---
        op = "OP-05"
        descripcion = "Crear y confirmar reserva de Sala Amazonas para Ana Torres"
        try:
            reserva = self._gestor_reservas.crear_reserva(
                "CLI-001", "SALA-01", horas=3,
                impuesto=0.19, descuento=0.0, audiovisual=True
            )
            costo = self._gestor_reservas.confirmar_reserva(reserva.id)
            self._ok(op, descripcion,
                     f"Reserva {reserva.id} confirmada. Costo: ${costo:,.2f} COP")

        except Exception as e:
            self._fallo(op, descripcion, str(e))

    def _op06_reserva_valida_equipo(self):
        """OP-06: Crear una reserva de equipo para CLI-002 con soporte técnico."""
        # --- Reserva valida de equipo ---
        op = "OP-06"
        descripcion = "Crear reserva de Laptop HP para Carlos Ruiz (con soporte)"
        try:
            reserva = self._gestor_reservas.crear_reserva(
                "CLI-002", "EQ-01", horas=8,
                impuesto=0.19, descuento=0.05,
                cantidad=2, con_soporte=True
            )
            costo = self._gestor_reservas.confirmar_reserva(reserva.id)
            self._ok(op, descripcion,
                     f"Reserva {reserva.id} confirmada. Costo: ${costo:,.2f} COP")

        except Exception as e:
            self._fallo(op, descripcion, str(e))

    def _op07_reserva_cliente_inexistente(self):
        """OP-07: Intentar crear una reserva con un ID de cliente que no existe.
        Debe lanzar ClienteNoEncontradoError."""
        # --- Error esperado: cliente inexistente ---
        op = "OP-07"
        descripcion = "Crear reserva con cliente inexistente (esperado: error)"
        try:
            self._gestor_reservas.crear_reserva(
                "CLI-999", "SALA-01", horas=2,
                impuesto=0.19
            )
            self._fallo(op, descripcion,
                        "No se lanzó excepción con cliente inexistente.")

        except ClienteNoEncontradoError as e:
            self._log.error(f"[{op}] Excepción capturada correctamente.", str(e))
            self._ok(op, descripcion,
                     f"ClienteNoEncontradoError capturada: {e}", esperaba_error=True)

        except Exception as e:
            self._fallo(op, descripcion, f"Excepción inesperada: {e}")

    def _op08_reserva_confirmada_y_procesada(self):
        """OP-08: Ciclo completo — crear, confirmar y procesar una reserva
        de asesoría para CLI-001."""
        # --- Ciclo completo de reserva ---
        op = "OP-08"
        descripcion = "Ciclo completo: crear → confirmar → procesar asesoría legal"
        try:
            reserva = self._gestor_reservas.crear_reserva(
                "CLI-001", "AS-01", horas=2,
                impuesto=0.19, descuento=0.0,
                presencial=True, num_sesiones=1
            )
            costo = self._gestor_reservas.confirmar_reserva(reserva.id)
            self._gestor_reservas.procesar_reserva(reserva.id)
            self._ok(op, descripcion,
                     f"Reserva {reserva.id} procesada. Costo: ${costo:,.2f} COP")

        except Exception as e:
            self._fallo(op, descripcion, str(e))

    def _op09_cancelar_reserva_ya_procesada(self):
        """OP-09: Intentar cancelar una reserva que ya fue procesada (OP-08).
        Debe lanzar OperacionNoPermitidaError (encadenamiento de excepciones)."""
        # --- Error esperado: cancelar procesada ---
        op = "OP-09"
        descripcion = "Cancelar reserva ya procesada (esperado: error)"

        # Buscamos la reserva procesada de OP-08 (la ultima del gestor)
        reservas = self._gestor.listar_reservas()
        reserva_procesada = next(
            (r for r in reversed(reservas)
             if r.estado.value == "Procesada"), None
        )

        if not reserva_procesada:
            self._fallo(op, descripcion,
                        "No se encontró reserva procesada para esta prueba.")
            return

        try:
            self._gestor_reservas.cancelar_reserva(
                reserva_procesada.id, "Intento de cancelación indebida"
            )
            self._fallo(op, descripcion,
                        "No se lanzó excepción al cancelar una reserva PROCESADA.")

        except OperacionNoPermitidaError as e:
            # Verificamos si hay causa encadenada
            causa = e.__cause__
            detalle = f"{e}"
            if causa:
                detalle += f" | Causa original: {causa}"
            self._log.error(f"[{op}] Excepción capturada correctamente.", detalle)
            self._ok(op, descripcion,
                     f"OperacionNoPermitidaError capturada: {e}",
                     esperaba_error=True)

        except Exception as e:
            self._fallo(op, descripcion, f"Excepción inesperada: {e}")

    def _op10_reserva_horas_invalidas(self):
        """OP-10: Intentar crear una reserva con horas negativas.
        Debe lanzar ReservaInvalidaError."""
        # --- Error esperado: horas invalidas ---
        op = "OP-10"
        descripcion = "Crear reserva con horas negativas (esperado: error)"
        try:
            self._gestor_reservas.crear_reserva(
                "CLI-002", "EQ-02", horas=-5,
                impuesto=0.19
            )
            self._fallo(op, descripcion,
                        "No se lanzó excepción con horas negativas.")

        except (ReservaInvalidaError, ServicioNoDisponibleError) as e:
            self._log.error(f"[{op}] Excepción capturada correctamente.", str(e))
            self._ok(op, descripcion,
                     f"Excepción capturada correctamente: {e}",
                     esperaba_error=True)

        except Exception as e:
            self._fallo(op, descripcion, f"Excepción inesperada: {e}")

    # ---------------------------------------------------------------
    # Helpers internos
    # ---------------------------------------------------------------

    def _ok(self, op: str, descripcion: str, detalle: str,
            esperaba_error: bool = False):
        """Registra una operación exitosa (o error esperado y bien capturado)."""
        # --- Registro de resultado exitoso ---
        self._log.info(
            f"[{op}] {'ERROR CONTROLADO' if esperaba_error else 'ÉXITO'}: {descripcion}",
            detalle
        )
        self._resultados.append({
            "op":           op,
            "descripcion":  descripcion,
            "exito":        True,
            "esperaba_error": esperaba_error,
            "detalle":      detalle,
        })

    def _fallo(self, op: str, descripcion: str, detalle: str):
        """Registra una operación que falló de forma inesperada."""
        # --- Registro de fallo inesperado ---
        self._log.critico(
            f"[{op}] FALLO INESPERADO: {descripcion}",
            detalle
        )
        self._resultados.append({
            "op":           op,
            "descripcion":  descripcion,
            "exito":        False,
            "esperaba_error": False,
            "detalle":      detalle,
        })