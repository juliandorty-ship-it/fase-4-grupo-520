"""Excepciones personalizadas del sistema Software FJ."""


class SoftwareFJError(Exception):
    """Excepción base: todas las demás excepciones del sistema heredan de ella."""

    def __init__(self, mensaje):
        # Llama al constructor de Exception para guardar el mensaje
        super().__init__(mensaje)
        # Guarda el mensaje en un atributo para poder leerlo después
        self.mensaje = mensaje


class ClienteInvalidoError(SoftwareFJError):
    """Se lanza cuando los datos de un cliente no son válidos."""


class ParametroFaltanteError(SoftwareFJError):
    """Se lanza cuando falta un parámetro obligatorio."""


class ServicioNoDisponibleError(SoftwareFJError):
    """Se lanza cuando un servicio no está disponible para reservar."""


class ServicioInvalidoError(SoftwareFJError):
    """Se lanza cuando los parámetros de un servicio son incorrectos."""


class ReservaInvalidaError(SoftwareFJError):
    """Se lanza cuando una reserva no se puede crear o procesar."""


class OperacionNoPermitidaError(SoftwareFJError):
    """Se lanza cuando se intenta una operación no permitida (ej. cancelar una reserva ya cancelada)."""


class CalculoInconsistenteError(SoftwareFJError):
    """Se lanza cuando un cálculo de costos da un resultado inconsistente."""


# Prueba rápida: solo se ejecuta si corres este archivo directamente
if __name__ == "__main__":
    try:
        # Lanza una excepción personalizada a propósito
        raise ClienteInvalidoError("Correo electrónico inválido")
    except SoftwareFJError as e:
        # Captura con la clase base y muestra el mensaje
        print(f"Error capturado: {e.mensaje}")