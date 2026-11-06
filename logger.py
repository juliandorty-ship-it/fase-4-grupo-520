"""Registro de eventos y errores del sistema Software FJ."""

import logging  # Módulo estándar de Python para registrar mensajes
import os  # Módulo para trabajar con rutas de archivos

# Ruta del archivo de logs: queda en la misma carpeta que este archivo
RUTA_LOGS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs.txt")

# Crea un logger con nombre propio para el sistema
logger = logging.getLogger("software_fj")
# Nivel mínimo de mensajes que se registrarán (INFO y superiores)
logger.setLevel(logging.INFO)

# Evita agregar el manejador dos veces si el módulo se importa varias veces
if not logger.handlers:
    # Manejador que escribe los mensajes en el archivo logs.txt
    manejador = logging.FileHandler(RUTA_LOGS, encoding="utf-8")
    # Formato de cada línea: fecha y hora | nivel | mensaje
    formato = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    # Asocia el formato al manejador
    manejador.setFormatter(formato)
    # Conecta el manejador al logger
    logger.addHandler(manejador)


def registrar_evento(mensaje):
    """Registra un evento normal (operación exitosa, información)."""
    logger.info(mensaje)


def registrar_error(mensaje, error=None):
    """Registra un error. Si se pasa la excepción, guarda su tipo y su causa."""
    if error is not None:
        # Registra el mensaje junto con el tipo de excepción y su texto
        logger.error("%s | %s: %s", mensaje, type(error).__name__, error)
        # Si la excepción fue encadenada (raise ... from ...), registra la causa
        if error.__cause__ is not None:
            logger.error(
                "Causa original: %s: %s",
                type(error.__cause__).__name__,
                error.__cause__,
            )
    else:
        # Si no hay excepción, registra solo el mensaje
        logger.error(mensaje)


# Prueba rápida: solo se ejecuta si corres este archivo directamente
if __name__ == "__main__":
    registrar_evento("Sistema iniciado")
    try:
        # Provoca un error a propósito (división por cero)
        resultado = 10 / 0
    except ZeroDivisionError as e:
        registrar_error("Fallo en prueba de cálculo", e)
    print("Prueba terminada. Revisa el archivo logs.txt")