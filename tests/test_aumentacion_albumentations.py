"""
tests/test_aumentacion_albumentations.py - Pruebas unitarias para el módulo de aumentación con Albumentations.
Cubre casos de éxito, validación OWASP/STRIDE, conversión uint8 y transformaciones.
"""

import unittest
import numpy as np
from src.aumentacion_albumentations import (
    aplicar_aumentacion_albumentations,
    crear_pipeline_aumentacion_microscopia,
    validar_tamano_imagen
)


class TestAumentacionAlbumentations(unittest.TestCase):
    """Casos de prueba para aumentación con Albumentations."""

    def setUp(self) -> None:
        """Configuración inicial para las pruebas."""
        self.imagen_prueba = np.random.randint(0, 256, (128, 128, 3), dtype=np.uint8)

    def test_aplicar_aumentacion_albumentations(self) -> None:
        """Verifica que la aumentación devuelva un arreglo numpy uint8 válido."""
        resultado = aplicar_aumentacion_albumentations(self.imagen_prueba, probabilidad=1.0)
        self.assertIsInstance(resultado, np.ndarray)
        self.assertEqual(resultado.dtype, np.uint8)
        self.assertEqual(resultado.shape, self.imagen_prueba.shape)

    def test_validar_tamano_imagen_exitoso(self) -> None:
        """Verifica que imágenes pequeñas pasen la validación OWASP."""
        try:
            validar_tamano_imagen(self.imagen_prueba)
        except ValueError:
            self.fail("validar_tamano_imagen lanzó una excepción inesperada para una imagen válida.")

    def test_validar_tamano_imagen_fallido(self) -> None:
        """Verifica que imágenes gigantescas lancen ValueError por seguridad."""
        imagen_grande = np.zeros((5000, 5000, 3), dtype=np.uint8)
        with self.assertRaises(ValueError):
            validar_tamano_imagen(imagen_grande, tamano_maximo_bytes=1000)

    def test_pipeline_creacion(self) -> None:
        """Verifica que el pipeline se cree correctamente."""
        pipeline = crear_pipeline_aumentacion_microscopia(p=0.5)
        self.assertIsNotNone(pipeline)


if __name__ == "__main__":
    unittest.main()

