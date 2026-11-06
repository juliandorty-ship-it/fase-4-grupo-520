"""Servicios de Software FJ: clase abstracta Servicio y tres servicios especializados."""

from abc import abstractmethod  # Para declarar métodos abstractos

from entidades import EntidadBase
from excepciones import (
    CalculoInconsistenteError,
    ParametroFaltanteError,
    ServicioInvalidoError,
    ServicioNoDisponibleError,
    SoftwareFJError,
)
from logger import registrar_error, registrar_evento

# Impuesto por defecto (IVA 19 %)
IVA = 0.19


class Servicio(EntidadBase):
    """Clase abstracta de la que heredan todos los servicios."""

    def __init__(self, identificador, nombre, tarifa_hora):
        # Inicializa la parte heredada (identificador)
        super().__init__(identificador)
        # Valida que el nombre exista
        if nombre is None or str(nombre).strip() == "":
            raise ParametroFaltanteError("El nombre del servicio es obligatorio")
        self._nombre = str(nombre).strip()
        try:
            # Convierte la tarifa a número decimal
            tarifa = float(tarifa_hora)
        except (TypeError, ValueError) as e:
            # Encadenamiento: conserva el error original como causa
            raise ServicioInvalidoError("La tarifa por hora debe ser un número") from e
        # La tarifa debe ser positiva
        if tarifa <= 0:
            raise ServicioInvalidoError("La tarifa por hora debe ser mayor a 0")
        self._tarifa_hora = tarifa
        # Todo servicio nuevo está disponible
        self._disponible = True

    @property
    def nombre(self):
        return self._nombre

    @property
    def tarifa_hora(self):
        return self._tarifa_hora

    @property
    def disponible(self):
        return self._disponible

    @disponible.setter
    def disponible(self, valor):
        # Solo acepta True o False
        if not isinstance(valor, bool):
            raise ServicioInvalidoError("La disponibilidad debe ser True o False")
        self._disponible = valor

    def verificar_disponibilidad(self):
        """Lanza una excepción si el servicio no está disponible."""
        if not self._disponible:
            raise ServicioNoDisponibleError(
                f"El servicio '{self._nombre}' no está disponible"
            )

    @staticmethod
    def _validar_horas(horas, minimo, maximo, etiqueta):
        """Convierte las horas a número y comprueba que estén en el rango."""
        try:
            horas = float(horas)
        except (TypeError, ValueError) as e:
            raise ServicioInvalidoError("Las horas deben ser un número") from e
        if not minimo <= horas <= maximo:
            raise ServicioInvalidoError(
                f"{etiqueta} permite entre {minimo} y {maximo} horas"
            )
        return horas

    @abstractmethod
    def validar_parametros(self, horas):
        """Valida los parámetros del servicio. Cada hijo la sobrescribe."""

    @abstractmethod
    def calcular_costo(self, horas):
        """Calcula el costo base (sin impuesto). Cada hijo la sobrescribe."""

    def calcular_costo_total(self, horas, impuesto=IVA, descuento=0.0):
        """Costo final. Sobrecarga con parámetros opcionales: impuesto y descuento."""
        # Los parámetros opcionales también se validan
        if not 0 <= descuento < 1:
            raise CalculoInconsistenteError("El descuento debe estar entre 0 y 1")
        if impuesto < 0:
            raise CalculoInconsistenteError("El impuesto no puede ser negativo")
        # Costo base calculado por la clase hija (polimorfismo)
        costo = self.calcular_costo(horas)
        total = costo * (1 - descuento) * (1 + impuesto)
        # Un total menor o igual a cero es un cálculo inconsistente
        if total <= 0:
            raise CalculoInconsistenteError("El costo total calculado es inválido")
        return round(total, 2)


class ReservaSala(Servicio):
    """Servicio de reserva de salas."""

    def __init__(self, identificador, nombre, tarifa_hora, capacidad):
        super().__init__(identificador, nombre, tarifa_hora)
        # La capacidad debe ser un entero mayor a 0
        if not isinstance(capacidad, int) or capacidad <= 0:
            raise ServicioInvalidoError("La capacidad debe ser un entero mayor a 0")
        self._capacidad = capacidad

    @property
    def capacidad(self):
        return self._capacidad

    def validar_parametros(self, horas):
        # Una sala se reserva entre 1 y 8 horas
        return self._validar_horas(horas, 1, 8, "La reserva de sala")

    def calcular_costo(self, horas):
        horas = self.validar_parametros(horas)
        return horas * self._tarifa_hora

    def describir(self):
        return (
            f"Servicio {self.identificador}: {self.nombre} (Reserva de sala) | "
            f"Tarifa/hora: {self.tarifa_hora} | Capacidad: {self.capacidad} personas"
        )


class AlquilerEquipo(Servicio):
    """Servicio de alquiler de equipos."""

    def __init__(self, identificador, nombre, tarifa_hora, cantidad):
        super().__init__(identificador, nombre, tarifa_hora)
        # La cantidad de equipos debe ser un entero mayor a 0
        if not isinstance(cantidad, int) or cantidad <= 0:
            raise ServicioInvalidoError("La cantidad debe ser un entero mayor a 0")
        self._cantidad = cantidad

    @property
    def cantidad(self):
        return self._cantidad

    def validar_parametros(self, horas):
        # Un equipo se alquila entre 1 y 24 horas
        return self._validar_horas(horas, 1, 24, "El alquiler de equipo")

    def calcular_costo(self, horas):
        horas = self.validar_parametros(horas)
        # El costo se multiplica por la cantidad de equipos
        return horas * self._tarifa_hora * self._cantidad

    def describir(self):
        return (
            f"Servicio {self.identificador}: {self.nombre} (Alquiler de equipo) | "
            f"Tarifa/hora: {self.tarifa_hora} | Cantidad: {self.cantidad}"
        )


class AsesoriaEspecializada(Servicio):
    """Servicio de asesoría especializada."""

    # Recargo según el nivel del asesor
    RECARGOS = {"junior": 1.0, "senior": 1.5}

    def __init__(self, identificador, nombre, tarifa_hora, nivel):
        super().__init__(identificador, nombre, tarifa_hora)
        nivel = str(nivel).strip().lower()
        # El nivel solo puede ser junior o senior
        if nivel not in self.RECARGOS:
            raise ServicioInvalidoError("El nivel debe ser 'junior' o 'senior'")
        self._nivel = nivel

    @property
    def nivel(self):
        return self._nivel

    def validar_parametros(self, horas):
        # Una asesoría dura entre 1 y 4 horas
        return self._validar_horas(horas, 1, 4, "La asesoría")

    def calcular_costo(self, horas):
        horas = self.validar_parametros(horas)
        # El asesor senior cuesta 50 % más
        return horas * self._tarifa_hora * self.RECARGOS[self._nivel]

    def describir(self):
        return (
            f"Servicio {self.identificador}: {self.nombre} (Asesoría especializada) | "
            f"Tarifa/hora: {self.tarifa_hora} | Nivel: {self.nivel}"
        )


# Prueba rápida: solo se ejecuta si corres este archivo directamente
if __name__ == "__main__":
    # Tres servicios válidos, uno de cada tipo
    sala = ReservaSala("S001", "Sala Ejecutiva", 50000, 10)
    equipo = AlquilerEquipo("E001", "Proyector", 20000, 2)
    asesoria = AsesoriaEspecializada("A001", "Asesoría en redes", 80000, "senior")

    # Polimorfismo: el mismo código funciona con los tres servicios
    for servicio, horas in [(sala, 3), (equipo, 4), (asesoria, 2)]:
        print(servicio.describir())
        print(f"Costo base {horas} horas: {servicio.calcular_costo(horas)}")
        registrar_evento(f"Servicio creado: {servicio.identificador}")

    # Sobrecarga: variantes de calcular_costo_total
    print(f"Costo con IVA: {sala.calcular_costo_total(3)}")
    print(f"Costo con 10% de descuento: {sala.calcular_costo_total(3, descuento=0.10)}")

    # Casos con error: el programa continúa después de cada uno
    try:
        ReservaSala("S002", "Sala Pequeña", -100, 5)
    except SoftwareFJError as e:
        registrar_error("Error al crear servicio", e)
        print(f"Error capturado: {e.mensaje}")

    try:
        sala.calcular_costo(12)
    except SoftwareFJError as e:
        registrar_error("Error al calcular costo", e)
        print(f"Error capturado: {e.mensaje}")

    try:
        sala.disponible = False
        sala.verificar_disponibilidad()
    except SoftwareFJError as e:
        registrar_error("Servicio no disponible", e)
        print(f"Error capturado: {e.mensaje}")