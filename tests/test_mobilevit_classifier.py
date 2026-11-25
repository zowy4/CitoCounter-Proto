"""
tests/test_mobilevit_classifier.py - Pruebas unitarias para el clasificador MobileViT-S y TTL (CITO-122).
"""

import unittest
import numpy as np
from pathlib import Path
from src.mobilevit_classifier import (
    MobileViTClassifier,
    validar_tamano_imagen_mobilevit
)


class TestMobileViTClassifier(unittest.TestCase):
    """Casos de prueba para MobileViTClassifier y Triple Transfer Learning."""

    def setUp(self) -> None:
        """Configura una imagen de recorte sintética para pruebas."""
        self.recorte_prueba = np.ones((64, 64, 3), dtype=np.uint8) * 150
        self.clasificador = MobileViTClassifier(num_classes=5)

    def test_clasificar_celda(self) -> None:
        """Verifica que la clasificación devuelva una estructura válida con clase y confianza."""
        resultado = self.clasificador.clasificar(self.recorte_prueba)
        self.assertIn("clase", resultado)
        self.assertIn("confianza", resultado)
        self.assertIn("probabilidades", resultado)
        self.assertIn(resultado["clase"], self.clasificador.clases)
        self.assertGreaterEqual(resultado["confianza"], 0.0)
        self.assertLessEqual(resultado["confianza"], 1.0)

    def test_validar_tamano_imagen_valido(self) -> None:
        """Verifica que imágenes de tamaño normal pasen la validación OWASP."""
        try:
            validar_tamano_imagen_mobilevit(self.recorte_prueba)
        except ValueError:
            self.fail("validar_tamano_imagen_mobilevit lanzó excepción inesperada.")

    def test_validar_tamano_imagen_fallido(self) -> None:
        """Verifica que imágenes excesivamente grandes lancen ValueError."""
        imagen_gigante = np.zeros((5000, 5000, 3), dtype=np.uint8)
        with self.assertRaises(ValueError):
            validar_tamano_imagen_mobilevit(imagen_gigante, tamano_maximo_bytes=1000)


if __name__ == "__main__":
    unittest.main()

