# Software FJ: Sistema Integral de Gestión de Clientes, Servicios y Reservas

Proyecto del componente práctico (Fase 4) del curso.
Es un sistema orientado a objetos en Python, sin base de datos que gestiona clientes,
servicios y reservas para la empresa ficticia *Software FJ*. Su énfasis está en el
**manejo avanzado de excepciones**: el programa sigue funcionando aunque haya datos
inválidos, servicios no disponibles u operaciones no permitidas, y cada error queda
registrado en un archivo de logs.

## Integrantes

Grupo 213023_520

- Ariel Felipe Gomez Rozo
- Diego Fernando Rojas Méndez
- Julio Cesar Jerez

Tutor: Jorge Eduardo Ospina

## Requisitos

- Python 3.8 o superior.
- No se necesita instalar ninguna librería externa: solo se usan módulos estándar
  (`abc`, `re`, `logging`, `os`).

## Estructura del proyecto

| Archivo | Contenido |
|---|---|
| `excepciones.py` | Excepción base `SoftwareFJError` y sus excepciones personalizadas |
| `logger.py` | Configuración del logger y funciones `registrar_evento()` y `registrar_error()` |
| `entidades.py` | Clase abstracta `EntidadBase` y clase `Cliente` |
| `servicios.py` | Clase abstracta `Servicio` y los servicios `ReservaSala`, `AlquilerEquipo` y `AsesoriaEspecializada` |
| `reserva.py` | Clase `Reserva` (confirmar, cancelar y procesar) |
| `simulacion.py` | 10 simulaciones: 5 válidas y 5 no válidas |
| `main.py` | Programa principal: simula 15 operaciones del sistema |
| `logs.txt` | Archivo donde se registran los eventos y errores |

## Cómo ejecutarlo

Desde una terminal, dentro de la carpeta del proyecto:

```bash
# Programa principal (15 operaciones)
python main.py

# Las 10 simulaciones (5 válidas y 5 no válidas)
python simulacion.py
```

Cada módulo también incluye una prueba rápida que se ejecuta solo al correr ese archivo
directamente, por ejemplo `python servicios.py` o `python reserva.py`.

Al terminar, revisa el archivo `logs.txt`: allí queda cada evento y cada error con su fecha,
su nivel (`INFO` o `ERROR`) y su mensaje.

## Diseño orientado a objetos

```
EntidadBase (abstracta)
├── Cliente
├── Servicio (abstracta)
│   ├── ReservaSala
│   ├── AlquilerEquipo
│   └── AsesoriaEspecializada
└── Reserva
```

### Clases principales

- **`EntidadBase`** (abstracta): guarda el identificador y obliga a las clases hijas a
  implementar `describir()`.
- **`Cliente`**: guarda nombre, correo y teléfono como atributos privados, con propiedades
  (`@property`) y validaciones:
  - Nombre: solo letras y espacios, mínimo 3 caracteres.
  - Correo: formato `texto@texto.texto`.
  - Teléfono: solo dígitos, entre 7 y 10.
- **`Servicio`** (abstracta): define los métodos abstractos `validar_parametros()` y
  `calcular_costo()`, y el método `calcular_costo_total()` con impuesto y descuento opcionales.
- **`ReservaSala`**: de 1 a 8 horas. Tiene capacidad de personas.
- **`AlquilerEquipo`**: de 1 a 24 horas. El costo se multiplica por la cantidad de equipos.
- **`AsesoriaEspecializada`**: de 1 a 4 horas. El asesor `senior` cuesta 50 % más que el `junior`.
- **`Reserva`**: integra cliente, servicio, duración y estado (`pendiente`, `confirmada` o
  `cancelada`). Implementa `confirmar()`, `cancelar()`, `calcular_costo()` y `procesar()`.

### Cálculo de costos

```
costo_total = costo_base × (1 − descuento) × (1 + impuesto)
```

El impuesto por defecto es el IVA (19 %) y el descuento por defecto es 0. El descuento debe
estar entre 0 y 1, y el impuesto no puede ser negativo.

## Principios de programación orientada a objetos

| Principio | Dónde se aplica |
|---|---|
| **Abstracción** | `EntidadBase` y `Servicio` son clases abstractas (`ABC` y `@abstractmethod`) |
| **Herencia** | `Cliente`, `Servicio` y `Reserva` heredan de `EntidadBase`; los tres servicios heredan de `Servicio` |
| **Polimorfismo** | `calcular_costo()`, `validar_parametros()` y `describir()` se sobrescriben en cada servicio y se usan con el mismo código |
| **Encapsulación** | Atributos privados (`_nombre`, `_correo`, `_estado`…) con propiedades y validaciones en los setters |
| **Sobrecarga** | Python no la tiene de forma nativa; se simula con parámetros opcionales en `calcular_costo_total()` y `Reserva.calcular_costo()` |

## Manejo de excepciones

### Excepciones personalizadas

Todas heredan de `SoftwareFJError`:

| Excepción | Cuándo se lanza |
|---|---|
| `ClienteInvalidoError` | Datos de cliente inválidos |
| `ParametroFaltanteError` | Falta un parámetro obligatorio |
| `ServicioInvalidoError` | Parámetros de servicio incorrectos |
| `ServicioNoDisponibleError` | El servicio no está disponible |
| `ReservaInvalidaError` | La reserva no se puede crear o procesar |
| `OperacionNoPermitidaError` | Operación no permitida (por ejemplo, cancelar dos veces) |
| `CalculoInconsistenteError` | Un cálculo de costos da un resultado inválido |

### Técnicas usadas

- **`try/except`**: captura de errores propios del sistema.
- **`try/except/else/finally`**: en `Reserva.procesar()`, `ejecutar_operacion()` de `main.py` y
  `ejecutar_simulacion()` de `simulacion.py`.
- **Encadenamiento de excepciones (`raise ... from e`)**: conserva la causa original del error.
  Se usa, por ejemplo, cuando el teléfono tiene letras, cuando la tarifa no es un número y
  cuando la duración de una reserva es inválida.
- **Captura de errores inesperados** con `except Exception`, para que el programa no se
  detenga nunca.

## Archivo de logs

`logger.py` crea el archivo `logs.txt` en la carpeta del proyecto. Cada línea tiene el
formato:

```
fecha y hora | NIVEL | mensaje
```

Si una excepción fue encadenada, el log guarda también la **causa original**.

## Simulaciones

**`simulacion.py`** ejecuta 10 simulaciones, sin base de datos y sin que un error detenga el programa:

| # | Tipo | Simulación |
|---|---|---|
| 1 | Válida | Registrar un cliente correcto |
| 2 | Válida | Crear los tres tipos de servicio |
| 3 | Válida | Crear y procesar una reserva |
| 4 | Válida | Calcular costos (polimorfismo y sobrecarga) |
| 5 | Válida | Cancelar una reserva confirmada |
| 6 | No válida | Cliente con teléfono con letras |
| 7 | No válida | Servicio con tarifa que no es un número |
| 8 | No válida | Reserva con duración fuera de rango |
| 9 | No válida | Reserva de un servicio no disponible |
| 10 | No válida | Descuento de 150 % (cálculo inconsistente) |

Al final se muestra cuántas simulaciones tuvieron el resultado esperado.

**`main.py`** simula 15 operaciones adicionales (clientes, servicios, reservas y cálculos,
válidos e inválidos) y muestra un resumen final.

## Información académica

Universidad Nacional Abierta y a Distancia (UNAD). Escuela de Ciencias Básicas, Tecnología e
Ingeniería (ECBTI). Curso: Programación (código 213023). Noviembre de 2026.
