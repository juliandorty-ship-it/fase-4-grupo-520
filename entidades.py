"""Entidades del sistema Software FJ: clase abstracta base y Cliente."""

import re  # Módulo para validar textos con expresiones regulares
from abc import ABC, abstractmethod  # Herramientas para crear clases abstractas

from excepciones import ClienteInvalidoError, ParametroFaltanteError
from logger import registrar_error, registrar_evento


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

    def __init__(self, identificador, nombre, correo, telefono):
        # Inicializa la parte heredada (identificador)
        super().__init__(identificador)
        # Al asignar, se ejecutan los setters con sus validaciones
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono

    # ---------- Nombre ----------
    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        # Parámetro faltante
        if valor is None or str(valor).strip() == "":
            raise ParametroFaltanteError("El nombre es obligatorio")
        valor = str(valor).strip()
        # Solo letras y espacios, mínimo 3 caracteres
        if not re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúÑñÜü ]{3,}", valor):
            raise ClienteInvalidoError(f"Nombre inválido: '{valor}'")
        self._nombre = valor

    # ---------- Correo ----------
    @property
    def correo(self):
        return self._correo

    @correo.setter
    def correo(self, valor):
        if valor is None or str(valor).strip() == "":
            raise ParametroFaltanteError("El correo es obligatorio")
        valor = str(valor).strip()
        # Formato básico: texto@texto.texto
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", valor):
            raise ClienteInvalidoError(f"Correo electrónico inválido: '{valor}'")
        self._correo = valor

    # ---------- Teléfono ----------
    @property
    def telefono(self):
        return self._telefono

    @telefono.setter
    def telefono(self, valor):
        if valor is None or str(valor).strip() == "":
            raise ParametroFaltanteError("El teléfono es obligatorio")
        valor = str(valor).strip()
        try:
            # Intenta convertir a número para comprobar que solo hay dígitos
            int(valor)
        except ValueError as e:
            # Encadenamiento de excepciones: conserva el error original como causa
            raise ClienteInvalidoError(
                "El teléfono solo debe contener números"
            ) from e
        # Longitud permitida: entre 7 y 10 dígitos
        if not 7 <= len(valor) <= 10:
            raise ClienteInvalidoError("El teléfono debe tener entre 7 y 10 dígitos")
        self._telefono = valor

    def describir(self):
        """Implementación del método abstracto de EntidadBase."""
        return (
            f"Cliente {self.identificador}: {self.nombre} | "
            f"{self.correo} | {self.telefono}"
        )


# Prueba rápida: solo se ejecuta si corres este archivo directamente
if __name__ == "__main__":
    # Caso 1: cliente válido
    try:
        cliente = Cliente("C001", "Ana Pérez", "ana@correo.com", "3001234567")
        print(cliente)
        registrar_evento(f"Cliente creado: {cliente.identificador}")
    except (ClienteInvalidoError, ParametroFaltanteError) as e:
        registrar_error("Error al crear cliente", e)

    # Caso 2: correo inválido
    try:
        Cliente("C002", "Luis Gómez", "luis#correo", "3109876543")
    except (ClienteInvalidoError, ParametroFaltanteError) as e:
        registrar_error("Error al crear cliente", e)
        print(f"Error capturado: {e.mensaje}")

    # Caso 3: teléfono con letras (excepción encadenada)
    try:
        Cliente("C003", "Marta Ruiz", "marta@correo.com", "abc123")
    except (ClienteInvalidoError, ParametroFaltanteError) as e:
        registrar_error("Error al crear cliente", e)
        print(f"Error capturado: {e.mensaje}")