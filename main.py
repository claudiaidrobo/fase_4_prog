"""
main.py
Punto de entrada de la aplicación Software FJ.
Inicializa el sistema y arranca la interfaz gráfica Tkinter.
"""

import sys
import os

# --- Configuracion del entorno de imports ---
# Aseguramos que el directorio raiz este en el path de Python
# para que los imports relativos funcionen correctamente.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# --- Dependencias internas ---
from ui.ventana_principal import VentanaPrincipal
from utils.logger import Logger


def main():
    """Funcion principal: inicializa el logger y arranca la UI."""
    # --- Arranque de servicios base ---
    log = Logger()
    log.info("=" * 50)
    log.info("Iniciando aplicación Software FJ — Fase 1")
    log.info("=" * 50)

    # --- Ejecucion de la interfaz ---
    try:
        app = VentanaPrincipal()
        app.ejecutar()
    except Exception as e:
        # --- Manejo de fallos inesperados ---
        log.critico("La aplicación terminó con un error inesperado.", str(e))
        raise
    finally:
        # --- Cierre ordenado ---
        log.info("Aplicación cerrada.")


if __name__ == "__main__":
    main()