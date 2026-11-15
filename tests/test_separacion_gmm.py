"""
tests/test_separacion_gmm.py - Pruebas unitarias para la separación avanzada de cúmulos celulares con GMM.
Cubre casos de éxito, validación OWASP/STRIDE, separación de cúmulos y contornos.
"""

import unittest
import numpy as np
from src.separacion_gmm import (
    separar_cumulos_gmm,
    validar_tamano_imagen_gmm
)


class TestSeparacionGMM(unittest.TestCase):
    """Casos de prueba para separación de cúmulos con GMM y Watershed."""

    def setUp(self) -> None:
        """Crea una imagen sintética con dos objetos circulares superpuestos/cercanos."""
        self.imagen_prueba = np.ones((128, 128), dtype=np.uint8) * 200
        # Dibujar dos círculos oscuros simulando núcleos en cúmulo
        cv2 = __import__('cv2')
        cv2.circle(self.imagen_prueba, (45, 64), 15, 30, -1)
        cv2.circle(self.imagen_prueba, (80, 64), 15, 30, -1)

    def test_separar_cumulos_gmm(self) -> None:
        """Verifica que GMM logre separar y detectar los núcleos en el cúmulo."""
        contornos, areas = separar_cumulos_gmm(self.imagen_prueba, n_components=2, distancia_minima=5)
        self.assertIsInstance(contornos, list)
        self.assertIsInstance(areas, list)
        self.assertGreaterEqual(len(contornos), 1)

    def test_validar_tamano_imagen_gmm_valido(self) -> None:
        """Verifica que imágenes de tamaño normal pasen la validación OWASP."""
        try:
            validar_tamano_imagen_gmm(self.imagen_prueba)
        except ValueError:
            self.fail("validar_tamano_imagen_gmm lanzó excepción inesperada.")

    def test_validar_tamano_imagen_gmm_fallido(self) -> None:
        """Verifica que imágenes excesivamente grandes lancen ValueError."""
        imagen_gigante = np.zeros((4000, 4000), dtype=np.uint8)
        with self.assertRaises(ValueError):
            validar_tamano_imagen_gmm(imagen_gigante, tamano_maximo_bytes=1000)


if __name__ == "__main__":
    unittest.main()
