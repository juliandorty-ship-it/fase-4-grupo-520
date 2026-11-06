"""Reserva de Software FJ: une cliente, servicio, duración y estado."""

from entidades import Cliente, EntidadBase
from excepciones import (
    CalculoInconsistenteError,
    OperacionNoPermitidaError,
    ReservaInvalidaError,
    SoftwareFJError,
)
from logger import registrar_error, registrar_evento
from servicios import IVA, AlquilerEquipo, ReservaSala, Servicio


class Reserva(EntidadBase):
    """Reserva de un servicio hecha por un cliente."""

    def __init__(self, identificador, cliente, servicio, horas):
        # Inicializa la parte heredada (identificador)
        super().__init__(identificador)
        # El cliente debe ser un objeto Cliente
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("La reserva requiere un cliente válido")
        # El servicio debe ser un objeto Servicio
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("La reserva requiere un servicio válido")
        try:
            # El propio servicio valida la duración según sus reglas
            horas = servicio.validar_parametros(horas)
        except SoftwareFJError as e:
            # Encadenamiento: conserva el error original como causa
            raise ReservaInvalidaError("Duración inválida para la reserva") from e
        self._cliente = cliente
        self._servicio = servicio
        self._horas = horas
        # Toda reserva nueva empieza pendiente
        self._estado = "pendiente"

    @property
    def cliente(self):
        return self._cliente

    @property
    def servicio(self):
        return self._servicio

    @property
    def horas(self):
        return self._horas

    @property
    def estado(self):
        return self._estado

    def confirmar(self):
        """Confirma la reserva si la operación está permitida."""
        if self._estado == "cancelada":
            raise OperacionNoPermitidaError(
                "No se puede confirmar una reserva cancelada"
            )
        if self._estado == "confirmada":
            raise OperacionNoPermitidaError("La reserva ya está confirmada")
        # Lanza ServicioNoDisponibleError si el servicio no está disponible
        self._servicio.verificar_disponibilidad()
        self._estado = "confirmada"

    def cancelar(self):
        """Cancela la reserva si la operación está permitida."""
        if self._estado == "cancelada":
            raise OperacionNoPermitidaError("La reserva ya está cancelada")
        self._estado = "cancelada"

    def calcular_costo(self, impuesto=IVA, descuento=0.0):
        """Costo de la reserva. Sobrecarga con impuesto y descuento opcionales."""
        try:
            return self._servicio.calcular_costo_total(
                self._horas, impuesto, descuento
            )
        except CalculoInconsistenteError as e:
            raise ReservaInvalidaError(
                "No se pudo calcular el costo de la reserva"
            ) from e

    def procesar(self):
        """Confirma la reserva con try/except/else/finally. Devuelve True o False."""
        try:
            # Intenta confirmar la reserva
            self.confirmar()
        except SoftwareFJError as e:
            # Si falla, registra el error y la aplicación sigue activa
            registrar_error(f"Reserva {self.identificador} fallida", e)
            return False
        else:
            # Solo se ejecuta si no hubo error
            costo = self.calcular_costo()
            registrar_evento(
                f"Reserva {self.identificador} confirmada. Costo total: {costo}"
            )
            return True
        finally:
            # Se ejecuta siempre, haya o no error
            registrar_evento(
                f"Procesamiento de la reserva {self.identificador} finalizado "
                f"(estado: {self._estado})"
            )

    def describir(self):
        """Implementación del método abstracto de EntidadBase."""
        return (
            f"Reserva {self.identificador}: {self._cliente.nombre} -> "
            f"{self._servicio.nombre} | {self._horas} horas | "
            f"Estado: {self._estado}"
        )


# Prueba rápida: solo se ejecuta si corres este archivo directamente
if __name__ == "__main__":
    cliente = Cliente("C001", "Ana Pérez", "ana@correo.com", "3001234567")
    sala = ReservaSala("S001", "Sala Ejecutiva", 50000, 10)
    equipo = AlquilerEquipo("E001", "Proyector", 20000, 2)

    # Caso 1: reserva exitosa
    reserva1 = Reserva("R001", cliente, sala, 3)
    print(reserva1.describir())
    print(f"Procesada: {reserva1.procesar()}")
    print(reserva1.describir())
    print(f"Costo con IVA: {reserva1.calcular_costo()}")
    print(f"Costo con 10% de descuento: {reserva1.calcular_costo(descuento=0.10)}")

    # Caso 2: procesar de nuevo una reserva ya confirmada
    print(f"Procesada de nuevo: {reserva1.procesar()}")

    # Caso 3: cancelar, y luego intentar cancelar y procesar otra vez
    reserva1.cancelar()
    print(reserva1.describir())
    try:
        reserva1.cancelar()
    except SoftwareFJError as e:
        registrar_error("Error al cancelar", e)
        print(f"Error capturado: {e.mensaje}")
    print(f"Procesar una reserva cancelada: {reserva1.procesar()}")

    # Caso 4: duración inválida (una sala permite máximo 8 horas)
    try:
        Reserva("R002", cliente, sala, 12)
    except SoftwareFJError as e:
        registrar_error("Error al crear reserva", e)
        print(f"Error capturado: {e.mensaje}")

    # Caso 5: servicio no disponible
    equipo.disponible = False
    reserva3 = Reserva("R003", cliente, equipo, 4)
    print(f"Procesada: {reserva3.procesar()}")

    # Caso 6: cliente inválido
    try:
        Reserva("R004", None, sala, 2)
    except SoftwareFJError as e:
        registrar_error("Error al crear reserva", e)
        print(f"Error capturado: {e.mensaje}")