"""Clase abstracta base y clase Cliente del sistema Software FJ."""

import re  # Módulo para validar textos con expresiones regulares
from abc import ABC, abstractmethod  # Herramientas para crear clases abstractas

from excepciones import (
    ClienteInvalidoError,
    ParametroFaltanteError,
    SoftwareFJError,
)


class EntidadBase(ABC):
    """Clase abstracta que representa entidades generales del sistema."""

    def __init__(self, identificador):
        # Valida que el identificador no sea None ni esté vacío
        if identificador is None or str(identificador).strip() == "":
            raise ParametroFaltanteError("El identificador es obligatorio")
        # Atributo privado (encapsulación)
        self._identificador = str(identificador).strip()

    @property
    def identificador(self):
        """Devuelve el identificador (solo lectura)."""
        return self._identificador

    @abstractmethod
    def describir(self):
        """Devuelve una descripción en texto. Cada clase hija la implementa."""

    def __str__(self):
        # Al imprimir el objeto se muestra su descripción
        return self.describir()


class Cliente(EntidadBase):
    """Cliente de Software FJ con validaciones y datos personales encapsulados."""

    def __init__(self, nombre, documento, correo):
        # El documento es el identificador del cliente; se valida antes de heredar
        super().__init__(self.validar_documento(documento))
        # Asigna nombre y correo; los setters ejecutan sus validaciones
        self.set_nombre(nombre)
        self.set_correo(correo)

    # ---------- Validaciones ----------
    @staticmethod
    def validar_nombre(valor):
        """Valida el nombre y lo devuelve sin espacios sobrantes."""
        # Parámetro faltante
        if valor is None or str(valor).strip() == "":
            raise ParametroFaltanteError("El nombre es obligatorio")
        valor = str(valor).strip()
        # Solo letras y espacios, mínimo 3 caracteres
        if not re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúÑñÜü ]{3,}", valor):
            raise ClienteInvalidoError(f"Nombre inválido: '{valor}'")
        return valor

    @staticmethod
    def validar_documento(valor):
        """Valida el documento y lo devuelve sin espacios sobrantes."""
        if valor is None or str(valor).strip() == "":
            raise ParametroFaltanteError("El documento es obligatorio")
        valor = str(valor).strip()
        try:
            # Intenta convertir a número para comprobar que hay dígitos
            int(valor)
        except ValueError as e:
            # Encadenamiento de excepciones: conserva el error original como causa
            raise ClienteInvalidoError(
                "El documento solo debe contener números"
            ) from e
        # isdigit descarta signos y guiones bajos que int() sí acepta
        if not valor.isdigit():
            raise ClienteInvalidoError("El documento solo debe contener números")
        # Longitud permitida: entre 5 y 12 dígitos
        if not 5 <= len(valor) <= 12:
            raise ClienteInvalidoError("El documento debe tener entre 5 y 12 dígitos")
        return valor

    @staticmethod
    def validar_correo(valor):
        """Valida el correo y lo devuelve sin espacios sobrantes."""
        if valor is None or str(valor).strip() == "":
            raise ParametroFaltanteError("El correo es obligatorio")
        valor = str(valor).strip()
        # Formato básico: texto@texto.texto
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", valor):
            raise ClienteInvalidoError(f"Correo electrónico inválido: '{valor}'")
        return valor

    # ---------- Getters y setters ----------
    def get_nombre(self):
        return self._nombre

    def set_nombre(self, valor):
        # Guarda el nombre solo si pasa la validación
        self._nombre = self.validar_nombre(valor)

    def get_documento(self):
        return self._identificador

    def set_documento(self, valor):
        # El documento es el identificador del cliente
        self._identificador = self.validar_documento(valor)

    def get_correo(self):
        return self._correo

    def set_correo(self, valor):
        # Guarda el correo solo si pasa la validación
        self._correo = self.validar_correo(valor)

    # Propiedades: permiten usar cliente.nombre, cliente.documento y cliente.correo
    nombre = property(get_nombre, set_nombre)
    documento = property(get_documento, set_documento)
    correo = property(get_correo, set_correo)

    def describir(self):
        """Implementación del método abstracto de EntidadBase."""
        return f"Cliente {self.documento}: {self.nombre} | {self.correo}"

    def mostrar_datos(self):
        """Muestra en pantalla los datos del cliente."""
        print(self.describir())


# Prueba rápida: solo se ejecuta si corres este archivo directamente
if __name__ == "__main__":
    # Caso 1: cliente válido
    cliente = Cliente("Ana Pérez", "1020304050", "ana@correo.com")
    cliente.mostrar_datos()

    # Caso 2: correo inválido
    try:
        Cliente("Luis Gómez", "1098765432", "luis#correo")
    except SoftwareFJError as e:
        print(f"Error capturado: {e.mensaje}")

    # Caso 3: documento con letras (excepción encadenada)
    try:
        Cliente("Marta Ruiz", "abc123", "marta@correo.com")
    except SoftwareFJError as e:
        print(f"Error capturado: {e.mensaje}")
        print(f"  Causa original: {type(e.__cause__).__name__}: {e.__cause__}")

    # Caso 4: nombre vacío
    try:
        Cliente("", "1020304050", "pedro@correo.com")
    except SoftwareFJError as e:
        print(f"Error capturado: {e.mensaje}")