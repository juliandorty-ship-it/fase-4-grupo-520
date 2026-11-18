"""Simulación de Software FJ: ejecuta 10 simulaciones (5 válidas y 5 no válidas)."""

from cliente import Cliente  # Clase Cliente con validaciones
from excepciones import ReservaInvalidaError, SoftwareFJError  # Excepción base y de reserva
from logger_config import RUTA_LOGS, registrar_error, registrar_evento  # Funciones del archivo de logs
from reserva import Reserva  # Clase Reserva (confirmar, cancelar, procesar)
from servicio import AlquilerEquipo, AsesoriaEspecializada, ReservaSala  # Los tres servicios

# Listas internas: reemplazan la base de datos (no se usa ningún motor de datos)
clientes = []  # Aquí se guardan los clientes registrados
servicios = []  # Aquí se guardan los servicios creados
reservas = []  # Aquí se guardan las reservas realizadas

# Tipos de simulación: se usan para decidir si se espera éxito o error
VALIDA = "VÁLIDA"  # La operación debe terminar bien
NO_VALIDA = "NO VÁLIDA"  # La operación debe terminar con un error controlado


def ejecutar_simulacion(numero, tipo, descripcion, accion):
    """Ejecuta una simulación sin que un error detenga el programa.

    Devuelve True si el resultado fue el esperado y False si no.
    """
    # Muestra el encabezado de la simulación en pantalla
    print(f"\n--- Simulación {numero} [{tipo}]: {descripcion} ---")
    # Deja constancia en el log de que la simulación empezó
    registrar_evento(f"Inicio de la simulación {numero} [{tipo}]: {descripcion}")
    # Variable que guardará qué ocurrió realmente
    obtenido = ""
    try:
        # Intenta ejecutar la operación (la función 'accion' recibida)
        resultado = accion()
    except SoftwareFJError as e:
        # Error propio del sistema: se registra y el programa continúa
        registrar_error(f"Simulación {numero} con error controlado", e)
        # Muestra el mensaje del error en pantalla
        print(f"ERROR controlado: {e.mensaje}")
        # Si la excepción fue encadenada (raise ... from ...), muestra su causa
        if e.__cause__ is not None:
            print(f"  Causa original: {type(e.__cause__).__name__}: {e.__cause__}")
        # Guarda el resultado obtenido
        obtenido = "error controlado"
    except Exception as e:
        # Error inesperado (no es de Software FJ): también se registra y se continúa
        registrar_error(f"Simulación {numero}: error inesperado", e)
        # Muestra el error en pantalla
        print(f"ERROR inesperado: {e}")
        # Guarda el resultado obtenido
        obtenido = "error inesperado"
    else:
        # Solo se ejecuta si no hubo ninguna excepción
        registrar_evento(f"Simulación {numero} exitosa")
        # Muestra el resultado de la operación
        print(f"OK: {resultado}")
        # Guarda el resultado obtenido
        obtenido = "exitosa"
    finally:
        # Se ejecuta siempre, haya o no error
        registrar_evento(f"Fin de la simulación {numero}")

    # Resultado esperado: éxito si es válida, error controlado si no es válida
    esperado = "exitosa" if tipo == VALIDA else "error controlado"
    # Compara lo esperado con lo obtenido
    cumplida = obtenido == esperado
    # Deja en el log si la simulación se comportó como se esperaba
    registrar_evento(
        f"Simulación {numero}: esperado = {esperado}, obtenido = {obtenido}, "
        f"{'CUMPLIDA' if cumplida else 'NO CUMPLIDA'}"
    )
    # Devuelve si se cumplió lo esperado
    return cumplida


# ====================== SIMULACIONES VÁLIDAS ======================
def sim_registrar_cliente():
    """Válida 1: registra un cliente con datos correctos."""
    # Crea el cliente (se ejecutan las validaciones de nombre, correo y documento)
    cliente = Cliente("Carlos Ramírez", "1020304050", "carlos.ramirez@correo.com")
    # Lo guarda en la lista interna de clientes
    clientes.append(cliente)
    # Registra el evento en el log
    registrar_evento(f"Cliente registrado: {cliente.identificador}")
    # Devuelve la descripción para mostrarla en pantalla
    return cliente.describir()


def sim_crear_servicios():
    """Válida 2: crea los tres tipos de servicio con datos correctos."""
    # Servicio 1: reserva de sala con capacidad para 12 personas
    sala = ReservaSala("S101", "Sala de Juntas", 60000, 12)
    # Servicio 2: alquiler de 3 portátiles
    equipo = AlquilerEquipo("E101", "Portátil", 25000, 3)
    # Servicio 3: asesoría con un asesor senior
    asesoria = AsesoriaEspecializada("A101", "Asesoría en ciberseguridad", 90000, "senior")
    # Guarda los tres servicios en la lista interna
    servicios.extend([sala, equipo, asesoria])
    # Registra el evento en el log
    registrar_evento("Servicios creados: S101, E101, A101")
    # Muestra la descripción de cada servicio (polimorfismo: mismo método, distinto resultado)
    return " || ".join(servicio.describir() for servicio in servicios)


def sim_reserva_exitosa():
    """Válida 3: crea y procesa una reserva correcta."""
    # Crea una reserva de 4 horas para la sala (el rango permitido es de 1 a 8 horas)
    reserva = Reserva("R101", clientes[0], servicios[0], 4)
    # Guarda la reserva en la lista interna
    reservas.append(reserva)
    # procesar() devuelve False si falla; en ese caso se lanza un error propio
    if not reserva.procesar():
        raise ReservaInvalidaError("No se pudo procesar la reserva R101")
    # Devuelve la descripción y el costo total con IVA
    return f"{reserva.describir()} | Costo total: {reserva.calcular_costo()}"


def sim_calculo_de_costos():
    """Válida 4: calcula costos con polimorfismo y con las variantes de la sobrecarga."""
    # Lista de pares (servicio, horas) con horas válidas para cada tipo de servicio
    casos = [(servicios[0], 2), (servicios[1], 5), (servicios[2], 3)]
    # Lista donde se guardan los textos de resultado
    partes = []
    # Recorre los tres servicios con el mismo código (polimorfismo)
    for servicio, horas in casos:
        # Costo con el impuesto por defecto (IVA)
        costo = servicio.calcular_costo_total(horas)
        # Agrega el resultado al texto
        partes.append(f"{servicio.nombre} ({horas} h): {costo}")
    # Variante con descuento del 10 %
    con_descuento = servicios[0].calcular_costo_total(2, descuento=0.10)
    # Variante con impuesto del 5 % y descuento del 10 %
    con_ambos = servicios[0].calcular_costo_total(2, impuesto=0.05, descuento=0.10)
    # Devuelve todos los resultados en un solo texto
    return (
        " | ".join(partes)
        + f" | Sala con 10% de descuento: {con_descuento}"
        + f" | Sala con 5% de impuesto y 10% de descuento: {con_ambos}"
    )


def sim_cancelar_reserva():
    """Válida 5: cancela una reserva confirmada."""
    # Toma la primera reserva (la que se procesó en la simulación 3)
    reserva = reservas[0]
    # Guarda el estado antes de cancelar
    antes = reserva.estado
    # Cancela la reserva (la primera cancelación sí está permitida)
    reserva.cancelar()
    # Devuelve el cambio de estado
    return f"Reserva {reserva.identificador}: {antes} -> {reserva.estado}"


# ====================== SIMULACIONES NO VÁLIDAS ======================
def sim_cliente_documento_invalido():
    """No válida 1: el documento tiene letras (excepción encadenada)."""
    # El documento no es numérico, por lo que Cliente lanza ClienteInvalidoError
    cliente = Cliente("Laura Gómez", "31x45y", "laura@correo.com")
    # Estas líneas no se alcanzan porque la línea anterior lanza el error
    clientes.append(cliente)
    return cliente.describir()


def sim_servicio_tarifa_invalida():
    """No válida 2: la tarifa por hora no es un número (excepción encadenada)."""
    # La tarifa "gratis" no se puede convertir a número: lanza ServicioInvalidoError
    servicio = ReservaSala("S102", "Sala Auditorio", "gratis", 20)
    # Estas líneas no se alcanzan porque la línea anterior lanza el error
    servicios.append(servicio)
    return servicio.describir()


def sim_reserva_duracion_invalida():
    """No válida 3: la duración está fuera del rango permitido por el servicio."""
    # Una asesoría solo permite de 1 a 4 horas; 9 horas lanza ReservaInvalidaError
    reserva = Reserva("R102", clientes[0], servicios[2], 9)
    # Estas líneas no se alcanzan porque la línea anterior lanza el error
    reservas.append(reserva)
    return reserva.describir()


def sim_servicio_no_disponible():
    """No válida 4: se intenta confirmar una reserva de un servicio no disponible."""
    # Crea un servicio nuevo para no afectar a los demás
    camara = AlquilerEquipo("E102", "Cámara", 15000, 1)
    # Lo marca como no disponible
    camara.disponible = False
    # La reserva se crea bien (2 horas es una duración válida)
    reserva = Reserva("R103", clientes[0], camara, 2)
    # Guarda la reserva; queda en estado "pendiente"
    reservas.append(reserva)
    # Al confirmar, lanza ServicioNoDisponibleError
    reserva.confirmar()
    # Esta línea no se alcanza porque la anterior lanza el error
    return reserva.describir()


def sim_calculo_inconsistente():
    """No válida 5: un descuento de 150 % es un cálculo inconsistente."""
    # El descuento debe estar entre 0 y 1; 1.5 lanza CalculoInconsistenteError
    return servicios[0].calcular_costo_total(3, descuento=1.5)


def ejecutar_simulaciones():
    """Ejecuta las 10 simulaciones, muestra el resumen y lo registra en el log."""
    # Vacía las listas por si la función se llama más de una vez
    clientes.clear()
    servicios.clear()
    reservas.clear()

    # Lista de simulaciones: (número, tipo, descripción, función)
    simulaciones = [
        (1, VALIDA, "Registrar un cliente con datos correctos", sim_registrar_cliente),
        (2, VALIDA, "Crear los tres tipos de servicio", sim_crear_servicios),
        (3, VALIDA, "Crear y procesar una reserva", sim_reserva_exitosa),
        (4, VALIDA, "Calcular costos (polimorfismo y sobrecarga)", sim_calculo_de_costos),
        (5, VALIDA, "Cancelar una reserva confirmada", sim_cancelar_reserva),
        (6, NO_VALIDA, "Registrar cliente con documento inválido", sim_cliente_documento_invalido),
        (7, NO_VALIDA, "Crear servicio con tarifa inválida", sim_servicio_tarifa_invalida),
        (8, NO_VALIDA, "Reserva con duración inválida", sim_reserva_duracion_invalida),
        (9, NO_VALIDA, "Reserva de un servicio no disponible", sim_servicio_no_disponible),
        (10, NO_VALIDA, "Cálculo de costo inconsistente", sim_calculo_inconsistente),
    ]

    # Deja constancia en el log de que la simulación general empezó
    registrar_evento("Inicio de la simulación de Software FJ (10 simulaciones)")
    # Contador de simulaciones que se comportaron como se esperaba
    cumplidas = 0
    # Recorre las simulaciones una por una
    for numero, tipo, descripcion, accion in simulaciones:
        # Si cumple lo esperado, suma una al contador
        if ejecutar_simulacion(numero, tipo, descripcion, accion):
            cumplidas += 1

    # Muestra el resumen final en pantalla
    print("\n========== RESUMEN ==========")
    print(f"Simulaciones ejecutadas: {len(simulaciones)}")
    print(f"Simulaciones con el resultado esperado: {cumplidas} de {len(simulaciones)}")
    print(f"Clientes registrados: {len(clientes)}")
    print(f"Servicios creados: {len(servicios)}")
    print(f"Reservas registradas: {len(reservas)}")
    # Muestra cada reserva con su estado final
    for reserva in reservas:
        print(f"  {reserva.describir()}")
    print(f"Revisa el archivo de logs en: {RUTA_LOGS}")
    # Deja el resumen en el log
    registrar_evento(
        f"Fin de la simulación de Software FJ: {cumplidas} de {len(simulaciones)} "
        f"simulaciones con el resultado esperado"
    )
    # Mensaje final: el programa nunca se detuvo por un error
    print("El programa terminó sin interrupciones.")
    # Devuelve el número de simulaciones cumplidas (útil si otro archivo lo llama)
    return cumplidas


# El programa arranca solo si se ejecuta este archivo directamente
if __name__ == "__main__":
    ejecutar_simulaciones()
