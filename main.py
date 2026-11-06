"""Programa principal de Software FJ: simula 15 operaciones del sistema."""

from entidades import Cliente
from excepciones import ReservaInvalidaError, SoftwareFJError
from logger import registrar_error, registrar_evento
from reserva import Reserva
from servicios import AlquilerEquipo, AsesoriaEspecializada, ReservaSala

# Listas internas: reemplazan la base de datos
clientes = []
servicios = []
reservas = []


def ejecutar_operacion(numero, descripcion, accion):
    """Ejecuta una operación sin que un error detenga el programa."""
    print(f"\n--- Operación {numero}: {descripcion} ---")
    registrar_evento(f"Inicio de la operación {numero}: {descripcion}")
    try:
        # Intenta ejecutar la operación
        resultado = accion()
    except SoftwareFJError as e:
        # Error propio del sistema: se registra y el programa continúa
        registrar_error(f"Operación {numero} fallida", e)
        print(f"ERROR controlado: {e.mensaje}")
        # Si la excepción fue encadenada, muestra la causa original
        if e.__cause__ is not None:
            print(f"  Causa original: {type(e.__cause__).__name__}: {e.__cause__}")
    except Exception as e:
        # Error inesperado: también se registra y el programa continúa
        registrar_error(f"Operación {numero}: error inesperado", e)
        print(f"ERROR inesperado: {e}")
    else:
        # Solo se ejecuta si no hubo error
        registrar_evento(f"Operación {numero} exitosa")
        print(f"OK: {resultado}")
    finally:
        # Se ejecuta siempre
        registrar_evento(f"Fin de la operación {numero}")


# ---------- Clientes ----------
def op_cliente_valido():
    cliente = Cliente("C001", "Ana Pérez", "ana@correo.com", "3001234567")
    clientes.append(cliente)
    return cliente.describir()


def op_cliente_correo_invalido():
    cliente = Cliente("C002", "Luis Gómez", "luis#correo", "3109876543")
    clientes.append(cliente)
    return cliente.describir()


def op_cliente_telefono_invalido():
    cliente = Cliente("C003", "Marta Ruiz", "marta@correo.com", "abc123")
    clientes.append(cliente)
    return cliente.describir()


def op_cliente_sin_nombre():
    cliente = Cliente("C004", "", "pedro@correo.com", "3001112233")
    clientes.append(cliente)
    return cliente.describir()


# ---------- Servicios ----------
def op_crear_sala():
    servicio = ReservaSala("S001", "Sala Ejecutiva", 50000, 10)
    servicios.append(servicio)
    return servicio.describir()


def op_crear_equipo():
    servicio = AlquilerEquipo("E001", "Proyector", 20000, 2)
    servicios.append(servicio)
    return servicio.describir()


def op_crear_asesoria():
    servicio = AsesoriaEspecializada("A001", "Asesoría en redes", 80000, "senior")
    servicios.append(servicio)
    return servicio.describir()


def op_servicio_tarifa_invalida():
    servicio = ReservaSala("S002", "Sala Pequeña", -100, 5)
    servicios.append(servicio)
    return servicio.describir()


def op_servicio_nivel_invalido():
    servicio = AsesoriaEspecializada("A002", "Asesoría básica", 60000, "experto")
    servicios.append(servicio)
    return servicio.describir()


# ---------- Reservas ----------
def op_reserva_exitosa():
    reserva = Reserva("R001", clientes[0], servicios[0], 3)
    reservas.append(reserva)
    # procesar() devuelve False si falla; en ese caso se lanza un error
    if not reserva.procesar():
        raise ReservaInvalidaError("No se pudo procesar la reserva R001")
    return f"{reserva.describir()} | Costo total: {reserva.calcular_costo()}"


def op_reserva_duracion_invalida():
    # Una sala permite máximo 8 horas
    reserva = Reserva("R002", clientes[0], servicios[0], 12)
    reservas.append(reserva)
    return reserva.describir()


def op_reserva_servicio_no_disponible():
    equipo = servicios[1]
    # Se marca el proyector como no disponible
    equipo.disponible = False
    reserva = Reserva("R003", clientes[0], equipo, 4)
    reservas.append(reserva)
    # Al confirmar, lanza ServicioNoDisponibleError
    reserva.confirmar()
    return reserva.describir()


def op_cancelar_dos_veces():
    reserva = reservas[0]
    reserva.cancelar()
    print(f"  Primera cancelación: estado = {reserva.estado}")
    # La segunda cancelación lanza OperacionNoPermitidaError
    reserva.cancelar()
    return reserva.describir()


# ---------- Cálculos ----------
def op_calculo_con_sobrecarga():
    sala = servicios[0]
    con_iva = sala.calcular_costo_total(3)
    con_descuento = sala.calcular_costo_total(3, descuento=0.10)
    con_ambos = sala.calcular_costo_total(3, impuesto=0.05, descuento=0.10)
    return (
        f"Costo con IVA: {con_iva} | Con 10% de descuento: {con_descuento} | "
        f"Con 5% de impuesto y 10% de descuento: {con_ambos}"
    )


def op_calculo_inconsistente():
    # Un descuento de 150 % es inconsistente
    return servicios[0].calcular_costo_total(3, descuento=1.5)


def main():
    # Lista de operaciones: (número, descripción, función)
    operaciones = [
        (1, "Registrar cliente válido", op_cliente_valido),
        (2, "Registrar cliente con correo inválido", op_cliente_correo_invalido),
        (3, "Registrar cliente con teléfono inválido", op_cliente_telefono_invalido),
        (4, "Registrar cliente sin nombre", op_cliente_sin_nombre),
        (5, "Crear servicio: reserva de sala", op_crear_sala),
        (6, "Crear servicio: alquiler de equipo", op_crear_equipo),
        (7, "Crear servicio: asesoría especializada", op_crear_asesoria),
        (8, "Crear servicio con tarifa inválida", op_servicio_tarifa_invalida),
        (9, "Crear asesoría con nivel inválido", op_servicio_nivel_invalido),
        (10, "Reserva exitosa", op_reserva_exitosa),
        (11, "Reserva con duración inválida", op_reserva_duracion_invalida),
        (12, "Reserva con servicio no disponible", op_reserva_servicio_no_disponible),
        (13, "Cancelar una reserva dos veces", op_cancelar_dos_veces),
        (14, "Cálculo de costos con sobrecarga", op_calculo_con_sobrecarga),
        (15, "Cálculo inconsistente", op_calculo_inconsistente),
    ]

    registrar_evento("Inicio de la simulación de Software FJ")
    for numero, descripcion, accion in operaciones:
        ejecutar_operacion(numero, descripcion, accion)

    # Resumen final
    print("\n========== RESUMEN ==========")
    print(f"Clientes registrados: {len(clientes)}")
    print(f"Servicios creados: {len(servicios)}")
    print(f"Reservas registradas: {len(reservas)}")
    for reserva in reservas:
        print(reserva.describir())
    registrar_evento("Fin de la simulación de Software FJ")
    print("El programa terminó sin interrupciones.")


# El programa arranca solo si se ejecuta este archivo directamente
if __name__ == "__main__":
    main()