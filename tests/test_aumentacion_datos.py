"""
tests/test_aumentacion_datos.py - Pruebas unitarias para el módulo de aumentación de datos (Fase 3.3).
"""

import unittest
import numpy as np

from src.aumentacion_datos import AumentadorMicroscopia


class TestAumentadorMicroscopia(unittest.TestCase):
    """Casos de prueba para las transformaciones de aumentación en microscopía."""

    def setUp(self) -> None:
        self.aumentador = AumentadorMicroscopia(semilla=42)
        self.imagen_bgr = np.random.randint(50, 200, (100, 100, 3), dtype=np.uint8)

    def test_desenfoque(self) -> None:
        """Verifica la aplicación de desenfoque."""
        res = self.aumentador.aplicar_desenfoque(self.imagen_bgr, intensidad=1.0)
        self.assertEqual(res.shape, self.imagen_bgr.shape)
        self.assertEqual(res.dtype, np.uint8)

    def test_ruido(self) -> None:
        """Verifica la adición de ruido gaussiano."""
        res = self.aumentador.aplicar_ruido(self.imagen_bgr, desviacion_estandar=10.0)
        self.assertEqual(res.shape, self.imagen_bgr.shape)
        self.assertEqual(res.dtype, np.uint8)

    def test_simular_condiciones_reales(self) -> None:
        """Verifica la simulación completa de condiciones reales."""
        res = self.aumentador.simular_condiciones_reales(self.imagen_bgr)
        self.assertEqual(res.shape, self.imagen_bgr.shape)
        self.assertEqual(res.dtype, np.uint8)


if __name__ == "__main__":
    unittest.main()
