"""
main.py — versión final
Punto de entrada de la aplicación Software FJ.
"""

# --- Dependencias estandar ---
import sys
import os

# --- Configuracion del path para imports locales ---
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# --- Dependencias internas ---
from ui.ventana_principal import VentanaPrincipal
from utils.logger import Logger


def main():
    # --- Arranque de servicios base ---
    log = Logger()
    log.info("=" * 55)
    log.info("Software FJ — Iniciando aplicación (Fase 4 completa)")
    log.info("=" * 55)

    # --- Ejecucion de la interfaz ---
    try:
        app = VentanaPrincipal()
        app.ejecutar()

    # --- Cierre controlado por el usuario ---
    except KeyboardInterrupt:
        log.advertencia("Aplicación cerrada por el usuario (KeyboardInterrupt).")

    # --- Manejo de fallos inesperados ---
    except Exception as e:
        log.critico("La aplicación terminó con un error fatal.", str(e))
        raise

    # --- Cierre ordenado ---
    finally:
        log.info("Sesión finalizada.")


if __name__ == "__main__":
    main()