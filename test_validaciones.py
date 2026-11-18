"""Pruebas de regresión de reservas, cálculos y simulaciones."""

import math
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

from cliente import Cliente
from excepciones import CalculoInconsistenteError, SoftwareFJError
from reserva import Reserva
from servicio import AlquilerEquipo, AsesoriaEspecializada, ReservaSala


class PruebasValidaciones(unittest.TestCase):
    def setUp(self):
        self.cliente = Cliente('Ana Perez', '1020304050', 'ana@correo.com')
        self.sala = ReservaSala('S1', 'Sala', 50000, 10)

    def reserva(self, identificador):
        return Reserva(identificador, self.cliente, self.sala, 2)

    def test_confirmacion_exclusiva_y_liberacion(self):
        primera = self.reserva('R1')
        segunda = self.reserva('R2')
        primera.confirmar()
        self.assertFalse(self.sala.disponible)
        with self.assertRaises(SoftwareFJError):
            segunda.confirmar()
        self.assertEqual(segunda.estado, 'pendiente')
        primera.cancelar()
        self.assertTrue(self.sala.disponible)
        segunda.confirmar()
        self.assertEqual(segunda.estado, 'confirmada')
        with self.assertRaises(SoftwareFJError):
            primera.cancelar()
        self.assertFalse(self.sala.disponible)

    def test_cancelar_pendiente_no_libera_otro_servicio_ocupado(self):
        primera = self.reserva('R1')
        pendiente = self.reserva('R2')
        primera.confirmar()
        pendiente.cancelar()
        self.assertEqual(pendiente.estado, 'cancelada')
        self.assertFalse(self.sala.disponible)
        with self.assertRaises(SoftwareFJError):
            pendiente.confirmar()

    def test_costo_fallido_no_confirma(self):
        reserva = self.reserva('R1')
        with patch.object(self.sala, 'calcular_costo_total', side_effect=CalculoInconsistenteError('Costo inválido')):
            self.assertFalse(reserva.procesar())
        self.assertEqual(reserva.estado, 'pendiente')
        self.assertTrue(self.sala.disponible)

    def test_tarifas_horas_y_cantidades_invalidas(self):
        for valor in [math.nan, math.inf, -math.inf, True, None, 'abc', 0, -1]:
            with self.subTest(valor=valor):
                with self.assertRaises(SoftwareFJError):
                    ReservaSala('X', 'Sala', valor, 10)
                with self.assertRaises(SoftwareFJError):
                    self.sala.calcular_costo(valor)
        with self.assertRaises(SoftwareFJError):
            ReservaSala('X', 'Sala', 100, True)
        with self.assertRaises(SoftwareFJError):
            AlquilerEquipo('X', 'Equipo', 100, True)

    def test_impuestos_descuentos_y_resultados_invalidos(self):
        for valor in [math.nan, math.inf, -math.inf, True, None, 'abc', -1]:
            for parametro in ['impuesto', 'descuento']:
                with self.subTest(valor=valor, parametro=parametro):
                    with self.assertRaises(SoftwareFJError):
                        self.sala.calcular_costo_total(2, **{parametro: valor})
        with self.assertRaises(SoftwareFJError):
            self.sala.calcular_costo_total(2, descuento=1)
        with self.assertRaises(SoftwareFJError):
            ReservaSala('X', 'Sala', 1e308, 10).calcular_costo_total(8)
        with self.assertRaises(SoftwareFJError):
            ReservaSala('X', 'Sala', 0.0001, 10).calcular_costo_total(1)

    def test_costos_validos_de_tres_servicios(self):
        self.assertEqual(self.sala.calcular_costo_total(3), 178500)
        self.assertEqual(self.sala.calcular_costo_total(3, descuento=.1), 160650)
        equipo = AlquilerEquipo('E1', 'Equipo', 20000, 2)
        asesoria = AsesoriaEspecializada('A1', 'Redes', 80000, 'senior')
        self.assertEqual(equipo.calcular_costo_total(4), 190400)
        self.assertEqual(asesoria.calcular_costo_total(2), 285600)

    def test_simulacion_diez_casos(self):
        resultado = self.ejecutar('simulacion.py')
        self.assertIn('Simulaciones con el resultado esperado: 10 de 10', resultado)
        self.assertNotIn('ERROR inesperado:', resultado)
        self.assertIn('cliente con documento inválido', resultado)

    def test_programa_principal_quince_operaciones(self):
        resultado = self.ejecutar('main.py')
        self.assertEqual(resultado.count('--- Operación '), 15)
        self.assertNotIn('ERROR inesperado:', resultado)
        self.assertIn('El programa terminó sin interrupciones.', resultado)

    def ejecutar(self, archivo):
        raiz = Path(__file__).resolve().parent
        proceso = subprocess.run([sys.executable, archivo], cwd=raiz, capture_output=True,
                                 text=True, timeout=15)
        self.assertEqual(proceso.returncode, 0, proceso.stderr)
        return proceso.stdout


if __name__ == '__main__':
    unittest.main()
